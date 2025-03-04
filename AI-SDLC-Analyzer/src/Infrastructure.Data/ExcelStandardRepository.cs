using Domain.Entities;
using Domain.Interfaces;
using OfficeOpenXml;

namespace Infrastructure.Data
{
    public class ExcelStandardRepository(string filePath) : IStandardRepository
    {
        private const string SheetName = "MLSR List";

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

            for (int row = 5; row <= rowCount; row++) // Assuming data starts at row 5
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

        public Standard GetStandardById(string mlrsId)
        {
            return GetAll().Find(s => s.MLSR_ID == mlrsId);
        }
    }
}