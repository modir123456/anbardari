using PersianFileCopierPro.Models;
using System.Runtime.InteropServices;

namespace PersianFileCopierPro.Services
{
    public class DriveService : IDriveService
    {
        private readonly ILogger<DriveService> _logger;
        private List<DriveModel> _cachedDrives = new();
        private DateTime _lastRefresh = DateTime.MinValue;
        private readonly TimeSpan _cacheExpiry = TimeSpan.FromSeconds(30);

        public DriveService(ILogger<DriveService> logger)
        {
            _logger = logger;
        }

        public async Task<List<DriveModel>> GetDrivesAsync()
        {
            if (_cachedDrives.Count == 0 || DateTime.Now - _lastRefresh > _cacheExpiry)
            {
                await RefreshDrivesAsync();
            }

            return _cachedDrives;
        }

        public async Task<DriveModel?> GetDriveAsync(string drivePath)
        {
            var drives = await GetDrivesAsync();
            return drives.FirstOrDefault(d => d.Path.Equals(drivePath, StringComparison.OrdinalIgnoreCase));
        }

        public async Task RefreshDrivesAsync()
        {
            try
            {
                var drives = new List<DriveModel>();
                var systemDrives = DriveInfo.GetDrives();

                foreach (var drive in systemDrives)
                {
                    try
                    {
                        if (!drive.IsReady)
                        {
                            drives.Add(new DriveModel
                            {
                                Name = $"{drive.Name} (Not Ready)",
                                Path = drive.Name,
                                DriveType = drive.DriveType.ToString(),
                                FileSystem = "Unknown",
                                TotalSize = 0,
                                FreeSpace = 0,
                                IsReady = false,
                                Icon = GetDriveIcon(drive.DriveType)
                            });
                            continue;
                        }

                        var driveModel = new DriveModel
                        {
                            Name = GetDriveName(drive),
                            Path = drive.Name,
                            DriveType = drive.DriveType.ToString(),
                            FileSystem = drive.DriveFormat,
                            TotalSize = drive.TotalSize,
                            FreeSpace = drive.TotalFreeSpace,
                            IsReady = true,
                            Icon = GetDriveIcon(drive.DriveType)
                        };

                        drives.Add(driveModel);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning($"⚠️ Could not access drive {drive.Name}: {ex.Message}");
                        drives.Add(new DriveModel
                        {
                            Name = $"{drive.Name} (Access Denied)",
                            Path = drive.Name,
                            DriveType = drive.DriveType.ToString(),
                            FileSystem = "Unknown",
                            TotalSize = 0,
                            FreeSpace = 0,
                            IsReady = false,
                            Icon = GetDriveIcon(drive.DriveType)
                        });
                    }
                }

                // Add special directories for easy access
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
                {
                    AddSpecialFolders(drives);
                }
                else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
                {
                    AddLinuxSpecialFolders(drives);
                }

                _cachedDrives = drives.OrderBy(d => d.Path).ToList();
                _lastRefresh = DateTime.Now;

                _logger.LogInformation($"💾 Refreshed {drives.Count} drives");
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to refresh drives: {ex.Message}");
            }

            await Task.CompletedTask;
        }

        public bool IsDriveReady(string drivePath)
        {
            try
            {
                var drive = DriveInfo.GetDrives().FirstOrDefault(d => 
                    d.Name.Equals(drivePath, StringComparison.OrdinalIgnoreCase));
                return drive?.IsReady ?? false;
            }
            catch
            {
                return false;
            }
        }

        private static string GetDriveName(DriveInfo drive)
        {
            var name = drive.Name;
            
            if (!string.IsNullOrWhiteSpace(drive.VolumeLabel))
            {
                name = $"{drive.VolumeLabel} ({drive.Name})";
            }

            var sizeText = FormatBytes(drive.TotalSize);
            return $"{name} - {sizeText}";
        }

        private static string GetDriveIcon(DriveType driveType)
        {
            return driveType switch
            {
                DriveType.Fixed => "💾",
                DriveType.Removable => "💿",
                DriveType.Network => "🌐",
                DriveType.CDRom => "💿",
                DriveType.Ram => "⚡",
                _ => "💾"
            };
        }

        private static void AddSpecialFolders(List<DriveModel> drives)
        {
            var specialFolders = new[]
            {
                (Environment.SpecialFolder.Desktop, "🖥️ دسکتاپ"),
                (Environment.SpecialFolder.MyDocuments, "📄 اسناد"),
                (Environment.SpecialFolder.MyPictures, "🖼️ تصاویر"),
                (Environment.SpecialFolder.MyMusic, "🎵 موزیک"),
                (Environment.SpecialFolder.MyVideos, "🎬 ویدیوها"),
                (Environment.SpecialFolder.DesktopDirectory, "🗂️ پوشه دسکتاپ")
            };

            foreach (var (folder, name) in specialFolders)
            {
                try
                {
                    var path = Environment.GetFolderPath(folder);
                    if (!string.IsNullOrEmpty(path) && Directory.Exists(path))
                    {
                        drives.Add(new DriveModel
                        {
                            Name = name,
                            Path = path,
                            DriveType = "Special",
                            FileSystem = "NTFS",
                            TotalSize = 0,
                            FreeSpace = 0,
                            IsReady = true,
                            Icon = name.Split(' ')[0]
                        });
                    }
                }
                catch
                {
                    // Ignore if special folder is not accessible
                }
            }
        }

        private static void AddLinuxSpecialFolders(List<DriveModel> drives)
        {
            var specialFolders = new[]
            {
                ("/home", "🏠 Home"),
                ("/tmp", "📁 Temp"),
                ("/var", "⚙️ Var"),
                ("/usr", "👤 Usr"),
                ("/opt", "📦 Opt")
            };

            foreach (var (path, name) in specialFolders)
            {
                if (Directory.Exists(path))
                {
                    drives.Add(new DriveModel
                    {
                        Name = name,
                        Path = path,
                        DriveType = "Directory",
                        FileSystem = "ext4",
                        TotalSize = 0,
                        FreeSpace = 0,
                        IsReady = true,
                        Icon = name.Split(' ')[0]
                    });
                }
            }
        }

        private static string FormatBytes(long bytes)
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