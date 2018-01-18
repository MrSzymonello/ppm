using System.IO;
using System.Text.RegularExpressions;
using Api.Models;
using Api.Services;
using Microsoft.Extensions.Options;
using Newtonsoft.Json;
using NUnit.Framework;

namespace Api.Tests
{
    public class PythonRunnerFileOutputTests
    {
        private readonly string dataCatalog = "tempdata";

        [TestCase("test_data/20170709_060220_971_time.json", false)]
        [TestCase("test_data/20160910_162232_887_time_optimal_parameters_not_found.json", true)]
        public void Outputs_files(string inputJsonPath, bool errors)
        {
            // create output files
            var options = Options.Create(new AppOptions()
            {
                Path = "python3",
                SavePlots = true,
                SaveErrorFile = true,
                SaveRawFile = true,
                SaveSummaryFile = true,
                DataCatalog = dataCatalog
            });

            var pythonRunner = new PythonRunner(options);

            Regex regex = new Regex(@"^.*\/((\d\d\d\d\d\d\d\d)_\d\d\d\d\d\d_\d\d\d)", RegexOptions.IgnoreCase);
            Match match = regex.Match(inputJsonPath);
            string filePrefix = match.Groups[1].Value; // like 20170709_060220_971
            string yyyymmdd = match.Groups[2].Value; // like 20170709

            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText(inputJsonPath));

            DirectoryAssert.DoesNotExist(new DirectoryInfo(options.Value.DataCatalog));

            // execute python script
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            DirectoryAssert.Exists(new DirectoryInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd)));

            FileAssert.Exists(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, filePrefix + "_time.txt")));
            
            if(errors == true)
            {
                FileAssert.DoesNotExist(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, filePrefix + "_1.png")));
                FileAssert.DoesNotExist(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, filePrefix + "_2.png")));
                FileAssert.DoesNotExist(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, yyyymmdd + ".txt")));
                FileAssert.Exists(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, "_errors.log")));
            }
            else
            {
                FileAssert.Exists(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, filePrefix + "_1.png")));
                FileAssert.Exists(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, filePrefix + "_2.png")));
                FileAssert.Exists(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, yyyymmdd + ".txt")));
                FileAssert.DoesNotExist(new FileInfo(Path.Combine(options.Value.DataCatalog, yyyymmdd, "_errors.log")));
            }
            
        }

        [TearDown]
        public void CleanUp()
        {
            Directory.Delete(dataCatalog, true);
        }
    }
}