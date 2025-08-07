using Newtonsoft.Json;
using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Services
{
    public class ConfigurationService : IConfigurationService
    {
        private readonly ILogger<ConfigurationService> _logger;
        private ConfigurationModel _configuration = new();
        private readonly string _configFilePath;

        public ConfigurationService(ILogger<ConfigurationService> logger)
        {
            _logger = logger;
            _configFilePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), 
                "PersianFileCopierPro", "config.json");
        }

        public async Task<ConfigurationModel> GetConfigurationAsync()
        {
            return await Task.FromResult(_configuration);
        }

        public async Task<bool> UpdateConfigurationAsync(ConfigurationModel configuration)
        {
            try
            {
                _configuration = configuration;
                return await SaveConfigurationAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to update configuration: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> SaveConfigurationAsync()
        {
            try
            {
                var directory = Path.GetDirectoryName(_configFilePath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                var json = JsonConvert.SerializeObject(_configuration, Formatting.Indented);
                await File.WriteAllTextAsync(_configFilePath, json);
                
                _logger.LogInformation($"💾 Configuration saved to {_configFilePath}");
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to save configuration: {ex.Message}");
                return false;
            }
        }

        public async Task LoadConfigurationAsync()
        {
            try
            {
                if (File.Exists(_configFilePath))
                {
                    var json = await File.ReadAllTextAsync(_configFilePath);
                    var config = JsonConvert.DeserializeObject<ConfigurationModel>(json);
                    
                    if (config != null)
                    {
                        _configuration = config;
                        _logger.LogInformation($"📖 Configuration loaded from {_configFilePath}");
                    }
                }
                else
                {
                    _logger.LogInformation("⚙️ Using default configuration");
                    await SaveConfigurationAsync(); // Save default config
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Failed to load configuration: {ex.Message}");
                _logger.LogInformation("⚙️ Using default configuration");
            }
        }
    }
}