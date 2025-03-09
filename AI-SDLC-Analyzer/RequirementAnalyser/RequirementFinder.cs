using OfficeOpenXml;

namespace RequirementAnalyser;

public class RequirementFinder
{
    private readonly WordEmbeddingModel embeddingModel;
    private readonly ExcelReader excelReader;

    public RequirementFinder(string embeddingModelPath, string excelFilePath)
    {
        embeddingModel = new WordEmbeddingModel(embeddingModelPath); // 🔹 Pass the word embedding model path
        excelReader = new ExcelReader(excelFilePath); // 🔹 Pass the Excel file path
    }
    
    public string FindClosestRequirement(string userQuery)
    {
        var allRequirements = excelReader.GetAllReqIndexes(); // 🔹 Get ReqIndex → Description

        // Convert user query into a vector
        float[] queryVector = embeddingModel.ConvertToVector(userQuery);

        string bestMatch = null;
        double bestSimilarity = -1.0;

        foreach (var entry in allRequirements)
        {
            float[] reqVector = embeddingModel.ConvertToVector(entry);
            double similarity = CosineSimilarity(queryVector, reqVector);

            if (similarity > bestSimilarity)
            {
                bestSimilarity = similarity;
                bestMatch = entry; // 🔹 Best matching Requirement Index
            }
        }

        return bestMatch;
    }

    private static double CosineSimilarity(float[] vec1, float[] vec2)
    {
        double dotProduct = vec1.Zip(vec2, (a, b) => a * b).Sum();
        double magnitudeA = Math.Sqrt(vec1.Sum(a => a * a));
        double magnitudeB = Math.Sqrt(vec2.Sum(b => b * b));

        return dotProduct / (magnitudeA * magnitudeB);
    }
}