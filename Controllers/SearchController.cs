using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Services;

namespace PersianFileCopierPro.Controllers
{
    [ApiController]
    [Route("api/search")]
    public class SearchController : ControllerBase
    {
        private readonly IFileOperationService _fileService;
        private readonly ILogger<SearchController> _logger;

        public SearchController(IFileOperationService fileService, ILogger<SearchController> logger)
        {
            _fileService = fileService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> SearchFiles([FromQuery] string path, [FromQuery] string? query = null, [FromQuery] string? type = null)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                var files = await _fileService.GetFilesAsync(path, query, type);
                return Ok(new { files, path, query, type });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error searching files in {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}