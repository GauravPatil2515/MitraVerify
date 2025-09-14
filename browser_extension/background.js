/**
 * MitraVerify Browser Extension - Background Service Worker
 * Handles content verification, notifications, and extension management
 */

// Extension configuration
const CONFIG = {
  API_BASE_URL: 'https://mitraverify.vercel.app/api',
  API_TIMEOUT: 30000,
  MAX_CACHE_SIZE: 1000,
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  AUTO_SCAN_DELAY: 2000, // 2 seconds
  VERIFICATION_DEBOUNCE: 1000, // 1 second
};

// Global state
let verificationCache = new Map();
let activeVerifications = new Set();
let userSettings = {};
let extensionStats = {
  totalVerifications: 0,
  misinformationDetected: 0,
  lastVerificationTime: null,
};

// Initialize extension
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('MitraVerify extension installed/updated');
  
  // Set up context menus
  setupContextMenus();
  
  // Initialize default settings
  await initializeSettings();
  
  // Show welcome notification on first install
  if (details.reason === 'install') {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon-48.png',
      title: 'MitraVerify Installed!',
      message: 'Right-click on text or images to verify content, or enable auto-scan in settings.',
    });
  }
  
  // Load stored stats
  const stored = await chrome.storage.local.get(['extensionStats']);
  if (stored.extensionStats) {
    extensionStats = { ...extensionStats, ...stored.extensionStats };
  }
});

// Set up context menus
function setupContextMenus() {
  chrome.contextMenus.removeAll(() => {
    // Text verification menu
    chrome.contextMenus.create({
      id: 'verify-text',
      title: 'Verify with MitraVerify',
      contexts: ['selection'],
    });
    
    // Image verification menu
    chrome.contextMenus.create({
      id: 'verify-image',
      title: 'Verify Image with MitraVerify',
      contexts: ['image'],
    });
    
    // Link verification menu
    chrome.contextMenus.create({
      id: 'verify-link',
      title: 'Verify Link with MitraVerify',
      contexts: ['link'],
    });
    
    // Page verification menu
    chrome.contextMenus.create({
      id: 'verify-page',
      title: 'Verify Current Page',
      contexts: ['page'],
    });
    
    // Separator
    chrome.contextMenus.create({
      id: 'separator1',
      type: 'separator',
      contexts: ['selection', 'image', 'link', 'page'],
    });
    
    // Settings menu
    chrome.contextMenus.create({
      id: 'open-settings',
      title: 'MitraVerify Settings',
      contexts: ['selection', 'image', 'link', 'page'],
    });
  });
}

// Initialize default settings
async function initializeSettings() {
  const defaultSettings = {
    autoScanEnabled: true,
    showNotifications: true,
    scanSocialMedia: true,
    scanNewsArticles: true,
    confidenceThreshold: 0.7,
    scanDelay: 2000,
    enabledSites: {
      facebook: true,
      twitter: true,
      instagram: true,
      youtube: true,
      whatsapp: true,
      news: true,
    },
    verificationMethods: {
      text: true,
      images: true,
      links: true,
    },
    uiSettings: {
      showInlineWarnings: true,
      highlightSuspiciousContent: true,
      showConfidenceScores: true,
      compactMode: false,
    },
  };
  
  const stored = await chrome.storage.sync.get(['userSettings']);
  userSettings = { ...defaultSettings, ...(stored.userSettings || {}) };
  
  // Save merged settings
  await chrome.storage.sync.set({ userSettings });
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  try {
    switch (info.menuItemId) {
      case 'verify-text':
        if (info.selectionText) {
          await verifyContent('text', { content: info.selectionText }, tab.id);
        }
        break;
        
      case 'verify-image':
        if (info.srcUrl) {
          await verifyContent('image', { url: info.srcUrl }, tab.id);
        }
        break;
        
      case 'verify-link':
        if (info.linkUrl) {
          await verifyContent('url', { url: info.linkUrl }, tab.id);
        }
        break;
        
      case 'verify-page':
        await verifyContent('url', { url: tab.url }, tab.id);
        break;
        
      case 'open-settings':
        chrome.runtime.openOptionsPage();
        break;
    }
  } catch (error) {
    console.error('Context menu action failed:', error);
  }
});

