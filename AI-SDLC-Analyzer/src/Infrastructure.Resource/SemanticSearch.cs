using Domain.Entities;
using Domain.Interfaces;

namespace Infrastructure.Resource
{
    public class SemanticSearch(IStandardRepository standardRepository, IRequirementRepository requirementRepository)
    {
        
        private readonly NlpProcessor _nlpProcessor = new();
        public List<RequirementOutput> FindMatchingRequirements(string query)
        {
            // Extract MLSR_ID from query
            string mlsrId = ExtractMlsrId(query);
            
            // Predict ReqIndex using Semantic Search
            string predictedReqIndex = _nlpProcessor.PredictReqIndex(query);

            Console.WriteLine($"📌 Extracted MLSR ID: {mlsrId}");
            Console.WriteLine($"🔢 Predicted ReqIndex: {predictedReqIndex}");
            
            // Load all requirements from Excel
            var requirements = requirementRepository.LoadRequirementsFromExcel();
            
            var results = requirements
                .Where(req => string.IsNullOrEmpty(predictedReqIndex) || req.Requirement_Index.Equals(predictedReqIndex, StringComparison.OrdinalIgnoreCase))
                .Select(req => new RequirementOutput
                {
                    RequirementDescription = req.Requirement_Index,
                    Category = req.Category,
                    ChangeInRequirement = GetFilteredChangeInRequirement(req.Change_In_Requirements,mlsrId)
                })
                .ToList();

            return results;
        }
        
        private string ExtractMlsrId(string query)
        {
            var mlsrMapping =standardRepository.LoadMlsrMapping(); // ✅ Load dynamically

            foreach (var kvp in mlsrMapping)
            {
                if (query.Contains(kvp.Key, StringComparison.OrdinalIgnoreCase))
                {
                    return kvp.Value;
                }
            }

            return string.Empty;
        }
        private List<string> GetFilteredChangeInRequirement(string changeInRequirements, string mlsrId)
        {
            if (string.IsNullOrEmpty(changeInRequirements))
                return new List<string>();

            // Split the change in requirement into lines
            var changes = changeInRequirements.Split(['\n', '\r'], StringSplitOptions.RemoveEmptyEntries);

            // If MLSR ID is available, return only the lines starting with it
            if (!string.IsNullOrEmpty(mlsrId))
            {
                var filteredChanges = changes.Where(line => line.TrimStart().StartsWith(mlsrId, StringComparison.OrdinalIgnoreCase)).ToList();
                return filteredChanges.Any() ? filteredChanges : changes.ToList(); // If no match, return all changes
            }
            return changes.ToList();
        }
    }
}