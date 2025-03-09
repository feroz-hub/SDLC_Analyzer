using OfficeOpenXml;

namespace RequirementAnalyser;

public class ExcelReader
{
    private readonly string filePath;
    public ExcelReader(string excelFilePath)
    {
        filePath = excelFilePath;
        ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
    }
    
    
    public List<string> GetAllReqIndexes()
    {
        var reqIndexes = new List<string>();

        using (var package = new ExcelPackage(new FileInfo(filePath)))
        {
            var worksheet = package.Workbook.Worksheets["Unique_Requirements"];
            
            for (int row = 3; row <= 219; row++)  // Adjust based on data range
            {
                string reqIndex = worksheet.Cells[row, 3].Text.Trim(); // Column 'B' = ReqIndex
                if (!string.IsNullOrEmpty(reqIndex))
                {
                    reqIndexes.Add(reqIndex);
                }
            }
        }

        return reqIndexes;
    }
}