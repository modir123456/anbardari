import React, { useState, useEffect } from 'react'
import { Toaster, toast } from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Copy, 
  Settings, 
  FolderOpen, 
  HardDrive, 
  Moon, 
  Sun,
  Bell,
  BellOff,
  Download,
  Play,
  Pause,
  X
} from 'lucide-react'
import { useAppStore } from './store/useAppStore'
import { FileExplorer } from './components/FileExplorer'
import { TaskManager } from './components/TaskManager'
import { SettingsPanel } from './components/SettingsPanel'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'

function App() {
  const { 
    isDarkMode, 
    toggleDarkMode, 
    isNotificationsEnabled,
    toggleNotifications,
    currentTab,
    setCurrentTab,
    isSettingsOpen,
    setIsSettingsOpen
  } = useAppStore()

  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [destination, setDestination] = useState('')

  useEffect(() => {
    // Apply dark mode class to document
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDarkMode])

  const handleStartCopy = async () => {
    if (selectedFiles.length === 0) {
      toast.error('هیچ فایلی انتخاب نشده است')
      return
    }
    
    if (!destination.trim()) {
      toast.error('لطفاً مقصد را انتخاب کنید')
      return
    }

    try {
      const response = await fetch('/api/copy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_files: selectedFiles,
          destination: destination.trim()
        })
      })

      const result = await response.json()
      
      if (result.success) {
        toast.success(`کپی شروع شد - شناسه: ${result.task_id}`)
        setCurrentTab('tasks')
      } else {
        toast.error('خطا در شروع کپی')
      }
    } catch (error) {
      console.error('Error starting copy:', error)
      toast.error('خطا در ارتباط با سرور')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900 font-persian">
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            fontFamily: 'Vazirmatn, sans-serif',
            direction: 'rtl'
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#ffffff'
            }
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#ffffff'
            }
          }
        }}
      />

      {/* Header */}
      <Header />

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          <div className="h-full flex flex-col">
            {/* Action Bar */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200/50 dark:border-gray-700/50 p-4">
              <div className="flex items-center gap-4 mb-4">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="مقصد کپی..."
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="input-field"
                  />
                </div>
                <motion.button
                  onClick={handleStartCopy}
                  className="btn-primary flex items-center gap-2"
                  whileTap={{ scale: 0.95 }}
                  disabled={selectedFiles.length === 0}
                >
                  <Copy className="w-4 h-4" />
                  شروع کپی ({selectedFiles.length})
                </motion.button>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center gap-2">
                <motion.button
                  onClick={toggleDarkMode}
                  className="btn-secondary p-2"
                  whileTap={{ scale: 0.95 }}
                  title={isDarkMode ? 'حالت روز' : 'حالت شب'}
                >
                  {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </motion.button>
                
                <motion.button
                  onClick={toggleNotifications}
                  className="btn-secondary p-2"
                  whileTap={{ scale: 0.95 }}
                  title={isNotificationsEnabled ? 'غیرفعال کردن اعلان‌ها' : 'فعال کردن اعلان‌ها'}
                >
                  {isNotificationsEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
                </motion.button>

                <motion.button
                  onClick={() => setIsSettingsOpen(true)}
                  className="btn-secondary p-2"
                  whileTap={{ scale: 0.95 }}
                  title="تنظیمات"
                >
                  <Settings className="w-4 h-4" />
                </motion.button>
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden">
              <AnimatePresence mode="wait">
                {currentTab === 'explorer' && (
                  <motion.div
                    key="explorer"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className="h-full"
                  >
                    <FileExplorer 
                      selectedFiles={selectedFiles}
                      onSelectionChange={setSelectedFiles}
                    />
                  </motion.div>
                )}
                
                {currentTab === 'tasks' && (
                  <motion.div
                    key="tasks"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className="h-full"
                  >
                    <TaskManager />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </main>
      </div>

      {/* Settings Modal */}
      <AnimatePresence>
        {isSettingsOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setIsSettingsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  ⚙️ تنظیمات
                </h2>
                <motion.button
                  onClick={() => setIsSettingsOpen(false)}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  whileTap={{ scale: 0.95 }}
                >
                  <X className="w-5 h-5" />
                </motion.button>
              </div>
              
              <div className="overflow-y-auto max-h-[calc(90vh-5rem)]">
                <SettingsPanel />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App