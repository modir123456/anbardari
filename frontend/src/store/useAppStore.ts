import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  // UI State
  isDarkMode: boolean
  isNotificationsEnabled: boolean
  currentTab: 'explorer' | 'tasks'
  isSettingsOpen: boolean
  
  // File Explorer State
  currentPath: string
  selectedFiles: string[]
  searchTerm: string
  
  // Settings State
  settings: {
    ui: {
      theme: 'dark' | 'light'
      language: 'fa' | 'en'
      notifications: boolean
      show_hidden_files: boolean
      compact_view: boolean
    }
    file_operations: {
      auto_resume: boolean
      verify_copy: boolean
      preserve_timestamps: boolean
      skip_existing: boolean
      create_log: boolean
    }
    advanced: {
      max_parallel_copies: number
      auto_index: boolean
      cache_enabled: boolean
    }
  }
  
  // Actions
  toggleDarkMode: () => void
  toggleNotifications: () => void
  setCurrentTab: (tab: 'explorer' | 'tasks') => void
  setIsSettingsOpen: (open: boolean) => void
  setCurrentPath: (path: string) => void
  setSelectedFiles: (files: string[]) => void
  setSearchTerm: (term: string) => void
  updateSettings: (settings: Partial<AppState['settings']>) => void
  
  // API Actions
  loadSettings: () => Promise<void>
  saveSettings: () => Promise<void>
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial State
      isDarkMode: true,
      isNotificationsEnabled: true,
      currentTab: 'explorer',
      isSettingsOpen: false,
      currentPath: 'all',
      selectedFiles: [],
      searchTerm: '',
      
      settings: {
        ui: {
          theme: 'dark',
          language: 'fa',
          notifications: true,
          show_hidden_files: false,
          compact_view: false
        },
        file_operations: {
          auto_resume: true,
          verify_copy: true,
          preserve_timestamps: true,
          skip_existing: false,
          create_log: true
        },
        advanced: {
          max_parallel_copies: 3,
          auto_index: true,
          cache_enabled: true
        }
      },
      
      // Actions
      toggleDarkMode: () => set((state) => ({ 
        isDarkMode: !state.isDarkMode,
        settings: {
          ...state.settings,
          ui: {
            ...state.settings.ui,
            theme: !state.isDarkMode ? 'dark' : 'light'
          }
        }
      })),
      
      toggleNotifications: () => set((state) => ({ 
        isNotificationsEnabled: !state.isNotificationsEnabled,
        settings: {
          ...state.settings,
          ui: {
            ...state.settings.ui,
            notifications: !state.isNotificationsEnabled
          }
        }
      })),
      
      setCurrentTab: (tab) => set({ currentTab: tab }),
      setIsSettingsOpen: (open) => set({ isSettingsOpen: open }),
      setCurrentPath: (path) => set({ currentPath: path }),
      setSelectedFiles: (files) => set({ selectedFiles: files }),
      setSearchTerm: (term) => set({ searchTerm: term }),
      
      updateSettings: (newSettings) => set((state) => ({
        settings: {
          ...state.settings,
          ...newSettings
        }
      })),
      
      loadSettings: async () => {
        try {
          const response = await fetch('/api/settings')
          if (response.ok) {
            const data = await response.json()
            set((state) => ({
              settings: data,
              isDarkMode: data.ui_settings?.theme === 'dark',
              isNotificationsEnabled: data.ui_settings?.notifications !== false
            }))
          }
        } catch (error) {
          console.error('Error loading settings:', error)
        }
      },
      
      saveSettings: async () => {
        try {
          const state = get()
          const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              key: 'all_settings',
              value: state.settings
            })
          })
          
          if (!response.ok) {
            throw new Error('Failed to save settings')
          }
        } catch (error) {
          console.error('Error saving settings:', error)
          throw error
        }
      }
    }),
    {
      name: 'persian-file-copier-store',
      partialize: (state) => ({
        isDarkMode: state.isDarkMode,
        isNotificationsEnabled: state.isNotificationsEnabled,
        settings: state.settings
      })
    }
  )
)