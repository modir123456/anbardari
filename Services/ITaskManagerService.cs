using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Services
{
    public interface ITaskManagerService
    {
        Task<string> CreateCopyTaskAsync(CopyRequest request);
        Task<Dictionary<string, TaskModel>> GetAllTasksAsync();
        Task<TaskModel?> GetTaskAsync(string taskId);
        Task<bool> PauseTaskAsync(string taskId);
        Task<bool> ResumeTaskAsync(string taskId);
        Task<bool> CancelTaskAsync(string taskId);
        Task<bool> RemoveTaskAsync(string taskId);
        Task<bool> PauseAllTasksAsync();
        Task<bool> ResumeAllTasksAsync();
        Task<bool> CancelAllTasksAsync();
        Task ClearCompletedTasksAsync();
        Task<string> ExportTaskLogAsync();
        event EventHandler<TaskProgress>? TaskProgressUpdated;
        event EventHandler<(string taskId, TaskModel task)>? TaskStatusChanged;
    }
}