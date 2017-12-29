using System.Collections.Generic;
using System.Threading.Tasks;
using ppm_api.Models;
using MongoDB.Driver;
using System;

namespace ppm_api.Services
{
    public class MongoService : IMongoService
    {
        private readonly IMongoDatabase database;

        public MongoService(IMongoDatabase database)
        {
            this.database = database;
        }

        public async Task<ProcessedPPM> Get(string id)
        {
            ProcessedPPM ppm = null;
            try
            {
                ppm = await database.GetCollection<ProcessedPPM>("ppms").Find(x => x.Id == id).SingleOrDefaultAsync();
            }
            catch(FormatException e)
            {
                Console.WriteLine($"Specified id={id} is not a valid 24 digit hex string.\n{e.Message}");
            }            
            return ppm;
        }

        public async Task<ProcessedPPM> Create(ProcessedPPM ppm)
        {
            await database.GetCollection<ProcessedPPM>("ppms").InsertOneAsync(ppm);            
            return ppm;
        }
  }
}