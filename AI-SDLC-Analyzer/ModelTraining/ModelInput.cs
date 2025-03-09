using Microsoft.ML.Data;

namespace ModelTraining;

public class TrainingData
{
    public string Reference_MLSR_ID { get; set; }
    public string Requirement { get; set; }
    public string Category { get; set; }
    public string Change_In_Requirements { get; set; }
    public string Standard_Ref_ID { get; set; } // ✅ Categorical (Will be converted to Key)
}

public class Standard
{
    public string MLSR_ID { get; set; }
    public string Standard_Ref_Name { get; set; }
    public string Standard_Ref_ID { get; set; }
}

public class Requirement
{
    public string Reference_MLSR_ID { get; set; }
    public string Requirement_Index { get; set; }
    public string Category { get; set; }
    public string Change_In_Requirements { get; set; }
}