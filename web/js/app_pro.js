/**
 * Persian File Copier Pro - Professional JavaScript Application
 * Enhanced with database integration, real-time updates, and complete feature set
 * شرکت فناوری نوآئران مثبت سبز
 */

// Global application state
let currentDrive = null;
let selectedFiles = [];
let currentFiles = [];
let currentTasks = [];
let appConfig = {};
let refreshInterval = null;
let driveMonitorInterval = null;
let currentPage = 1;
let totalPages = 1;
let itemsPerPage = 100;
let sortBy = 'name';
let sortOrder = 'asc';
let searchTerm = '';
let currentFormatFilter = 'همه فرمت‌ها';
let currentSizeFilter = 'همه اندازه‌ها';
let currentDateFilter = 'همه تاریخ‌ها';

// Application initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    console.log('🚀 Initializing Persian File Copier Pro...');
    
    try {
        // Load configuration
        await loadConfig();
        
        // Apply theme and fonts
        applyTheme(appConfig.ui_settings?.theme || 'dark');
        applyFont(appConfig.ui_settings?.font_family || 'Vazirmatn');
        
            // Initialize UI components
    initializeTabNavigation();
    initializeSearchAndFilters();
    initializeSettingsNavigation();
    initializeAdvancedSettingsAutoSave();
        
        // Load initial data
        await Promise.all([
            loadDrives(),
            loadLicenseInfo(),
            loadAdvancedSettings()
        ]);
        
        // Start monitoring services
        startTaskMonitoring();
        startDriveMonitoring();
        
        // Show welcome message
        showToast('🎉 Persian File Copier Pro آماده است!', 'success');
        
        console.log('✅ Application initialized successfully');
        
    } catch (error) {
        console.error('❌ Error initializing application:', error);
        showToast('خطا در راه‌اندازی برنامه', 'error');
    }
}

/**
 * Tab navigation functionality
 */
function initializeTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            button.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');
            
            // Load tab-specific data
            loadTabData(tabId);
        });
    });
}

/**
 * Initialize settings navigation
 */
function initializeSettingsNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const settingSections = document.querySelectorAll('.settings-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const sectionId = item.getAttribute('data-section');
            
            // Remove active class from all nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Remove active class from all sections
            settingSections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked nav item
            item.classList.add('active');
            
            // Show corresponding section
            const targetSection = document.getElementById(`${sectionId}-settings`);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });
}

/**
 * Initialize search and filter functionality
 */
function initializeSearchAndFilters() {
    const searchInput = document.getElementById('search-input');
    const formatFilter = document.getElementById('format-filter');
    const sizeFilter = document.getElementById('size-filter');
    const dateFilter = document.getElementById('date-filter');
    
    // Real-time search
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchTerm = e.target.value;
            updateSearchClearButton();
            scanCurrentDirectory();
        }, 300);
    });
    
    // Filter changes
    formatFilter.addEventListener('change', (e) => {
        currentFormatFilter = e.target.value;
        scanCurrentDirectory();
    });
    
    sizeFilter.addEventListener('change', (e) => {
        currentSizeFilter = e.target.value;
        scanCurrentDirectory();
    });
    
    dateFilter.addEventListener('change', (e) => {
        currentDateFilter = e.target.value;
        scanCurrentDirectory();
    });
    
    // Initialize clear button
    updateSearchClearButton();
}

/**
 * Update search clear button visibility
 */
function updateSearchClearButton() {
    const clearBtn = document.querySelector('.search-clear');
    const searchInput = document.getElementById('search-input');
    
    if (searchInput.value.length > 0) {
        clearBtn.style.display = 'flex';
    } else {
        clearBtn.style.display = 'none';
    }
}

/**
 * Clear search input
 */
function clearSearch() {
    const searchInput = document.getElementById('search-input');
    searchInput.value = '';
    searchTerm = '';
    updateSearchClearButton();
    scanCurrentDirectory();
}

/**
 * Load configuration from backend
 */
async function loadConfig() {
    try {
        appConfig = await eel.get_config()();
        console.log('📋 Configuration loaded:', appConfig);
    } catch (error) {
        console.error('❌ Error loading config:', error);
        // Use default config
        appConfig = {
            ui_settings: {
                theme: 'dark',
                font_family: 'Vazirmatn',
                font_size: 14
            }
        };
    }
}

/**
 * Save configuration to backend
 */
async function saveConfig() {
    try {
        await eel.save_config(appConfig)();
        console.log('💾 Configuration saved');
    } catch (error) {
        console.error('❌ Error saving config:', error);
    }
}

/**
 * Load tab-specific data
 */
async function loadTabData(tabId) {
    switch (tabId) {
        case 'files':
            await refreshFiles();
            break;
        case 'drives':
            await loadDrivesDetailed();
            break;
        case 'settings':
            await loadSettingsData();
            break;
        case 'about':
            // About tab doesn't need dynamic data
            break;
    }
}

/**
 * Drive Management
 */
async function loadDrives() {
    try {
        const drives = await eel.get_drives()();
        console.log('💾 Drives loaded:', drives);
        
        updateDrivesDisplay(drives);
        // Quick drives removed - using full drives list only
        updateHeaderStats();
        
    } catch (error) {
        console.error('❌ Error loading drives:', error);
        showToast('خطا در بارگذاری درایوها', 'error');
    }
}

/**
 * Update drives display
 */
