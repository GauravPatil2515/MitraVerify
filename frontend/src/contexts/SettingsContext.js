import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { toast } from 'react-toastify';

// Settings context
const SettingsContext = createContext();

// Settings action types
const SETTINGS_ACTIONS = {
  SET_THEME: 'SET_THEME',
  SET_LANGUAGE: 'SET_LANGUAGE',
  SET_NOTIFICATIONS: 'SET_NOTIFICATIONS',
  SET_PRIVACY: 'SET_PRIVACY',
  SET_ACCESSIBILITY: 'SET_ACCESSIBILITY',
  SET_PREFERENCES: 'SET_PREFERENCES',
  RESET_SETTINGS: 'RESET_SETTINGS',
  IMPORT_SETTINGS: 'IMPORT_SETTINGS',
};

// Default settings
const defaultSettings = {
  // Theme settings
  theme: {
    mode: 'light', // 'light' | 'dark' | 'auto'
    primaryColor: '#1976d2',
    fontSize: 'medium', // 'small' | 'medium' | 'large'
    compactMode: false,
  },

  // Language and localization
  language: 'en', // 'en' | 'hi' | 'bn' | 'ta' | 'mr' | 'te' | 'gu' | 'kn' | 'ml' | 'pa'
  region: 'IN', // Country code
  dateFormat: 'DD/MM/YYYY',
  timeFormat: '24h', // '12h' | '24h'

  // Notification preferences
  notifications: {
    email: {
      verificationResults: true,
      weeklyDigest: true,
      educationalTips: true,
      securityAlerts: true,
      productUpdates: false,
    },
    push: {
      verificationComplete: true,
      newFeatures: false,
      reminders: true,
    },
    inApp: {
      achievements: true,
      tips: true,
      warnings: true,
    },
  },

  // Privacy settings
  privacy: {
    shareAnalytics: true,
    saveVerificationHistory: true,
    allowPersonalization: true,
    shareUsageData: false,
    enableCookies: true,
  },

  // Accessibility settings
  accessibility: {
    highContrast: false,
    reducedMotion: false,
    screenReader: false,
    largeText: false,
    keyboardNavigation: false,
  },

  // Verification preferences
  verification: {
    autoAnalyze: true,
    showConfidence: true,
    detailedResults: true,
    saveToHistory: true,
    quickShare: false,
  },

  // Education preferences
  education: {
    difficulty: 'intermediate', // 'beginner' | 'intermediate' | 'advanced'
    reminders: true,
    progressTracking: true,
    competitiveMode: false,
  },

  // Interface preferences
  interface: {
    sidebarCollapsed: false,
    showTutorials: true,
    compactCards: false,
    animationsEnabled: true,
    soundEnabled: false,
  },

  // Developer settings (for advanced users)
  developer: {
    debugMode: false,
    showApiErrors: false,
    logLevel: 'error', // 'debug' | 'info' | 'warn' | 'error'
  },
};

// Settings reducer
const settingsReducer = (state, action) => {
  switch (action.type) {
    case SETTINGS_ACTIONS.SET_THEME:
      return {
        ...state,
        theme: { ...state.theme, ...action.payload },
      };

    case SETTINGS_ACTIONS.SET_LANGUAGE:
      return {
        ...state,
        language: action.payload.language,
        region: action.payload.region || state.region,
      };

    case SETTINGS_ACTIONS.SET_NOTIFICATIONS:
      return {
        ...state,
        notifications: { ...state.notifications, ...action.payload },
      };

    case SETTINGS_ACTIONS.SET_PRIVACY:
      return {
        ...state,
        privacy: { ...state.privacy, ...action.payload },
      };

    case SETTINGS_ACTIONS.SET_ACCESSIBILITY:
      return {
        ...state,
        accessibility: { ...state.accessibility, ...action.payload },
      };

    case SETTINGS_ACTIONS.SET_PREFERENCES:
      return {
        ...state,
        [action.payload.category]: {
          ...state[action.payload.category],
          ...action.payload.settings,
        },
      };

    case SETTINGS_ACTIONS.RESET_SETTINGS:
      return { ...defaultSettings };

    case SETTINGS_ACTIONS.IMPORT_SETTINGS:
      return { ...state, ...action.payload };

    default:
      return state;
  }
};

