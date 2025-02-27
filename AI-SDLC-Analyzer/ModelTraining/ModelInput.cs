using Microsoft.ML.Data;

namespace ModelTraining;

public class TrainingData
{
    public string ReferenceMLSRID { get; set; }
    public string Requirement { get; set; }
    public string Category { get; set; }
    public string ChangeInRequirements { get; set; }
    public string StandardRefID { get; set; }
    
    [ColumnName("Label")] // This is the label column needed for regression!
    public float Label { get; set; }
}

public class Standard
{
    public string MLSRID { get; set; }
    public string StandardName { get; set; }
    public string StandardRefID { get; set; }
}

public class Requirement
{
    public string ReferenceMLSRID { get; set; }
    public string RequirementDescription { get; set; }
    public string Category { get; set; }
    public string ChangeInRequirements { get; set; }
}