using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Api.Models;

namespace Api.Services
{
    public class PythonRunner : IPythonRunner
    {
        public async Task<ProcessedPPM> ProcessRawData(RawPPM rawPPM)
        {
            ProcessStartInfo pythonProcess = new ProcessStartInfo()
            {
                FileName = "python",
                Arguments = $"..\\..\\..\\python\\ppm_server.py {rawPPM.SampleRate.ToString().Replace(',','.')} {rawPPM.TakenAt.ToString().Replace(',','.')}",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true
            };

            return await Task<ProcessedPPM>.Run(() => {            
                using (Process process = Process.Start(pythonProcess))
                {
                    // send encoded samples to the Python script using stdin                
                    using(StreamWriter writer = process.StandardInput)
                    {
                        writer.Write(rawPPM.Base64samples);
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
        }
    }
}