function updateDrivesDisplay(drives) {
    const drivesList = document.getElementById('drives-list');
    
    if (!drives || drives.length === 0) {
        drivesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">💾</div>
                <p>هیچ درایوی یافت نشد</p>
            </div>
        `;
        return;
    }
    
    drivesList.innerHTML = drives.map(drive => `
        <div class="drive-item" data-path="${drive.path}" onclick="selectDrive('${drive.path}')">
            <div class="drive-icon">${drive.icon || '💾'}</div>
            <div class="drive-info">
                <div class="drive-name">${drive.name || drive.path}</div>
                <div class="drive-details">
                    <span>${drive.free_space || '0 B'} آزاد</span>
                    <span>${drive.total_space || '0 B'} کل</span>
                </div>
                <div class="drive-progress">
                    <div class="drive-progress-fill" style="width: ${drive.usage_percent || 0}%"></div>
                </div>
            </div>
            <div class="drive-actions">
                <button class="drive-action-btn" onclick="event.stopPropagation(); toggleDriveAutoIndex('${drive.path}')" title="ایندکس خودکار">
                    ${drive.auto_index ? '🔄' : '⏸️'}
                </button>
                <button class="drive-action-btn" onclick="event.stopPropagation(); startDriveIndex('${drive.path}')" title="ایندکس دستی">
                    🔍
                </button>
            </div>
        </div>
    `).join('');
    
    // Update header count
    document.getElementById('drives-count').textContent = drives.length;
}

// Quick drives function removed - using full drives list only

/**
 * Select a drive and scan its files
 */
async function selectDrive(drivePath) {
    // If files are selected, start copy operation instead
    if (selectedFiles.length > 0) {
        await startCopyOperation(drivePath);
        return;
    }
    
    currentDrive = drivePath;
    currentPage = 1;
    
    // Update UI
    document.querySelectorAll('.drive-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    const selectedItem = document.querySelector(`[data-path="${drivePath}"]`);
    if (selectedItem) {
        selectedItem.classList.add('selected');
    }
    
    // Update stats
    document.getElementById('current-drive-text').textContent = drivePath;
    
    // Scan directory
    await scanCurrentDirectory();
    
    showToast(`📁 درایو ${drivePath} انتخاب شد`, 'info');
}

/**
 * Toggle drive auto-indexing
 */
async function toggleDriveAutoIndex(drivePath) {
    try {
        // Get current status (this would need to be tracked)
        const currentStatus = true; // Placeholder
        const newStatus = !currentStatus;
        
        await eel.set_drive_auto_index(drivePath, newStatus)();
        
        showToast(
            `ایندکس خودکار درایو ${drivePath} ${newStatus ? 'فعال' : 'غیرفعال'} شد`,
            'success'
        );
        
        await loadDrives();
        
    } catch (error) {
        console.error('❌ Error toggling drive auto-index:', error);
        showToast('خطا در تغییر تنظیمات ایندکس', 'error');
    }
}

/**
 * Start manual drive indexing
 */
async function startDriveIndex(drivePath) {
    try {
        await eel.start_drive_index(drivePath)();
        showToast(`🔍 ایندکس‌گذاری درایو ${drivePath} شروع شد`, 'info');
        
    } catch (error) {
        console.error('❌ Error starting drive index:', error);
        showToast('خطا در شروع ایندکس‌گذاری', 'error');
    }
}

/**
 * Refresh drives list
 */
async function refreshDrives() {
    showToast('🔄 در حال بروزرسانی درایوها...', 'info');
    await loadDrives();
}

/**
 * File Management
 */
async function scanCurrentDirectory() {
    if (!currentDrive) {
        // If no drive selected, show all files
        currentDrive = 'all';
    }
    
    try {
        const offset = (currentPage - 1) * itemsPerPage;
        
        console.log(`🔍 Scanning: drive=${currentDrive}, search="${searchTerm}", format=${currentFormatFilter}`);
        
        const files = await eel.scan_directory(
            currentDrive,
            searchTerm,
            currentFormatFilter,
            currentSizeFilter,
            itemsPerPage,
            offset
        )();
        
        console.log(`📄 Found ${files.length} files`);
        
        currentFiles = files;
        updateFileList(files);
        updateFileCount(files.length);
        updatePagination();
        
        // Show helpful message if no files found
        if (files.length === 0 && (searchTerm || currentFormatFilter !== 'همه فرمت‌ها' || currentSizeFilter !== 'همه اندازه‌ها')) {
            showToast('🔍 هیچ فایلی یافت نشد. فیلترها را پاک کنید یا تغییر دهید', 'info', 5000);
        }
        
    } catch (error) {
        console.error('❌ Error scanning directory:', error);
        showToast('خطا در اسکن پوشه', 'error');
    }
}

/**
 * Update file list display
 */
function updateFileList(files) {
    const fileList = document.getElementById('file-list');
    
    if (!files || files.length === 0) {
        fileList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📁</div>
                <p>فایلی یافت نشد</p>
                <small>فیلترها را تغییر دهید یا درایو دیگری انتخاب کنید</small>
            </div>
        `;
        return;
    }
    
    fileList.innerHTML = files.map(file => `
        <div class="file-item ${file.selected ? 'selected' : ''}" 
             data-path="${file.path}" 
             onclick="toggleFileSelection('${file.path}')"
             oncontextmenu="showContextMenu(event, '${file.path}')">
            <div class="file-checkbox">
                <input type="checkbox" ${file.selected ? 'checked' : ''} 
                       onchange="toggleFileSelection('${file.path}')">
            </div>
            <div class="file-name">${file.name}</div>
            <div class="file-path">${file.path}</div>
            <div class="file-type">${file.type || '📄 فایل'}</div>
            <div class="file-size">${formatSize(file.size)}</div>
            <div class="file-date">${formatDate(file.modified)}</div>
        </div>
    `).join('');
    
    // Highlight search results
    if (searchTerm) {
        highlightSearchResults(searchTerm);
    }
}

/**
 * Toggle file selection
 */
