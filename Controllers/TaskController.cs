using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Models;
using PersianFileCopierPro.Services;

namespace PersianFileCopierPro.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TaskController : ControllerBase
    {
        private readonly ITaskManagerService _taskManager;
        private readonly ILogger<TaskController> _logger;

        public TaskController(ITaskManagerService taskManager, ILogger<TaskController> logger)
        {
            _taskManager = taskManager;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> GetTasks()
        {
            try
            {
                var tasks = await _taskManager.GetAllTasksAsync();
                return Ok(new { tasks });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting tasks: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("{taskId}")]
        public async Task<IActionResult> GetTask(string taskId)
        {
            try
            {
                var task = await _taskManager.GetTaskAsync(taskId);
                if (task == null)
                    return NotFound(new { error = "Task not found" });

                return Ok(task);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting task {taskId}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("copy")]
        public async Task<IActionResult> CreateCopyTask([FromBody] CopyRequest request)
        {
            try
            {
                if (request.SourceFiles == null || !request.SourceFiles.Any())
                    return BadRequest(new { error = "Source files are required" });

                if (string.IsNullOrWhiteSpace(request.Destination))
                    return BadRequest(new { error = "Destination is required" });

                var taskId = await _taskManager.CreateCopyTaskAsync(request);
                return Ok(new { task_id = taskId, message = "Copy task created successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error creating copy task: {ex.Message}");
                return StatusCode(500, new { error = "Failed to create copy task" });
            }
        }

        [HttpPost("{taskId}/pause")]
        public async Task<IActionResult> PauseTask(string taskId)
        {
            try
            {
                var success = await _taskManager.PauseTaskAsync(taskId);
                if (!success)
                    return BadRequest(new { error = "Cannot pause task" });

                return Ok(new { message = "Task paused successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error pausing task {taskId}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("{taskId}/resume")]
        public async Task<IActionResult> ResumeTask(string taskId)
        {
            try
            {
                var success = await _taskManager.ResumeTaskAsync(taskId);
                if (!success)
                    return BadRequest(new { error = "Cannot resume task" });

                return Ok(new { message = "Task resumed successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error resuming task {taskId}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("{taskId}/cancel")]
        public async Task<IActionResult> CancelTask(string taskId)
        {
            try
            {
                var success = await _taskManager.CancelTaskAsync(taskId);
                if (!success)
                    return BadRequest(new { error = "Cannot cancel task" });

                return Ok(new { message = "Task cancelled successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error cancelling task {taskId}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpDelete("{taskId}")]
        public async Task<IActionResult> RemoveTask(string taskId)
        {
            try
            {
                var success = await _taskManager.RemoveTaskAsync(taskId);
                if (!success)
                    return NotFound(new { error = "Task not found" });

                return Ok(new { message = "Task removed successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error removing task {taskId}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("{taskId}/retry")]
        public async Task<IActionResult> RetryTask(string taskId)
        {
            try
            {
                var task = await _taskManager.GetTaskAsync(taskId);
                if (task == null)
                    return NotFound(new { error = "Task not found" });

                // Create a new task with the same parameters
                var request = new CopyRequest
                {
                    SourceFiles = task.SourceFiles,
                    Destination = task.Destination,
                    SourceDevice = task.SourceDevice,
                    DestDevice = task.DestDevice
                };

                var newTaskId = await _taskManager.CreateCopyTaskAsync(request);
                return Ok(new { task_id = newTaskId, message = "Task retried successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error retrying task {taskId}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("pause-all")]
        public async Task<IActionResult> PauseAllTasks()
        {
            try
            {
                await _taskManager.PauseAllTasksAsync();
                return Ok(new { message = "All tasks paused successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error pausing all tasks: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("resume-all")]
        public async Task<IActionResult> ResumeAllTasks()
        {
            try
            {
                await _taskManager.ResumeAllTasksAsync();
                return Ok(new { message = "All tasks resumed successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error resuming all tasks: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("cancel-all")]
        public async Task<IActionResult> CancelAllTasks()
        {
            try
            {
                await _taskManager.CancelAllTasksAsync();
                return Ok(new { message = "All tasks cancelled successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error cancelling all tasks: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("clear-completed")]
        public async Task<IActionResult> ClearCompletedTasks()
        {
            try
            {
                await _taskManager.ClearCompletedTasksAsync();
                return Ok(new { message = "Completed tasks cleared successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error clearing completed tasks: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("export")]
        public async Task<IActionResult> ExportTaskLog()
        {
            try
            {
                var filePath = await _taskManager.ExportTaskLogAsync();
                
                if (!System.IO.File.Exists(filePath))
                    return NotFound(new { error = "Export file not found" });

                var fileBytes = await System.IO.File.ReadAllBytesAsync(filePath);
                var fileName = Path.GetFileName(filePath);

                // Clean up temp file
                System.IO.File.Delete(filePath);

                return File(fileBytes, "application/json", fileName);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error exporting task log: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}