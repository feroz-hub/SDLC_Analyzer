using System;
using System.IO;
using Microsoft.ML;
using Microsoft.ML.Data;
using Microsoft.ML.Transforms.Text;

public class WordEmbeddingModel_Glove300D
{
    private readonly MLContext mlContext;
    private readonly string modelPath = "WordEmbedding_glove300D_Model.zip";

    public WordEmbeddingModel_Glove300D()
    {
        mlContext = new MLContext();
    }

    public void TrainAndSaveModel(string dataPath)
    {
        IDataView dataView = mlContext.Data.LoadFromTextFile<ModelInput>(
            dataPath, separatorChar: ',', hasHeader: true);

        var pipeline = mlContext.Transforms.Text.TokenizeIntoWords("TokenizedText", nameof(ModelInput.UserQuery))
            .Append(mlContext.Transforms.Text.ApplyWordEmbedding("Features", "TokenizedText",
                WordEmbeddingEstimator.PretrainedModelKind.GloVe300D))  // ✅ Built-in ML.NET GloVe Model
            .Append(mlContext.Transforms.Conversion.MapValueToKey("Label", nameof(ModelInput.RequirementIndex)))
            .Append(mlContext.MulticlassClassification.Trainers.SdcaMaximumEntropy("Label", "Features"))
            .Append(mlContext.Transforms.Conversion.MapKeyToValue("PredictedLabel"));
        var model = pipeline.Fit(dataView);
        mlContext.Model.Save(model, dataView.Schema, modelPath);
        Console.WriteLine("✅ FastText Model trained and saved.");
    }

    public string PredictRequirementIndex(string inputQuery)
    {
        if (!File.Exists(modelPath))
        {
            Console.WriteLine("⚠ Model not found. Train the model first.");
            return null;
        }

        ITransformer loadedModel = mlContext.Model.Load(modelPath, out _);
        var predictor = mlContext.Model.CreatePredictionEngine<ModelInput, ModelOutput>(loadedModel);

        var prediction = predictor.Predict(new ModelInput { UserQuery = inputQuery });
        return prediction.RequirementIndex;
    }
}