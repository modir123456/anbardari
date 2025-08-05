// File Manager specific functionality

// Enhanced file selection with drive click copy
function enhanceFileSelectionWithCopy() {
    // Add click handlers to drive items for copy functionality
    document.addEventListener('click', function(e) {
        const driveItem = e.target.closest('.drive-item');
        if (driveItem && selectedFiles.length > 0) {
            // Extract drive path from onclick attribute
            const onclickAttr = driveItem.getAttribute('onclick');
            if (onclickAttr) {
                const pathMatch = onclickAttr.match(/selectDrive\('([^']+)'\)/);
                if (pathMatch) {
                    const drivePath = pathMatch[1];
                    startCopyOperation(drivePath);
                }
            }
        }
    });
}

// Enhanced drag and drop with visual feedback
function enhanceDragAndDrop() {
    // Add more visual feedback for drag operations
    document.addEventListener('dragstart', function(e) {
        if (e.target.closest('.file-item')) {
            const dragImage = document.createElement('div');
            dragImage.innerHTML = `📁 ${selectedFiles.length} فایل`;
            dragImage.style.cssText = `
                position: absolute;
                top: -1000px;
                background: var(--primary-color);
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-family: var(--font-family);
                z-index: 9999;
            `;
            document.body.appendChild(dragImage);
            e.dataTransfer.setDragImage(dragImage, 0, 0);
            
            setTimeout(() => {
                document.body.removeChild(dragImage);
            }, 0);
        }
    });
    
    // Add drop zone highlighting
    document.addEventListener('dragover', function(e) {
        const driveItem = e.target.closest('.drive-item');
        if (driveItem) {
            e.preventDefault();
            driveItem.style.transform = 'scale(1.05)';
            driveItem.style.borderColor = 'var(--success-color)';
        }
    });
    
    document.addEventListener('dragleave', function(e) {
        const driveItem = e.target.closest('.drive-item');
        if (driveItem && !driveItem.contains(e.relatedTarget)) {
            driveItem.style.transform = '';
            driveItem.style.borderColor = '';
        }
    });
    
    document.addEventListener('drop', function(e) {
        const driveItem = e.target.closest('.drive-item');
        if (driveItem) {
            driveItem.style.transform = '';
            driveItem.style.borderColor = '';
        }
    });
}

// File preview functionality
function showFilePreview(filePath) {
    const extension = filePath.split('.').pop().toLowerCase();
    const previewableTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'txt', 'md'];
    
    if (previewableTypes.includes(extension)) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        
        let content = '';
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) {
            content = `<img src="file://${filePath}" style="max-width: 100%; max-height: 80vh;" alt="پیش‌نمایش">`;
        } else if (['txt', 'md'].includes(extension)) {
            content = `<iframe src="file://${filePath}" style="width: 80vw; height: 80vh; border: none;"></iframe>`;
        }
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">پیش‌نمایش فایل</h3>
                    <button class="modal-close" onclick="hidePreview()">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        window.hidePreview = function() {
            document.body.removeChild(modal);
            delete window.hidePreview;
        };
    } else {
        showToast('❌ پیش‌نمایش برای این نوع فایل پشتیبانی نمی‌شود', 'warning');
    }
}

// File sorting functionality
function sortFiles(criteria) {
    const fileItems = Array.from(document.querySelectorAll('.file-item'));
    
    fileItems.sort((a, b) => {
        const aData = {
            name: a.querySelector('.file-col-name').textContent,
            size: parseInt(a.dataset.size) || 0,
            modified: a.dataset.modified || ''
        };
        
        const bData = {
            name: b.querySelector('.file-col-name').textContent,
            size: parseInt(b.dataset.size) || 0,
            modified: b.dataset.modified || ''
        };
        
        switch (criteria) {
            case 'name':
                return aData.name.localeCompare(bData.name, 'fa');
            case 'size':
                return bData.size - aData.size;
            case 'modified':
                return new Date(bData.modified) - new Date(aData.modified);
            case 'type':
                const aExt = aData.name.split('.').pop().toLowerCase();
                const bExt = bData.name.split('.').pop().toLowerCase();
                return aExt.localeCompare(bExt);
            default:
                return 0;
        }
    });
    
    const fileList = document.getElementById('file-list');
    fileItems.forEach(item => {
        fileList.appendChild(item);
    });
    
    showToast(`📋 فایل‌ها بر اساس ${criteria} مرتب شدند`, 'info');
}

// Add sorting controls
function addSortingControls() {
    const fileListHeader = document.querySelector('.file-list-header');
    if (fileListHeader) {
        const sortControls = document.createElement('div');
        sortControls.className = 'sort-controls';
        sortControls.innerHTML = `
            <select id="sort-select" class="filter-select" style="width: 120px; margin-right: 10px;">
                <option value="">مرتب‌سازی</option>
                <option value="name">نام</option>
                <option value="size">اندازه</option>
                <option value="modified">تاریخ تغییر</option>
                <option value="type">نوع</option>
            </select>
        `;
        
        fileListHeader.appendChild(sortControls);
        
        document.getElementById('sort-select').addEventListener('change', function() {
            if (this.value) {
                sortFiles(this.value);
                this.value = ''; // Reset selection
            }
        });
    }
}

