using System.Threading.Tasks;
using Api.Models;

namespace Api.Services
{
    public interface IPythonRunner
    {
        Task<(ProcessedPPM processedPPM, string errors)> ProcessRawData(RawPPM rawPPM);
    }
}