using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;
using PersianFileCopierPro.Hubs;
using PersianFileCopierPro.Services;
using System.Drawing;
using System.Text.Json;
using System.Windows.Forms;

namespace PersianFileCopierPro
{
    internal static class Program
    {
        private static WebApplication? _app;
        private static Form? _mainForm;
        private static WebView2? _webView;
        private static NotifyIcon? _notifyIcon;

        [STAThread]
        static async Task Main(string[] args)
        {
            // Check if running as console app (for development)
            if (args.Contains("--console"))
            {
                await RunAsConsoleApp();
                return;
            }

            // Enable visual styles for Windows Forms
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            try
            {
                // Start the web server in background
                _ = Task.Run(StartWebServerAsync);

                // Wait for server to start
                await Task.Delay(3000);

                // Create and show the main window
                await CreateMainWindowAsync();

                // Run the Windows Forms application
                Application.Run();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در راه‌اندازی برنامه: {ex.Message}", "خطا", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static async Task RunAsConsoleApp()
        {
            var builder = WebApplication.CreateBuilder();
            ConfigureServices(builder);
            
            var app = builder.Build();
            ConfigurePipeline(app);

            var port = Environment.GetEnvironmentVariable("PORT") ?? "5000";
            app.Urls.Add($"http://localhost:{port}");

            Console.WriteLine($"🎉 Persian File Copier Pro 3.6.0 - Console Mode");
            Console.WriteLine($"🌐 Server running on: http://localhost:{port}");

            await app.RunAsync();
        }

        private static async Task StartWebServerAsync()
        {
            try
            {
                var builder = WebApplication.CreateBuilder();
                ConfigureServices(builder);
                
                // Suppress console output for GUI mode
                builder.Logging.ClearProviders();

                _app = builder.Build();
                ConfigurePipeline(_app);

                await _app.RunAsync("http://localhost:5000");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در راه‌اندازی سرور: {ex.Message}", "خطا", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static void ConfigureServices(WebApplicationBuilder builder)
        {
            // Add services to the container
            builder.Services.AddControllers()
                .AddJsonOptions(options =>
                {
                    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
                    options.JsonSerializerOptions.WriteIndented = true;
                });

            // Add SignalR for real-time updates
            builder.Services.AddSignalR();

            // Add custom services
            builder.Services.AddSingleton<ITaskManagerService, TaskManagerService>();
            builder.Services.AddSingleton<IFileOperationService, FileOperationService>();
            builder.Services.AddSingleton<IDriveService, DriveService>();
            builder.Services.AddSingleton<IConfigurationService, ConfigurationService>();
            builder.Services.AddSingleton<ILicenseService, LicenseService>();

            // Add CORS
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowAll", policy =>
                {
                    policy.AllowAnyOrigin()
                          .AllowAnyMethod()
                          .AllowAnyHeader();
                });
            });
        }

        private static void ConfigurePipeline(WebApplication app)
        {
            // Configure the HTTP request pipeline
            app.UseStaticFiles();
            app.UseCors("AllowAll");
            app.UseRouting();
            app.MapControllers();
            app.MapHub<TaskHub>("/ws");

            // Serve the main page
            app.MapFallbackToFile("index.html");
        }

        private static async Task CreateMainWindowAsync()
        {
            _mainForm = new Form
            {
                Text = "Persian File Copier Pro",
                Size = new Size(1400, 900),
                StartPosition = FormStartPosition.CenterScreen,
                MinimumSize = new Size(1200, 700),
                Icon = SystemIcons.Application
            };

            // Create WebView2 control
            _webView = new WebView2
            {
                Dock = DockStyle.Fill
            };

            _mainForm.Controls.Add(_webView);

            // Initialize WebView2
            await InitializeWebViewAsync();

            // Create system tray icon
            CreateNotifyIcon();

            // Handle form events
            _mainForm.FormClosing += (s, e) =>
            {
                e.Cancel = true;
                _mainForm.Hide();
                _notifyIcon?.ShowBalloonTip(3000, "Persian File Copier Pro", 
                    "برنامه در پس‌زمینه اجرا می‌شود", ToolTipIcon.Info);
            };

            _mainForm.Show();
        }

        private static async Task InitializeWebViewAsync()
        {
            try
            {
                await _webView!.EnsureCoreWebView2Async();
                
                // Configure WebView2 settings
                var settings = _webView.CoreWebView2.Settings;
                settings.AreGeneralAutofillEnabled = false;
                settings.ArePasswordAutosaveEnabled = false;
                settings.AreBrowserAcceleratorKeysEnabled = false;
                settings.AreDefaultContextMenusEnabled = false;
                settings.AreDevToolsEnabled = false;

                // Navigate to the application
                _webView.CoreWebView2.Navigate("http://localhost:5000");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در راه‌اندازی رابط کاربری: {ex.Message}", "خطا", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static void CreateNotifyIcon()
        {
            _notifyIcon = new NotifyIcon
            {
                Icon = SystemIcons.Application,
                Text = "Persian File Copier Pro",
                Visible = true
            };

            var contextMenu = new ContextMenuStrip();
            contextMenu.Items.Add("نمایش برنامه", null, (s, e) => 
            {
                _mainForm?.Show();
                if (_mainForm != null)
                {
                    _mainForm.WindowState = FormWindowState.Normal;
                    _mainForm.BringToFront();
                }
            });
            contextMenu.Items.Add("-");
            contextMenu.Items.Add("خروج", null, (s, e) => 
            {
                if (_notifyIcon != null)
                    _notifyIcon.Visible = false;
                _app?.StopAsync();
                Application.Exit();
            });

            _notifyIcon.ContextMenuStrip = contextMenu;
            _notifyIcon.DoubleClick += (s, e) =>
            {
                _mainForm?.Show();
                if (_mainForm != null)
                {
                    _mainForm.WindowState = FormWindowState.Normal;
                    _mainForm.BringToFront();
                }
            };
        }
    }
}