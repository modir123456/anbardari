using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;
using PersianFileCopierPro.Hubs;
using PersianFileCopierPro.Services;
using System.Drawing;
using System.Net.Http;
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
        private static TaskCompletionSource<bool>? _serverStarted;

        [STAThread]
        static void Main(string[] args)
        {
            // Check if running as console app (for development)
            if (args.Contains("--console"))
            {
                RunAsConsoleApp().GetAwaiter().GetResult();
                return;
            }

            // Enable visual styles for Windows Forms
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            _serverStarted = new TaskCompletionSource<bool>();

            // Start the web server in background
            _ = Task.Run(StartWebServerAsync);

            // Create and configure the main form on UI thread
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

            // Initialize WebView2 synchronously on UI thread
            InitializeWebViewAsync().GetAwaiter().GetResult();

            // Create system tray icon
            CreateNotifyIcon();

            _mainForm.FormClosing += (s, e) =>
            {
                e.Cancel = true;
                _mainForm.Hide();
                _notifyIcon?.ShowBalloonTip(3000, "Persian File Copier Pro", 
                    "برنامه در پس‌زمینه اجرا می‌شود", ToolTipIcon.Info);
            };

            // Wait for server to start before showing the form
            _serverStarted.Task.Wait();

            _mainForm.Show();
            Application.Run(_mainForm);
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

                // Add a simple health check endpoint
                _app.MapGet("/health", () => "OK");

                Console.WriteLine("Server starting on http://localhost:5000...");
                _serverStarted?.SetResult(true);

                await _app.RunAsync("http://localhost:5000");
            }
            catch (Exception ex)
            {
                _serverStarted?.SetException(ex);
                MessageBox.Show($"خطا در راه‌اندازی سرور: {ex.Message}", "خطا", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                Console.WriteLine($"Server Start Exception: {ex}");
            }
        }

        private static void ConfigureServices(WebApplicationBuilder builder)
        {
            builder.Services.AddControllers()
                .AddJsonOptions(options =>
                {
                    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
                    options.JsonSerializerOptions.WriteIndented = true;
                });

            builder.Services.AddSignalR();

            builder.Services.AddSingleton<ITaskManagerService, TaskManagerService>();
            builder.Services.AddSingleton<IFileOperationService, FileOperationService>();
            builder.Services.AddSingleton<IDriveService, DriveService>();
            builder.Services.AddSingleton<IConfigurationService, ConfigurationService>();
            builder.Services.AddSingleton<ILicenseService, LicenseService>();

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
            app.UseStaticFiles();
            app.UseCors("AllowAll");
            app.UseRouting();
            app.MapControllers();
            app.MapHub<TaskHub>("/ws");
            app.MapFallbackToFile("index.html");
        }

        private static async Task InitializeWebViewAsync()
        {
            try
            {
                _webView!.CoreWebView2InitializationCompleted += async (sender, e) =>
                {
                    if (!e.IsSuccess)
                    {
                        MessageBox.Show($"WebView2 initialization failed: {e.InitializationException?.Message}\n" +
                            $"HResult: {e.InitializationException?.HResult:X}", "Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
                        Console.WriteLine($"WebView2 Init Failed: {e.InitializationException}");
                        return;
                    }

                    var settings = _webView.CoreWebView2.Settings;
                    settings.IsGeneralAutofillEnabled = false;
                    settings.IsPasswordAutosaveEnabled = false;
                    settings.AreBrowserAcceleratorKeysEnabled = false;
                    settings.AreDefaultContextMenusEnabled = false;
                    settings.AreDevToolsEnabled = false;

                    // Wait for server health check
                    using (var client = new HttpClient())
                    {
                        client.Timeout = TimeSpan.FromSeconds(10);
                        var response = await client.GetAsync("http://localhost:5000/health");
                        if (response.IsSuccessStatusCode)
                        {
                            Console.WriteLine("Server health check passed. Navigating to http://localhost:5000...");
                            _webView.CoreWebView2.Navigate("http://localhost:5000");
                        }
                        else
                        {
                            MessageBox.Show("Server is not ready. Please try again.", "Error",
                                MessageBoxButtons.OK, MessageBoxIcon.Error);
                            Console.WriteLine($"Server health check failed: {response.StatusCode}");
                        }
                    }
                };

                Console.WriteLine("Initializing WebView2...");
                var thread = Thread.CurrentThread;
                Console.WriteLine($"Init Thread ID: {thread.ManagedThreadId}, ApartmentState: {thread.GetApartmentState()}");
                await _webView!.EnsureCoreWebView2Async(null);
                Console.WriteLine("WebView2 initialized successfully.");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در راه‌اندازی رابط کاربری: {ex.Message}\nStackTrace: {ex.StackTrace}", "خطا",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                Console.WriteLine($"WebView2 Init Exception: {ex}");
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
                _app?.StopAsync().Wait();
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