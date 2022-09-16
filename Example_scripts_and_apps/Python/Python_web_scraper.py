from chalice import Chalice
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

app = Chalice(app_name='EskomLoadShedding')


#HELPER Functions - called in actual API routes

#get current stage
def get_stage():
    print("Getting Current Load Shedding Stage")
    # GetStage Endpoint
    URL = "http://loadshedding.eskom.co.za/LoadShedding/GetStatus"
    r = requests.get(url = URL)
    data = r.json()
    stage = data -1
    return stage

#scrape the schedule based on area and stage
#example ESKOM CALL:
# first number is suburb ID
# second is stage (only 1-4 at this time)
# 3rd appears to relate to province but appears to have no effect but fails if empty
# 4th also appears to have no known reason or effect but fails if empty
# http://loadshedding.eskom.co.za/LoadShedding/GetScheduleM/1020663/2/3/8
def get_schedule(area_id,stage):
    uri = "http://loadshedding.eskom.co.za/LoadShedding/GetScheduleM/" + area_id + "/" + stage + "/3/8"
    data_raw = requests.get(uri)
    soup = BeautifulSoup(data_raw.text, 'html.parser')
    days = soup.find_all(class_='scheduleDay')
    # we need this to prefix the year onto the date from eskom (needed in other functions)
    now = datetime.now()

    data_dict = {}

    for day in days:
        day_obj = day.find_all('div')
        #Wed, 11 Mar
        # TODO fix case for new year....
        date_str = str(now.year) + " " + day_obj[0].text.strip()
        #date = datetime.strptime(date_str, '%Y %a, %d %b')

        shedding_list = day.find_all('div')
        #SKIP first item in each list - its the date we grabbed it above - here is purely iterating over the actual load shedding windows
        shedding_iterator = iter(shedding_list)
        next(shedding_iterator)

        # day list
        day_dict = {}
        count = 1
        for item in shedding_iterator:
            #build a list of starts and stops
            # item 0 and 2 is start and end
            # TODO convert the strings to times
            shedding_window =  item.text.strip().split()
            if len(shedding_window) > 2:
                day_dict[count] = {'start': shedding_window[0], 'end': shedding_window[2]}
            #print(item.text.strip().split())
            count += 1

        data_dict[date_str] = day_dict

    return data_dict

def next_shedding_window(area_id,stage):
    #get schedule for the area and stage
    # iterate over dates/windows until we have a suitable match and break
    # pull out start time and end time and calculate
    # if current time < start time then calc hours
    # if current time > start time and less than end time then 0
    # if current time > start time and > end time, look for next window
    #return an object of various parameters:
    # date, start time, end time, hours until, minutes until, seconds until

    now = datetime.now()
    schedule = get_schedule(area_id,stage)

    for day in schedule:
        if len(schedule[day]) > 0:
            #load shedding happens on this day - extract it and check date/time for future/past
            date = datetime.strptime(day, '%Y %a, %d %b')
            #print(date)
            #extract the windows and work out relative position to NOW for start and then end - iterate until we find a complete match
            i = 1
            while i <= len(schedule[day]):
                #this day has shedding windows so now we need to calculate it
                # get start and end to do the maths
                hours_until_window = 0
                minutes_until_window = 0
                seconds_until_window = 0
                start_time = schedule[day][i]['start']
                end_time = schedule[day][i]['end']
                window_start = datetime.strptime(day + ' ' + schedule[day][i]['start'], '%Y %a, %d %b %H:%M')
                window_end = datetime.strptime(day + ' ' + schedule[day][i]['end'], '%Y %a, %d %b %H:%M')
                #print(now)
                #print(window_start, window_end)

                time_delta_start = window_start - now
                time_delta_end = window_end - now

                #if delta to start is negative, check delta to end greater than zero
                # If both negative - discount it and move on
                # if one is negative - set time to window = 0
                # if start is positive = time to windw

                if window_start > now:
                    print("this window is in future so setting values")
                    hours_until_window = time_delta_start.total_seconds() / 3600
                    minutes_until_window = time_delta_start.total_seconds() / 60
                    seconds_until_window = time_delta_start.total_seconds()
                elif window_end > now:
                    # set to 0 we are in the window
                    print("this window is live so setting values to 0")
                    hours_until_window = 0
                    minutes_until_window = 0
                    seconds_until_window = 0
                else:
                    # this is a dud window
                    # test for this and break
                    print("this window is in the past, iterating")
                    hours_until_window = -1

                # if hours_until_window is -1 we need to iterate, anything else breaks out
                print(hours_until_window)
                i += 1
                if (hours_until_window == -1): continue

                print("we reached this point now to return data")
                result = {"date":str(date), "start_time":start_time, "end_time":end_time, "hours_to_start":hours_until_window, "minutes_to_start":minutes_until_window, "seconds_to_start":seconds_until_window}
                return result
                           
        # else: no load shedding skip processing to next day
        else:
            continue
        
        # if we have data from above calculate the metrics and output it
        
@app.route('/')
def index():
    return {'hello': 'world'}

# Gets the Current Eskom Load Shedding Stage from Eskom API and presents it as an Int
# 0 - no Load shedding, 1-8 Stage 1-8
@app.route('/Stage')
def current_stage():
    stage = get_stage()
    return stage

#get full available schedule for an area and stage
@app.route('/Schedule/{area_id}/{stage}')
def get_full_schedule(area_id,stage):
    return get_schedule(area_id,stage)

#get full available schedule for an area and current stage
@app.route('/Schedule/{area_id}')
def get_full_schedule_current_stage(area_id):
    stage = str(get_stage())
    return get_schedule(area_id,stage)

#Gets the Next Shedding window for a given Area ID and Load Shedding Stage
@app.route('/NextShedding/{area_id}/{stage}')
def next_shedding_stage(area_id,stage):
    return next_shedding_window(area_id,stage)

#Gets next shedding when stage is not supplied (dynamically go and get current stage)
@app.route('/NextShedding/{area_id}')
def next_shedding(area_id):
    stage = str(get_stage())
    return next_shedding_window(area_id,stage)