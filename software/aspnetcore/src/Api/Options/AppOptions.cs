namespace Api
{
    public class AppOptions
    {
        public string Path { get; set; }
        public string DataCatalog { get; set; }
        public bool SavePlots { get; set; }
        public bool SaveRawFile {get; set;}
        public bool SaveSummaryFile {get;set;}
        public bool SaveErrorFile {get;set;}
    }
}
