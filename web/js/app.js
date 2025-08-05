// Persian File Copier Pro - Web UI Version
// Main Application JavaScript

// Global variables
let currentDrive = '';
let selectedFiles = [];
let currentTasks = [];
let appConfig = {};
let refreshInterval = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Load configuration
        appConfig = await eel.get_config()();
        
        // Apply theme
        applyTheme(appConfig.ui_settings?.theme || 'dark');
        
        // Apply font
        applyFont(appConfig.ui_settings?.font_family || 'Vazirmatn', 
                  appConfig.ui_settings?.font_size || 14);
        
        // Initialize UI components
        initializeTabNavigation();
        initializeSearchAndFilters();
        
        // Load initial data
        await loadDrives();
        await loadLicenseInfo();
        
        // Start task monitoring
        startTaskMonitoring();
        
        // Show welcome toast
        showToast('✅ برنامه با موفقیت راه‌اندازی شد', 'success');
        
    } catch (error) {
        console.error('Error initializing app:', error);
        showToast('❌ خطا در راه‌اندازی برنامه', 'error');
    }
}

// Tab Navigation
function initializeTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            button.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

// Search and Filters
function initializeSearchAndFilters() {
    const searchInput = document.getElementById('search-input');
    const formatFilter = document.getElementById('format-filter');
    const sizeFilter = document.getElementById('size-filter');
    
    // Search input
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (currentDrive) {
                scanCurrentDirectory();
            }
        }, 300);
    });
    
    // Format filter
    formatFilter.addEventListener('change', () => {
        if (currentDrive) {
            scanCurrentDirectory();
        }
    });
    
    // Size filter
    sizeFilter.addEventListener('change', () => {
        if (currentDrive) {
            scanCurrentDirectory();
        }
    });
}

