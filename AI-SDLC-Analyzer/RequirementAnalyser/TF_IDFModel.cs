using System;
using System.IO;
using Microsoft.ML;
using Microsoft.ML.Data;

public class TF_IDFModel
{
    private readonly MLContext mlContext;
    private readonly string modelPath = "TF_IDF_model.zip";

    public TF_IDFModel()
    {
        mlContext = new MLContext();
    }

    public void TrainAndSaveModel(string dataPath)
    {
        IDataView dataView = mlContext.Data.LoadFromTextFile<ModelInput>(
            dataPath, separatorChar: ',', hasHeader: true);

        var pipeline = mlContext.Transforms.Text.FeaturizeText("Features", nameof(ModelInput.UserQuery))
            .Append(mlContext.Transforms.Conversion.MapValueToKey("Label", nameof(ModelInput.RequirementIndex)))
            .Append(mlContext.MulticlassClassification.Trainers.SdcaMaximumEntropy("Label", "Features"))
            .Append(mlContext.Transforms.Conversion.MapKeyToValue("PredictedLabel"));

        var model = pipeline.Fit(dataView);
        mlContext.Model.Save(model, dataView.Schema, modelPath);
        Console.WriteLine("✅ TF-IDF Model trained and saved.");
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

public class ModelInput
{
    [LoadColumn(0)]
    public string UserQuery { get; set; }

    [LoadColumn(1)]
    public string RequirementIndex { get; set; }
}

public class ModelOutput
{
    [ColumnName("PredictedLabel")]
    public string RequirementIndex { get; set; }
}