function toggleFileSelection(filePath) {
    const fileIndex = currentFiles.findIndex(f => f.path === filePath);
    if (fileIndex !== -1) {
        currentFiles[fileIndex].selected = !currentFiles[fileIndex].selected;
        
        // Update selectedFiles array
        if (currentFiles[fileIndex].selected) {
            if (!selectedFiles.includes(filePath)) {
                selectedFiles.push(filePath);
            }
        } else {
            const selectedIndex = selectedFiles.indexOf(filePath);
            if (selectedIndex !== -1) {
                selectedFiles.splice(selectedIndex, 1);
            }
        }
        
        updateFileList(currentFiles);
        updateSelectionInfo();
    }
}

/**
 * Select all files
 */
function selectAllFiles() {
    const allSelected = currentFiles.every(f => f.selected);
    
    currentFiles.forEach(file => {
        file.selected = !allSelected;
        
        if (file.selected && !selectedFiles.includes(file.path)) {
            selectedFiles.push(file.path);
        } else if (!file.selected) {
            const index = selectedFiles.indexOf(file.path);
            if (index !== -1) {
                selectedFiles.splice(index, 1);
            }
        }
    });
    
    // Update select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    selectAllCheckbox.checked = !allSelected;
    
    updateFileList(currentFiles);
    updateSelectionInfo();
}

/**
 * Toggle select all checkbox
 */
function toggleSelectAll() {
    selectAllFiles();
}

/**
 * Update selection information
 */
function updateSelectionInfo() {
    const selectedCount = selectedFiles.length;
    const totalSize = selectedFiles.reduce((sum, filePath) => {
        const file = currentFiles.find(f => f.path === filePath);
        return sum + (file ? file.size : 0);
    }, 0);
    
    document.getElementById('selected-count-text').textContent = selectedCount;
    document.getElementById('total-size-text').textContent = formatSize(totalSize);
    
    // Show/hide bulk operations
    const bulkControls = document.querySelector('.bulk-operations');
    if (bulkControls) {
        bulkControls.style.display = selectedCount > 0 ? 'flex' : 'none';
    }
    
    // Show instruction for copy operation
    if (selectedCount > 0) {
        showToast(`📂 ${selectedCount} فایل انتخاب شد. روی درایو مقصد کلیک کنید تا کپی شروع شود`, 'info', 3000);
    }
}

/**
 * Update file count display
 */
function updateFileCount(count) {
    document.getElementById('file-count-text').textContent = count;
    document.getElementById('indexed-files-count').textContent = count;
}

/**
 * Update pagination
 */
function updatePagination() {
    const paginationText = document.getElementById('pagination-text');
    const pageNumbers = document.getElementById('page-numbers');
    const prevBtn = document.querySelector('.pagination-controls .btn:first-child');
    const nextBtn = document.querySelector('.pagination-controls .btn:last-child');
    
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, currentFiles.length);
    
    paginationText.textContent = `نمایش ${startItem} تا ${endItem} از ${currentFiles.length} فایل`;
    
    // Calculate total pages (this would need total count from backend)
    totalPages = Math.ceil(currentFiles.length / itemsPerPage);
    
    // Update page numbers
    let pageNumbersHTML = '';
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    for (let i = startPage; i <= endPage; i++) {
        pageNumbersHTML += `
            <button class="btn btn-small ${i === currentPage ? 'btn-primary' : ''}" 
                    onclick="goToPage(${i})">${i}</button>
        `;
    }
    
    pageNumbers.innerHTML = pageNumbersHTML;
    
    // Update navigation buttons
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
}

/**
 * Go to specific page
 */
function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        scanCurrentDirectory();
    }
}

/**
 * Previous page
 */
function previousPage() {
    if (currentPage > 1) {
        goToPage(currentPage - 1);
    }
}

/**
 * Next page
 */
function nextPage() {
    if (currentPage < totalPages) {
        goToPage(currentPage + 1);
    }
}

/**
 * Refresh files
 */
async function refreshFiles() {
    showToast('🔄 در حال بروزرسانی فایل‌ها...', 'info');
    await scanCurrentDirectory();
}

/**
 * Sort files
 */