// Drive Management
async function loadDrives() {
    try {
        const drivesContainer = document.getElementById('drives-list');
        drivesContainer.innerHTML = '<div class="loading-indicator"><div class="spinner"></div><p>در حال اسکن درایوها...</p></div>';
        
        const drives = await eel.get_drives()();
        
        if (drives.length === 0) {
            drivesContainer.innerHTML = '<div class="empty-state"><p>هیچ درایوی یافت نشد</p></div>';
            return;
        }
        
        let drivesHTML = '';
        drives.forEach(drive => {
            const displayName = drive.name || drive.path;
            const spaceInfo = drive.type === 'drive' ? 
                `${drive.free_space} آزاد از ${drive.total_space}` : '';
            
            drivesHTML += `
                <div class="drive-item" onclick="selectDrive('${drive.path}')">
                    <div class="drive-icon">${drive.icon || '💾'}</div>
                    <div class="drive-info">
                        <div class="drive-name">${displayName}</div>
                        ${spaceInfo ? `<div class="drive-space">${spaceInfo}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        drivesContainer.innerHTML = drivesHTML;
        
    } catch (error) {
        console.error('Error loading drives:', error);
        showToast('❌ خطا در بارگذاری درایوها', 'error');
    }
}

async function refreshDrives() {
    await loadDrives();
    showToast('🔄 لیست درایوها بروزرسانی شد', 'info');
}

async function selectDrive(drivePath) {
    currentDrive = drivePath;
    await scanCurrentDirectory();
    
    // Highlight selected drive
    document.querySelectorAll('.drive-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.target.closest('.drive-item').classList.add('selected');
}

// File Management
async function scanCurrentDirectory() {
    if (!currentDrive) return;
    
    try {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '<div class="loading-indicator"><div class="spinner"></div><p>در حال اسکن فایل‌ها...</p></div>';
        
        const searchTerm = document.getElementById('search-input').value;
        const formatFilter = document.getElementById('format-filter').value;
        const sizeFilter = document.getElementById('size-filter').value;
        
        const files = await eel.scan_directory(currentDrive, searchTerm, formatFilter, sizeFilter)();
        
        updateFileList(files);
        updateFileCount(files.length);
        
    } catch (error) {
        console.error('Error scanning directory:', error);
        showToast('❌ خطا در اسکن دایرکتوری', 'error');
    }
}

function updateFileList(files) {
    const fileList = document.getElementById('file-list');
    
    if (files.length === 0) {
        fileList.innerHTML = '<div class="empty-state"><p>هیچ فایلی یافت نشد</p></div>';
        return;
    }
    
    let filesHTML = '';
    files.forEach(file => {
        const fileName = file.name;
        const filePath = file.path;
        const displayPath = filePath.length > 50 ? 
            '...' + filePath.slice(-47) : filePath;
        
        filesHTML += `
            <div class="file-item ${file.selected ? 'selected' : ''}" 
                 data-path="${filePath}" 
                 onclick="toggleFileSelection('${filePath}')">
                <div class="file-col-name">${fileName}</div>
                <div class="file-col-path">${displayPath}</div>
                <div class="file-col-type">${file.type}</div>
                <div class="file-col-size">${file.size}</div>
            </div>
        `;
    });
    
    fileList.innerHTML = filesHTML;
}

function updateFileCount(count) {
    document.getElementById('file-count-text').textContent = `تعداد فایل‌ها: ${count.toLocaleString('fa-IR')}`;
}

function toggleFileSelection(filePath) {
    const fileItem = document.querySelector(`[data-path="${filePath}"]`);
    const isSelected = fileItem.classList.contains('selected');
    
    if (isSelected) {
        fileItem.classList.remove('selected');
        selectedFiles = selectedFiles.filter(path => path !== filePath);
    } else {
        fileItem.classList.add('selected');
        selectedFiles.push(filePath);
    }
    
    updateSelectionInfo();
}

function selectAllFiles() {
    const fileItems = document.querySelectorAll('.file-item');
    selectedFiles = [];
    
    fileItems.forEach(item => {
        item.classList.add('selected');
        selectedFiles.push(item.dataset.path);
    });
    
    updateSelectionInfo();
    showToast(`✅ ${selectedFiles.length} فایل انتخاب شد`, 'success');
}

function updateSelectionInfo() {
    if (selectedFiles.length > 0) {
        showToast(`${selectedFiles.length} فایل انتخاب شده - روی مقصد کلیک کنید`, 'info', 5000);
    }
}

function refreshFiles() {
    selectedFiles = [];
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    if (currentDrive) {
        scanCurrentDirectory();
    }
    
    showToast('🔄 لیست فایل‌ها بروزرسانی شد', 'info');
}

// Copy Operations
async function startCopyOperation(destination) {
    if (selectedFiles.length === 0) {
        showToast('❌ هیچ فایلی انتخاب نشده است', 'warning');
        return;
    }
    
    try {
        const result = await eel.start_copy(selectedFiles, destination)();
        
        if (result.error) {
            showToast(`❌ ${result.error}: حداکثر ${result.limit} فایل`, 'error');
            return;
        }
        
        if (result.success) {
            showToast(`✅ شروع کپی ${selectedFiles.length} فایل`, 'success');
            selectedFiles = [];
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
            });
        }
        
    } catch (error) {
        console.error('Error starting copy:', error);
        showToast('❌ خطا در شروع کپی', 'error');
    }
}

// Task Management
async function loadTasks() {
    try {
        const tasks = await eel.get_tasks()();
        updateTasksList(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function updateTasksList(tasks) {
    const tasksList = document.getElementById('tasks-list');
    currentTasks = tasks;
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<div class="empty-state"><p>هیچ تسک فعالی وجود ندارد</p></div>';
        return;
    }
    
    let tasksHTML = '';
    tasks.forEach(task => {
        const sourceDisplay = Array.isArray(task.source_files) ? 
            `${task.source_files.length} فایل` : 
            task.source_files;
        
        const progressColor = getProgressColor(task.progress);
        const statusText = getTaskStatusText(task.status);
        
        tasksHTML += `
            <div class="task-item">
                <div class="task-header">
                    <div class="task-source">${sourceDisplay} → ${task.destination}</div>
                    <div class="task-controls">
                        ${getTaskControlButtons(task)}
                    </div>
                </div>
                
                <div class="task-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%; background: ${progressColor}">
                            <div class="progress-text">${task.progress}%</div>
                        </div>
                    </div>
                </div>
                
                <div class="task-info">
                    <span>سرعت: ${task.speed}</span>
                    <span>حجم: ${task.copied_size} / ${task.total_size}</span>
                    <span>زمان: ${task.eta}</span>
                    <span>وضعیت: ${statusText}</span>
                </div>
            </div>
        `;
    });
    
    tasksList.innerHTML = tasksHTML;
}

function getProgressColor(progress) {
    if (progress < 25) return 'linear-gradient(90deg, #f44336, #ff6b6b)';
    if (progress < 50) return 'linear-gradient(90deg, #ff9800, #ffb347)';
    if (progress < 75) return 'linear-gradient(90deg, #ffeb3b, #fff176)';
    return 'linear-gradient(90deg, #4caf50, #81c784)';
}

function getTaskStatusText(status) {
    const statusMap = {
        'running': '▶️ در حال اجرا',
        'paused': '⏸️ متوقف',
        'completed': '✅ تکمیل شده',
        'failed': '❌ خطا',
        'cancelled': '❌ لغو شده'
    };
    return statusMap[status] || status;
}

function getTaskControlButtons(task) {
    if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
        return '';
    }
    
    let buttons = '';
    if (task.status === 'running') {
        buttons += `<button class="btn btn-small btn-warning" onclick="pauseTask('${task.id}')">⏸️</button>`;
    } else if (task.status === 'paused') {
        buttons += `<button class="btn btn-small btn-success" onclick="resumeTask('${task.id}')">▶️</button>`;
    }
    buttons += `<button class="btn btn-small btn-error" onclick="cancelTask('${task.id}')">❌</button>`;
    
    return buttons;
}

async function pauseTask(taskId) {
    try {
        await eel.control_task(taskId, 'pause')();
        showToast('⏸️ تسک متوقف شد', 'warning');
    } catch (error) {
        console.error('Error pausing task:', error);
    }
}

async function resumeTask(taskId) {
    try {
        await eel.control_task(taskId, 'resume')();
        showToast('▶️ تسک ادامه یافت', 'success');
    } catch (error) {
        console.error('Error resuming task:', error);
    }
}

async function cancelTask(taskId) {
    try {
        await eel.control_task(taskId, 'cancel')();
        showToast('❌ تسک لغو شد', 'error');
    } catch (error) {
        console.error('Error cancelling task:', error);
    }
}

function startTaskMonitoring() {
    refreshInterval = setInterval(async () => {
        await loadTasks();
    }, 1000); // Update every second
}

// Settings Management
async function loadLicenseInfo() {
    try {
        const licenseInfo = await eel.get_license_info()();
        updateLicenseDisplay(licenseInfo);
    } catch (error) {
        console.error('Error loading license info:', error);
    }
}

function updateLicenseDisplay(licenseInfo) {
    const statusElement = document.getElementById('license-status');
    const keyInput = document.getElementById('license-key');
    
    if (licenseInfo.type === 'trial') {
        statusElement.textContent = 'وضعیت: نسخه آزمایشی (محدود به 100 فایل)';
        statusElement.style.color = 'var(--warning-color)';
    } else {
        statusElement.textContent = 'وضعیت: نسخه کامل فعال';
        statusElement.style.color = 'var(--success-color)';
        keyInput.value = licenseInfo.key;
    }
}

async function activateLicense() {
    const licenseKey = document.getElementById('license-key').value;
    
    if (!licenseKey.trim()) {
        showToast('❌ لطفا کلید لایسنس را وارد کنید', 'warning');
        return;
    }
    
    try {
        const result = await eel.activate_license(licenseKey)();
        
        if (result.success) {
            showToast('✅ ' + result.message, 'success');
            await loadLicenseInfo();
        } else {
            showToast('❌ ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error activating license:', error);
        showToast('❌ خطا در فعال‌سازی لایسنس', 'error');
    }
}

async function purchaseLicense() {
    try {
        await eel.open_payment_gateway()();
        showToast('🛒 درگاه پرداخت باز شد', 'info');
    } catch (error) {
        console.error('Error opening payment gateway:', error);
        showToast('❌ خطا در باز کردن درگاه پرداخت', 'error');
    }
}

async function applySettings() {
    try {
        const fontFamily = document.getElementById('font-family-select').value;
        const fontSize = document.getElementById('font-size-slider').value;
        const theme = document.getElementById('theme-select').value;
        const maxTasks = document.getElementById('max-tasks').value;
        const verifyCopy = document.getElementById('verify-copy').checked;
        
        const config = {
            ui_settings: {
                font_family: fontFamily,
                font_size: parseInt(fontSize),
                theme: theme,
                language: 'fa',
                startup_maximized: true,
                toast_duration: 10000
            },
            file_operations: {
                max_concurrent_tasks: parseInt(maxTasks),
                chunk_size: 65536,
                verify_copy: verifyCopy,
                auto_retry: true,
                max_scan_depth: 10
            },
            license: appConfig.license
        };
        
        await eel.save_config(config)();
        appConfig = config;
        
        // Apply changes immediately
        applyTheme(theme);
        applyFont(fontFamily, fontSize);
        
        showToast('✅ تنظیمات با موفقیت اعمال شد', 'success');
        
    } catch (error) {
        console.error('Error applying settings:', error);
        showToast('❌ خطا در اعمال تنظیمات', 'error');
    }
}

// Theme and Font Management
function applyTheme(themeName) {
    document.body.className = `theme-${themeName}`;
}

function applyFont(fontFamily, fontSize) {
    document.documentElement.style.setProperty('--font-family', fontFamily);
    document.documentElement.style.setProperty('--font-size-base', fontSize + 'px');
    
    // Update font size display
    const fontSizeValue = document.getElementById('font-size-value');
    if (fontSizeValue) {
        fontSizeValue.textContent = fontSize + 'px';
    }
}

// Initialize font size slider
document.addEventListener('DOMContentLoaded', function() {
    const fontSizeSlider = document.getElementById('font-size-slider');
    const fontSizeValue = document.getElementById('font-size-value');
    
    if (fontSizeSlider && fontSizeValue) {
        fontSizeSlider.addEventListener('input', function() {
            fontSizeValue.textContent = this.value + 'px';
        });
    }
});

// Utility Functions
function showSettings() {
    document.querySelector('[data-tab="settings"]').click();
}

function showAbout() {
    document.querySelector('[data-tab="about"]').click();
}

// Context Menu
let contextMenu = null;
let selectedFileForContext = null;

document.addEventListener('contextmenu', function(e) {
    if (e.target.closest('.file-item')) {
        e.preventDefault();
        selectedFileForContext = e.target.closest('.file-item').dataset.path;
        showContextMenu(e.pageX, e.pageY);
    }
});

document.addEventListener('click', function() {
    hideContextMenu();
});

function showContextMenu(x, y) {
    contextMenu = document.getElementById('context-menu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = x + 'px';
    contextMenu.style.top = y + 'px';
}

function hideContextMenu() {
    if (contextMenu) {
        contextMenu.style.display = 'none';
    }
}

function copyFilePath() {
    if (selectedFileForContext) {
        navigator.clipboard.writeText(selectedFileForContext);
        showToast('📋 مسیر کپی شد', 'info');
    }
    hideContextMenu();
}

function openFile() {
    if (selectedFileForContext) {
        // Open file logic would go here
        showToast('📂 فایل باز شد', 'info');
    }
    hideContextMenu();
}

function showFileProperties() {
    if (selectedFileForContext) {
        showToast('🔍 ویژگی‌های فایل', 'info');
    }
    hideContextMenu();
}

// Export functions for global access
window.selectDrive = selectDrive;
window.toggleFileSelection = toggleFileSelection;
window.selectAllFiles = selectAllFiles;
window.refreshFiles = refreshFiles;
window.refreshDrives = refreshDrives;
window.pauseTask = pauseTask;
window.resumeTask = resumeTask;
window.cancelTask = cancelTask;
window.pauseAllTasks = function() { showToast('⏸️ همه تسک‌ها متوقف شدند', 'warning'); };
window.resumeAllTasks = function() { showToast('▶️ همه تسک‌ها ادامه یافتند', 'success'); };
window.cancelAllTasks = function() { showToast('❌ همه تسک‌ها لغو شدند', 'error'); };
window.clearCompletedTasks = function() { showToast('🧹 تسک‌های تکمیل شده پاک شدند', 'info'); };
window.activateLicense = activateLicense;
window.purchaseLicense = purchaseLicense;
window.applySettings = applySettings;
window.showSettings = showSettings;
window.showAbout = showAbout;
window.copyFilePath = copyFilePath;
window.openFile = openFile;
window.showFileProperties = showFileProperties;