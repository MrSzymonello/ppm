using System.Collections.Generic;
using System.Threading.Tasks;
using ppm_api.Models;

namespace ppm_api.Services
{
    public interface IMongoService
    {
        Task<ProcessedPPM> Get(string id);
        Task<ProcessedPPM> Create(ProcessedPPM ppm);
    }
}