using System.Text.RegularExpressions;

namespace Domain;

public static class Helper
{
    public static string GetProjectRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory != null && !directory.Name.Equals("AI-SDLC-Analyzer", StringComparison.OrdinalIgnoreCase))
        {
            directory = directory.Parent;
        }
        if (directory == null)
            throw new DirectoryNotFoundException("Project root directory 'AI-SDLC-Analyzer' not found.");
        return directory.FullName;
    }
    
    public static string ExtractMlsrPrefix(string mlsrId)
    {
        if (string.IsNullOrEmpty(mlsrId))
            return string.Empty;

        // Regular expression to extract part before the underscore (e.g., MLSR049 from MLSR049_1677)
        var match = Regex.Match(mlsrId, @"^([A-Za-z]+\d+)");
        
        // If there's a match, return the first group (the prefix part)
        return match.Success ? match.Groups[1].Value : string.Empty;
    }
    public static string ExtractMlsrIdFromChange(string change)
    {
        var match = Regex.Match(change, @"(MLSR\d{3,4}_\d{2,4})"); // Updated regex to support 4 digits
        return match.Success ? match.Value : string.Empty;
    }
    private static string NormalizeText(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return string.Empty;

        // Remove multiple spaces and normalize spaces around '/'
        return Regex.Replace(input, @"\s+\/\s+", "/")  // Normalize slashes
            .Replace("  ", " ")                // Replace double spaces with a single space
            .Trim();                           // Trim spaces
    }
}