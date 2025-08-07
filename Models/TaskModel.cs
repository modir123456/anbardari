using System.Text.Json.Serialization;

namespace PersianFileCopierPro.Models
{
    public enum TaskStatus
    {
        Preparing,
        Running,
        Paused,
        Completed,
        Failed,
        Cancelled
    }

    public class TaskModel
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [JsonPropertyName("status")]
        public TaskStatus Status { get; set; } = TaskStatus.Preparing;
        
        [JsonPropertyName("type")]
        public string Type { get; set; } = "copy";
        
        [JsonPropertyName("source_files")]
        public List<string> SourceFiles { get; set; } = new();
        
        [JsonPropertyName("destination")]
        public string Destination { get; set; } = string.Empty;
        
        [JsonPropertyName("source_device")]
        public string? SourceDevice { get; set; }
        
        [JsonPropertyName("dest_device")]
        public string? DestDevice { get; set; }
        
        [JsonPropertyName("current_file")]
        public string? CurrentFile { get; set; }
        
        [JsonPropertyName("progress")]
        public double Progress { get; set; } = 0;
        
        [JsonPropertyName("speed")]
        public long Speed { get; set; } = 0;
        
        [JsonPropertyName("eta")]
        public long Eta { get; set; } = 0;
        
        [JsonPropertyName("copied_files")]
        public int CopiedFiles { get; set; } = 0;
        
        [JsonPropertyName("total_files")]
        public int TotalFiles { get; set; } = 0;
        
        [JsonPropertyName("copied_size")]
        public long CopiedSize { get; set; } = 0;
        
        [JsonPropertyName("total_size")]
        public long TotalSize { get; set; } = 0;
        
        [JsonPropertyName("start_time")]
        public DateTime StartTime { get; set; } = DateTime.Now;
        
        [JsonPropertyName("end_time")]
        public DateTime? EndTime { get; set; }
        
        [JsonPropertyName("error")]
        public string? Error { get; set; }
        
        [JsonIgnore]
        public CancellationTokenSource CancellationTokenSource { get; set; } = new();
        public bool IsPaused { get; set; } = false;
    }

    public class TaskProgress
    {
        [JsonPropertyName("task_id")]
        public string TaskId { get; set; } = string.Empty;
        
        [JsonPropertyName("progress")]
        public double Progress { get; set; }
        
        [JsonPropertyName("speed")]
        public long Speed { get; set; }
        
        [JsonPropertyName("eta")]
        public long Eta { get; set; }
        
        [JsonPropertyName("copied_files")]
        public int CopiedFiles { get; set; }
        
        [JsonPropertyName("total_files")]
        public int TotalFiles { get; set; }
        
        [JsonPropertyName("copied_size")]
        public long CopiedSize { get; set; }
        
        [JsonPropertyName("total_size")]
        public long TotalSize { get; set; }
        
        [JsonPropertyName("current_file")]
        public string? CurrentFile { get; set; }
    }

    public class CopyRequest
    {
        [JsonPropertyName("source_files")]
        public List<string> SourceFiles { get; set; } = new();
        
        [JsonPropertyName("destination")]
        public string Destination { get; set; } = string.Empty;
        
        [JsonPropertyName("source_device")]
        public string? SourceDevice { get; set; }
        
        [JsonPropertyName("dest_device")]
        public string? DestDevice { get; set; }
    }

    public class ActivateLicenseRequest
    {
        public string LicenseKey { get; set; } = string.Empty;
    }

    public class GenerateLicenseRequest
    {
        public string MachineId { get; set; } = string.Empty;
        public int ValidityDays { get; set; } = 365;
    }
}