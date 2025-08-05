// UI Management and Toast Notifications

// Toast Notification System
let toastContainer = null;
let toastCounter = 0;

function initializeToastContainer() {
    toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'info', duration = 3000) {
    if (!toastContainer) {
        initializeToastContainer();
    }
    
    toastCounter++;
    const toastId = `toast-${toastCounter}`;
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast toast-${type} slide-in`;
    
    const iconMap = {
        'success': '✅',
        'error': '❌', 
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${iconMap[type] || 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="closeToast('${toastId}')">×</button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        closeToast(toastId);
    }, duration);
    
    return toastId;
}

function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.add('fade-out');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// Drag and Drop Functionality
function initializeDragAndDrop() {
    const fileItems = document.querySelectorAll('.file-item');
    const driveItems = document.querySelectorAll('.drive-item');
    
    // Make file items draggable
    fileItems.forEach(item => {
        item.draggable = true;
        item.addEventListener('dragstart', handleFileDragStart);
    });
    
    // Make drive items drop targets
    driveItems.forEach(item => {
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
    });
}

function handleFileDragStart(e) {
    const filePath = e.target.dataset.path;
    if (!selectedFiles.includes(filePath)) {
        toggleFileSelection(filePath);
    }
    e.dataTransfer.setData('text/plain', JSON.stringify(selectedFiles));
}

function handleDragOver(e) {
    e.preventDefault();
    e.target.closest('.drive-item').classList.add('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    const driveItem = e.target.closest('.drive-item');
    driveItem.classList.remove('drag-over');
    
    try {
        const draggedFiles = JSON.parse(e.dataTransfer.getData('text/plain'));
        const destination = driveItem.onclick.toString().match(/'([^']+)'/)[1];
        
        if (draggedFiles.length > 0) {
            startCopyOperation(destination);
        }
    } catch (error) {
        console.error('Error handling drop:', error);
        showToast('❌ خطا در انتقال فایل‌ها', 'error');
    }
}

// Modal Management
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('fade-in');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('fade-out');
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade-out');
            document.body.style.overflow = 'auto';
        }, 300);
    }
}

// Progress Bar Animation
function animateProgressBar(element, targetProgress) {
    const currentProgress = parseInt(element.style.width) || 0;
    const increment = (targetProgress - currentProgress) / 20;
    
    let current = currentProgress;
    const interval = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= targetProgress) || 
            (increment < 0 && current <= targetProgress)) {
            current = targetProgress;
            clearInterval(interval);
        }
        element.style.width = current + '%';
    }, 50);
}

// Loading States
function showLoading(elementId, message = 'در حال بارگذاری...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading-indicator">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const loading = element.querySelector('.loading-indicator');
        if (loading) {
            loading.remove();
        }
    }
}

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+A - Select All Files
        if (e.ctrlKey && e.key === 'a' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            selectAllFiles();
        }
        
        // Ctrl+R - Refresh
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            refreshFiles();
        }
        
        // F5 - Refresh Drives
        if (e.key === 'F5') {
            e.preventDefault();
            refreshDrives();
        }
        
        // Escape - Clear Selection
        if (e.key === 'Escape') {
            selectedFiles = [];
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
            });
            hideContextMenu();
        }
        
        // Delete - Remove Selected Files (placeholder)
        if (e.key === 'Delete' && selectedFiles.length > 0) {
            showToast(`🗑️ حذف ${selectedFiles.length} فایل انتخاب شده`, 'warning');
        }
    });
}

// Responsive Utilities
function isSmallScreen() {
    return window.innerWidth <= 768;
}

function isMediumScreen() {
    return window.innerWidth <= 1200 && window.innerWidth > 768;
}

// Theme Utilities
function getThemeVariables(theme) {
    const themes = {
        'dark': {
            '--bg-primary': '#1a1a1a',
            '--bg-secondary': '#2d2d2d',
            '--bg-tertiary': '#404040',
            '--text-primary': '#ffffff',
            '--text-secondary': '#cccccc',
            '--text-light': '#999999',
            '--border-color': '#404040',
            '--border-hover': '#555555'
        },
        'light': {
            '--bg-primary': '#ffffff',
            '--bg-secondary': '#f5f5f5',
            '--bg-tertiary': '#eeeeee',
            '--text-primary': '#333333',
            '--text-secondary': '#666666',
            '--text-light': '#999999',
            '--border-color': '#dddddd',
            '--border-hover': '#cccccc'
        },
        'blue': {
            '--bg-primary': '#0d1421',
            '--bg-secondary': '#1e2a3a',
            '--bg-tertiary': '#2d3e50',
            '--text-primary': '#ecf0f1',
            '--text-secondary': '#bdc3c7',
            '--text-light': '#95a5a6',
            '--border-color': '#34495e',
            '--border-hover': '#4a5f7a'
        },
        'green': {
            '--bg-primary': '#0d1f0d',
            '--bg-secondary': '#1a2e1a',
            '--bg-tertiary': '#2d4a2d',
            '--text-primary': '#e8f5e8',
            '--text-secondary': '#c8e6c9',
            '--text-light': '#a5d6a7',
            '--border-color': '#388e3c',
            '--border-hover': '#4caf50'
        }
    };
    
    return themes[theme] || themes['dark'];
}

function applyThemeVariables(theme) {
    const variables = getThemeVariables(theme);
    const root = document.documentElement;
    
    Object.entries(variables).forEach(([property, value]) => {
        root.style.setProperty(property, value);
    });
}

// Smooth Scrolling
function smoothScrollTo(element, duration = 500) {
    const target = typeof element === 'string' ? document.getElementById(element) : element;
    if (!target) return;
    
    const targetPosition = target.offsetTop;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = easeInOutQuad(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }
    
    function easeInOutQuad(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

// File Size Formatting
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Number Formatting (Persian)
function formatNumberPersian(number) {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    return number.toString().replace(/\d/g, (digit) => persianDigits[digit]);
}

// Date Formatting (Persian)
function formatDatePersian(date) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    try {
        return new Intl.DateTimeFormat('fa-IR', options).format(new Date(date));
    } catch {
        return date;
    }
}

// Copy to Clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('📋 متن کپی شد', 'success');
        return true;
    } catch (error) {
        console.error('Failed to copy text:', error);
        showToast('❌ خطا در کپی متن', 'error');
        return false;
    }
}

// Download File
function downloadTextFile(content, filename) {
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Local Storage Utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        return false;
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

// Debounce Function
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Throttle Function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Initialize UI components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeToastContainer();
    initializeKeyboardShortcuts();
    
    // Initialize after a short delay to ensure other scripts have loaded
    setTimeout(() => {
        initializeDragAndDrop();
    }, 100);
});

// Window resize handler
window.addEventListener('resize', debounce(() => {
    // Re-initialize drag and drop for responsive changes
    initializeDragAndDrop();
}, 250));

// Export functions for global access
window.showToast = showToast;
window.closeToast = closeToast;
window.showModal = showModal;
window.hideModal = hideModal;
window.animateProgressBar = animateProgressBar;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.smoothScrollTo = smoothScrollTo;
window.formatFileSize = formatFileSize;
window.formatNumberPersian = formatNumberPersian;
window.formatDatePersian = formatDatePersian;
window.copyToClipboard = copyToClipboard;
window.downloadTextFile = downloadTextFile;
window.saveToLocalStorage = saveToLocalStorage;
window.loadFromLocalStorage = loadFromLocalStorage;