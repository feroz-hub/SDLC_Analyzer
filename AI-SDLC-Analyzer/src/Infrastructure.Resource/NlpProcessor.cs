using Domain;
using Microsoft.ML;
using Microsoft.ML.Data;

namespace Infrastructure.Resource
{
    public class NlpProcessor
    {
        private static readonly string ProjectRoot = Helper.GetProjectRoot();
        private static readonly string ReqIndexModelPath = Path.Combine(ProjectRoot, "src", "Infrastructure.Resource", "ml_model_reqIndex220_Lower.zip");
        private static readonly MLContext mlContext = new MLContext();
        private static readonly PredictionEngine<RequirementData, RequirementPrediction> _indexPredictionEngine;

        // Static constructor to initialize once when the project starts
        static NlpProcessor()
        {
            Console.WriteLine("Initializing NLP Processor...");
            Console.WriteLine("Project Root: " + ProjectRoot);
            Console.WriteLine("Loading Model: " + ReqIndexModelPath);

            try
            {
                var reqIndexModel = mlContext.Model.Load(ReqIndexModelPath, out _);
                _indexPredictionEngine = mlContext.Model.CreatePredictionEngine<RequirementData, RequirementPrediction>(reqIndexModel);
                Console.WriteLine("Model Loaded Successfully!");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error Loading Model: " + ex.Message);
                throw;
            }
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
