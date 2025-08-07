using Microsoft.AspNetCore.StaticFiles;
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
            // Enable visual styles for Windows Forms
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            // Start the web server in background
            _ = Task.Run(StartWebServer);

            // Wait a moment for server to start
            await Task.Delay(2000);

            // Create and show the main window
            CreateMainWindow();

            // Run the Windows Forms application
            Application.Run();
        }

        private static async Task StartWebServer()
        {
            var builder = WebApplication.CreateBuilder();

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

            // Configure logging to suppress console output
            builder.Logging.ClearProviders();

            _app = builder.Build();

            // Configure the HTTP request pipeline
            _app.UseStaticFiles();
            _app.UseCors("AllowAll");
            _app.UseRouting();
            _app.MapControllers();
            _app.MapHub<TaskHub>("/taskHub");

            // Serve the main page
            _app.MapFallbackToFile("index.html");

            try
            {
                await _app.RunAsync("http://localhost:5000");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در راه‌اندازی سرور: {ex.Message}", "خطا", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static void CreateMainWindow()
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
            InitializeWebView();

            // Create system tray icon
            CreateNotifyIcon();

            // Handle form events
            _mainForm.FormClosing += (s, e) =>
            {
                e.Cancel = true;
                _mainForm.Hide();
                _notifyIcon!.ShowBalloonTip(3000, "Persian File Copier Pro", 
                    "برنامه در پس‌زمینه اجرا می‌شود", ToolTipIcon.Info);
            };

            _mainForm.Show();
        }

        private static async void InitializeWebView()
        {
            try
            {
                await _webView!.EnsureCoreWebView2Async();
                
                // Configure WebView2 settings
                _webView.CoreWebView2.Settings.AreGeneralAutofillEnabled = false;
                _webView.CoreWebView2.Settings.ArePasswordAutosaveEnabled = false;
                _webView.CoreWebView2.Settings.IsGeneralAutofillEnabled = false;
                _webView.CoreWebView2.Settings.IsPasswordAutosaveEnabled = false;
                _webView.CoreWebView2.Settings.AreBrowserAcceleratorKeysEnabled = false;
                _webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
                _webView.CoreWebView2.Settings.AreDevToolsEnabled = false;

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
                _mainForm!.Show();
                _mainForm.WindowState = FormWindowState.Normal;
                _mainForm.BringToFront();
            });
            contextMenu.Items.Add("-");
            contextMenu.Items.Add("خروج", null, (s, e) => 
            {
                _notifyIcon.Visible = false;
                _app?.StopAsync();
                Application.Exit();
            });

            _notifyIcon.ContextMenuStrip = contextMenu;
            _notifyIcon.DoubleClick += (s, e) =>
            {
                _mainForm!.Show();
                _mainForm.WindowState = FormWindowState.Normal;
                _mainForm.BringToFront();
            };
        }
    }
}