using PersianFileCopierPro.Models;
using System.Text.RegularExpressions;

namespace PersianFileCopierPro.Services
{
    public class FileOperationService : IFileOperationService
    {
        private readonly ILogger<FileOperationService> _logger;
        private const int BufferSize = 1024 * 1024; // 1MB buffer

        public FileOperationService(ILogger<FileOperationService> logger)
        {
            _logger = logger;
        }

        public async Task CopyFileAsync(string sourcePath, string destinationPath, Action<long> progressCallback, CancellationToken cancellationToken)
        {
            try
            {
                var sourceInfo = new FileInfo(sourcePath);
                if (!sourceInfo.Exists)
                {
                    throw new FileNotFoundException($"Source file not found: {sourcePath}");
                }

                // Ensure destination directory exists
                var destDir = Path.GetDirectoryName(destinationPath);
                if (!string.IsNullOrEmpty(destDir) && !Directory.Exists(destDir))
                {
                    Directory.CreateDirectory(destDir);
                }

                // Determine final destination path
                var finalDestPath = destinationPath;
                if (Directory.Exists(destinationPath))
                {
                    finalDestPath = Path.Combine(destinationPath, sourceInfo.Name);
                }

                var buffer = new byte[BufferSize];
                long totalCopied = 0;

                using var sourceStream = new FileStream(sourcePath, FileMode.Open, FileAccess.Read, FileShare.Read, BufferSize, FileOptions.SequentialScan);
                using var destStream = new FileStream(finalDestPath, FileMode.Create, FileAccess.Write, FileShare.None, BufferSize, FileOptions.SequentialScan);

                int bytesRead;
                while ((bytesRead = await sourceStream.ReadAsync(buffer, 0, buffer.Length, cancellationToken)) > 0)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    
                    await destStream.WriteAsync(buffer, 0, bytesRead, cancellationToken);
                    totalCopied += bytesRead;
                    
                    progressCallback?.Invoke(totalCopied);
                    
                    // Small delay to allow for UI updates and cancellation checks
                    if (totalCopied % (BufferSize * 10) == 0)
                    {
                        await Task.Delay(1, cancellationToken);
                    }
                }

                // Copy file attributes
                File.SetCreationTime(finalDestPath, sourceInfo.CreationTime);
                File.SetLastWriteTime(finalDestPath, sourceInfo.LastWriteTime);
                File.SetAttributes(finalDestPath, sourceInfo.Attributes);

                _logger.LogDebug($"✅ Successfully copied {sourcePath} to {finalDestPath} ({totalCopied} bytes)");
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to copy {sourcePath}: {ex.Message}");
                throw;
            }
        }

        public async Task CopyDirectoryAsync(string sourcePath, string destinationPath, Action<long>? progressCallback = null, CancellationToken cancellationToken = default)
        {
            try
            {
                if (!Directory.Exists(sourcePath))
                {
                    throw new DirectoryNotFoundException($"Source directory not found: {sourcePath}");
                }

                // Create destination directory
                var destDirInfo = new DirectoryInfo(destinationPath);
                if (destDirInfo.Exists)
                {
                    // If destination exists, create subdirectory with source name
                    var sourceDirName = new DirectoryInfo(sourcePath).Name;
                    destinationPath = Path.Combine(destinationPath, sourceDirName);
                }

                Directory.CreateDirectory(destinationPath);

                // Copy all files in current directory
                var sourceDir = new DirectoryInfo(sourcePath);
                foreach (var file in sourceDir.GetFiles())
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    
                    var destFilePath = Path.Combine(destinationPath, file.Name);
                    await CopyFileAsync(file.FullName, destFilePath, progressCallback, cancellationToken);
                }

                // Recursively copy subdirectories
                foreach (var subDir in sourceDir.GetDirectories())
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    
                    var destSubDirPath = Path.Combine(destinationPath, subDir.Name);
                    await CopyDirectoryAsync(subDir.FullName, destSubDirPath, progressCallback, cancellationToken);
                }

