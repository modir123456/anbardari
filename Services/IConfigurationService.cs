using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Services
{
    public interface IConfigurationService
    {
        Task<ConfigurationModel> GetConfigurationAsync();
        Task<bool> UpdateConfigurationAsync(ConfigurationModel configuration);
        Task<bool> SaveConfigurationAsync();
        Task LoadConfigurationAsync();
    }
}