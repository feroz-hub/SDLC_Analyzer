using System.Net.Http.Json;

namespace Infrastructure.Resource;

public class PythonNlpProcessor(HttpClient httpClient)
{
    private readonly HttpClient _httpClient = httpClient;
    
    public string PredictReqIndex(string query)
    {
        var requestBody = new
        {
            user_query = query,
            model_name = "all-MiniLM-L6-v2",
            method = "cosine",
            top_k = 1
        };

        var response = _httpClient.PostAsJsonAsync("http://127.0.0.1:8000/search/", requestBody).Result;

        if (response.IsSuccessStatusCode)
        {
            var result = response.Content.ReadFromJsonAsync<SearchApiResponse>().Result;
            return result?.Results?.FirstOrDefault()?.Text ?? string.Empty;
        }

        Console.WriteLine($"❌ Failed to call FastAPI. Status: {response.StatusCode}");
        return string.Empty;
    }
}
public class SearchResult
{
    public string Text { get; set; }
    public float Score { get; set; }
}

public class SearchApiResponse
{
    public string Query { get; set; }
    public string Method { get; set; }
    public string Model_Name { get; set; }
    public int Top_K { get; set; }
    public List<SearchResult> Results { get; set; }
}
