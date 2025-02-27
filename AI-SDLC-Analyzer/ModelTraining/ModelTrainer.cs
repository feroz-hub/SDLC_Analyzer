namespace ModelTraining;

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.ML;


public class ModelTrainer
{
    // ✅ Get absolute path to src/SentimentAPI/
    private static readonly string ProjectRoot = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../"));
    
    private static readonly string InfrastructureResourcePath = Path.Combine(ProjectRoot, "src/Infrastructure.Resource");
    private static readonly string StandardsDataPath = "StandardsData.csv";
    private static readonly string RequirementsDataPath = "RequirementsData.csv";
    //private static readonly string ModelPath = "ml_model.zip";
    private static readonly string ModelPath =Path.Combine(InfrastructureResourcePath,"ml_model.zip");

    private MLContext _mlContext = new();
    private Dictionary<string, float> _labelMapping = new(); // ✅ Label conversion dictionary

    public void TrainAndSaveModel()
    {
        //Console.WriteLine($"Saving model to: {ModelPath}");
        if (!Directory.Exists(InfrastructureResourcePath))
        {
            Console.WriteLine($"❌ Error: Infrastructure resource directory does not exist at {InfrastructureResourcePath}");
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

        var sampleData = trainingData.Take(2000).ToList(); // Adjust size if needed

        // ✅ Convert 'StandardRefID' to float (label encoding)
        var encodedData = EncodeLabels(sampleData);

        IDataView dataView = _mlContext.Data.LoadFromEnumerable(encodedData);
        var model = TrainModel(dataView);
        SaveModel(model, dataView.Schema);
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
                RequirementDescription = columns[1].Trim().Length > 500 ? columns[1].Trim().Substring(0, 500) : columns[1].Trim(),
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

    private List<EncodedTrainingData> EncodeLabels(List<TrainingData> data)
    {
        Console.WriteLine("🔢 Encoding Labels...");
        int index = 1; // Start indexing from 1
        foreach (var item in data)
        {
            if (!_labelMapping.ContainsKey(item.StandardRefID))
            {
                _labelMapping[item.StandardRefID] = index++;
            }
        }

        return data.Select(d => new EncodedTrainingData
        {
            ReferenceMLSRID = d.ReferenceMLSRID,
            Requirement = d.Requirement,
            Category = d.Category,
            ChangeInRequirements = d.ChangeInRequirements,
            StandardRefID = _labelMapping[d.StandardRefID] // Convert to float
        }).ToList();
    }

    private ITransformer TrainModel(IDataView dataView)
    {
        Console.WriteLine("🚀 Training Model...");

        var pipeline = _mlContext.Transforms.Text.FeaturizeText("RequirementFeatures", nameof(EncodedTrainingData.Requirement))
                        .Append(_mlContext.Transforms.Text.FeaturizeText("CategoryFeatures", nameof(EncodedTrainingData.Category)))
                        .Append(_mlContext.Transforms.Text.FeaturizeText("ChangeFeatures", nameof(EncodedTrainingData.ChangeInRequirements)))
                        .Append(_mlContext.Transforms.Concatenate("Features", "RequirementFeatures", "CategoryFeatures", "ChangeFeatures"))
                        .Append(_mlContext.Transforms.NormalizeMinMax("Features"))
                        .Append(_mlContext.Regression.Trainers.FastTree(
                                labelColumnName: nameof(EncodedTrainingData.StandardRefID), // ✅ Use numerical label
                                featureColumnName: "Features",
                                numberOfTrees: 50,
                                numberOfLeaves: 10,
                                learningRate: 0.2));

        return pipeline.Fit(dataView);
    }

    private void SaveModel(ITransformer model, DataViewSchema schema)
    {
        Console.WriteLine("💾 Saving Model...");
        _mlContext.Model.Save(model, schema, ModelPath);

      
        Console.WriteLine($"✅ Model saved at: {ModelPath}");
    }
}



public class EncodedTrainingData
{
    public string ReferenceMLSRID { get; set; }
    public string Requirement { get; set; }
    public string Category { get; set; }
    public string ChangeInRequirements { get; set; }
    public float StandardRefID { get; set; } // Converted label (numerical)
}


