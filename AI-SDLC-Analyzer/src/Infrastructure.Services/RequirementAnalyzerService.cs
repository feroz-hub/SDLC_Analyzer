using Domain.Entities;
using Domain.Interfaces;
using Infrastructure.Resource;
using RequirementData = Domain.Entities.RequirementData;


namespace Infrastructure.Services
{
    public class RequirementAnalyzerService(
        IRequirementRepository requirementRepository,
        IStandardRepository standardRepository,
        SemanticSearch semanticSearch)
    {
        public List<StandardRequirement> GetAllRequirements()
        {
            return requirementRepository.GetAllStandardRequirements();
        }

        public List<Standard> GetAllStandards()
        {
            return standardRepository.GetAll();
        }

        public List<RequirementOutput> SearchRequirements(string query)
        {
            var requirements = requirementRepository.GetAllStandardRequirements();
            return semanticSearch.FindMatchingRequirements( query); //(query, requirements);
        }

        public StandardRequirement GetRequirementById(string id)
        {
            return requirementRepository.GetRequirementById(id);
        }

        public Standard GetStandardById(string id)
        {
            return standardRepository.GetStandardById(id);
        }
    }
}