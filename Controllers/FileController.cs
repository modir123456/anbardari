using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Services;

namespace PersianFileCopierPro.Controllers
{
    [ApiController]
    [Route("api/files")]
    public class FileController : ControllerBase
    {
        private readonly IFileOperationService _fileService;
        private readonly ILogger<FileController> _logger;

        public FileController(IFileOperationService fileService, ILogger<FileController> logger)
        {
            _fileService = fileService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> GetFiles([FromQuery] string path, [FromQuery] string? search = null, [FromQuery] string? type = null)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                var files = await _fileService.GetFilesAsync(path, search, type);
                return Ok(new { files, path, search, type });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting files from {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("create-directory")]
        public async Task<IActionResult> CreateDirectory([FromBody] CreateDirectoryRequest request)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(request.Path))
                    return BadRequest(new { error = "Path is required" });

                var success = await _fileService.CreateDirectoryAsync(request.Path);
                if (!success)
                    return StatusCode(500, new { error = "Failed to create directory" });

                return Ok(new { message = "Directory created successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error creating directory {request.Path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpDelete("file")]
        public async Task<IActionResult> DeleteFile([FromQuery] string path)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                var success = await _fileService.DeleteFileAsync(path);
                if (!success)
                    return NotFound(new { error = "File not found or could not be deleted" });

                return Ok(new { message = "File deleted successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error deleting file {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpDelete("directory")]
        public async Task<IActionResult> DeleteDirectory([FromQuery] string path, [FromQuery] bool recursive = false)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                var success = await _fileService.DeleteDirectoryAsync(path, recursive);
                if (!success)
                    return NotFound(new { error = "Directory not found or could not be deleted" });

                return Ok(new { message = "Directory deleted successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error deleting directory {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("size")]
        public async Task<IActionResult> GetDirectorySize([FromQuery] string path)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                var size = await _fileService.GetDirectorySizeAsync(path);
                return Ok(new { size, path });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting directory size {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("count")]
        public async Task<IActionResult> GetFileCount([FromQuery] string path)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                var count = await _fileService.GetFileCountAsync(path);
                return Ok(new { count, path });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting file count {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("exists")]
        public IActionResult CheckExists([FromQuery] string path, [FromQuery] string type = "file")
        {
            try
            {
                if (string.IsNullOrWhiteSpace(path))
                    return BadRequest(new { error = "Path is required" });

                // Decode the path
                path = Uri.UnescapeDataString(path);

                bool exists = type.ToLowerInvariant() switch
                {
                    "directory" => _fileService.DirectoryExists(path),
                    _ => _fileService.FileExists(path)
                };

                return Ok(new { exists, path, type });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error checking existence {path}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }

    public class CreateDirectoryRequest
    {
        public string Path { get; set; } = string.Empty;
    }
}