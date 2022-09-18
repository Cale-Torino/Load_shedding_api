using LoadShedding.NET.Clients;
using LoadShedding.NET.Objects;
using System.Windows.Forms;

namespace Eskom_API_Example
{
    //https://github.com/IsaTippens/LoadShedding.NET
    public partial class Form1 : Form
    {
        //Create instance
        readonly EskomLoadSheddingClient ELSC = new();
        public Form1()
        {
            InitializeComponent();
        }

        private async void Form1_Load(object sender, EventArgs e)
        {
            bool ils = await ELSC.IsLoadShedding();
            richTextBox.AppendText($"{ils}\n");
        }

        private async void GetMunicipalities()
        {
            List<LoadShedding.NET.Objects.Municipality> i = await ELSC.GetMunicipalities(LoadShedding.NET.Provinces.KwaZuluNatal);
            foreach (var item in i)
            {
                richTextBox.AppendText($"{item.Name}, {item.ID}\n");
            }
        }

        private async void Get()
        {
            HttpResponseMessage i = await ELSC.Get("https://github.com/IsaTippens/LoadShedding.NET");
            richTextBox.AppendText($"{i.Headers}\n");
        }

        private async void GetScheduleData()
        {
            string i = await ELSC.GetScheduleData(63591, 4, 9);
            richTextBox.AppendText($"{i}\n");
        }

        private async void GetSuburbsData()
        {
            Municipality m = new Municipality();
            string i = await ELSC.GetSuburbsData(m);
            richTextBox.AppendText($"{i}\n");
        }

        private void Test_button_Click(object sender, EventArgs e)
        {
            richTextBox.Clear();
            //GetMunicipalities();
            //Get();
            //GetScheduleData();
            GetSuburbsData();
        }
    }
}