// Handle keyboard commands
chrome.commands.onCommand.addListener(async (command) => {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const tab = tabs[0];
  
  if (!tab) return;
  
  try {
    switch (command) {
      case 'verify_selected_text':
        chrome.tabs.sendMessage(tab.id, { action: 'verifySelectedText' });
        break;
        
      case 'toggle_auto_scan':
        userSettings.autoScanEnabled = !userSettings.autoScanEnabled;
        await chrome.storage.sync.set({ userSettings });
        chrome.tabs.sendMessage(tab.id, { 
          action: 'toggleAutoScan', 
          enabled: userSettings.autoScanEnabled 
        });
        
        // Show notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon-48.png',
          title: 'Auto-scan ' + (userSettings.autoScanEnabled ? 'Enabled' : 'Disabled'),
          message: userSettings.autoScanEnabled 
            ? 'Content will be automatically scanned for misinformation'
            : 'Automatic scanning has been disabled',
        });
        break;
        
      case 'open_full_report':
        chrome.tabs.create({ url: 'https://mitraverify.vercel.app/dashboard' });
        break;
    }
  } catch (error) {
    console.error('Command execution failed:', error);
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender, sendResponse);
  return true; // Keep the message channel open for async responses
});

// Main message handler
async function handleMessage(message, sender, sendResponse) {
  try {
    switch (message.action) {
      case 'verifyContent':
        const result = await verifyContent(
          message.contentType, 
          message.data, 
          sender.tab?.id
        );
        sendResponse({ success: true, result });
        break;
        
      case 'getSettings':
        sendResponse({ success: true, settings: userSettings });
        break;
        
      case 'updateSettings':
        userSettings = { ...userSettings, ...message.settings };
        await chrome.storage.sync.set({ userSettings });
        sendResponse({ success: true });
        break;
        
      case 'getStats':
        sendResponse({ success: true, stats: extensionStats });
        break;
        
      case 'clearCache':
        verificationCache.clear();
        sendResponse({ success: true });
        break;
        
      case 'reportFeedback':
        await reportFeedback(message.feedback);
        sendResponse({ success: true });
        break;
        
      default:
        sendResponse({ success: false, error: 'Unknown action' });
    }
  } catch (error) {
    console.error('Message handling error:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// Content verification function
async function verifyContent(contentType, data, tabId) {
  const cacheKey = `${contentType}:${JSON.stringify(data)}`;
  
  // Check cache first
  if (verificationCache.has(cacheKey)) {
    const cached = verificationCache.get(cacheKey);
    if (Date.now() - cached.timestamp < CONFIG.CACHE_DURATION) {
      return cached.result;
    }
    verificationCache.delete(cacheKey);
  }
  
  // Prevent duplicate verifications
  if (activeVerifications.has(cacheKey)) {
    return { status: 'pending', message: 'Verification in progress...' };
  }
  
  activeVerifications.add(cacheKey);
  
  try {
    // Call verification API
    const response = await fetch(`${CONFIG.API_BASE_URL}/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Extension-Version': chrome.runtime.getManifest().version,
      },
      body: JSON.stringify({
        content_type: contentType,
        ...data,
      }),
      signal: AbortSignal.timeout(CONFIG.API_TIMEOUT),
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Cache the result
    verificationCache.set(cacheKey, {
      result,
      timestamp: Date.now(),
    });
    
    // Clean cache if it gets too large
    if (verificationCache.size > CONFIG.MAX_CACHE_SIZE) {
      const oldestKey = verificationCache.keys().next().value;
      verificationCache.delete(oldestKey);
    }
    
    // Update stats
    extensionStats.totalVerifications++;
    extensionStats.lastVerificationTime = Date.now();
    
    if (result.result?.status === 'false') {
      extensionStats.misinformationDetected++;
    }
    
    // Save stats
    await chrome.storage.local.set({ extensionStats });
    
    // Show notification if enabled and content is suspicious
    if (userSettings.showNotifications && shouldShowNotification(result)) {
      showVerificationNotification(result, tabId);
    }
    
    // Send result to content script if tab is available
    if (tabId) {
      try {
        chrome.tabs.sendMessage(tabId, {
          action: 'verificationResult',
          result,
          cacheKey,
        });
      } catch (error) {
        console.log('Could not send result to content script:', error.message);
      }
    }
    
    return result;
    
  } catch (error) {
    console.error('Verification failed:', error);
    
    const errorResult = {
      status: 'error',
      message: 'Verification failed. Please try again.',
      error: error.message,
    };
    
    return errorResult;
    
  } finally {
    activeVerifications.delete(cacheKey);
  }
}

// Determine if notification should be shown
function shouldShowNotification(result) {
  if (!result.result) return false;
  
  const status = result.result.status;
  const confidence = result.result.confidence || 0;
  
  // Show notification for false or questionable content above threshold
  return (status === 'false' || status === 'questionable') && 
         confidence >= userSettings.confidenceThreshold;
}

// Show verification notification
function showVerificationNotification(result, tabId) {
  const status = result.result?.status || 'unknown';
  const confidence = result.result?.confidence || 0;
  
  const statusMessages = {
    'false': '⚠️ Misinformation Detected',
    'questionable': '🤔 Content Needs Verification',
    'verified': '✅ Content Verified',
    'insufficient_info': 'ℹ️ Insufficient Information',
  };
  
  const title = statusMessages[status] || '❓ Verification Complete';
  
  let message = `Confidence: ${(confidence * 100).toFixed(0)}%`;
  if (result.result?.explanation) {
    message += `\n${result.result.explanation.substring(0, 100)}...`;
  }
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon-48.png',
    title,
    message,
    buttons: [
      { title: 'View Details' },
      { title: 'Dismiss' },
    ],
  });
}

// Handle notification clicks
chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
  if (buttonIndex === 0) { // View Details
    chrome.tabs.create({ url: 'https://mitraverify.vercel.app/dashboard' });
  }
  chrome.notifications.clear(notificationId);
});

// Report user feedback
async function reportFeedback(feedback) {
  try {
    await fetch(`${CONFIG.API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Extension-Version': chrome.runtime.getManifest().version,
      },
      body: JSON.stringify(feedback),
    });
  } catch (error) {
    console.error('Failed to report feedback:', error);
  }
}

// Periodic cleanup of cache and stats
setInterval(() => {
  const now = Date.now();
  
  // Clean expired cache entries
  for (const [key, value] of verificationCache.entries()) {
    if (now - value.timestamp > CONFIG.CACHE_DURATION) {
      verificationCache.delete(key);
    }
  }
  
  // Save stats periodically
  chrome.storage.local.set({ extensionStats });
}, 60000); // Every minute

// Handle extension suspend/resume
chrome.runtime.onSuspend.addListener(() => {
  // Save any pending data before suspension
  chrome.storage.local.set({ extensionStats });
});

// Listen for tab updates to potentially scan new content
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && userSettings.autoScanEnabled) {
    try {
      // Only scan if it's a supported site
      const url = new URL(tab.url);
      const domain = url.hostname.toLowerCase();
      
      const supportedDomains = [
        'facebook.com', 'www.facebook.com',
        'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
        'instagram.com', 'www.instagram.com',
        'youtube.com', 'www.youtube.com',
        'whatsapp.com', 'web.whatsapp.com',
      ];
      
      const isNewssite = domain.includes('news') || 
                        domain.includes('times') || 
                        domain.includes('hindu') || 
                        domain.includes('ndtv') ||
                        domain.includes('zee') ||
                        domain.includes('aaj');
      
      if (supportedDomains.some(d => domain.includes(d)) || 
          (isNewssite && userSettings.enabledSites.news)) {
        
        // Send message to content script to start scanning
        chrome.tabs.sendMessage(tabId, {
          action: 'startAutoScan',
          settings: userSettings,
        });
      }
    } catch (error) {
      // Invalid URL or tab not ready
      console.log('Tab update handling skipped:', error.message);
    }
  }
});

// Badge management
function updateBadge(tabId, count) {
  if (count > 0) {
    chrome.action.setBadgeText({
      text: count.toString(),
      tabId: tabId,
    });
    chrome.action.setBadgeBackgroundColor({
      color: count > 5 ? '#f44336' : '#ff9800', // Red for high count, orange for low
      tabId: tabId,
    });
  } else {
    chrome.action.setBadgeText({ text: '', tabId: tabId });
  }
}

// Export utilities for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    verifyContent,
    shouldShowNotification,
    CONFIG,
  };
}
