using System.Text.RegularExpressions;

namespace Infrastructure.Resource
{
    public class NlpProcessor
    {
        public static string PreprocessText(string input)
        {
            if (string.IsNullOrWhiteSpace(input)) return string.Empty;

            // Convert to lowercase
            input = input.ToLower();

            // Remove special characters
            input = Regex.Replace(input, @"[^a-z0-9\s]", "");

            // Remove extra spaces
            input = Regex.Replace(input, @"\s+", " ").Trim();

            return input;
        }
    }
}