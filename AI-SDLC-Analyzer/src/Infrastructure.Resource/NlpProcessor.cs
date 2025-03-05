using Microsoft.ML;
using System;
using System.IO;
using System.Text.RegularExpressions;
using Domain.Entities;
using Microsoft.ML.Data;

namespace Infrastructure.Resource
{
    public class NlpProcessor
    {
        private readonly MLContext _mlContext;
        private ITransformer _model;
        private PredictionEngine<NLPInput, NLPFeatures> _predictionEngine;
        private static readonly string ProjectRoot =
            Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../../"));

        private static readonly string InfrastructureResourcePath =
            Path.Combine(ProjectRoot, "src/Infrastructure.Resource/");

        // ✅ Ensure the correct Excel file name is used
        private static readonly string TrainingModel = "ml_model.zip";
        
        private static readonly string filePath = Path.Combine(InfrastructureResourcePath, TrainingModel);
        
        public NlpProcessor()
        {
            _mlContext = new MLContext();
            LoadModel();
        }

        private void LoadModel()
        {
            if (!File.Exists(filePath))
            {
                Console.WriteLine("❌ NLP Model not found. Train the model first.");
                return;
            }

            _model = _mlContext.Model.Load(filePath, out _);
            _predictionEngine = _mlContext.Model.CreatePredictionEngine<NLPInput, NLPFeatures>(_model);

            Console.WriteLine("✅ NLP Model Loaded Successfully.");
        }

        public static string PreprocessText(string input)
        {
            if (string.IsNullOrWhiteSpace(input)) return string.Empty;

            // Convert to lowercase
            input = input.ToLower();

            // Remove special characters
            input = Regex.Replace(input, @"[^a-z0-9\s]", "");

            // Remove extra spaces
            input = Regex.Replace(input, @"\s+", " ").Trim();

            return input;
        }

        public float[] GetTextEmbedding(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return new float[512];

            string cleanText = PreprocessText(text);
            var input = new NLPInput { Text = cleanText };
            var prediction = _predictionEngine.Predict(input);

            return prediction.Features ?? new float[512]; // Return zero vector if null
        }
    }

    public class NLPInput
    {
        public string Text { get; set; }

        [VectorType(512)] // Ensure this matches the embedding size
        public float[] Features { get; set; }
    }

    public class NLPFeatures
    {
        [VectorType(512)]
        public float[] Features { get; set; }
    }
}
