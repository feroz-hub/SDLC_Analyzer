namespace Domain.Entities
{
    public class StandardRequirement
    {
        public string ReferenceMLSRID { get; set; } // Unique Identifier
        public string RequirementDescription { get; set; }
        public string Category { get; set; }
        public string ChangeInRequirement { get; set; }
    }
}