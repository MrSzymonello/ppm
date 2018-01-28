using System.Collections.Generic;
using System.Threading.Tasks;
using Api.Models;

namespace Api.Services
{
    public interface IMongoService
    {
        Task<ProcessedPPM> Get(string id);
        Task<List<ProcessedPPM>> GetAll();
        Task<ProcessedPPM> Create(ProcessedPPM ppm);
    }
}