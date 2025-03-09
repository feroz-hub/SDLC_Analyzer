using Domain.Entities;

namespace Domain.Interfaces;


    public interface IRequirementRepository
    {
        List<StandardRequirement> GetAllStandardRequirements();
        StandardRequirement GetRequirementById(string id);
        List<RequirementData> LoadRequirementsFromExcel();
        List<string> GetAllReqIndexes();
    }
