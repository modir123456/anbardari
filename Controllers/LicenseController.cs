using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Models;
using PersianFileCopierPro.Services;

namespace PersianFileCopierPro.Controllers
{
    [ApiController]
    [Route("api/license")]
    public class LicenseController : ControllerBase
    {
        private readonly ILicenseService _licenseService;
        private readonly ILogger<LicenseController> _logger;

        public LicenseController(ILicenseService licenseService, ILogger<LicenseController> logger)
        {
            _licenseService = licenseService;
            _logger = logger;
        }

        [HttpGet]
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

        [HttpPost("activate")]
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

        [HttpGet("machine-id")]
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

        [HttpPost("generate")]
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

        [HttpGet("validate")]
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
    }


}