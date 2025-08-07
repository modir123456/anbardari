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
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public TaskStatus Status { get; set; } = TaskStatus.Preparing;
        public string Type { get; set; } = "copy";
        public List<string> SourceFiles { get; set; } = new();
        public string Destination { get; set; } = string.Empty;
        public string? SourceDevice { get; set; }
        public string? DestDevice { get; set; }
        public string? CurrentFile { get; set; }
        public double Progress { get; set; } = 0;
        public long Speed { get; set; } = 0;
        public long Eta { get; set; } = 0;
        public int CopiedFiles { get; set; } = 0;
        public int TotalFiles { get; set; } = 0;
        public long CopiedSize { get; set; } = 0;
        public long TotalSize { get; set; } = 0;
        public DateTime StartTime { get; set; } = DateTime.Now;
        public DateTime? EndTime { get; set; }
        public string? Error { get; set; }
        public CancellationTokenSource CancellationTokenSource { get; set; } = new();
        public bool IsPaused { get; set; } = false;
    }

    public class TaskProgress
    {
        public string TaskId { get; set; } = string.Empty;
        public double Progress { get; set; }
        public long Speed { get; set; }
        public long Eta { get; set; }
        public int CopiedFiles { get; set; }
        public int TotalFiles { get; set; }
        public long CopiedSize { get; set; }
        public long TotalSize { get; set; }
        public string? CurrentFile { get; set; }
    }

    public class CopyRequest
    {
        public List<string> SourceFiles { get; set; } = new();
        public string Destination { get; set; } = string.Empty;
        public string? SourceDevice { get; set; }
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