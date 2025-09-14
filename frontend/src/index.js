import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { HelmetProvider } from 'react-helmet-async';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';

import App from './App';
import theme from './theme';
import { AuthProvider } from './contexts/AuthContext';
import { SettingsProvider } from './contexts/SettingsContext';
import reportWebVitals from './reportWebVitals';

import 'react-toastify/dist/ReactToastify.css';
import './index.css';

// Create a React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
      retryDelay: 1000,
    },
  },
});

// Error boundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log error to monitoring service
    console.error('Error boundary caught an error:', error, errorInfo);
    
    // You can also log the error to an error reporting service here
    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: error.toString(),
        fatal: false
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '50px',
          textAlign: 'center',
          fontFamily: 'Inter, sans-serif'
        }}>
          <h1 style={{ color: '#d32f2f', marginBottom: '20px' }}>
            Something went wrong
          </h1>
          <p style={{ color: '#666', marginBottom: '30px' }}>
            We're sorry for the inconvenience. Please try refreshing the page.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#1976d2',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Refresh Page
          </button>
          {process.env.NODE_ENV === 'development' && (
            <details style={{ marginTop: '30px', textAlign: 'left' }}>
              <summary>Error Details (Development)</summary>
              <pre style={{ 
                background: '#f5f5f5', 
                padding: '20px', 
                borderRadius: '8px',
                overflow: 'auto',
                marginTop: '10px'
              }}>
                {this.state.error && this.state.error.toString()}
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// Performance monitoring
const sendToAnalytics = (metric) => {
  // Send to Google Analytics
  if (window.gtag) {
    window.gtag('event', metric.name, {
      value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      event_category: 'Web Vitals',
      event_label: metric.id,
      non_interaction: true,
    });
  }
  
  // Send to custom analytics endpoint
  if (process.env.NODE_ENV === 'production') {
    fetch('/api/analytics/web-vitals', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metric),
    }).catch(console.error);
  }
};

// Check for service worker updates
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  navigator.serviceWorker.ready.then(registration => {
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // New content is available, show update notification
          if (window.confirm('New version available! Would you like to refresh?')) {
            window.location.reload();
          }
        }
      });
    });
  });
}

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <HelmetProvider>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <SettingsProvider>
                <AuthProvider>
                  <App />
                  <ToastContainer
                    position="top-right"
                    autoClose={5000}
                    hideProgressBar={false}
                    newestOnTop={false}
                    closeOnClick
                    rtl={false}
                    pauseOnFocusLoss
                    draggable
                    pauseOnHover
                    theme="light"
                    style={{ zIndex: 10000 }}
                  />
                </AuthProvider>
              </SettingsProvider>
            </ThemeProvider>
          </BrowserRouter>
          {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
        </QueryClientProvider>
      </HelmetProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

// Performance monitoring
reportWebVitals(sendToAnalytics);

// Register for push notifications (if supported)
if ('Notification' in window && 'serviceWorker' in navigator) {
  navigator.serviceWorker.ready.then(registration => {
    return registration.pushManager.getSubscription()
      .then(subscription => {
        if (!subscription) {
          // User is not subscribed, you can prompt them later
          console.log('Push notifications not subscribed');
        } else {
          console.log('Push notifications subscribed');
        }
      });
  });
}

// Add global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  if (window.gtag) {
    window.gtag('event', 'exception', {
      description: event.error?.toString() || 'Unknown error',
      fatal: false
    });
  }
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  if (window.gtag) {
    window.gtag('event', 'exception', {
      description: event.reason?.toString() || 'Unknown promise rejection',
      fatal: false
    });
  }
});

// Accessibility improvements
// Commenting out axe-core for now - can be added later
// if (process.env.NODE_ENV === 'development') {
//   import('@axe-core/react').then(axe => {
//     axe.default(React, ReactDOM, 1000);
//   });
// }
