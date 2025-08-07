using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Services
{
    public interface IDriveService
    {
        Task<List<DriveModel>> GetDrivesAsync();
        Task<DriveModel?> GetDriveAsync(string drivePath);
        Task RefreshDrivesAsync();
        bool IsDriveReady(string drivePath);
    }
}