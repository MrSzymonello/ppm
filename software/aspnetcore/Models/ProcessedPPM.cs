using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ppm_api.Models
{
    public class ProcessedPPM
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }
        public double B { get; set; }
        public double FitFrequency { get; set; }
        public double FFTFrequency { get; set; }
        public double FFTAmplitude { get; set; }
        public double T0 { get; set; }
        public double A { get; set; }
        public double X0Error { get; set; }
        public double FError { get; set; }
        public double T0Error { get; set; }
        public double AError { get; set; }
        public double Y0Error { get; set; }
        public double TakenAt { get; set; }
        public double SampleRate { get; set; }
        public int NumberOfSamples { get; set; }
    }
}