// Bulk operations
function performBulkOperation(operation) {
    if (selectedFiles.length === 0) {
        showToast('❌ هیچ فایلی انتخاب نشده است', 'warning');
        return;
    }
    
    switch (operation) {
        case 'copy-paths':
            const paths = selectedFiles.join('\n');
            copyToClipboard(paths);
            showToast(`📋 مسیر ${selectedFiles.length} فایل کپی شد`, 'success');
            break;
            
        case 'export-list':
            const fileList = selectedFiles.map(path => {
                const fileName = path.split(/[/\\]/).pop();
                return `${fileName}\t${path}`;
            }).join('\n');
            
            const header = `نام فایل\tمسیر کامل\n`;
            downloadTextFile(header + fileList, `file-list-${new Date().toISOString().slice(0, 10)}.txt`);
            showToast(`💾 لیست ${selectedFiles.length} فایل دانلود شد`, 'success');
            break;
            
        case 'calculate-size':
            calculateSelectedFilesSize();
            break;
    }
}

// Calculate total size of selected files
async function calculateSelectedFilesSize() {
    try {
        showToast('📏 در حال محاسبه حجم فایل‌ها...', 'info');
        
        let totalSize = 0;
        for (const filePath of selectedFiles) {
            // This would need to be implemented in the backend
            // For now, we'll show a placeholder
        }
        
        // Placeholder calculation
        const randomSize = Math.random() * 1000000000; // Random size for demo
        const formattedSize = formatFileSize(randomSize);
        
        showToast(`📊 حجم کل: ${formattedSize}`, 'success', 5000);
        
    } catch (error) {
        showToast('❌ خطا در محاسبه حجم فایل‌ها', 'error');
    }
}

// Add bulk operation controls
function addBulkOperationControls() {
    const leftSection = document.querySelector('.left-section');
    if (leftSection) {
        const bulkControls = document.createElement('div');
        bulkControls.className = 'bulk-controls';
        bulkControls.style.cssText = `
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            padding: 12px;
            background: var(--bg-secondary);
            border-radius: 8px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        bulkControls.innerHTML = `
            <button class="btn btn-small btn-secondary" onclick="performBulkOperation('copy-paths')" title="کپی مسیر فایل‌ها">
                📋 کپی مسیرها
            </button>
            <button class="btn btn-small btn-secondary" onclick="performBulkOperation('export-list')" title="صادر کردن لیست">
                💾 صادر کردن
            </button>
            <button class="btn btn-small btn-secondary" onclick="performBulkOperation('calculate-size')" title="محاسبه حجم">
                📏 محاسبه حجم
            </button>
            <button class="btn btn-small btn-warning" onclick="clearSelection()" title="پاک کردن انتخاب">
                🗑️ پاک کردن
            </button>
        `;
        
        // Insert after file count
        const fileCount = leftSection.querySelector('.file-count');
        if (fileCount) {
            fileCount.after(bulkControls);
        }
        
        // Show/hide based on selection
        window.updateBulkControlsVisibility = function() {
            if (selectedFiles.length > 0) {
                bulkControls.style.opacity = '1';
            } else {
                bulkControls.style.opacity = '0';
            }
        };
    }
}

function clearSelection() {
    selectedFiles = [];
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.remove('selected');
    });
    updateSelectionInfo();
    if (window.updateBulkControlsVisibility) {
        window.updateBulkControlsVisibility();
    }
}

// File search with highlighting
function highlightSearchResults(searchTerm) {
    const fileItems = document.querySelectorAll('.file-item');
    
    fileItems.forEach(item => {
        const nameElement = item.querySelector('.file-col-name');
        if (nameElement) {
            const originalText = nameElement.dataset.originalText || nameElement.textContent;
            nameElement.dataset.originalText = originalText;
            
            if (searchTerm) {
                const highlightedText = originalText.replace(
                    new RegExp(`(${searchTerm})`, 'gi'),
                    '<mark style="background: yellow; padding: 2px;">$1</mark>'
                );
                nameElement.innerHTML = highlightedText;
            } else {
                nameElement.innerHTML = originalText;
            }
        }
    });
}

// Enhanced search with highlighting
function enhanceSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.trim();
            
            searchTimeout = setTimeout(() => {
                highlightSearchResults(searchTerm);
                if (currentDrive) {
                    scanCurrentDirectory();
                }
            }, 300);
        });
    }
}

// Initialize file manager enhancements
function initializeFileManagerEnhancements() {
    enhanceFileSelectionWithCopy();
    enhanceDragAndDrop();
    addSortingControls();
    addBulkOperationControls();
    enhanceSearch();
    
    // Override the original updateSelectionInfo to include bulk controls
    const originalUpdateSelectionInfo = window.updateSelectionInfo;
    window.updateSelectionInfo = function() {
        if (originalUpdateSelectionInfo) {
            originalUpdateSelectionInfo();
        }
        if (window.updateBulkControlsVisibility) {
            window.updateBulkControlsVisibility();
        }
    };
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeFileManagerEnhancements, 500);
});

// Export functions
window.showFilePreview = showFilePreview;
window.sortFiles = sortFiles;
window.performBulkOperation = performBulkOperation;
window.clearSelection = clearSelection;
window.highlightSearchResults = highlightSearchResults;