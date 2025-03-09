
using Domain.Entities;
using Domain.Interfaces;
using Microsoft.ML.Data;


namespace Infrastructure.Resource
{
    public class SemanticSearch
    {
       
        private static readonly string ProjectRoot =
            Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../../"));
        private static readonly string CsvPath =
            Path.Combine(ProjectRoot, "src/Infrastructure.Resource/RequirementIndexTraining.csv");
        private readonly List<RequirementData> _requirements;
        private readonly IStandardRepository _standardRepository;
        private readonly IRequirementRepository _requirementRepository;
        private readonly NlpProcessor _nlpProcessor ;
        public SemanticSearch(IStandardRepository standardRepository,IRequirementRepository requirementRepository)
        {
            _nlpProcessor = new NlpProcessor();
            _standardRepository = standardRepository;
            _requirementRepository = requirementRepository;
            _requirements = LoadRequirements(CsvPath);
        }
        
        public List<RequirementOutput> FindMatchingRequirements(string query)
        {
            // Extract MLSR_ID from query
            string mlsrId = ExtractMlsrId(query);
        
            // Predict Category using ML Model
            //string predictedCategory = _nlpProcessor.PredictCategory(query);
        
            // Predict ReqIndex using Semantic Search
            string predictedReqIndex = _nlpProcessor.PredictReqIndex(query);
        
            //Console.WriteLine($"🔍 Predicted Category: {predictedCategory}");
            Console.WriteLine($"📌 Extracted MLSR ID: {mlsrId}");
            Console.WriteLine($"🔢 Predicted ReqIndex: {predictedReqIndex}");
        
           
            // Load all requirements from Excel
            var requirements = _requirementRepository.LoadRequirementsFromExcel();

            var results = requirements
                .Where(req => string.IsNullOrEmpty(predictedReqIndex) || req.Requirement_Index.Equals(predictedReqIndex, StringComparison.OrdinalIgnoreCase))
                .Select(req => new RequirementOutput
                {
                    RequirementDescription = req.Requirement_Index,
                    Category = req.Category,
                    ChangeInRequirement = req.Change_In_Requirements?
                        .Split(['\n', '\r'], StringSplitOptions.RemoveEmptyEntries)
                        .ToList() ?? new List<string>()
                })
                .ToList();

            return results;
            //         var results = requirements
                // .Where(req => 
                //     (string.IsNullOrEmpty(mlsrId) || req.MLSR_ID.StartsWith(mlsrId)) &&
                //     (string.IsNullOrEmpty(predictedCategory) || req.Category.Equals(predictedCategory, StringComparison.OrdinalIgnoreCase)) &&
                //     (string.IsNullOrEmpty(predictedReqIndex) || req.Requirement_Index.Equals(predictedReqIndex, StringComparison.OrdinalIgnoreCase)))
                // .ToList();
        }
        
        

        private List<RequirementData> LoadRequirements(string csvpath)
        {
            var data = new List<RequirementData>();
            var lines = File.ReadAllLines(CsvPath).Skip(1); // Skip header

            foreach (var line in lines)
            {
                var parts = line.Split(',');
                if (parts.Length == 2)
                {
                    data.Add(new RequirementData { UserQuery = parts[0], RequirementIndex = parts[1] });
                }
            }
            return data;
        }
        public string FindBestMatch(string userQuery)
        {
            var featurizedQuery = Featurize(userQuery);
            var bestMatch = _requirements
                .Select(r => new { r.RequirementIndex, Score = CosineSimilarity(Featurize(r.UserQuery), featurizedQuery) })
                .OrderByDescending(r => r.Score)
                .FirstOrDefault();

            return bestMatch?.RequirementIndex ?? "No relevant match found";
        }
        private float[] Featurize(string text)
        {
            return text.ToLower()
                .Split(new[] { ' ', '.', ',', '-', '_' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(word => (float)word.GetHashCode()) // Simple embedding
                .ToArray();
        }

        private float CosineSimilarity(float[] vec1, float[] vec2)
        {
            if (vec1.Length != vec2.Length) return 0;
            float dotProduct = vec1.Zip(vec2, (x, y) => x * y).Sum();
            float magnitude1 = (float)Math.Sqrt(vec1.Sum(x => x * x));
            float magnitude2 = (float)Math.Sqrt(vec2.Sum(y => y * y));

            return magnitude1 * magnitude2 == 0 ? 0 : dotProduct / (magnitude1 * magnitude2);
        }
        private string ExtractMlsrId(string query)
        {
            var mlsrMapping =_standardRepository.LoadMlsrMapping(); // ✅ Load dynamically

            foreach (var kvp in mlsrMapping)
            {
                if (query.Contains(kvp.Key, StringComparison.OrdinalIgnoreCase))
                {
                    return kvp.Value;
                }
            }

            return string.Empty;
        }
        // private class RequirementData
        // {
        //     [LoadColumn(0)] public string UserQuery { get; set; }
        //     [LoadColumn(1)] public string RequirementIndex { get; set; }
        // }
    }
}