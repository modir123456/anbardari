using Newtonsoft.Json;
using PersianFileCopierPro.Models;
using System.Management;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

namespace PersianFileCopierPro.Services
{
    public class LicenseService : ILicenseService
    {
        private readonly ILogger<LicenseService> _logger;
        private LicenseInfo _licenseInfo = new();
        private readonly string _licenseFilePath;

        public LicenseService(ILogger<LicenseService> logger)
        {
            _logger = logger;
            _licenseFilePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), 
                "PersianFileCopierPro", "license.json");
            
            _ = Task.Run(LoadLicenseAsync);
        }

        public async Task<LicenseInfo> GetLicenseInfoAsync()
        {
            _licenseInfo.MachineId = await GetMachineIdAsync();
            return _licenseInfo;
        }

        public async Task<bool> ActivateLicenseAsync(string licenseKey)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(licenseKey))
                    return false;

                var machineId = await GetMachineIdAsync();
                
                // Validate license format (PFC-PRO-2024-XXXXXXXX-XXXX)
                if (!licenseKey.StartsWith("PFC-PRO-2024-"))
                    return false;

                // For demo purposes, accept any license key that follows the format
                // In a real application, you would validate against a server or encrypted data
                var parts = licenseKey.Split('-');
                if (parts.Length != 5)
                    return false;

                _licenseInfo.LicenseKey = licenseKey;
                _licenseInfo.MachineId = machineId;
                _licenseInfo.IsActivated = true;
                _licenseInfo.IsTrial = licenseKey.Contains("TRIAL");
                _licenseInfo.LicenseType = _licenseInfo.IsTrial ? "Trial" : "Pro";
                _licenseInfo.ExpiryDate = DateTime.Now.AddYears(1);

                await SaveLicenseAsync();
                
                _logger.LogInformation($"✅ License activated: {licenseKey}");
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to activate license: {ex.Message}");
                return false;
            }
        }

        public async Task<string> GetMachineIdAsync()
        {
            try
            {
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
                {
                    return await GetWindowsMachineIdAsync();
                }
                else
                {
                    return await GetLinuxMachineIdAsync();
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning($"⚠️ Could not get machine ID: {ex.Message}");
                return Environment.MachineName;
            }
        }

        public async Task<bool> ValidateLicenseAsync()
        {
            try
            {
                if (!_licenseInfo.IsActivated)
                    return false;

                if (_licenseInfo.ExpiryDate.HasValue && _licenseInfo.ExpiryDate.Value < DateTime.Now)
                {
                    _licenseInfo.IsActivated = false;
                    await SaveLicenseAsync();
                    return false;
                }

                return true;
            }
            catch
            {
                return false;
            }
        }

        public async Task<string> GenerateLicenseAsync(string machineId, int validityDays = 365)
        {
            try
            {
                var timestamp = DateTime.Now.ToString("yyyyMMdd");
                var hash = ComputeHash($"{machineId}-{timestamp}-{validityDays}");
                var licenseKey = $"PFC-PRO-2024-{hash[..8].ToUpperInvariant()}-{hash[8..12].ToUpperInvariant()}";
                
                _logger.LogInformation($"🔑 Generated license: {licenseKey} for machine: {machineId}");
                return await Task.FromResult(licenseKey);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to generate license: {ex.Message}");
                return string.Empty;
            }
        }

        private async Task LoadLicenseAsync()
        {
            try
            {
                if (File.Exists(_licenseFilePath))
                {
                    var json = await File.ReadAllTextAsync(_licenseFilePath);
                    var license = JsonConvert.DeserializeObject<LicenseInfo>(json);
                    
                    if (license != null)
                    {
                        _licenseInfo = license;
                        _logger.LogInformation("📖 License loaded");
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to load license: {ex.Message}");
            }
        }

        private async Task SaveLicenseAsync()
        {
            try
            {
                var directory = Path.GetDirectoryName(_licenseFilePath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                var json = JsonConvert.SerializeObject(_licenseInfo, Formatting.Indented);
                await File.WriteAllTextAsync(_licenseFilePath, json);
                
                _logger.LogInformation("💾 License saved");
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to save license: {ex.Message}");
            }
        }

        private async Task<string> GetWindowsMachineIdAsync()
        {
            try
            {
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
                {
                    using var searcher = new ManagementObjectSearcher("SELECT UUID FROM Win32_ComputerSystemProduct");
                    var collection = searcher.Get();
                    
                    foreach (ManagementObject obj in collection)
                    {
                        var uuid = obj["UUID"]?.ToString();
                        if (!string.IsNullOrEmpty(uuid))
                        {
                            return await Task.FromResult(uuid);
                        }
                    }
                }
            }
            catch
            {
                // Fallback to machine name + hash
            }

            return await Task.FromResult(ComputeHash(Environment.MachineName + Environment.UserName));
        }

        private async Task<string> GetLinuxMachineIdAsync()
        {
            try
            {
                var machineIdPaths = new[] { "/etc/machine-id", "/var/lib/dbus/machine-id" };
                
                foreach (var path in machineIdPaths)
                {
                    if (File.Exists(path))
                    {
                        var machineId = await File.ReadAllTextAsync(path);
                        return machineId.Trim();
                    }
                }
            }
            catch
            {
                // Fallback to machine name + hash
            }

            return ComputeHash(Environment.MachineName + Environment.UserName);
        }

        private static string ComputeHash(string input)
        {
            using var sha256 = SHA256.Create();
            var bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(input));
            return Convert.ToHexString(bytes)[..16];
        }
    }
}