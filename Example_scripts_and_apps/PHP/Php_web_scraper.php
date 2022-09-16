<?php
$request_time = time();
$timer=(10 * 60);

function write2db($time2db, $rate2db) {
$data = array(
    'timestamp' => $time2db,
    'loadshedding_status' => $rate2db,
);
$data = json_encode($data);
file_put_contents('data.db', $data);
}

$loaded_data = file_get_contents('data.db' );
$data = json_decode($loaded_data, TRUE);
$timestamp = $data["timestamp"];   //
$loadshedding_status = $data["loadshedding_status"]; 

if ($timestamp + $timer <= $request_time){
    $loadshedding_status = getLoadshedding();
    if (!empty($loadshedding_status)){

    write2db($request_time, $loadshedding_status);
    }
    else {
    write2db($request_time, '');
    }
}
if (!empty($loadshedding_status)){
    echo $loadshedding_status;
}
    
function getLoadshedding() {
  // Get loadshedding status live from eskom

$url = "https://loadshedding.eskom.co.za/LoadShedding/GetStatus?_=".$request_time;
$page_content = get_web_page($url);
$page_content = mb_convert_encoding($page_content, 'HTML-ENTITIES', "UTF-8");
return $page_content["content"];
}

   /**
     * Get a web file (HTML, XHTML, XML, image, etc.) from a URL.  Return an
     * array containing the HTTP server response header fields and content.
     */
    function get_web_page($url)
    {
        $user_agent='Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_7 rv:2.0) Gecko/20130831 Firefox/35.0';

        $options = array(

            CURLOPT_CUSTOMREQUEST  =>"GET",        //set request type post or get
            CURLOPT_POST           =>false,        //set to GET
            CURLOPT_USERAGENT      => $user_agent, //set user agent
            CURLOPT_COOKIEFILE     =>"cookie.txt", //set cookie file
            CURLOPT_COOKIEJAR      =>"cookie.txt", //set cookie jar
            CURLOPT_RETURNTRANSFER => true,     // return web page
            CURLOPT_HEADER         => false,    // don't return headers
            CURLOPT_FOLLOWLOCATION => true,     // follow redirects
            CURLOPT_ENCODING       => "",       // handle all encodings
            CURLOPT_AUTOREFERER    => true,     // set referer on redirect
            CURLOPT_CONNECTTIMEOUT => 120,      // timeout on connect
            CURLOPT_TIMEOUT        => 120,      // timeout on response
            CURLOPT_MAXREDIRS      => 10,       // stop after 10 redirects
        );

        $ch      = curl_init( $url );
        curl_setopt_array( $ch, $options );
        $content = curl_exec( $ch );
        $err     = curl_errno( $ch );
        $errmsg  = curl_error( $ch );
        $header  = curl_getinfo( $ch );
        curl_close( $ch );

        $header['errno']   = $err;
        $header['errmsg']  = $errmsg;
        $header['content'] = $content;
        return $header;
    }
?>