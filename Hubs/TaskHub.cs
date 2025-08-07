using Microsoft.AspNetCore.SignalR;
using PersianFileCopierPro.Models;

namespace PersianFileCopierPro.Hubs
{
    public class TaskHub : Hub
    {
        public async Task JoinGroup(string groupName)
        {
            await Groups.AddToGroupAsync(Context.ConnectionId, groupName);
        }

        public async Task LeaveGroup(string groupName)
        {
            await Groups.RemoveFromGroupAsync(Context.ConnectionId, groupName);
        }

        public async Task SendTaskUpdate(string taskId, TaskModel taskData)
        {
            await Clients.All.SendAsync("task_update", new { task_id = taskId, task_data = taskData });
        }

        public async Task SendTaskProgress(string taskId, TaskProgress progressData)
        {
            await Clients.All.SendAsync("task_progress", new { task_id = taskId, progress_data = progressData });
        }

        public async Task SendTaskCompleted(string taskId)
        {
            await Clients.All.SendAsync("task_completed", new { task_id = taskId });
        }

        public async Task SendTaskStarted(string taskId, TaskModel taskData)
        {
            await Clients.All.SendAsync("task_started", new { task_id = taskId, task_data = taskData });
        }

        public async Task Ping()
        {
            await Clients.Caller.SendAsync("pong");
        }

        public override async Task OnConnectedAsync()
        {
            Console.WriteLine($"🔗 Client connected: {Context.ConnectionId}");
            await base.OnConnectedAsync();
        }

        public override async Task OnDisconnectedAsync(Exception? exception)
        {
            Console.WriteLine($"❌ Client disconnected: {Context.ConnectionId}");
            await base.OnDisconnectedAsync(exception);
        }
    }
}