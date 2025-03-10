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

        public List<string> GetAllStandardNames()
        {
            return standardRepository.GetALlStandardNames();
        }
        public List<Standard> GetAllStandards()
        {
            return standardRepository.GetAll();
        }

        public List<RequirementOutput> SearchRequirements(string query)
        {
            return semanticSearch.FindMatchingRequirements( query); 
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