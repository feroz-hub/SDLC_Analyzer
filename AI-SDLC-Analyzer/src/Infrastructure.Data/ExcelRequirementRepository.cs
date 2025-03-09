using Domain.Entities;
using Domain.Interfaces;
using OfficeOpenXml;

namespace Infrastructure.Data;

public class ExcelRequirementRepository( ) : IRequirementRepository
{
   
    private static readonly string ProjectRoot =
        Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../../"));

    private static readonly string InfrastructureResourcePath =
        Path.Combine(ProjectRoot, "src/Infrastructure.Resource/Resources");

// ✅ Ensure the correct Excel file name is used
    private static readonly string ExcelFileName = "MLCR_Cybersecurity_Product_Requirements.xlsm";
    private static readonly string FilePath = Path.Combine(InfrastructureResourcePath, ExcelFileName);

    private const string SheetName = "Unique_Requirements"; // Adjust as needed
    public List<string> GetAllReqIndexes()
    {
        var reqIndexes = new List<string>();

        using (var package = new ExcelPackage(new FileInfo(FilePath)))
        {
            var worksheet = package.Workbook.Worksheets["Unique_Requirement"];
            
            for (int row = 3; row <= 219; row++)  // Adjust based on data range
            {
                string reqIndex = worksheet.Cells[row, 2].Text.Trim(); // Column 'B' = ReqIndex
                if (!string.IsNullOrEmpty(reqIndex))
                {
                    reqIndexes.Add(reqIndex);
                }
            }
        }

        return reqIndexes;
    }
    public List<StandardRequirement> GetAllStandardRequirements()
    {
        var requirements = new List<StandardRequirement>();

        if (!File.Exists(FilePath))
            throw new FileNotFoundException($"❌ Excel file not found at {FilePath}");

        ExcelPackage.LicenseContext = LicenseContext.NonCommercial;  // EPPlus license

        using var package = new ExcelPackage(new FileInfo(FilePath));
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
    
    public List<RequirementData> LoadRequirementsFromExcel()
    {
        ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
        var requirements = new List<RequirementData>();

        using (var package = new ExcelPackage(new FileInfo(FilePath)))
        {
            var sheet = package.Workbook.Worksheets["Unique_Requirements"];

            for (int row = 3; row <= 219; row++)
            {
                string fullMlsrId = sheet.Cells[row, 2].Text;
                string reqIndex = sheet.Cells[row, 3].Text;
                string category = sheet.Cells[row, 8].Text;
                string changeInRequirements = sheet.Cells[row, 4].Text;

                requirements.Add(new RequirementData
                {
                    MLSR_ID = fullMlsrId,
                    Requirement_Index = reqIndex,
                    Category = category,
                    Change_In_Requirements = changeInRequirements
                });
            }
        }
        return requirements;
    }
    
    public StandardRequirement GetRequirementById(string id)
    {
        return GetAllStandardRequirements().Find(r => r.ReferenceMLSRID == id);
    }
}