function sortFiles(criteria) {
    if (sortBy === criteria) {
        sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        sortBy = criteria;
        sortOrder = 'asc';
    }
    
    // Update sort indicators
    document.querySelectorAll('.sort-indicator').forEach(indicator => {
        indicator.className = 'sort-indicator';
    });
    
    const activeIndicator = document.querySelector(`[onclick="sortFiles('${criteria}')"] .sort-indicator`);
    if (activeIndicator) {
        activeIndicator.classList.add(sortOrder);
    }
    
    // Sort current files
    currentFiles.sort((a, b) => {
        let valueA, valueB;
        
        switch (criteria) {
            case 'name':
                valueA = a.name.toLowerCase();
                valueB = b.name.toLowerCase();
                break;
            case 'size':
                valueA = a.size;
                valueB = b.size;
                break;
            case 'type':
                valueA = a.type;
                valueB = b.type;
                break;
            case 'modified':
                valueA = a.modified;
                valueB = b.modified;
                break;
            default:
                return 0;
        }
        
        if (valueA < valueB) return sortOrder === 'asc' ? -1 : 1;
        if (valueA > valueB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });
    
    updateFileList(currentFiles);
}

/**
 * Reset all filters and search
 */
function resetFilters() {
    // Reset search
    searchTerm = '';
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Reset filters
    currentFormatFilter = 'همه فرمت‌ها';
    currentSizeFilter = 'همه اندازه‌ها';
    currentDateFilter = 'همه تاریخ‌ها';
    
    const formatFilter = document.getElementById('format-filter');
    const sizeFilter = document.getElementById('size-filter');
    const dateFilter = document.getElementById('date-filter');
    
    if (formatFilter) formatFilter.value = currentFormatFilter;
    if (sizeFilter) sizeFilter.value = currentSizeFilter;
    if (dateFilter) dateFilter.value = currentDateFilter;
    
    // Reset pagination
    currentPage = 1;
    
    // Refresh results
    scanCurrentDirectory();
    
    showToast('🔄 فیلترها پاک شدند', 'success');
}

/**
 * Copy Operations
 */
async function startCopyOperation(destination = null) {
    if (selectedFiles.length === 0) {
        showToast('هیچ فایلی انتخاب نشده است', 'warning');
        return;
    }
    
    // If no destination provided, show instruction
    if (!destination) {
        showToast('فایل‌ها را انتخاب کردید. حالا روی درایو مقصد کلیک کنید', 'info', 5000);
        return;
    }
    
    try {
        showToast('⏳ در حال شروع کپی...', 'info');
        const result = await eel.start_copy(selectedFiles, destination)();
        
        if (result.error) {
            if (result.expired) {
                showToast('❌ نسخه آزمایشی منقضی شده. لطفاً لایسنس تهیه کنید', 'error');
            } else if (result.limit) {
                showToast(`❌ محدودیت نسخه آزمایشی: حداکثر ${result.limit} فایل`, 'error');
            } else {
                showToast(`❌ خطا: ${result.error}`, 'error');
            }
            return;
        }
        
        showToast(`✅ کپی ${selectedFiles.length} فایل با موفقیت شروع شد`, 'success');
        
        // Clear selection
        selectedFiles = [];
        currentFiles.forEach(f => f.selected = false);
        updateFileList(currentFiles);
        updateSelectionInfo();
        
    } catch (error) {
        console.error('❌ Error starting copy:', error);
        showToast('خطا در شروع کپی', 'error');
    }
}

/**
 * Task Management
 */
async function loadTasks() {
    try {
        const tasks = await eel.get_tasks()();
        currentTasks = tasks;
        updateTasksList(tasks);
        updateHeaderStats();
        
    } catch (error) {
        console.error('❌ Error loading tasks:', error);
    }
}

/**
 * Update tasks list display
 */
function updateTasksList(tasks) {
    const tasksList = document.getElementById('tasks-list');
    
    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <p>هیچ تسک فعالی وجود ندارد</p>
                <small>فایل‌هایی را انتخاب کنید و روی مقصد کلیک کنید</small>
            </div>
        `;
        return;
    }
    
    tasksList.innerHTML = tasks.map(task => {
        const statusClass = getTaskStatusClass(task.status);
        const progressColor = getProgressColor(task.progress);
        
        return `
            <div class="task-item" data-task-id="${task.id}">
                <div class="task-header">
                    <div class="task-title">${task.current_file || 'در انتظار...'}</div>
                    <div class="task-status ${statusClass}">
                        ${getTaskStatusText(task.status)}
                    </div>
                </div>
                
                <div class="task-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%; background: ${progressColor}"></div>
                    </div>
                    <div class="progress-text">
                        <span>${task.progress}%</span>
                        <span>${task.speed || '0 MB/s'}</span>
                    </div>
                </div>
                
                <div class="task-info">
                    <div>📁 فایل‌ها: ${task.files_copied || 0}/${task.total_files || 0}</div>
                    <div>💾 حجم: ${task.copied_size || '0 B'}/${task.total_size || '0 B'}</div>
                    <div>⏱️ زمان باقی: ${task.eta || 'محاسبه...'}</div>
                    <div>📂 مقصد: ${task.destination || '-'}</div>
                </div>
                
                <div class="task-controls-inline">
                    ${getTaskControlButtons(task)}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Get task status CSS class
 */
function getTaskStatusClass(status) {
    const statusMap = {
        'running': 'running',
        'completed': 'completed',
        'paused': 'paused',
        'cancelled': 'cancelled',
        'failed': 'cancelled'
    };
    return statusMap[status] || 'running';
}

/**
 * Get progress color based on percentage
 */
function getProgressColor(progress) {
    if (progress < 25) return 'linear-gradient(90deg, #ff6b6b, #ffa500)';
    if (progress < 50) return 'linear-gradient(90deg, #ffa500, #ffeb3b)';
    if (progress < 75) return 'linear-gradient(90deg, #ffeb3b, #4caf50)';
    return 'linear-gradient(90deg, #4caf50, #2e7d32)';
}

/**
 * Get task status text
 */
function getTaskStatusText(status) {
    const statusMap = {
        'running': '🔄 در حال اجرا',
        'completed': '✅ تکمیل شده',
        'paused': '⏸️ متوقف شده',
        'cancelled': '❌ لغو شده',
        'failed': '❌ خطا'
    };
    return statusMap[status] || '🔄 در حال اجرا';
}

/**
 * Get task control buttons
 */
function getTaskControlButtons(task) {
    const taskId = task.id;
    
    if (task.status === 'completed' || task.status === 'cancelled' || task.status === 'failed') {
        return `
            <button class="btn btn-small btn-secondary" onclick="removeTask('${taskId}')">
                🗑️ حذف
            </button>
        `;
    }
    
    if (task.status === 'paused') {
        return `
            <button class="btn btn-small btn-success" onclick="resumeTask('${taskId}')">
                ▶️ ادامه
            </button>
            <button class="btn btn-small btn-error" onclick="cancelTask('${taskId}')">
                ❌ لغو
            </button>
        `;
    }
    
    return `
        <button class="btn btn-small btn-warning" onclick="pauseTask('${taskId}')">
            ⏸️ توقف
        </button>
        <button class="btn btn-small btn-error" onclick="cancelTask('${taskId}')">
            ❌ لغو
        </button>
    `;
}

/**
 * Task control functions
 */
async function pauseTask(taskId) {
    await controlTask(taskId, 'pause');
}

async function resumeTask(taskId) {
    await controlTask(taskId, 'resume');
}

async function cancelTask(taskId) {
    await controlTask(taskId, 'cancel');
}

async function removeTask(taskId) {
    // Remove from UI immediately
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskElement) {
        taskElement.remove();
    }
    
    // Remove from tasks array
    const taskIndex = currentTasks.findIndex(t => t.id === taskId);
    if (taskIndex !== -1) {
        currentTasks.splice(taskIndex, 1);
    }
    
    updateHeaderStats();
}

/**
 * Control task (pause/resume/cancel)
 */
async function controlTask(taskId, action) {
    try {
        await eel.control_task(taskId, action)();
        
        const actionText = {
            'pause': 'متوقف',
            'resume': 'ادامه داده',
            'cancel': 'لغو'
        };
        
        showToast(`تسک ${actionText[action]} شد`, 'success');
        
    } catch (error) {
        console.error(`❌ Error ${action} task:`, error);
        showToast(`خطا در ${action} تسک`, 'error');
    }
}

/**
 * Bulk task operations
 */
async function pauseAllTasks() {
    const runningTasks = currentTasks.filter(t => t.status === 'running');
    for (const task of runningTasks) {
        await pauseTask(task.id);
    }
}

async function resumeAllTasks() {
    const pausedTasks = currentTasks.filter(t => t.status === 'paused');
    for (const task of pausedTasks) {
        await resumeTask(task.id);
    }
}

async function cancelAllTasks() {
    const activeTasks = currentTasks.filter(t => 
        t.status === 'running' || t.status === 'paused'
    );
    for (const task of activeTasks) {
        await cancelTask(task.id);
    }
}

async function clearCompletedTasks() {
    const completedTasks = currentTasks.filter(t => 
        t.status === 'completed' || t.status === 'cancelled' || t.status === 'failed'
    );
    for (const task of completedTasks) {
        await removeTask(task.id);
    }
}

/**
 * Start task monitoring
 */
function startTaskMonitoring() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(async () => {
        await loadTasks();
    }, 1000); // Update every second
}

