using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Api.Models;
using Microsoft.Extensions.Options;

namespace Api.Services
{
    public class PythonRunner : IPythonRunner
    {
        private readonly IOptions<AppOptions> appOptions;

        public PythonRunner(IOptions<AppOptions> appOptions)
        {
            this.appOptions = appOptions;
        }
        
        public async Task<(ProcessedPPM processedPPM, string errors)> ProcessRawData(RawPPM rawPPM)
        {
            string pythonScriptPath = Path.Combine(Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location), "ppm_server.py");
            ProcessStartInfo pythonProcess = new ProcessStartInfo()
            {
                FileName = "python",
                Arguments = $"{pythonScriptPath} -d {appOptions.Value.DataCatalog} {(appOptions.Value.CreatePlots ? "-p" : "")} -r -s {rawPPM.SampleRate.ToString().Replace(',','.')} {rawPPM.TakenAt.ToString().Replace(',','.')}",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true
            };

            string errors = null;
            
            ProcessedPPM results = await Task<ProcessedPPM>.Run(() => {            
                using (Process process = Process.Start(pythonProcess))
                {
                    // send encoded samples to the Python script using stdin                
                    using(StreamWriter writer = process.StandardInput)
                    {
                        writer.Write(rawPPM.Base64samples);
                    }
                    
                    // listen for possible error messages
                    using(StreamReader reader = process.StandardError)
                    {
                        errors = reader.ReadToEnd();
                    }

                    // listen for ppm analysis results from the Python script
                    // construct PPM object
                    using (StreamReader reader = process.StandardOutput)
                    {
                        string[] split = reader.ReadToEnd().Split('\t');
                        ProcessedPPM ppm;
                        if(split[0] == "OK")
                        {
                            Thread.CurrentThread.CurrentCulture = CultureInfo.InvariantCulture;
                            return ppm = new ProcessedPPM()
                            {
                                B = double.Parse(split[1]),
                                FitFrequency = double.Parse(split[2]),
                                FFTFrequency = double.Parse(split[3]),
                                T0 = double.Parse(split[4]),
                                FFTAmplitude = double.Parse(split[5]),
                                A = double.Parse(split[6]),
                                X0Error = double.Parse(split[7]),
                                FError = double.Parse(split[8]),
                                T0Error = double.Parse(split[9]),
                                AError = double.Parse(split[10]),
                                Y0Error = double.Parse(split[11]),
                                TakenAt = rawPPM.TakenAt,        
                                SampleRate = rawPPM.SampleRate,
                                NumberOfSamples = int.Parse(split[12])
                            };
                        }
                        else return null;                        
                    }
                }
            });

            return (processedPPM: results, errors: errors);
        }
    }
}