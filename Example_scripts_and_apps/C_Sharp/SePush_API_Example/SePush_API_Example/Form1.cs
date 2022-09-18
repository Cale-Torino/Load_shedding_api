using helloserve.SePush;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;

namespace SePush_API_Example
{ 
    public partial class Form1 : Form
    {
        private SePushClient sePushclient;
        private SePushOptions options = new();
        private Mock<IOptionsMonitor<SePushOptions>> optionsMock = new();
        private Mock<ILogger<SePushClient>> loggerMock = new();
        public Form1()
        {
            InitializeComponent();
        }

        public void Setup()
        {
            IConfiguration config = new ConfigurationBuilder()
                .AddInMemoryCollection()
                .Build();

            options.Token = "fzizvRSAOvkrlqFgk09r";//fzizvRSAOvkrlqFgk09r yourtokengoeshere

            optionsMock.SetupGet(x => x.CurrentValue).Returns(options);

            sePushclient = new SePushClient(optionsMock.Object, loggerMock.Object);
        }
        private void Form1_Load(object sender, EventArgs e)
        {
            Setup();
        }

        private async void Status()
        {
            //act
            try
            {
                var result = await sePushclient.StatusAsync();

                var areas = await sePushclient.AreasSearchAsync("Cape Town");

                richTextBox.AppendText($"IsLoadshedding? : {result.Eskom}\n");

                foreach (var i in areas)
                {
                    richTextBox.AppendText($"Area in CT : {i.Id}, {i.Name}\n");
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Query Status() Error!", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

        }

        private void Test_button_Click(object sender, EventArgs e)
        {          
            Status();
        }
    }
}