/**
 * Start drive monitoring
 */
function startDriveMonitoring() {
    if (driveMonitorInterval) {
        clearInterval(driveMonitorInterval);
    }
    
    driveMonitorInterval = setInterval(async () => {
        await loadDrives();
    }, 5000); // Check every 5 seconds
}

/**
 * Update header statistics
 */
function updateHeaderStats() {
    const activeTasks = currentTasks.filter(t => 
        t.status === 'running' || t.status === 'paused'
    ).length;
    
    document.getElementById('active-tasks-count').textContent = activeTasks;
}

/**
 * Settings Management
 */
async function loadLicenseInfo() {
    try {
        const licenseInfo = await eel.get_license_info()();
        updateLicenseDisplay(licenseInfo);
        
    } catch (error) {
        console.error('❌ Error loading license info:', error);
    }
}

/**
 * Update license display
 */
function updateLicenseDisplay(licenseInfo) {
    const licenseType = document.getElementById('license-type');
    const licenseStatus = document.getElementById('license-status');
    const licenseLimits = document.getElementById('license-limits');
    const licenseMachine = document.getElementById('license-machine');
    
    if (licenseType) licenseType.textContent = licenseInfo.type === 'trial' ? 'نسخه آزمایشی' : 'نسخه حرفه‌ای';
    if (licenseStatus) licenseStatus.textContent = `وضعیت: ${licenseInfo.status === 'active' ? 'فعال' : 'غیرفعال'}`;
    if (licenseLimits) {
        const limit = licenseInfo.type === 'trial' ? 
            `محدودیت: ${licenseInfo.trial_files_limit} فایل` : 
            'بدون محدودیت';
        licenseLimits.textContent = limit;
    }
    if (licenseMachine) licenseMachine.textContent = `شناسه دستگاه: ${licenseInfo.machine_id}`;
}

/**
 * Activate license
 */
async function activateLicense() {
    const licenseKey = document.getElementById('license-key').value.trim();
    
    if (!licenseKey) {
        showToast('کلید لایسنس را وارد کنید', 'warning');
        return;
    }
    
    try {
        const result = await eel.activate_license(licenseKey)();
        
        if (result.success) {
            showToast('✅ لایسنس با موفقیت فعال شد', 'success');
            await loadLicenseInfo();
        } else {
            showToast(`❌ ${result.message}`, 'error');
        }
        
    } catch (error) {
        console.error('❌ Error activating license:', error);
        showToast('خطا در فعال‌سازی لایسنس', 'error');
    }
}

/**
 * Purchase license
 */
async function purchaseLicense() {
    try {
        await eel.open_payment_gateway()();
        showToast('🛒 درگاه پرداخت باز شد', 'info');
        
    } catch (error) {
        console.error('❌ Error opening payment gateway:', error);
        showToast('خطا در باز کردن درگاه پرداخت', 'error');
    }
}

/**
 * Theme and Font Management
 */
