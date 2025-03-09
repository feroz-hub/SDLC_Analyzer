using Microsoft.ML;
using Microsoft.ML.Data;
using Microsoft.ML.Transforms.Text;
using OfficeOpenXml;


namespace ModelTraining;

public class ModelTrainerVer2
{
    private static readonly string ProjectRoot = Helper.GetProjectRoot();
    private static readonly string InfrastructureResourcePath = Path.Combine(ProjectRoot, "src","Infrastructure.Resource");
    private static readonly string ModelPathReqIndex = Path.Combine(InfrastructureResourcePath,"ml_model_reqIndex.zip");
    private const string DataPath = "RequirementIndexTraining.csv";
    private readonly MLContext _context = new();

    public void TrainAndSaveModel()
    {
        if (!Directory.Exists(InfrastructureResourcePath))
        {
            Console.WriteLine(
                $"❌ Error: Infrastructure resource directory does not exist at {InfrastructureResourcePath}");
            return;
        }
        DeleteExistingModels();
        
       // Load Data
        var trainDataView = _context.Data.LoadFromTextFile<RequirementData>(DataPath, separatorChar: ',', hasHeader: true);
        
        // ✅ Train-Test Split (80% Train, 20% Test)
        var trainTestSplit = _context.Data.TrainTestSplit(trainDataView, testFraction: 0.2);
        var trainData = trainTestSplit.TrainSet;
        var testData = trainTestSplit.TestSet;
        var reqModelIndexModel = ReqIndexTrainModel(trainDataView);
        EvaluateModel(reqModelIndexModel, testData);
        
        SaveModel(reqModelIndexModel, trainData.Schema,ModelPathReqIndex);
    }

    private void DeleteExistingModels()
    {
        if (File.Exists(ModelPathReqIndex)) File.Delete(ModelPathReqIndex);
        // if (File.Exists(ModelPath)) File.Delete(ModelPath);
        Console.WriteLine("🗑️ Old models deleted.");
    }
    
    
    private ITransformer ReqIndexTrainModel(IDataView  trainData)
    {
        Console.WriteLine("🚀 Training Model...");
        // Define ML.NET pipeline
        var pipeline = _context.Transforms.Text.TokenizeIntoWords("TokenizedText", nameof(RequirementData.UserQuery))
            .Append(_context.Transforms.Text.ApplyWordEmbedding("Features", "TokenizedText",
                WordEmbeddingEstimator.PretrainedModelKind.GloVe300D))  // ✅ Built-in ML.NET GloVe Model
            .Append(_context.Transforms.Conversion.MapValueToKey("Label", nameof(RequirementData.RequirementIndex)))
            .Append(_context.MulticlassClassification.Trainers.SdcaMaximumEntropy("Label", "Features"))
            .Append(_context.Transforms.Conversion.MapKeyToValue("PredictedLabel"));

        return pipeline.Fit(trainData);
    }

    private void EvaluateModel(ITransformer model, IDataView testData)
    {
        Console.WriteLine("📊 Evaluating Model...");
        var predictions = model.Transform(testData);
        var metrics = _context.MulticlassClassification.Evaluate(predictions, "Label");

        Console.WriteLine($"🔍 Accuracy: {metrics.MicroAccuracy:P2} (Micro), {metrics.MacroAccuracy:P2} (Macro)");
        Console.WriteLine($"🛠 Log Loss: {metrics.LogLoss:F4}");
    }
    private void SaveModel(ITransformer model, DataViewSchema schema, string savePath)
    {
        Console.WriteLine($"💾 Saving Model at {savePath}...");
        _context.Model.Save(model, schema, savePath);
        Console.WriteLine($"✅ Model saved at: {savePath}");
    }


    private class RequirementData
    {
        [LoadColumn(0)] public string UserQuery { get; set; }
        [LoadColumn(1)] public string RequirementIndex { get; set; }
    }
}

