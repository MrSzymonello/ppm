using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Api.Models;
using Api.Services;
using Swashbuckle.AspNetCore.Examples;

namespace Api.Controllers
{
    [Route("api/[controller]")]
    public class PPMController : Controller
    {
        private readonly IMongoService mongoService;
        private readonly IPythonRunner pythonRunner;

        public PPMController(IMongoService mongoService, IPythonRunner pythonRunner)
        {
            this.pythonRunner = pythonRunner;
            this.mongoService = mongoService;
        }

        // GET api/ppm/{id}
        [HttpGet("{id}", Name = "GetPPMById")]
        public async Task<IActionResult> Get(string id)
        {
            var ppm = await mongoService.Get(id);
            if (ppm != null) return Ok(ppm);
            else return NotFound();
        }

        // POST api/ppm
        [HttpPost]
        [SwaggerRequestExample(typeof(RawPPM), typeof(RawPPMExample))]
        public async Task<IActionResult> Post([FromBody]RawPPM value)
        {
            var results = await pythonRunner.ProcessRawData(value);
            if(results.processedPPM != null)
            {
                ProcessedPPM created = await mongoService.Create(results.processedPPM);
                string location = Url.RouteUrl("GetPPMById", new { id = results.processedPPM.Id }, Request.Scheme, Request.Host.ToUriComponent());
                return Created(location, created);
            }
            else
            {
                return Ok(new {errors = $"PPM analysis failed: \n{results.errors}"});
            }
        }
    }
}
