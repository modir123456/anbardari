using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Models;
using PersianFileCopierPro.Services;

namespace PersianFileCopierPro.Controllers
{
    [ApiController]
    [Route("api/config")]
    public class ConfigController : ControllerBase
    {
        private readonly IConfigurationService _configService;
        private readonly ILicenseService _licenseService;
        private readonly ILogger<ConfigController> _logger;

        public ConfigController(
            IConfigurationService configService,
            ILicenseService licenseService,
            ILogger<ConfigController> logger)
        {
            _configService = configService;
            _licenseService = licenseService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> GetConfiguration()
        {
            try
            {
                var config = await _configService.GetConfigurationAsync();
                return Ok(config);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting configuration: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost]
        public async Task<IActionResult> UpdateConfiguration([FromBody] ConfigurationModel configuration)
        {
            try
            {
                var success = await _configService.UpdateConfigurationAsync(configuration);
                if (!success)
                    return StatusCode(500, new { error = "Failed to update configuration" });

                return Ok(new { message = "Configuration updated successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error updating configuration: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("license")]
        public async Task<IActionResult> GetLicense()
        {
            try
            {
                var license = await _licenseService.GetLicenseInfoAsync();
                return Ok(license);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting license: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("license/activate")]
        public async Task<IActionResult> ActivateLicense([FromBody] ActivateLicenseRequest request)
        {
            try
            {
                var success = await _licenseService.ActivateLicenseAsync(request.LicenseKey);
                if (!success)
                    return BadRequest(new { error = "Invalid license key" });

                var license = await _licenseService.GetLicenseInfoAsync();
                return Ok(new { message = "License activated successfully", license });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error activating license: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("license/machine-id")]
        public async Task<IActionResult> GetMachineId()
        {
            try
            {
                var machineId = await _licenseService.GetMachineIdAsync();
                return Ok(new { machine_id = machineId });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting machine ID: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("license/generate")]
        public async Task<IActionResult> GenerateLicense([FromBody] GenerateLicenseRequest request)
        {
            try
            {
                var licenseKey = await _licenseService.GenerateLicenseAsync(request.MachineId, request.ValidityDays);
                if (string.IsNullOrEmpty(licenseKey))
                    return StatusCode(500, new { error = "Failed to generate license" });

                return Ok(new { license_key = licenseKey, machine_id = request.MachineId, validity_days = request.ValidityDays });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error generating license: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("license/validate")]
        public async Task<IActionResult> ValidateLicense()
        {
            try
            {
                var isValid = await _licenseService.ValidateLicenseAsync();
                return Ok(new { is_valid = isValid });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error validating license: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("version")]
        public IActionResult GetVersion()
        {
            try
            {
                var version = new
                {
                    app_name = "Persian File Copier Pro",
                    version = "3.5.0",
                    company = "Persian File Copier Team",
                    build_date = DateTime.Now.ToString("yyyy-MM-dd"),
                    platform = Environment.OSVersion.Platform.ToString(),
                    runtime = Environment.Version.ToString()
                };

                return Ok(version);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting version: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }


}