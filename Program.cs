using PersianFileCopierPro.Hubs;
using PersianFileCopierPro.Services;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

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

// Configure logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();

var app = builder.Build();

// Configure the HTTP request pipeline
app.UseStaticFiles();
app.UseCors("AllowAll");
app.UseRouting();
app.MapControllers();
app.MapHub<TaskHub>("/ws");

// Serve the main page
app.MapFallbackToFile("index.html");

// Configure the host
var port = Environment.GetEnvironmentVariable("PORT") ?? "5000";
app.Urls.Add($"http://localhost:{port}");

Console.WriteLine($"🎉 Persian File Copier Pro 3.6.0 - Ready!");
Console.WriteLine($"🌐 Server running on: http://localhost:{port}");
Console.WriteLine($"📱 Persian File Copier Pro is starting...");

app.Run();