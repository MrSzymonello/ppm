using NUnit.Framework;
using Moq;
using Api;
using Api.Services;
using Api.Controllers;
using Api.Models;
using Newtonsoft.Json;
using System.IO;
using Microsoft.Extensions.Options;
using System.Threading.Tasks;

namespace Tests
{
    public class PythonRunnerDataAnalysisTests
    {        
        private PythonRunner pythonRunner;

        [OneTimeSetUp]
        public void Setup()
        {
            // do not create any output files
            var options = Options.Create(new AppOptions()
            {
                SavePlots = false,
                SaveErrorFile = false,
                SaveRawFile = false,
                SaveSummaryFile = false
            });

            pythonRunner = new PythonRunner(options);
        }

        [Test]
        public void Returns_correct_results()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20170709_060220_971_time.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.Greater(results.processedPPM.B, 50124.2);
            Assert.Less(results.processedPPM.B, 50124.5);

            Assert.Greater(results.processedPPM.FitFrequency, 2133.2);
            Assert.Less(results.processedPPM.FitFrequency, 2133.4);

            Assert.Greater(results.processedPPM.FFTFrequency, 2133.4);
            Assert.Less(results.processedPPM.FFTFrequency, 2133.6);

            Assert.Greater(results.processedPPM.T0, 1.0);
            Assert.Less(results.processedPPM.T0, 2.0);

            Assert.AreEqual(results.processedPPM.TakenAt, rawPPM.TakenAt);

            Assert.AreEqual(results.processedPPM.SampleRate, rawPPM.SampleRate);

            // restore number of samples from Base64 encoded string length
            // length of all samples encoded in Base64
            int numberOfSamples = rawPPM.Base64samples.Length;
            // bytes number of all samples before conversion to Base64 string
            // 3 bytes convert to 4 bytes in Base64
            numberOfSamples = numberOfSamples * 3 / 4;
            // number of 12 bit samples
            numberOfSamples = numberOfSamples * 8 / 12;
            // and we're ready to assert
            Assert.AreEqual(results.processedPPM.NumberOfSamples, numberOfSamples);

            StringAssert.AreEqualIgnoringCase(string.Empty, results.errors);
        }

        [Test]
        public void Returns_t0_x0_f_error()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20160716_185655_020_time_t0_x0_f_error.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.IsNull(results.processedPPM);
            StringAssert.Contains("t0_error = ", results.errors);
            StringAssert.Contains("x0_error = ", results.errors);
            StringAssert.Contains("f_error = ", results.errors);
        }

        [Test]
        public void Returns_covariance_of_the_parameters_could_not_be_estimated_error()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20160716_190124_861_time_covariance_of_the_parameters_could_not_be_estimated.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.IsNull(results.processedPPM);
            StringAssert.Contains("Covariance of the parameters could not be estimated", results.errors);
        }

        [Test]
        public void Returns_t0_negative_t0_error()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20160720_100613_940_time_t0_negative_t0_error.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.IsNull(results.processedPPM);
            StringAssert.Contains("t0 = ", results.errors);
            StringAssert.Contains("t0_error = ", results.errors);
        }

        [Test]
        public void Returns_t0_too_big_error()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20160910_160518_699_time_t0_too_big.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.IsNull(results.processedPPM);
            StringAssert.Contains("t0 = ", results.errors);
        }

        [Test]
        public void Returns_optimal_parameters_not_found_error()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20160910_162232_887_time_optimal_parameters_not_found.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.IsNull(results.processedPPM);
            StringAssert.Contains("Optimal parameters not found", results.errors);
        }

        [Test]
        public void Returns_overflow_encountered_in_exp_error()
        {
            var rawPPM = JsonConvert.DeserializeObject<RawPPM>(File.ReadAllText("test_data/20170804_191702_756_time_overflow_encountered_in_exp.json"));
            var results = pythonRunner.ProcessRawData(rawPPM).Result;

            Assert.IsNull(results.processedPPM);
            StringAssert.Contains("overflow encountered in exp", results.errors);
        }
    }
}