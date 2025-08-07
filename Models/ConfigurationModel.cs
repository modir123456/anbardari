namespace PersianFileCopierPro.Models
{
    public class ConfigurationModel
    {
        public string AppName { get; set; } = "Persian File Copier Pro";
        public string Version { get; set; } = "3.5.0";
        public string Company { get; set; } = "Persian File Copier Team";
        public int MaxConcurrentTasks { get; set; } = 3;
        public int BufferSize { get; set; } = 1048576; // 1MB
        public bool VerifyAfterCopy { get; set; } = true;
        public bool CreateDestinationFolder { get; set; } = true;
        public bool AutoDeviceDetect { get; set; } = true;
        public string LogLevel { get; set; } = "INFO";
        public bool EnableRealTimeUpdates { get; set; } = true;
        public int UpdateIntervalMs { get; set; } = 500;
    }

    public class LicenseInfo
    {
        public string LicenseKey { get; set; } = string.Empty;
        public string MachineId { get; set; } = string.Empty;
        public DateTime? ExpiryDate { get; set; }
        public bool IsActivated { get; set; } = false;
        public bool IsTrial { get; set; } = false;
        public string LicenseType { get; set; } = "Free";
        public int DaysRemaining => ExpiryDate.HasValue ? (int)(ExpiryDate.Value - DateTime.Now).TotalDays : 0;
    }
}