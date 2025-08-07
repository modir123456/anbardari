using Microsoft.AspNetCore.StaticFiles;
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
builder.Logging.AddConsole();
builder.Logging.AddDebug();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseStaticFiles();

// Configure custom content types
var contentTypeProvider = new FileExtensionContentTypeProvider();
contentTypeProvider.Mappings[".js"] = "application/javascript; charset=utf-8";
contentTypeProvider.Mappings[".css"] = "text/css; charset=utf-8";
contentTypeProvider.Mappings[".html"] = "text/html; charset=utf-8";

app.UseStaticFiles(new StaticFileOptions
{
    ContentTypeProvider = contentTypeProvider
});

app.UseRouting();
app.UseCors("AllowAll");

app.MapControllers();
app.MapHub<TaskHub>("/ws");

// Serve the main page
app.MapGet("/", async context =>
{
    context.Response.ContentType = "text/html; charset=utf-8";
    await context.Response.SendFileAsync("wwwroot/index.html");
});

// Configure the host
var port = Environment.GetEnvironmentVariable("PORT") ?? "8548";
app.Urls.Add($"http://0.0.0.0:{port}");

Console.WriteLine($"🎉 Persian File Copier Pro 3.5.0 - Ready!");
Console.WriteLine($"🌐 Server running on: http://localhost:{port}");
Console.WriteLine($"📱 Persian File Copier Pro is starting...");

app.Run();