function applyTheme(themeName) {
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${themeName}`);
    
    // Update theme selector
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.value = themeName;
    }
    
    // Save to config
    if (!appConfig.ui_settings) appConfig.ui_settings = {};
    appConfig.ui_settings.theme = themeName;
    saveConfig();
}

function applyFont(fontFamily) {
    document.body.style.fontFamily = `'${fontFamily}', 'B Nazanin', Tahoma, Arial, sans-serif`;
    
    // Update font selector
    const fontSelect = document.getElementById('font-family-select');
    if (fontSelect) {
        fontSelect.value = fontFamily;
    }
    
    // Save to config
    if (!appConfig.ui_settings) appConfig.ui_settings = {};
    appConfig.ui_settings.font_family = fontFamily;
    saveConfig();
}

/**
 * Utility Functions
 */
function showSettings() {
    const settingsTab = document.querySelector('[data-tab="settings"]');
    if (settingsTab) {
        settingsTab.click();
    }
}

function showAbout() {
    const aboutTab = document.querySelector('[data-tab="about"]');
    if (aboutTab) {
        aboutTab.click();
    }
}

/**
 * Context Menu
 */
function showContextMenu(event, filePath) {
    event.preventDefault();
    event.stopPropagation();
    
    // Hide any existing context menu first
    hideContextMenu();
    
    const contextMenu = document.getElementById('context-menu');
    if (!contextMenu) return;
    
    // Position menu
    contextMenu.style.left = event.pageX + 'px';
    contextMenu.style.top = event.pageY + 'px';
    
    // Store current file path
    contextMenu.dataset.filePath = filePath;
    
    // Show menu
    contextMenu.classList.add('show');
    
    // Hide on click outside (delay to prevent immediate hiding)
    setTimeout(() => {
        document.addEventListener('click', hideContextMenu, { once: true });
    }, 10);
}

function hideContextMenu() {
    const contextMenu = document.getElementById('context-menu');
    if (contextMenu) {
        contextMenu.classList.remove('show');
    }
}

function copyFilePath() {
    const contextMenu = document.getElementById('context-menu');
    const filePath = contextMenu.dataset.filePath;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(filePath);
        showToast('مسیر فایل کپی شد', 'success');
    }
    
    hideContextMenu();
}

function openFile() {
    // Implementation would depend on Eel capabilities
    hideContextMenu();
    showToast('قابلیت باز کردن فایل در نسخه‌های بعدی اضافه خواهد شد', 'info');
}

function showFileProperties() {
    // Implementation for file properties
    hideContextMenu();
    showToast('قابلیت نمایش ویژگی‌ها در نسخه‌های بعدی اضافه خواهد شد', 'info');
}

/**
 * Format utility functions
 */
function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('fa-IR');
}

/**
 * Toast Notifications
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-hide after duration
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

/**
 * Highlight search results
 */
function highlightSearchResults(searchTerm) {
    if (!searchTerm) return;
    
    const fileNames = document.querySelectorAll('.file-name');
    fileNames.forEach(nameElement => {
        const text = nameElement.textContent;
        const highlightedText = text.replace(
            new RegExp(`(${searchTerm})`, 'gi'),
            '<mark>$1</mark>'
        );
        nameElement.innerHTML = highlightedText;
    });
}

/**
 * View toggle functionality
 */
function toggleView(viewType) {
    const fileList = document.getElementById('file-list');
    
    if (viewType === 'grid') {
        fileList.classList.add('grid-view');
    } else {
        fileList.classList.remove('grid-view');
    }
    
    // Update view buttons
    document.querySelectorAll('.view-options .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

/**
 * Advanced search modal
 */
function showAdvancedSearch() {
    showToast('جستجوی پیشرفته در نسخه‌های بعدی اضافه خواهد شد', 'info');
}

// Export functions for global access
window.selectDrive = selectDrive;
window.toggleFileSelection = toggleFileSelection;
window.selectAllFiles = selectAllFiles;
window.toggleSelectAll = toggleSelectAll;
window.sortFiles = sortFiles;
window.refreshFiles = refreshFiles;
window.refreshDrives = refreshDrives;
window.clearSearch = clearSearch;
window.pauseTask = pauseTask;
window.resumeTask = resumeTask;
window.cancelTask = cancelTask;
window.pauseAllTasks = pauseAllTasks;
window.resumeAllTasks = resumeAllTasks;
window.cancelAllTasks = cancelAllTasks;
window.clearCompletedTasks = clearCompletedTasks;
window.activateLicense = activateLicense;
window.purchaseLicense = purchaseLicense;
window.showSettings = showSettings;
/**
 * Advanced Settings Functions
 */

// Check database status
async function checkDatabaseStatus() {
    try {
        const statusElement = document.getElementById('db-status');
        statusElement.textContent = 'در حال بررسی...';
        
        const status = await eel.get_database_status()();
        const { files_count, size, last_cleanup } = status;
        
        const sizeInMB = (size / (1024 * 1024)).toFixed(2);
        statusElement.innerHTML = `
            📊 ${files_count.toLocaleString('fa-IR')} فایل ایندکس شده<br>
            💾 ${sizeInMB} مگابایت فضا<br>
            🧹 آخرین پاک‌سازی: ${last_cleanup || 'هیچ‌وقت'}
        `;
        
        showToast('✅ وضعیت پایگاه داده بررسی شد', 'success');
    } catch (error) {
        console.error('Error checking database status:', error);
        document.getElementById('db-status').textContent = '❌ خطا در بررسی';
        showToast('❌ خطا در بررسی وضعیت پایگاه داده', 'error');
    }
}

// Optimize database
async function optimizeDatabase() {
    try {
        showToast('🔧 شروع بهینه‌سازی پایگاه داده...', 'info');
        
        const result = await eel.optimize_database()();
        
        if (result.success) {
            showToast(`✅ بهینه‌سازی کامل شد. ${result.message}`, 'success');
            await checkDatabaseStatus(); // Refresh status
        } else {
            showToast(`❌ خطا در بهینه‌سازی: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error optimizing database:', error);
        showToast('❌ خطا در بهینه‌سازی پایگاه داده', 'error');
    }
}

// Confirm database reset
function confirmDatabaseReset() {
    const confirmed = confirm(
        '⚠️ هشدار!\n\n' +
        'این عمل تمام داده‌های ایندکس شده را پاک می‌کند.\n' +
        'آیا مطمئن هستید که می‌خواهید ادامه دهید؟\n\n' +
        'این عمل غیرقابل بازگشت است!'
    );
    
    if (confirmed) {
        resetDatabase();
    }
}

