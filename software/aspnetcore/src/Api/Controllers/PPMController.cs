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
        public async Task<IActionResult> Post([FromBody]RawPPM value)
        {
            ProcessedPPM ppm = await pythonRunner.ProcessRawData(value);
            if(ppm != null)
            {
                ProcessedPPM created = await mongoService.Create(ppm);
                string location = Url.RouteUrl("GetPPMById", new { id = ppm.Id }, Request.Scheme, Request.Host.ToUriComponent());
                return Created(location, created);
            }
            else
            {
                return Ok("PPM analysis failed");
            }
        }
    }
}
