# Persian File Copier Pro

A modern, feature-rich file copying application with a beautiful GUI built using Python and CustomTkinter.

## Features

### 🚀 Core Features
- **Multi-threaded file copying** with real-time progress tracking
- **Tabbed interface** for better organization (File Explorer, Copy Tasks, Settings)
- **Smart file search** with name and extension filtering
- **Directory navigation** with breadcrumb support
- **Drag-and-drop like experience** with queue management

### 📊 Progress Tracking
- Individual task progress with speed monitoring
- Overall progress bar for all tasks
- Real-time file transfer statistics
- Detailed status information for each operation

### ⚙️ Advanced Settings
- **Configurable buffer size** for optimal performance
- **Thread pool management** (1-8 concurrent operations)
- **File conflict resolution** (prompt, overwrite, skip)
- **Theme selection** (dark, light, system)
- **Persistent settings** and file cache

### 🎨 Modern UI/UX
- **Dark/Light theme support**
- **Responsive design** with proper scrolling
- **Intuitive controls** with keyboard shortcuts
- **Status bar** with real-time information
- **Professional styling** using CustomTkinter

## Installation

1. **Install Python 3.8 or higher**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python file_copier_app.py
   ```

## Usage

### File Explorer Tab
1. **Navigate directories** using the Browse button or double-click folders
2. **Search files** by name or extension (e.g., `.pdf`, `.jpg`)
3. **Select files** you want to copy
4. **Set destination** folder using the Browse button
5. **Add to queue** using the "Add Selected to Queue" button

### Copy Tasks Tab
1. **View all queued tasks** with detailed information
2. **Start all tasks** or manage individual operations
3. **Monitor progress** with real-time updates
4. **Pause/Resume** operations as needed
5. **Reorder tasks** using Move Up/Down buttons
6. **Clear completed** tasks to keep the list clean

### Settings Tab
- **Performance Settings:**
  - Buffer Size: Adjust for optimal copying speed (1-1024 KB)
  - Max Threads: Control concurrent operations (1-8 threads)
  
- **Behavior Settings:**
  - File Exists Policy: Choose how to handle duplicate files
  
- **Appearance Settings:**
  - Theme: Select between dark, light, or system theme

## Keyboard Shortcuts

- **Double-click folder** in File Explorer to navigate
- **Double-click task** to pause/resume individual operation
- **Ctrl+A equivalent** using "Select All" button
- **Search as you type** in the search field

## File Management

The application creates several files for persistent storage:
- `settings.json` - User preferences and configuration
- `file_cache.json` - Cached file information for faster browsing
- `copy_log.txt` - Detailed operation logs

## System Requirements

- **Python 3.8+**
- **Windows/Linux/macOS** (cross-platform)
- **Minimum 4GB RAM** recommended
- **CustomTkinter library**

## Error Handling

The application includes comprehensive error handling:
- **File permission errors** are logged and displayed
- **Network interruptions** are handled gracefully
- **Invalid paths** are validated before operations
- **Partial failures** don't stop other tasks

## Performance Tips

1. **Adjust buffer size** based on your storage type:
   - SSDs: 256-512 KB
   - HDDs: 64-128 KB
   - Network drives: 32-64 KB

2. **Optimize thread count**:
   - Local copies: 2-4 threads
   - Network copies: 1-2 threads
   - Mixed operations: 3-6 threads

3. **Use file filtering** to reduce memory usage with large directories

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.8+ is installed
- Install required dependencies: `pip install customtkinter`

**Slow copying performance:**
- Reduce buffer size for network operations
- Decrease thread count for mechanical drives
- Check available disk space

**UI appears broken:**
- Update CustomTkinter: `pip install --upgrade customtkinter`
- Reset settings by deleting `settings.json`

**Files not appearing:**
- Check directory permissions
- Refresh the file list manually
- Clear and rebuild the file cache

## Contributing

This application is designed to be easily extensible. Key areas for enhancement:
- Additional file operation types (move, delete, sync)
- Network location support
- File integrity verification
- Batch rename operations
- Integration with cloud storage services

## License

This project is open source and available under the MIT License.

## Support

For issues, feature requests, or questions, please refer to the application logs in `copy_log.txt` for detailed error information.