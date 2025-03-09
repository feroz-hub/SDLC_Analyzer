using Microsoft.ML;

using Microsoft.ML.Data;

namespace Infrastructure.Resource
{
    public class NlpProcessor
    {
       // private static readonly string ProjectRoot = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../../"));

        // private static readonly string CategoryModelPath =
        //     Path.Combine(ProjectRoot, "src/Infrastructure.Resource/ml_excelModel.zip");

        //private static readonly string ReqIndexModelPath = Path.Combine(ProjectRoot, "src/Infrastructure.Resource/ml_model_reqIndex.zip");
        private static readonly string ProjectRoot = GetProjectRoot();
 
        private static readonly string ReqIndexModelPath = Path.Combine(ProjectRoot, "src", "Infrastructure.Resource", "ml_model_reqIndex.zip");
        //private readonly PredictionEngine<RequirementPrediction, CategoryPredictionResult> _categoryPredictionEngine;
        private readonly PredictionEngine<RequirementData, RequirementPrediction> _indexPredictionEngine;

        public NlpProcessor()
        {
            var mlContext = new MLContext();
            Console.WriteLine("NLP Processor Initialized");
            Console.WriteLine("Project Root: " + ProjectRoot);
            Console.WriteLine(ReqIndexModelPath);
            // Load category prediction model
           
            // var categoryModel = mlContext.Model.Load(CategoryModelPath, out _);
            // _categoryPredictionEngine = mlContext.Model.CreatePredictionEngine<RequirementPrediction, CategoryPredictionResult>(categoryModel);

            // Load requirement index prediction model
            var reqIndexModel = mlContext.Model.Load(ReqIndexModelPath, out _);
            _indexPredictionEngine = mlContext.Model.CreatePredictionEngine<RequirementData, RequirementPrediction>(reqIndexModel);
           
        }
        
        private static string GetProjectRoot()
        {
            var directory = new DirectoryInfo(AppContext.BaseDirectory);
            while (directory != null && !directory.Name.Equals("AI-SDLC-Analyzer", StringComparison.OrdinalIgnoreCase))
            {
                directory = directory.Parent;
            }
 
            if (directory == null)
            {
                throw new DirectoryNotFoundException("Project root directory 'AI-SDLC-Analyzer' not found.");
            }
 
            return directory.FullName;
        }

        // public string PredictCategory(string query)
        // {
        //     var prediction = _categoryPredictionEngine.Predict(new RequirementPrediction { Text = query });
        //     return prediction.PredictedCategory;
        // }

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
