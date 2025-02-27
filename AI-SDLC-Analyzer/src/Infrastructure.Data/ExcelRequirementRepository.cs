using Domain;
using Domain.Entities;
using Domain.Interfaces;
using OfficeOpenXml;

namespace Infrastructure.Data;

public class ExcelRequirementRepository(string filePath) : IRequirementRepository
{
    private readonly string _filePath = filePath;
    private const string SheetName = "Unique Requirement"; // Adjust as needed

    public List<StandardRequirement> GetAllStandardRequirements()
    {
        var requirements = new List<StandardRequirement>();

        if (!File.Exists(filePath))
            throw new FileNotFoundException($"❌ Excel file not found at {filePath}");

        ExcelPackage.LicenseContext = LicenseContext.NonCommercial;  // EPPlus license

        using var package = new ExcelPackage(new FileInfo(filePath));
        var worksheet = package.Workbook.Worksheets[SheetName];

        if (worksheet == null)
            throw new Exception($"❌ Sheet '{SheetName}' not found in the Excel file.");

        int rowCount = worksheet.Dimension.Rows;

        for (int row = 3; row <= rowCount; row++)  // Skip headers
        {
            requirements.Add(new StandardRequirement
            {
                ReferenceMLSRID = worksheet.Cells[row, 2].Text,
                RequirementDescription = worksheet.Cells[row, 3].Text.Length > 500 
                    ? worksheet.Cells[row, 3].Text.Substring(0, 500) 
                    : worksheet.Cells[row, 3].Text,
                Category = worksheet.Cells[row, 8].Text,
                ChangeInRequirement = worksheet.Cells[row, 4].Text
                
                
            });
        }

        return requirements;
    }
    
    public StandardRequirement GetRequirementById(string id)
    {
        return GetAllStandardRequirements().Find(r => r.ReferenceMLSRID == id);
    }
}