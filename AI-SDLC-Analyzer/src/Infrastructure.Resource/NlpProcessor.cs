using Domain;
using Microsoft.ML;
using Microsoft.ML.Data;

namespace Infrastructure.Resource
{
    public class NlpProcessor
    {
        private static readonly string ProjectRoot = Helper.GetProjectRoot();
        private static readonly string ReqIndexModelPath = Path.Combine(ProjectRoot, "src", "Infrastructure.Resource", "ml_model_reqIndex220.zip");
        private readonly PredictionEngine<RequirementData, RequirementPrediction> _indexPredictionEngine;

        public NlpProcessor()
        {
            var mlContext = new MLContext();
            Console.WriteLine("NLP Processor Initialized");
            Console.WriteLine("Project Root: " + ProjectRoot);
            Console.WriteLine(ReqIndexModelPath);
            
            // Load requirement index prediction model
            var reqIndexModel = mlContext.Model.Load(ReqIndexModelPath, out _);
            _indexPredictionEngine = mlContext.Model.CreatePredictionEngine<RequirementData, RequirementPrediction>(reqIndexModel);
        }
        
        public string PredictReqIndex(string query)
        {
            var prediction = _indexPredictionEngine.Predict(new RequirementData() { UserQuery = query });
            return prediction.RequirementIndex;
        }
    }

    public class RequirementData
    {
        [LoadColumn(0)] public string UserQuery { get; set; }
        [LoadColumn(1)] public string RequirementIndex { get; set; }
    }

    public class RequirementPrediction
    {
        [ColumnName("PredictedLabel")] public string RequirementIndex;
    }
}
