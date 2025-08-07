using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Services;
using System.Runtime.InteropServices;

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

        [HttpPost]
        public async Task<IActionResult> SearchFiles([FromBody] SearchRequest request)
        {
            try
            {
                // Default to root search if no specific drive
                string searchPath = "C:\\"; // Default for Windows
                
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux) || 
                    RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
                {
                    searchPath = "/";
                }

                // If specific drive is selected, use that path
                if (!string.IsNullOrWhiteSpace(request.Drive) && request.Drive != "all")
                {
                    searchPath = request.Drive;
                }

                var files = await _fileService.GetFilesAsync(searchPath, request.Search, request.Type);
                
                // Apply additional filtering if needed
                if (!string.IsNullOrWhiteSpace(request.Search))
                {
                    files = files.Where(f => f.Name.Contains(request.Search, StringComparison.OrdinalIgnoreCase)).ToList();
                }

                if (!string.IsNullOrWhiteSpace(request.Type) && request.Type != "all")
                {
                    files = files.Where(f => f.IsDirectory || IsFileOfType(f.Extension, request.Type)).ToList();
                }

                // Limit results
                if (request.Limit > 0)
                {
                    files = files.Take(request.Limit).ToList();
                }

                return Ok(new { files, success = true });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error searching files: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        private static bool IsFileOfType(string extension, string type)
        {
            return type.ToLowerInvariant() switch
            {
                "image" => IsImageFile(extension),
                "video" => IsVideoFile(extension),
                "audio" => IsAudioFile(extension),
                "document" => IsDocumentFile(extension),
                "archive" => IsArchiveFile(extension),
                _ => true
            };
        }

        private static bool IsImageFile(string extension)
        {
            string[] imageExtensions = { ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".raw" };
            return imageExtensions.Contains(extension.ToLowerInvariant());
        }

        private static bool IsVideoFile(string extension)
        {
            string[] videoExtensions = { ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp" };
            return videoExtensions.Contains(extension.ToLowerInvariant());
        }

        private static bool IsAudioFile(string extension)
        {
            string[] audioExtensions = { ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a" };
            return audioExtensions.Contains(extension.ToLowerInvariant());
        }

        private static bool IsDocumentFile(string extension)
        {
            string[] docExtensions = { ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt" };
            return docExtensions.Contains(extension.ToLowerInvariant());
        }

        private static bool IsArchiveFile(string extension)
        {
            string[] archiveExtensions = { ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz" };
                         return archiveExtensions.Contains(extension.ToLowerInvariant());
         }
     }

     public class SearchRequest
     {
         public string Search { get; set; } = string.Empty;
         public string Drive { get; set; } = "all";
         public string Type { get; set; } = "all";
         public int Limit { get; set; } = 1000;
         public bool FastMode { get; set; } = true;
     }
 }