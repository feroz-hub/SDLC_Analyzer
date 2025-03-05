using Microsoft.AspNetCore.Mvc;
using Infrastructure.Services;

namespace API.Controllers
{
    [ApiController]
    [Route("api/requirements")]
    
    public class RequirementAnalyzerController(RequirementAnalyzerService requirementAnalyzerService) : ControllerBase
    {
        /// <summary>
        /// Get all Standard Requirements.
        /// </summary>
        [HttpGet]
        public IActionResult GetAllRequirements()
        {
            var requirements = requirementAnalyzerService.GetAllRequirements();
            return Ok(requirements);
        }

        /// <summary>
        /// Get all Standards.
        /// </summary>
        [HttpGet("standards")]
        public IActionResult GetAllStandards()
        {
            var standards = requirementAnalyzerService.GetAllStandards();
            return Ok(standards);
        }

        /// <summary>
        /// Search Requirements using AI-based Semantic Search.
        /// </summary>
        [HttpGet("search")]
        public IActionResult SearchRequirements([FromQuery] string query)
        {
            if (string.IsNullOrWhiteSpace(query))
                return BadRequest("Query cannot be empty.");

            var results = requirementAnalyzerService.SearchRequirements(query);

            if (results.Count == 0)
                return NotFound("No matching requirements found.");

            return Ok(results);
        }

        /// <summary>
        /// Get a specific Requirement by ID.
        /// </summary>
        [HttpGet("{id}")]
        public IActionResult GetRequirementById(string id)
        {
            var requirement = requirementAnalyzerService.GetRequirementById(id);
            if (requirement == null)
                return NotFound($"Requirement with ID {id} not found.");

            return Ok(requirement);
        }

        /// <summary>
        /// Get a specific Standard by ID.
        /// </summary>
        [HttpGet("standards/{id}")]
        public IActionResult GetStandardById(string id)
        {
            var standard = requirementAnalyzerService.GetStandardById(id);
            if (standard == null)
                return NotFound($"Standard with ID {id} not found.");

            return Ok(standard);
        }
    }
}