// Reset database
async function resetDatabase() {
    try {
        showToast('⚠️ در حال بازنشانی پایگاه داده...', 'warning');
        
        const result = await eel.reset_database()();
        
        if (result.success) {
            showToast('✅ پایگاه داده با موفقیت بازنشانی شد', 'success');
            await checkDatabaseStatus(); // Refresh status
            await loadDrives(); // Reload drives
        } else {
            showToast(`❌ خطا در بازنشانی: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error resetting database:', error);
        showToast('❌ خطا در بازنشانی پایگاه داده', 'error');
    }
}

// Load advanced settings
async function loadAdvancedSettings() {
    try {
        const config = await eel.get_config()();
        
        // System settings
        document.getElementById('debug-logging').checked = config.advanced?.debug_logging || false;
        document.getElementById('auto-save').checked = config.advanced?.auto_save_settings !== false;
        document.getElementById('memory-optimization').checked = config.advanced?.memory_optimization !== false;
        document.getElementById('performance-mode').value = config.advanced?.performance_mode || 'balanced';
        
        // Database settings
        document.getElementById('cleanup-days').value = config.advanced?.database_cleanup_days || 30;
        
        // Load database status
        await checkDatabaseStatus();
        
    } catch (error) {
        console.error('Error loading advanced settings:', error);
        showToast('❌ خطا در بارگیری تنظیمات پیشرفته', 'error');
    }
}

// Save advanced settings
async function saveAdvancedSettings() {
    try {
        const settings = {
            debug_logging: document.getElementById('debug-logging').checked,
            auto_save_settings: document.getElementById('auto-save').checked,
            memory_optimization: document.getElementById('memory-optimization').checked,
            performance_mode: document.getElementById('performance-mode').value,
            database_cleanup_days: parseInt(document.getElementById('cleanup-days').value) || 30
        };
        
        const result = await eel.save_advanced_settings(settings)();
        
        if (result.success) {
            showToast('✅ تنظیمات پیشرفته ذخیره شد', 'success');
        } else {
            showToast(`❌ خطا در ذخیره تنظیمات: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error saving advanced settings:', error);
        showToast('❌ خطا در ذخیره تنظیمات', 'error');
    }
}

// Auto-save when settings change
function initializeAdvancedSettingsAutoSave() {
    // Advanced settings
    const advancedInputs = [
        'debug-logging',
        'auto-save', 
        'memory-optimization',
        'performance-mode',
        'cleanup-days'
    ];
    
    advancedInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', () => {
                if (document.getElementById('auto-save')?.checked) {
                    setTimeout(saveAdvancedSettings, 500); // Debounce
                }
            });
        }
    });
    
    // File operation settings
    const fileOpInputs = [
        'max-tasks',
        'chunk-size',
        'verify-copy',
        'auto-retry',
        'max-retry',
        'skip-existing',
        'preserve-timestamps',
        'show-hidden',
        'follow-symlinks'
    ];
    
    fileOpInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', () => {
                setTimeout(saveFileOperationSettings, 500); // Debounce
            });
        }
    });
    
    // UI settings
    const uiInputs = [
        'font-family-select',
        'font-size-slider',
        'font-weight-select',
        'theme-select',
        'direction-select',
        'compact-mode',
        'startup-maximized',
        'show-tooltips',
        'animation-speed'
    ];
    
    uiInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', () => {
                setTimeout(saveUISettings, 500); // Debounce
            });
        }
    });
}

