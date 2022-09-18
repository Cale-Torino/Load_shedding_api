using helloserve.SePush;
using Microsoft.Extensions.DependencyInjection;

namespace SePush_API_Example
{
    internal partial class TestClass<T>
    {
        public void ConfigureServices(IServiceCollection services)
        {
            // some other code...
            services.AddSePush(config =>
            {
                config.Token = "yourtokengoeshere";
            });
            //services.AddSePush();
        }
        public TestClass(ISePush sePushClient)
        {
            var status = sePushClient.StatusAsync();
            var areas = sePushClient.AreasSearchAsync("Cape Town");
        }
    }
}
