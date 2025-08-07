using Microsoft.AspNetCore.Mvc;
using PersianFileCopierPro.Services;

namespace PersianFileCopierPro.Controllers
{
    [ApiController]
    [Route("api/drives")]
    public class DriveController : ControllerBase
    {
        private readonly IDriveService _driveService;
        private readonly ILogger<DriveController> _logger;

        public DriveController(IDriveService driveService, ILogger<DriveController> logger)
        {
            _driveService = driveService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> GetDrives()
        {
            try
            {
                var drives = await _driveService.GetDrivesAsync();
                return Ok(new { drives });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting drives: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("{drivePath}")]
        public async Task<IActionResult> GetDrive(string drivePath)
        {
            try
            {
                // Decode the drive path
                drivePath = Uri.UnescapeDataString(drivePath);
                
                var drive = await _driveService.GetDriveAsync(drivePath);
                if (drive == null)
                    return NotFound(new { error = "Drive not found" });

                return Ok(drive);
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error getting drive {drivePath}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("refresh")]
        public async Task<IActionResult> RefreshDrives()
        {
            try
            {
                await _driveService.RefreshDrivesAsync();
                var drives = await _driveService.GetDrivesAsync();
                return Ok(new { drives, message = "Drives refreshed successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error refreshing drives: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("{drivePath}/ready")]
        public IActionResult IsDriveReady(string drivePath)
        {
            try
            {
                // Decode the drive path
                drivePath = Uri.UnescapeDataString(drivePath);
                
                var isReady = _driveService.IsDriveReady(drivePath);
                return Ok(new { is_ready = isReady });
            }
            catch (Exception ex)
            {
                _logger.LogError($"❌ Error checking drive readiness {drivePath}: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}