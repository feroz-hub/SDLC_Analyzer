namespace ModelTraining;

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
}