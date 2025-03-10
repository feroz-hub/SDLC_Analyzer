using System.Text.RegularExpressions;
using Domain;
using Domain.Entities;
using Domain.Interfaces;

namespace Infrastructure.Resource
{
    public class SemanticSearch
    {

        private readonly IStandardRepository _standardRepository ;
        private readonly IRequirementRepository _requirementRepository ;
        private readonly NlpProcessor _nlpProcessor;
        private List<ProductRequirement> _productRequirements;
        private List<Standard> _standardRequirements;

        public SemanticSearch(IStandardRepository repository, IRequirementRepository requirementRepository)
        {
            _nlpProcessor = new NlpProcessor();
            _standardRepository = repository;
            _requirementRepository=requirementRepository;
            LoadProductRequirements();
            LoadAllStandardRequirements();
            
        }
        private void LoadProductRequirements()
        {
            // Load the data once and store it in a field
            _productRequirements = _requirementRepository.GetLoadProductRequirementsFromExcel();
        }

        private void LoadAllStandardRequirements()
        {
            _standardRequirements=_standardRepository.GetAll();
        }
        

        public List<RequirementOutput> FindMatchingRequirements(string query)
        {
            // Extract MLSR_ID from query
            string mlsrId = ExtractMlsrId(query);

            string userQuery = query.ToLower();
            // Predict ReqIndex using Semantic Search
            string predictedReqIndex = _nlpProcessor.PredictReqIndex(userQuery);

            Console.WriteLine($"📌 Extracted MLSR ID: {mlsrId}");
            Console.WriteLine($"🔢 Predicted ReqIndex: {predictedReqIndex}");

            // Load all requirements from Excel
            var requirements = _requirementRepository.LoadRequirementsFromExcel();

            var results = requirements
                .Where(req => string.IsNullOrEmpty(predictedReqIndex) || req.Requirement_Index.Trim().Equals(predictedReqIndex.Trim(), StringComparison.OrdinalIgnoreCase)).Select(req => new RequirementOutput
                {
                    RequirementDescription = req.Requirement_Index,
                    Category = req.Category,
                    ChangeInRequirement = GetFilteredChangeInRequirement(req.Change_In_Requirements, mlsrId)
                })
                .ToList();
            // Debug: print out to verify what is being compared
            Console.WriteLine($"Predicted ReqIndex: {predictedReqIndex}");
            Console.WriteLine($"Filtered Requirements Count: {results.Count}");
            return results;
        }

        private string ExtractMlsrId(string query)
        {
            var mlsrMapping = _standardRepository.LoadMlsrMapping(); // ✅ Load dynamically

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

            var finalChanges = new List<string>();

            // If MLSR ID is available, filter changes and add description for filtered changes
            if (!string.IsNullOrEmpty(mlsrId))
            {
                var filteredChanges = changes
                    .Where(line => line.TrimStart().StartsWith(mlsrId, StringComparison.OrdinalIgnoreCase))
                    .ToList();

                // If we have filtered changes, process and add descriptions
                foreach (var change in filteredChanges)
                {
                    var mlsrIdInChange = Helper.ExtractMlsrIdFromChange(change);
                    if (!string.IsNullOrEmpty(mlsrIdInChange))
                    {
                        var requirementDescription = GetRequirementDescriptionFromProductSheet(mlsrIdInChange);
                        var standardRefName = GetRequirementStandardFromStandardSheet(mlsrIdInChange);
                        if (!string.IsNullOrEmpty(requirementDescription))
                        {
                            finalChanges.Add($"{standardRefName} - {requirementDescription}");
                        }
                    }
                    else
                    {
                        finalChanges.Add(change); // Add the change without description if no MLSR ID is found
                    }
                }

                return finalChanges;
            }

            // If MLSR ID is not available, process all changes and add description for each change
            foreach (var change in changes)
            {
                var mlsrIdInChange = Helper.ExtractMlsrIdFromChange(change);
                if (!string.IsNullOrEmpty(mlsrIdInChange))
                {
                    var requirementDescription = GetRequirementDescriptionFromProductSheet(mlsrIdInChange);
                    var standardRefName = GetRequirementStandardFromStandardSheet(mlsrIdInChange);
                    if (!string.IsNullOrEmpty(requirementDescription))
                    {
                        finalChanges.Add($"{standardRefName} - {requirementDescription}");
                    }
                }
                else
                {
                    finalChanges.Add(change); // Add the change without description if no MLSR ID is found
                }
            }

            return finalChanges;
        }

      
       
        
        // Helper method to get the requirement description from Product Requirement sheet
        private string GetRequirementDescriptionFromProductSheet(string mlsrId)
        {
            if (string.IsNullOrEmpty(mlsrId))
                return string.Empty;
            // Search for the corresponding MLSR ID and return the requirement description (column E)
            var requirement = _productRequirements
                .FirstOrDefault(req => req.MLSR_Id.Equals(mlsrId, StringComparison.OrdinalIgnoreCase));
            return requirement?.Requirement ?? "Requirement not found";
        }

        private string GetRequirementStandardFromStandardSheet(string mlsrId)
        {
            if (string.IsNullOrEmpty(mlsrId))
                return string.Empty;
            var standardMlsr  = Helper.ExtractMlsrPrefix(mlsrId);
            var requirement = _standardRequirements
                .FirstOrDefault(req => req.MLSR_ID.Equals(standardMlsr, StringComparison.OrdinalIgnoreCase));

            return requirement?.StandardRefID ?? "Requirement not found";
        }
        private static string NormalizeText(string input)
        {
            if (string.IsNullOrWhiteSpace(input))
                return string.Empty;

            // Remove multiple spaces and normalize spaces around '/'
            return Regex.Replace(input, @"\s+\/\s+", "/")  // Normalize slashes
                .Replace("  ", " ")                // Replace double spaces with a single space
                .Trim();                           // Trim spaces
        }
    }
}