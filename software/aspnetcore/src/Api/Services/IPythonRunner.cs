using System.Threading.Tasks;
using Api.Models;

namespace Api.Services
{
    public interface IPythonRunner
    {
        Task<ProcessedPPM> ProcessRawData(RawPPM rawPPM);
    }
}