using Domain;
using Domain.Entities;
using Domain.Interfaces;
using OfficeOpenXml;

namespace Infrastructure.Data
{
    public class ExcelStandardRepository() : IStandardRepository
    {
        private const string SheetName = "MLSR_List";
        private static readonly string ProjectRoot = Helper.GetProjectRoot();

        private static readonly string InfrastructureResourcePath =
            Path.Combine(ProjectRoot, "src","Infrastructure.Resource","Resources");

       // ✅ Ensure the correct Excel file name is used
        private static readonly string ExcelFileName = "MLCR_Cybersecurity_Product_Requirements.xlsm";
        private static readonly string filePath = Path.Combine(InfrastructureResourcePath, ExcelFileName);

        public List<Standard> GetAll()
        {
            var standards = new List<Standard>();

            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            using var package = new ExcelPackage(new FileInfo(filePath));
            var worksheet = package.Workbook.Worksheets[SheetName];
            if (worksheet == null)
            {
                throw new Exception($"Sheet '{SheetName}' not found in Excel file.");
            }

            int rowCount = worksheet.Dimension.Rows;

            for (int row = 6; row <= rowCount; row++) // Assuming data starts at row 5
            {
                var standard = new Standard
                {
                    MLSR_ID = worksheet.Cells[row, 2].Text.Trim(), // Column B
                    StandardType = worksheet.Cells[row, 3].Text.Trim(), // Column C
                    StandardRefID = worksheet.Cells[row, 4].Text.Trim(), // Column D
                    StandardRefName = worksheet.Cells[row, 5].Text.Trim() // Column E
                };

                standards.Add(standard);
            }

            return standards;
        }
        
        public Dictionary<string, string> LoadMlsrMapping()
        {
            var mlsrMapping = new Dictionary<string, string>();

            using var package = new ExcelPackage(new FileInfo(filePath));
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;

            var mlsrSheet = package.Workbook.Worksheets[SheetName];

            // ✅ Read MLSR List Data dynamically
            for (int row = 6; row <= 44; row++)
            {
                string standardName = mlsrSheet.Cells[row, 4].Text.Trim(); // Standard Name (e.g., "NIST SP 800-53 R4")
                string mlsrId = mlsrSheet.Cells[row, 2].Text.Trim();       // MLSR ID (e.g., "MLSR049")
                if (!string.IsNullOrEmpty(standardName) && !string.IsNullOrEmpty(mlsrId))
                {
                    mlsrMapping[standardName.ToUpper()] = mlsrId;
                }
            }
            return mlsrMapping;
        }

        public List<string> GetALlStandardNames()
        {
            var standardNames = new List<string>();

            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            using var package = new ExcelPackage(new FileInfo(filePath));
            var worksheet = package.Workbook.Worksheets[SheetName];
            if (worksheet == null)
            {
                throw new Exception($"Sheet '{SheetName}' not found in Excel file.");
            }

            int rowCount = worksheet.Dimension.Rows;

            for (int row = 6; row <= rowCount; row++) // Assuming data starts at row 6
            {
                var standardRefName = worksheet.Cells[row, 4].Text.Trim(); // Column D

                if (!string.IsNullOrEmpty(standardRefName))
                {
                    standardNames.Add(standardRefName);
                }
            }

            return standardNames;
        }

        public Standard GetStandardById(string mlrsId)
        {
            return GetAll().Find(s => s.MLSR_ID == mlrsId);
        }
    }
}