// Get stored settings from localStorage
const getStoredSettings = () => {
  try {
    const stored = localStorage.getItem('mitraverify_settings');
    if (stored) {
      const parsedSettings = JSON.parse(stored);
      // Merge with default settings to handle new settings added in updates
      return { ...defaultSettings, ...parsedSettings };
    }
  } catch (error) {
    console.error('Error loading settings from localStorage:', error);
  }
  return defaultSettings;
};

// Settings provider component
export const SettingsProvider = ({ children }) => {
  const [settings, dispatch] = useReducer(settingsReducer, getStoredSettings());

  // Save settings to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('mitraverify_settings', JSON.stringify(settings));
    } catch (error) {
      console.error('Error saving settings to localStorage:', error);
      toast.error('Failed to save settings');
    }
  }, [settings]);

  // Apply theme changes to document
  useEffect(() => {
    const root = document.documentElement;
    
    // Apply theme mode
    if (settings.theme.mode === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else if (settings.theme.mode === 'light') {
      root.setAttribute('data-theme', 'light');
    } else {
      // Auto mode - use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }

    // Apply font size
    root.style.setProperty('--base-font-size', {
      small: '14px',
      medium: '16px',
      large: '18px',
    }[settings.theme.fontSize]);

    // Apply primary color
    root.style.setProperty('--primary-color', settings.theme.primaryColor);

    // Apply accessibility settings
    if (settings.accessibility.highContrast) {
      root.setAttribute('data-contrast', 'high');
    } else {
      root.removeAttribute('data-contrast');
    }

    if (settings.accessibility.reducedMotion) {
      root.style.setProperty('--animation-duration', '0.01ms');
    } else {
      root.style.removeProperty('--animation-duration');
    }

  }, [settings.theme, settings.accessibility]);

  // Apply language changes
  useEffect(() => {
    document.documentElement.lang = settings.language;
  }, [settings.language]);

  // Setting update functions
  const updateTheme = (themeSettings) => {
    dispatch({
      type: SETTINGS_ACTIONS.SET_THEME,
      payload: themeSettings,
    });
  };

  const updateLanguage = (language, region) => {
    dispatch({
      type: SETTINGS_ACTIONS.SET_LANGUAGE,
      payload: { language, region },
    });
    toast.success('Language updated successfully');
  };

  const updateNotifications = (notificationSettings) => {
    dispatch({
      type: SETTINGS_ACTIONS.SET_NOTIFICATIONS,
      payload: notificationSettings,
    });
    toast.success('Notification preferences updated');
  };

  const updatePrivacy = (privacySettings) => {
    dispatch({
      type: SETTINGS_ACTIONS.SET_PRIVACY,
      payload: privacySettings,
    });
    toast.success('Privacy settings updated');
  };

  const updateAccessibility = (accessibilitySettings) => {
    dispatch({
      type: SETTINGS_ACTIONS.SET_ACCESSIBILITY,
      payload: accessibilitySettings,
    });
    toast.success('Accessibility settings updated');
  };

  const updatePreferences = (category, preferenceSettings) => {
    dispatch({
      type: SETTINGS_ACTIONS.SET_PREFERENCES,
      payload: { category, settings: preferenceSettings },
    });
  };

  const resetSettings = () => {
    dispatch({ type: SETTINGS_ACTIONS.RESET_SETTINGS });
    toast.success('Settings reset to defaults');
  };

  const exportSettings = () => {
    try {
      const settingsData = JSON.stringify(settings, null, 2);
      const blob = new Blob([settingsData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = 'mitraverify-settings.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
      toast.success('Settings exported successfully');
    } catch (error) {
      console.error('Error exporting settings:', error);
      toast.error('Failed to export settings');
    }
  };

  const importSettings = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          
          // Validate imported settings
          if (typeof importedSettings === 'object' && importedSettings !== null) {
            // Merge with current settings to ensure all required fields exist
            const mergedSettings = { ...settings, ...importedSettings };
            
            dispatch({
              type: SETTINGS_ACTIONS.IMPORT_SETTINGS,
              payload: mergedSettings,
            });
            
            toast.success('Settings imported successfully');
            resolve(true);
          } else {
            throw new Error('Invalid settings format');
          }
        } catch (error) {
          console.error('Error importing settings:', error);
          toast.error('Failed to import settings - invalid format');
          reject(error);
        }
      };
      
      reader.onerror = () => {
        toast.error('Failed to read settings file');
        reject(new Error('File read error'));
      };
      
      reader.readAsText(file);
    });
  };

  // Utility functions
  const getLanguageDirection = () => {
    // RTL languages
    const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
    return rtlLanguages.includes(settings.language) ? 'rtl' : 'ltr';
  };

  const getTimeFormat = () => {
    return settings.timeFormat === '12h' ? 'h:mm A' : 'HH:mm';
  };

  const getDateTimeFormat = () => {
    return `${settings.dateFormat} ${getTimeFormat()}`;
  };

  const shouldShowTutorials = () => {
    return settings.interface.showTutorials;
  };

  const shouldUseAnimations = () => {
    return settings.interface.animationsEnabled && !settings.accessibility.reducedMotion;
  };

  const getThemeMode = () => {
    if (settings.theme.mode === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return settings.theme.mode;
  };

  // Analytics and usage tracking (respecting privacy settings)
  const trackSettingChange = (setting, value) => {
    if (settings.privacy.shareUsageData) {
      // Send analytics event
      if (window.gtag) {
        window.gtag('event', 'setting_changed', {
          setting_name: setting,
          setting_value: value,
          user_id: settings.privacy.shareAnalytics ? 'anonymous' : null,
        });
      }
    }
  };

  // Context value
  const value = {
    // Settings state
    settings,

    // Update functions
    updateTheme,
    updateLanguage,
    updateNotifications,
    updatePrivacy,
    updateAccessibility,
    updatePreferences,

    // Utility functions
    resetSettings,
    exportSettings,
    importSettings,
    getLanguageDirection,
    getTimeFormat,
    getDateTimeFormat,
    shouldShowTutorials,
    shouldUseAnimations,
    getThemeMode,
    trackSettingChange,

    // Computed values
    isDarkMode: getThemeMode() === 'dark',
    isRTL: getLanguageDirection() === 'rtl',
    animationsEnabled: shouldUseAnimations(),
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

// Custom hook to use settings context
export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

// Hook for theme-specific functionality
export const useTheme = () => {
  const { settings, updateTheme, isDarkMode, getThemeMode } = useSettings();
  
  return {
    theme: settings.theme,
    updateTheme,
    isDarkMode,
    themeMode: getThemeMode(),
    toggleTheme: () => {
      const newMode = isDarkMode ? 'light' : 'dark';
      updateTheme({ mode: newMode });
    },
  };
};

// Hook for notification preferences
export const useNotificationPreferences = () => {
  const { settings, updateNotifications } = useSettings();
  
  return {
    notifications: settings.notifications,
    updateNotifications,
    shouldNotify: (type, category) => {
      return settings.notifications[category]?.[type] ?? false;
    },
  };
};

// Hook for accessibility features
export const useAccessibility = () => {
  const { settings, updateAccessibility } = useSettings();
  
  return {
    accessibility: settings.accessibility,
    updateAccessibility,
    isHighContrast: settings.accessibility.highContrast,
    isReducedMotion: settings.accessibility.reducedMotion,
    isLargeText: settings.accessibility.largeText,
  };
};

export default SettingsContext;
