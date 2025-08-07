namespace PersianFileCopierPro.Models
{
    public class DriveModel
    {
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public string DriveType { get; set; } = string.Empty;
        public string FileSystem { get; set; } = string.Empty;
        public long TotalSize { get; set; } = 0;
        public long FreeSpace { get; set; } = 0;
        public long UsedSpace => TotalSize - FreeSpace;
        public double UsagePercentage => TotalSize > 0 ? (double)UsedSpace / TotalSize * 100 : 0;
        public bool IsReady { get; set; } = true;
        public string Icon { get; set; } = "💾";
    }

    public class FileModel
    {
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public string Extension { get; set; } = string.Empty;
        public long Size { get; set; } = 0;
        public DateTime ModifiedDate { get; set; } = DateTime.Now;
        public DateTime CreatedDate { get; set; } = DateTime.Now;
        public bool IsDirectory { get; set; } = false;
        public string Icon { get; set; } = "📄";
        public string SizeFormatted => FormatFileSize(Size);

        private static string FormatFileSize(long bytes)
        {
            if (bytes == 0) return "0 B";
            
            string[] suffixes = { "B", "KB", "MB", "GB", "TB" };
            int suffixIndex = 0;
            double size = bytes;
            
            while (size >= 1024 && suffixIndex < suffixes.Length - 1)
            {
                size /= 1024;
                suffixIndex++;
            }
            
            return $"{size:N2} {suffixes[suffixIndex]}";
        }
    }
}