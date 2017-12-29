using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using ppm_api.Models;
using ppm_api.Services;

namespace ppm_api.Controllers
{
    [Route("api/[controller]")]
    public class PPMController : Controller
    {
        private readonly IMongoService mongoService;

        public PPMController(IMongoService mongoService)
        {
            this.mongoService = mongoService;
        }

        // GET api/ppm/{id}
        [HttpGet("{id}", Name="GetPPMById")]
        public async Task<IActionResult> Get(string id)
        {
            var ppm = await mongoService.Get(id);
            if(ppm != null) return Ok(ppm);
            else return NotFound();
        }

        // POST api/ppm
        [HttpPost]
        public async Task<IActionResult> Post([FromBody]RawPPM value)
        {
            ProcessStartInfo pythonProcess = new ProcessStartInfo()
            {
                FileName = "python",
                Arguments = $"..\\python\\ppm_server.py {value.SampleRate.ToString().Replace(',','.')} {value.TakenAt.ToString().Replace(',','.')}",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardInput = true,
                RedirectStandardOutput = true
            };

            using (Process process = Process.Start(pythonProcess))
            {
                // send encoded samples to the Python script using stdin                
                using(StreamWriter writer = process.StandardInput)
                {
                    writer.Write(value.Base64samples);
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
                        ppm = new ProcessedPPM()
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
                            TakenAt = value.TakenAt,        
                            SampleRate = value.SampleRate,
                            NumberOfSamples = int.Parse(split[12])
                        };
                        
                        ProcessedPPM created = await mongoService.Create(ppm);
                        string location = Url.RouteUrl("GetPPMById", new {id = ppm.Id}, Request.Scheme, Request.Host.ToUriComponent());
                        return Created(location, created);
                    }
                    else
                    {
                        // ERROR
                        return Ok("PPM analysis failed");
                    }
                    
                }
            }
        }
    }
}
