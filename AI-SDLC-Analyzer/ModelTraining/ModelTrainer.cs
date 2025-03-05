namespace ModelTraining;

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.ML;

public class ModelTrainer
{
    private static readonly string ProjectRoot =
        Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../"));

    private static readonly string InfrastructureResourcePath =
        Path.Combine(ProjectRoot, "src/Infrastructure.Resource");

    private const string StandardsDataPath = "StandardsData.csv";
    private const string RequirementsDataPath = "RequirementsData.csv";
    private static readonly string ModelPath = Path.Combine(InfrastructureResourcePath, "ml_model.zip");

    private readonly MLContext _mlContext = new();

    public void TrainAndSaveModel()
    {
        if (!Directory.Exists(InfrastructureResourcePath))
        {
            Console.WriteLine(
                $"❌ Error: Infrastructure resource directory does not exist at {InfrastructureResourcePath}");
            return;
        }

        if (File.Exists(ModelPath))
        {
            Console.WriteLine("ℹ️ Existing model found. Deleting...");
            File.Delete(ModelPath);
        }

        var standards = LoadStandardsData();
        var requirements = LoadRequirementsData();
        var trainingData = JoinData(standards, requirements);

        // ✅ Train-Test Split (80% Train, 20% Test)
        var shuffledData = _mlContext.Data.LoadFromEnumerable(trainingData);
        var trainTestSplit = _mlContext.Data.TrainTestSplit(shuffledData, testFraction: 0.2);
        var trainData = trainTestSplit.TrainSet;
        var testData = trainTestSplit.TestSet;

        var model = TrainModel(trainData);
        EvaluateModel(model, testData);
        SaveModel(model, trainData.Schema);
    }

    private List<Standard> LoadStandardsData()
    {
        Console.WriteLine("📌 Loading Standards Data...");
        var standards = new List<Standard>();

        if (!File.Exists(StandardsDataPath))
            throw new FileNotFoundException($"❌ Standards data file not found: {StandardsDataPath}");

        foreach (var line in File.ReadAllLines(StandardsDataPath).Skip(1))
        {
            var columns = line.Split(',');
            if (columns.Length < 3) continue;
            standards.Add(new Standard
            {
                MLSRID = columns[0].Trim(),
                StandardName = columns[1].Trim(),
                StandardRefID = columns[2].Trim()
            });
        }

        return standards;
    }

    private List<Requirement> LoadRequirementsData()
    {
        Console.WriteLine("📌 Loading Requirements Data...");
        var requirements = new List<Requirement>();

        if (!File.Exists(RequirementsDataPath))
            throw new FileNotFoundException($"❌ Requirements data file not found: {RequirementsDataPath}");

        foreach (var line in File.ReadAllLines(RequirementsDataPath).Skip(1))
        {
            var columns = line.Split(',');
            if (columns.Length < 4) continue;
            requirements.Add(new Requirement
            {
                ReferenceMLSRID = columns[0].Trim(),
                RequirementDescription = columns[1].Trim().Length > 500
                    ? columns[1].Trim().Substring(0, 500)
                    : columns[1].Trim(),
                Category = columns[2].Trim(),
                ChangeInRequirements = columns[3].Trim()
            });
        }

        return requirements;
    }

    private List<TrainingData> JoinData(List<Standard> standards, List<Requirement> requirements)
    {
        Console.WriteLine("🔄 Mapping Standards to Requirements...");
        var trainingData = new List<TrainingData>();

        foreach (var req in requirements)
        {
            var matchedStandard = standards.FirstOrDefault(s => req.ReferenceMLSRID.StartsWith(s.MLSRID));
            if (matchedStandard != null)
            {
                trainingData.Add(new TrainingData
                {
                    ReferenceMLSRID = req.ReferenceMLSRID,
                    Requirement = req.RequirementDescription,
                    Category = req.Category,
                    ChangeInRequirements = req.ChangeInRequirements,
                    StandardRefID = matchedStandard.StandardRefID
                });
            }
        }

        return trainingData;
    }

    private ITransformer TrainModel(IDataView trainData)
    {
        Console.WriteLine("🚀 Training Model...");

        var pipeline = _mlContext.Transforms.Conversion
            .MapValueToKey("Label", nameof(TrainingData.StandardRefID)) // ✅ Convert StandardRefID to Key
            .Append(_mlContext.Transforms.Text.FeaturizeText("RequirementFeatures", nameof(TrainingData.Requirement)))
            .Append(_mlContext.Transforms.Text.FeaturizeText("CategoryFeatures", nameof(TrainingData.Category)))
            .Append(_mlContext.Transforms.Text.FeaturizeText("ChangeFeatures",
                nameof(TrainingData.ChangeInRequirements)))
            .Append(_mlContext.Transforms.Text.FeaturizeText("ReferenceMLSRIDFeatures",
                nameof(TrainingData.ReferenceMLSRID))) // ✅ Featurize ReferenceMLSRID
            .Append(_mlContext.Transforms.Concatenate("Features", "RequirementFeatures", "CategoryFeatures",
                "ChangeFeatures", "ReferenceMLSRIDFeatures"))
            .Append(_mlContext.Transforms.NormalizeMinMax("Features"))
            .Append(_mlContext.MulticlassClassification.Trainers
                .SdcaMaximumEntropy("Label", "Features")) // ✅ Use Classification Model
            .Append(_mlContext.Transforms.Conversion.MapKeyToValue("PredictedLabel"));

        return pipeline.Fit(trainData);
    }

    private void EvaluateModel(ITransformer model, IDataView testData)
    {
        Console.WriteLine("📊 Evaluating Model...");
        var predictions = model.Transform(testData);
        var metrics = _mlContext.MulticlassClassification.Evaluate(predictions, "Label");

        Console.WriteLine($"🔍 Accuracy: {metrics.MicroAccuracy:P2} (Micro), {metrics.MacroAccuracy:P2} (Macro)");
        Console.WriteLine($"🛠 Log Loss: {metrics.LogLoss:F4}");
    }

    private void SaveModel(ITransformer model, DataViewSchema schema)
    {
        Console.WriteLine("💾 Saving Model...");
        _mlContext.Model.Save(model, schema, ModelPath);
        Console.WriteLine($"✅ Model saved at: {ModelPath}");
    }


    public class TrainingData
    {
        public string ReferenceMLSRID { get; set; }
        public string Requirement { get; set; }
        public string Category { get; set; }
        public string ChangeInRequirements { get; set; }
        public string StandardRefID { get; set; } // ✅ Categorical (Will be converted to Key)
    }
}
