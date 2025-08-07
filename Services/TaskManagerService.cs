using Microsoft.AspNetCore.SignalR;
using Newtonsoft.Json;
using PersianFileCopierPro.Hubs;
using PersianFileCopierPro.Models;
using System.Collections.Concurrent;
using System.Diagnostics;

namespace PersianFileCopierPro.Services
{
    public class TaskManagerService : ITaskManagerService
    {
        private readonly ConcurrentDictionary<string, TaskModel> _tasks = new();
        private readonly IHubContext<TaskHub> _hubContext;
        private readonly IFileOperationService _fileOperationService;
        private readonly ILogger<TaskManagerService> _logger;
        
        public event EventHandler<TaskProgress>? TaskProgressUpdated;
        public event EventHandler<(string taskId, TaskModel task)>? TaskStatusChanged;

        public TaskManagerService(
            IHubContext<TaskHub> hubContext,
            IFileOperationService fileOperationService,
            ILogger<TaskManagerService> logger)
        {
            _hubContext = hubContext;
            _fileOperationService = fileOperationService;
            _logger = logger;
        }

        public async Task<string> CreateCopyTaskAsync(CopyRequest request)
        {
            var task = new TaskModel
            {
                SourceFiles = request.SourceFiles,
                Destination = request.Destination,
                SourceDevice = request.SourceDevice,
                DestDevice = request.DestDevice,
                Status = TaskStatus.Preparing
            };

            _tasks[task.Id] = task;
            
            // Calculate total size and file count
            await CalculateTaskMetricsAsync(task);
            
            // Start the copy operation in background
            _ = Task.Run(async () => await ExecuteCopyTaskAsync(task));
            
            // Notify clients
            await _hubContext.Clients.All.SendAsync("task_started", new { task_id = task.Id, task_data = task });
            
            _logger.LogInformation($"✅ Created copy task {task.Id} for {task.SourceFiles.Count} files");
            
            return task.Id;
        }

        public async Task<Dictionary<string, TaskModel>> GetAllTasksAsync()
        {
            return await Task.FromResult(_tasks.ToDictionary(kvp => kvp.Key, kvp => kvp.Value));
        }

        public async Task<TaskModel?> GetTaskAsync(string taskId)
        {
            _tasks.TryGetValue(taskId, out var task);
            return await Task.FromResult(task);
        }

        public async Task<bool> PauseTaskAsync(string taskId)
        {
            if (_tasks.TryGetValue(taskId, out var task) && task.Status == TaskStatus.Running)
            {
                task.IsPaused = true;
                task.Status = TaskStatus.Paused;
                await NotifyTaskStatusChanged(taskId, task);
                _logger.LogInformation($"⏸️ Paused task {taskId}");
                return true;
            }
            return false;
        }

        public async Task<bool> ResumeTaskAsync(string taskId)
        {
            if (_tasks.TryGetValue(taskId, out var task) && task.Status == TaskStatus.Paused)
            {
                task.IsPaused = false;
                task.Status = TaskStatus.Running;
                await NotifyTaskStatusChanged(taskId, task);
                _logger.LogInformation($"▶️ Resumed task {taskId}");
                return true;
            }
            return false;
        }

        public async Task<bool> CancelTaskAsync(string taskId)
        {
            if (_tasks.TryGetValue(taskId, out var task))
            {
                task.CancellationTokenSource.Cancel();
                task.Status = TaskStatus.Cancelled;
                task.EndTime = DateTime.Now;
                await NotifyTaskStatusChanged(taskId, task);
                _logger.LogInformation($"⏹️ Cancelled task {taskId}");
                return true;
            }
            return false;
        }

        public async Task<bool> RemoveTaskAsync(string taskId)
        {
            if (_tasks.TryRemove(taskId, out var task))
            {
                if (task.Status == TaskStatus.Running)
                {
                    task.CancellationTokenSource.Cancel();
                }
                _logger.LogInformation($"🗑️ Removed task {taskId}");
                return await Task.FromResult(true);
            }
            return false;
        }

        public async Task<bool> PauseAllTasksAsync()
        {
            var runningTasks = _tasks.Values.Where(t => t.Status == TaskStatus.Running).ToList();
            foreach (var task in runningTasks)
            {
                await PauseTaskAsync(task.Id);
            }
            return true;
        }

        public async Task<bool> ResumeAllTasksAsync()
        {
            var pausedTasks = _tasks.Values.Where(t => t.Status == TaskStatus.Paused).ToList();
            foreach (var task in pausedTasks)
            {
                await ResumeTaskAsync(task.Id);
            }
            return true;
        }

        public async Task<bool> CancelAllTasksAsync()
        {
            var activeTasks = _tasks.Values.Where(t => 
                t.Status == TaskStatus.Running || 
                t.Status == TaskStatus.Paused || 
                t.Status == TaskStatus.Preparing).ToList();
            
            foreach (var task in activeTasks)
            {
                await CancelTaskAsync(task.Id);
            }
            return true;
        }

        public async Task ClearCompletedTasksAsync()
        {
            var completedTasks = _tasks.Where(kvp => 
                kvp.Value.Status == TaskStatus.Completed || 
                kvp.Value.Status == TaskStatus.Failed || 
                kvp.Value.Status == TaskStatus.Cancelled).ToList();

            foreach (var (taskId, _) in completedTasks)
            {
                _tasks.TryRemove(taskId, out _);
            }

            _logger.LogInformation($"🧹 Cleared {completedTasks.Count} completed tasks");
            await Task.CompletedTask;
        }

