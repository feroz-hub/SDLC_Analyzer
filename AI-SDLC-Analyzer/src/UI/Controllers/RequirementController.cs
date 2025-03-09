using Domain.Entities;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;

namespace UI.Controllers;



public class RequirementController : Controller
{
    private readonly HttpClient _httpClient;

    public RequirementController(IHttpClientFactory httpClientFactory)
    {
        _httpClient = httpClientFactory.CreateClient();
    }

    public IActionResult Chat()
    {
        return View();
    }

    [HttpPost]
    public async Task<JsonResult> ChatQuery([FromBody] ChatRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Query))
        {
            return Json(new { error = "Query cannot be empty." });
        }

        string apiUrl = $"http://localhost:5135/api/requirements/search?query={request.Query}";

        try
        {
            var response = await _httpClient.GetAsync(apiUrl);
            response.EnsureSuccessStatusCode();
            var jsonResponse = await response.Content.ReadAsStringAsync();

            var requirements = JsonConvert.DeserializeObject<List<RequirementOutput>>(jsonResponse);
            return Json(requirements);
        }
        catch
        {
            return Json(new { error = "⚠️ Error retrieving data from API." });
        }
    }
}

public class ChatRequest
{
    public string Query { get; set; }
}
