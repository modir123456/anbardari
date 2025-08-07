using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Services
{
    public interface ILicenseService
    {
        Task<LicenseInfo> GetLicenseInfoAsync();
        Task<bool> ActivateLicenseAsync(string licenseKey);
        Task<string> GetMachineIdAsync();
        Task<bool> ValidateLicenseAsync();
        Task<string> GenerateLicenseAsync(string machineId, int validityDays = 365);
    }
}