// Save file operation settings
async function saveFileOperationSettings() {
    try {
        const settings = {
            max_concurrent_tasks: parseInt(document.getElementById('max-tasks')?.value) || 5,
            chunk_size: parseInt(document.getElementById('chunk-size')?.value) * 1024 || 65536, // Convert KB to bytes
            verify_copy: document.getElementById('verify-copy')?.checked || false,
            auto_retry: document.getElementById('auto-retry')?.checked || false,
            retry_attempts: parseInt(document.getElementById('max-retry')?.value) || 3,
            skip_existing: document.getElementById('skip-existing')?.checked || false,
            preserve_permissions: document.getElementById('preserve-timestamps')?.checked || false,
            show_hidden_files: document.getElementById('show-hidden')?.checked || false,
            follow_symlinks: document.getElementById('follow-symlinks')?.checked || false
        };
        
        const result = await eel.save_file_operation_settings(settings)();
        
        if (result.success) {
            showToast('✅ تنظیمات عملیات فایل ذخیره شد', 'success');
        } else {
            showToast(`❌ خطا در ذخیره: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error saving file operation settings:', error);
        showToast('❌ خطا در ذخیره تنظیمات', 'error');
    }
}

// Save UI settings
async function saveUISettings() {
    try {
        const settings = {
            font_family: document.getElementById('font-family-select')?.value || 'Vazirmatn',
            font_size: parseInt(document.getElementById('font-size-slider')?.value) || 14,
            font_weight: document.getElementById('font-weight-select')?.value || 'normal',
            theme: document.getElementById('theme-select')?.value || 'dark',
            direction: document.getElementById('direction-select')?.value || 'rtl',
            compact_mode: document.getElementById('compact-mode')?.checked || false,
            startup_maximized: document.getElementById('startup-maximized')?.checked || true,
            show_tooltips: document.getElementById('show-tooltips')?.checked || true,
            animation_speed: document.getElementById('animation-speed')?.value || 'normal'
        };
        
        const result = await eel.save_ui_settings(settings)();
        
        if (result.success) {
            showToast('✅ تنظیمات رابط کاربری ذخیره شد', 'success');
            
            // Apply changes immediately
            applyFont(settings.font_family);
            applyTheme(settings.theme);
            
            // Update font size display
            const fontSizeValue = document.getElementById('font-size-value');
            if (fontSizeValue) {
                fontSizeValue.textContent = settings.font_size + 'px';
            }
        } else {
            showToast(`❌ خطا در ذخیره: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error saving UI settings:', error);
        showToast('❌ خطا در ذخیره تنظیمات', 'error');
    }
}

// Export functions to window
window.showAbout = showAbout;
window.showContextMenu = showContextMenu;
window.hideContextMenu = hideContextMenu;
window.copyFilePath = copyFilePath;
window.openFile = openFile;
window.showFileProperties = showFileProperties;
window.showToast = showToast;
window.applyTheme = applyTheme;
window.applyFont = applyFont;
window.toggleView = toggleView;
window.showAdvancedSearch = showAdvancedSearch;
window.goToPage = goToPage;
window.previousPage = previousPage;
window.nextPage = nextPage;

// Advanced Settings
window.checkDatabaseStatus = checkDatabaseStatus;
window.optimizeDatabase = optimizeDatabase;
window.confirmDatabaseReset = confirmDatabaseReset;
window.resetDatabase = resetDatabase;
window.loadAdvancedSettings = loadAdvancedSettings;
window.saveAdvancedSettings = saveAdvancedSettings;

// Utility functions
window.resetFilters = resetFilters;
window.saveFileOperationSettings = saveFileOperationSettings;
window.saveUISettings = saveUISettings;

/**
 * Load settings data
 */
async function loadSettingsData() {
    try {
        console.log('📋 Loading settings data...');
        
        // Load UI settings
        try {
            const uiSettings = await eel.get_config('ui_settings')();
            if (uiSettings && Object.keys(uiSettings).length > 0) {
                updateUISettingsForm(uiSettings);
                console.log('✅ UI settings loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load UI settings:', error);
        }
        
        // Load file operation settings
        try {
            const fileOpSettings = await eel.get_config('file_operations')();
            if (fileOpSettings && Object.keys(fileOpSettings).length > 0) {
                updateFileOperationSettingsForm(fileOpSettings);
                console.log('✅ File operation settings loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load file operation settings:', error);
        }
        
        // Load advanced settings
        try {
            const advancedSettings = await eel.get_config('advanced')();
            if (advancedSettings && Object.keys(advancedSettings).length > 0) {
                updateAdvancedSettingsForm(advancedSettings);
                console.log('✅ Advanced settings loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load advanced settings:', error);
        }
        
        // Load license info
        try {
            const licenseInfo = await eel.get_license_info()();
            if (licenseInfo) {
                updateLicenseInfo(licenseInfo);
                console.log('✅ License info loaded');
            }
        } catch (error) {
            console.warn('⚠️ Could not load license info:', error);
        }
        
        console.log('⚙️ Settings data loading completed');
    } catch (error) {
        console.error('❌ Error loading settings data:', error);
        showToast('خطا در بارگزاری تنظیمات', 'error');
    }
}

function updateUISettingsForm(settings) {
    const elements = {
        'font-family-select': settings.font_family,
        'font-size-slider': settings.font_size,
        'font-weight-select': settings.font_weight,
        'theme-select': settings.theme,
        'direction-select': settings.direction,
        'compact-mode': settings.compact_mode,
        'startup-maximized': settings.startup_maximized,
        'show-tooltips': settings.show_tooltips,
        'animation-speed': settings.animation_speed
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            try {
                if (element.type === 'checkbox') {
                    element.checked = Boolean(value);
                } else {
                    element.value = value;
                }
            } catch (error) {
                console.warn(`Could not update element ${id}:`, error);
            }
        }
    }
    
    // Update font size display
    const fontSizeValue = document.getElementById('font-size-value');
    if (fontSizeValue && settings.font_size) {
        fontSizeValue.textContent = settings.font_size + 'px';
    }
}

function updateFileOperationSettingsForm(settings) {
    const elements = {
        'max-tasks': settings.max_concurrent_tasks,
        'chunk-size': settings.chunk_size ? Math.floor(settings.chunk_size / 1024) : 64,
        'verify-copy': settings.verify_copy,
        'auto-retry': settings.auto_retry,
        'max-retry': settings.retry_attempts,
        'skip-existing': settings.skip_existing,
        'preserve-timestamps': settings.preserve_permissions,
        'show-hidden': settings.show_hidden_files,
        'follow-symlinks': settings.follow_symlinks
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            try {
                if (element.type === 'checkbox') {
                    element.checked = Boolean(value);
                } else {
                    element.value = value;
                }
            } catch (error) {
                console.warn(`Could not update element ${id}:`, error);
            }
        }
    }
}

function updateAdvancedSettingsForm(settings) {
    const elements = {
        'debug-logging': settings.debug_logging,
        'auto-save': settings.auto_save_settings,
        'memory-optimization': settings.memory_optimization,
        'performance-mode': settings.performance_mode,
        'cleanup-days': settings.database_cleanup_days
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            try {
                if (element.type === 'checkbox') {
                    element.checked = Boolean(value);
                } else {
                    element.value = value;
                }
            } catch (error) {
                console.warn(`Could not update element ${id}:`, error);
            }
        }
    }
}

function updateLicenseInfo(info) {
    try {
        const statusElement = document.querySelector('.license-status');
        const keyElement = document.getElementById('license-key');
        
        if (statusElement && info.status) {
            statusElement.innerHTML = `
                <div class="status-badge ${info.status === 'active' ? 'status-active' : 'status-inactive'}">
                    ${info.status === 'active' ? '✅ فعال' : '❌ غیرفعال'}
                </div>
            `;
        }
        
        if (keyElement && info.key) {
            keyElement.value = info.key;
        }
    } catch (error) {
        console.warn('Could not update license info:', error);
    }
}

// Export settings functions
window.loadSettingsData = loadSettingsData;