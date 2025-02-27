using Microsoft.ML;
using Microsoft.ML.Data;
using Domain.Entities;

namespace Infrastructure.Resource
{
    public class SemanticSearch
    {
        private readonly MLContext _mlContext;
        private PredictionEngine<RequirementInput, RequirementPrediction> _predictionEngine;
        private ITransformer _model;

        private static readonly string ModelPath = "src/Infrastructure.Resource/ml_model.zip";

        public SemanticSearch()
        {
            _mlContext = new MLContext();
            LoadModel();
        }

        private void LoadModel()
        {
            if (!System.IO.File.Exists(ModelPath))
            {
                Console.WriteLine("❌ ML Model not found. Train the model first.");
                return;
            }

            DataViewSchema schema;
            _model = _mlContext.Model.Load(ModelPath, out schema);
            _predictionEngine = _mlContext.Model.CreatePredictionEngine<RequirementInput, RequirementPrediction>(_model);
            Console.WriteLine("✅ ML Model Loaded Successfully.");
        }

        public List<StandardRequirement> FindSimilarRequirements(string query, List<StandardRequirement> allRequirements, float threshold = 0.75f)
        {
            var results = new List<(StandardRequirement requirement, float similarity)>();

            foreach (var req in allRequirements)
            {
                var prediction = _predictionEngine.Predict(new RequirementInput { Requirement = query });
                float similarityScore = CosineSimilarity(prediction.Features, ExtractFeatures(req.RequirementDescription));

                if (similarityScore >= threshold)
                {
                    results.Add((req, similarityScore));
                }
            }

            return results.OrderByDescending(r => r.similarity).Select(r => r.requirement).ToList();
        }

        private float[] ExtractFeatures(string text)
        {
            var input = new RequirementInput { Requirement = text };
            var prediction = _predictionEngine.Predict(input);
            return prediction.Features;
        }

        private float CosineSimilarity(float[] vectorA, float[] vectorB)
        {
            if (vectorA.Length != vectorB.Length) return 0;

            float dotProduct = 0, magnitudeA = 0, magnitudeB = 0;

            for (int i = 0; i < vectorA.Length; i++)
            {
                dotProduct += vectorA[i] * vectorB[i];
                magnitudeA += vectorA[i] * vectorA[i];
                magnitudeB += vectorB[i] * vectorB[i];
            }

            magnitudeA = (float)Math.Sqrt(magnitudeA);
            magnitudeB = (float)Math.Sqrt(magnitudeB);

            return (magnitudeA * magnitudeB == 0) ? 0 : dotProduct / (magnitudeA * magnitudeB);
        }
    }

    public class RequirementInput
    {
        public string Requirement { get; set; }
        [VectorType(512)] // Adjust vector size as needed
        public float[] Features { get; set; }
    }

    public class RequirementPrediction
    {
        [VectorType(512)]
        public float[] Features { get; set; }
    }
}