                _logger.LogDebug($"✅ Successfully copied directory {sourcePath} to {destinationPath}");
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to copy directory {sourcePath}: {ex.Message}");
                throw;
            }
        }

        public async Task<List<FileModel>> GetFilesAsync(string path, string? searchQuery = null, string? typeFilter = null)
        {
            var files = new List<FileModel>();

            try
            {
                if (!Directory.Exists(path))
                {
                    return files;
                }

                var directoryInfo = new DirectoryInfo(path);
                
                // Get directories
                var directories = directoryInfo.GetDirectories()
                    .Where(d => !d.Attributes.HasFlag(FileAttributes.Hidden) && !d.Attributes.HasFlag(FileAttributes.System))
                    .Select(d => new FileModel
                    {
                        Name = d.Name,
                        Path = d.FullName,
                        Extension = string.Empty,
                        Size = 0,
                        ModifiedDate = d.LastWriteTime,
                        CreatedDate = d.CreationTime,
                        IsDirectory = true,
                        Icon = "📁"
                    });

                // Get files
                var fileInfos = directoryInfo.GetFiles()
                    .Where(f => !f.Attributes.HasFlag(FileAttributes.Hidden) && !f.Attributes.HasFlag(FileAttributes.System))
                    .Select(f => new FileModel
                    {
                        Name = f.Name,
                        Path = f.FullName,
                        Extension = f.Extension.ToLowerInvariant(),
                        Size = f.Length,
                        ModifiedDate = f.LastWriteTime,
                        CreatedDate = f.CreationTime,
                        IsDirectory = false,
                        Icon = GetFileIcon(f.Extension)
                    });

                files.AddRange(directories);
                files.AddRange(fileInfos);

                // Apply search filter
                if (!string.IsNullOrWhiteSpace(searchQuery))
                {
                    var regex = new Regex(Regex.Escape(searchQuery), RegexOptions.IgnoreCase);
                    files = files.Where(f => regex.IsMatch(f.Name)).ToList();
                }

                // Apply type filter
                if (!string.IsNullOrWhiteSpace(typeFilter))
                {
                    files = typeFilter.ToLowerInvariant() switch
                    {
                        "image" => files.Where(f => f.IsDirectory || IsImageFile(f.Extension)).ToList(),
                        "video" => files.Where(f => f.IsDirectory || IsVideoFile(f.Extension)).ToList(),
                        "audio" => files.Where(f => f.IsDirectory || IsAudioFile(f.Extension)).ToList(),
                        "document" => files.Where(f => f.IsDirectory || IsDocumentFile(f.Extension)).ToList(),
                        "archive" => files.Where(f => f.IsDirectory || IsArchiveFile(f.Extension)).ToList(),
                        _ => files
                    };
                }

                // Sort directories first, then by name
                files = files.OrderBy(f => !f.IsDirectory).ThenBy(f => f.Name).ToList();
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to get files from {path}: {ex.Message}");
            }

            return await Task.FromResult(files);
        }

        public async Task<bool> CreateDirectoryAsync(string path)
        {
            try
            {
                Directory.CreateDirectory(path);
                _logger.LogInformation($"📁 Created directory: {path}");
                return await Task.FromResult(true);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to create directory {path}: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> DeleteFileAsync(string path)
        {
            try
            {
                if (File.Exists(path))
                {
                    File.Delete(path);
                    _logger.LogInformation($"🗑️ Deleted file: {path}");
                    return await Task.FromResult(true);
                }
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to delete file {path}: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> DeleteDirectoryAsync(string path, bool recursive = false)
        {
            try
            {
                if (Directory.Exists(path))
                {
                    Directory.Delete(path, recursive);
                    _logger.LogInformation($"🗑️ Deleted directory: {path}");
                    return await Task.FromResult(true);
                }
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to delete directory {path}: {ex.Message}");
                return false;
            }
        }

        public async Task<long> GetDirectorySizeAsync(string path)
        {
            try
            {
                if (!Directory.Exists(path))
                    return 0;

                var dirInfo = new DirectoryInfo(path);
                var size = dirInfo.GetFiles("*", SearchOption.AllDirectories).Sum(f => f.Length);
                return await Task.FromResult(size);
            }
            catch
            {
                return 0;
            }
        }

        public async Task<int> GetFileCountAsync(string path)
        {
            try
            {
                if (!Directory.Exists(path))
                    return 0;

                var dirInfo = new DirectoryInfo(path);
                var count = dirInfo.GetFiles("*", SearchOption.AllDirectories).Length;
                return await Task.FromResult(count);
            }
            catch
            {
                return 0;
            }
        }

        public bool FileExists(string path) => File.Exists(path);

        public bool DirectoryExists(string path) => Directory.Exists(path);

        private static string GetFileIcon(string extension)
        {
            return extension.ToLowerInvariant() switch
            {
                ".jpg" or ".jpeg" or ".png" or ".gif" or ".bmp" or ".svg" or ".webp" => "🖼️",
                ".mp4" or ".avi" or ".mkv" or ".mov" or ".wmv" or ".flv" or ".webm" => "🎬",
                ".mp3" or ".wav" or ".flac" or ".aac" or ".ogg" or ".wma" => "🎵",
                ".pdf" => "📕",
                ".doc" or ".docx" => "📘",
                ".xls" or ".xlsx" => "📗",
                ".ppt" or ".pptx" => "📙",
                ".txt" or ".md" => "📄",
                ".zip" or ".rar" or ".7z" or ".tar" or ".gz" => "📦",
                ".exe" or ".msi" => "⚙️",
                ".dll" => "🔧",
                ".iso" => "💿",
                _ => "📄"
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
}