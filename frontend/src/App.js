import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Box, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';

import { useAuth } from './contexts/AuthContext';
import { useSettings } from './contexts/SettingsContext';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import LoadingScreen from './components/common/LoadingScreen';
import ErrorBoundary from './components/common/ErrorBoundary';

// Lazy load components for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const VerifyPage = lazy(() => import('./pages/VerifyPage'));
const LearnPage = lazy(() => import('./pages/LearnPage'));
const HistoryPage = lazy(() => import('./pages/HistoryPage'));
const VerificationInterface = lazy(() => import('./components/verification/VerificationInterface'));
const EducationalDashboard = lazy(() => import('./components/education/EducationalDashboard'));
const ResultsDisplay = lazy(() => import('./components/verification/ResultsDisplay'));
const ProgressTracker = lazy(() => import('./components/education/ProgressTracker'));
const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));
const HelpPage = lazy(() => import('./pages/HelpPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Public route wrapper (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

// Loading fallback component
const PageLoader = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="400px"
    flexDirection="column"
    gap={2}
  >
    <CircularProgress size={40} />
    <Box sx={{ color: 'text.secondary', fontSize: '0.875rem' }}>
      Loading...
    </Box>
  </Box>
);

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  in: {
    opacity: 1,
    y: 0,
  },
  out: {
    opacity: 0,
    y: -20,
  },
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.4,
};

// Animated page wrapper
const AnimatedPage = ({ children }) => {
  const { animationsEnabled } = useSettings();
  
  if (!animationsEnabled) {
    return <>{children}</>;
  }
  
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
    >
      {children}
    </motion.div>
  );
};

function App() {
  const { settings, isDarkMode } = useSettings();
  const { isAuthenticated } = useAuth();

  return (
    <ErrorBoundary>
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.default',
          color: 'text.primary',
        }}
      >
        {/* SEO Meta Tags */}
        <Helmet>
          <title>MitraVerify - AI-Powered Misinformation Detection</title>
          <meta
            name="description"
            content="Verify news, images, and social media content instantly with AI-powered fact-checking technology designed for Indian users."
          />
          <meta name="theme-color" content={isDarkMode ? '#121212' : '#1976d2'} />
          <meta name="robots" content="index,follow" />
          <meta name="language" content={settings.language} />
          <meta name="geo.region" content={settings.region} />
          
          {/* Open Graph */}
          <meta property="og:title" content="MitraVerify - AI-Powered Misinformation Detection" />
          <meta property="og:description" content="Verify news, images, and social media content instantly with AI-powered fact-checking technology." />
          <meta property="og:type" content="website" />
          <meta property="og:url" content="https://mitraverify.vercel.app" />
          <meta property="og:image" content="/og-image.png" />
          
          {/* Twitter Card */}
          <meta name="twitter:card" content="summary_large_image" />
          <meta name="twitter:title" content="MitraVerify - AI-Powered Misinformation Detection" />
          <meta name="twitter:description" content="Verify news, images, and social media content instantly with AI-powered fact-checking technology." />
          <meta name="twitter:image" content="/twitter-image.png" />
          
          {/* Preload critical resources */}
          <link rel="preload" href="/fonts/Inter-Regular.woff2" as="font" type="font/woff2" crossOrigin="" />
          <link rel="preload" href="/fonts/Poppins-SemiBold.woff2" as="font" type="font/woff2" crossOrigin="" />
          
          {/* Structured Data */}
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              "name": "MitraVerify",
              "description": "AI-powered misinformation detection and education platform",
              "url": "https://mitraverify.vercel.app",
              "applicationCategory": "EducationalApplication",
              "operatingSystem": "Any",
              "browserRequirements": "Requires JavaScript",
              "author": {
                "@type": "Organization",
                "name": "MitraVerify Team"
              },
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "INR"
              }
            })}
          </script>
        </Helmet>

        {/* Navigation Bar */}
        <Navbar />

        {/* Main Content */}
        <Box component="main" sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public Routes */}
              <Route
                path="/"
                element={
                  <AnimatedPage>
                    <HomePage />
                  </AnimatedPage>
                }
              />
              
              <Route
                path="/about"
                element={
                  <AnimatedPage>
                    <AboutPage />
                  </AnimatedPage>
                }
              />
              
              <Route
                path="/contact"
                element={
                  <AnimatedPage>
                    <ContactPage />
                  </AnimatedPage>
                }
              />
              
              <Route
                path="/privacy"
                element={
                  <AnimatedPage>
                    <PrivacyPage />
                  </AnimatedPage>
                }
              />
              
              <Route
                path="/terms"
                element={
                  <AnimatedPage>
                    <TermsPage />
                  </AnimatedPage>
                }
              />
              
              <Route
                path="/help"
                element={
                  <AnimatedPage>
                    <HelpPage />
                  </AnimatedPage>
                }
              />

              {/* Authentication Routes */}
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <AnimatedPage>
                      <LoginPage />
                    </AnimatedPage>
                  </PublicRoute>
                }
              />
              
              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <AnimatedPage>
                      <RegisterPage />
                    </AnimatedPage>
                  </PublicRoute>
                }
              />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <DashboardPage />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/verify"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <VerifyPage />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/learn"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <LearnPage />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/history"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <HistoryPage />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              {/* Legacy routes for backwards compatibility */}
              <Route
                path="/verification"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <VerificationInterface />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/education"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <EducationalDashboard />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/education/progress"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <ProgressTracker />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/results/:id"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <ResultsDisplay />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <ProfilePage />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/settings"
                element={
                  <ProtectedRoute>
                    <AnimatedPage>
                      <SettingsPage />
                    </AnimatedPage>
                  </ProtectedRoute>
                }
              />

              {/* Catch-all route */}
              <Route
                path="*"
                element={
                  <AnimatedPage>
                    <NotFoundPage />
                  </AnimatedPage>
                }
              />
            </Routes>
          </Suspense>
        </Box>

        {/* Footer */}
        <Footer />
      </Box>
    </ErrorBoundary>
  );
}

export default App;