        public async Task<string> ExportTaskLogAsync()
        {
            var exportData = new
            {
                export_time = DateTime.Now,
                tasks = _tasks.Values.Select(t => new
                {
                    id = t.Id,
                    status = t.Status.ToString(),
                    source_files = t.SourceFiles,
                    destination = t.Destination,
                    progress = t.Progress,
                    start_time = t.StartTime,
                    end_time = t.EndTime,
                    error = t.Error,
                    copied_files = t.CopiedFiles,
                    total_files = t.TotalFiles,
                    copied_size = t.CopiedSize,
                    total_size = t.TotalSize
                })
            };

            var json = JsonConvert.SerializeObject(exportData, Formatting.Indented);
            var fileName = $"task-log-{DateTime.Now:yyyy-MM-dd-HH-mm-ss}.json";
            var filePath = Path.Combine(Path.GetTempPath(), fileName);
            
            await File.WriteAllTextAsync(filePath, json);
            return filePath;
        }

        private async Task CalculateTaskMetricsAsync(TaskModel task)
        {
            long totalSize = 0;
            int totalFiles = 0;

            foreach (var sourceFile in task.SourceFiles)
            {
                if (File.Exists(sourceFile))
                {
                    var fileInfo = new FileInfo(sourceFile);
                    totalSize += fileInfo.Length;
                    totalFiles++;
                }
                else if (Directory.Exists(sourceFile))
                {
                    var dirInfo = new DirectoryInfo(sourceFile);
                    var files = dirInfo.GetFiles("*", SearchOption.AllDirectories);
                    totalSize += files.Sum(f => f.Length);
                    totalFiles += files.Length;
                }
            }

            task.TotalSize = totalSize;
            task.TotalFiles = totalFiles;
            
            await Task.CompletedTask;
        }

        private async Task ExecuteCopyTaskAsync(TaskModel task)
        {
            try
            {
                task.Status = TaskStatus.Running;
                await NotifyTaskStatusChanged(task.Id, task);

                var stopwatch = Stopwatch.StartNew();
                long lastCopiedSize = 0;

                foreach (var sourceFile in task.SourceFiles)
                {
                    if (task.CancellationTokenSource.Token.IsCancellationRequested)
                    {
                        task.Status = TaskStatus.Cancelled;
                        break;
                    }

                    // Wait if paused
                    while (task.IsPaused && !task.CancellationTokenSource.Token.IsCancellationRequested)
                    {
                        await Task.Delay(100);
                    }

                    task.CurrentFile = sourceFile;
                    await _fileOperationService.CopyFileAsync(sourceFile, task.Destination, 
                        (progress) => UpdateTaskProgress(task, progress, stopwatch, ref lastCopiedSize),
                        task.CancellationTokenSource.Token);

                    task.CopiedFiles++;
                }

                if (!task.CancellationTokenSource.Token.IsCancellationRequested)
                {
                    task.Status = TaskStatus.Completed;
                    task.Progress = 100;
                    task.EndTime = DateTime.Now;
                    
                    await _hubContext.Clients.All.SendAsync("task_completed", new { task_id = task.Id });
                    _logger.LogInformation($"✅ Task {task.Id} completed successfully");
                }
            }
            catch (Exception ex)
            {
                task.Status = TaskStatus.Failed;
                task.Error = ex.Message;
                task.EndTime = DateTime.Now;
                _logger.LogError($"❌ Task {task.Id} failed: {ex.Message}");
            }
            finally
            {
                await NotifyTaskStatusChanged(task.Id, task);
            }
        }

        private void UpdateTaskProgress(TaskModel task, long copiedBytes, Stopwatch stopwatch, ref long lastCopiedSize)
        {
            task.CopiedSize += copiedBytes - lastCopiedSize;
            lastCopiedSize = copiedBytes;
            
            if (task.TotalSize > 0)
            {
                task.Progress = (double)task.CopiedSize / task.TotalSize * 100;
            }

            // Calculate speed and ETA
            var elapsed = stopwatch.Elapsed;
            if (elapsed.TotalSeconds > 0)
            {
                task.Speed = (long)(task.CopiedSize / elapsed.TotalSeconds);
                
                if (task.Speed > 0)
                {
                    var remainingBytes = task.TotalSize - task.CopiedSize;
                    task.Eta = (long)(remainingBytes / task.Speed);
                }
            }

            var progress = new TaskProgress
            {
                TaskId = task.Id,
                Progress = task.Progress,
                Speed = task.Speed,
                Eta = task.Eta,
                CopiedFiles = task.CopiedFiles,
                TotalFiles = task.TotalFiles,
                CopiedSize = task.CopiedSize,
                TotalSize = task.TotalSize,
                CurrentFile = task.CurrentFile
            };

            TaskProgressUpdated?.Invoke(this, progress);
            
            // Send via SignalR
            _ = Task.Run(async () => await _hubContext.Clients.All.SendAsync("task_progress", 
                new { task_id = task.Id, progress_data = progress }));
        }

        private async Task NotifyTaskStatusChanged(string taskId, TaskModel task)
        {
            TaskStatusChanged?.Invoke(this, (taskId, task));
            await _hubContext.Clients.All.SendAsync("task_update", new { task_id = taskId, task_data = task });
        }
    }
}