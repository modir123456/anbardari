using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Services
{
    public interface IFileOperationService
    {
        Task CopyFileAsync(string sourcePath, string destinationPath, Action<long> progressCallback, CancellationToken cancellationToken, TaskModel? task = null);
        Task CopyDirectoryAsync(string sourcePath, string destinationPath, Action<long> progressCallback, CancellationToken cancellationToken, TaskModel? task = null);
        Task<List<FileModel>> GetFilesAsync(string path, string? searchQuery = null, string? typeFilter = null);
        Task<bool> CreateDirectoryAsync(string path);
        Task<bool> DeleteFileAsync(string path);
        Task<bool> DeleteDirectoryAsync(string path, bool recursive = false);
        Task<long> GetDirectorySizeAsync(string path);
        Task<int> GetFileCountAsync(string path);
        bool FileExists(string path);
        bool DirectoryExists(string path);
    }
}