namespace Domain.Entities;

public class RequirementOutput
{ 
    public string RequirementDescription { get; set; }
    public string Category { get; set; }
    public List<string> ChangeInRequirement { get; set; }
    
}