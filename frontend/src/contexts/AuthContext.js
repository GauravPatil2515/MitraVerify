import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import axios from 'axios';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = 30000; // 30 seconds
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Auth context
const AuthContext = createContext();

// Auth action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  UPDATE_PROFILE: 'UPDATE_PROFILE',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
  REFRESH_TOKEN: 'REFRESH_TOKEN',
};

// Auth reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        loading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        loading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        loading: false,
        error: null,
        message: 'Registration successful! Please check your email to verify your account.',
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload,
        isAuthenticated: false,
        user: null,
        token: null,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
        error: null,
        message: null,
      };

    case AUTH_ACTIONS.UPDATE_PROFILE:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
        message: null,
      };

    case AUTH_ACTIONS.REFRESH_TOKEN:
      return {
        ...state,
        token: action.payload,
      };

    default:
      return state;
  }
};

// Initial auth state
const initialAuthState = {
  isAuthenticated: false,
  user: null,
  token: localStorage.getItem('token'),
  loading: false,
  error: null,
  message: null,
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);
  const queryClient = useQueryClient();

  // Setup axios interceptors
  useEffect(() => {
    // Request interceptor to add auth token
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        const token = state.token || localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle auth errors
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Try to refresh token
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              const response = await axios.post('/auth/refresh', {
                refresh_token: refreshToken,
              });

              const { access_token } = response.data;
              localStorage.setItem('token', access_token);
              dispatch({ type: AUTH_ACTIONS.REFRESH_TOKEN, payload: access_token });

              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return axios(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            logout();
          }
        }

        return Promise.reject(error);
      }
    );

    // Cleanup interceptors
    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [state.token]);

  // Check if user is already logged in on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (token && userData) {
      try {
        const user = JSON.parse(userData);
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user, token },
        });
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('refreshToken');
      }
    }
  }, []);

  // Login function
  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await axios.post('/login', credentials);
      const { user, access_token } = response.data;

      // Store tokens and user data
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user, token: access_token },
      });

      toast.success(`Welcome back, ${user.username}!`);
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed. Please try again.';
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.REGISTER_START });

    try {
      // Transform frontend data to match backend expectations
      const backendData = {
        username: userData.name,  // Backend expects 'username', frontend sends 'name'
        email: userData.email,
        password: userData.password,
        preferred_language: userData.language
      };

      const response = await axios.post('/register', backendData);
      
      dispatch({
        type: AUTH_ACTIONS.REGISTER_SUCCESS,
        payload: response.data,
      });

      toast.success('Registration successful! Please check your email to verify your account.');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed. Please try again.';
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: errorMessage,
      });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      // Call logout API to invalidate token on server
      await axios.post('/auth/logout');
    } catch (error) {
      console.error('Logout API error:', error);
    }

    // Clear local storage
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');

    // Clear React Query cache
    queryClient.clear();

    dispatch({ type: AUTH_ACTIONS.LOGOUT });
    toast.info('You have been logged out successfully.');
  };

  // Update profile function
  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/auth/profile', profileData);
      const updatedUser = response.data.user;

      // Update local storage
      localStorage.setItem('user', JSON.stringify(updatedUser));

      dispatch({
        type: AUTH_ACTIONS.UPDATE_PROFILE,
        payload: updatedUser,
      });

      toast.success('Profile updated successfully!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Profile update failed.';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Change password function
  const changePassword = async (passwordData) => {
    try {
      await axios.put('/auth/change-password', passwordData);
      toast.success('Password changed successfully!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Password change failed.';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Verify email function
  const verifyEmail = async (token) => {
    try {
      const response = await axios.post('/auth/verify-email', { token });
      toast.success('Email verified successfully!');
      return { success: true, data: response.data };
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Email verification failed.';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Forgot password function
  const forgotPassword = async (email) => {
    try {
      await axios.post('/auth/forgot-password', { email });
      toast.success('Password reset instructions sent to your email!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Failed to send reset email.';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Reset password function
  const resetPassword = async (token, newPassword) => {
    try {
      await axios.post('/auth/reset-password', { token, password: newPassword });
      toast.success('Password reset successfully!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Password reset failed.';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Check if user has permission
  const hasPermission = (permission) => {
    if (!state.user) return false;
    return state.user.permissions?.includes(permission) || state.user.role === 'admin';
  };

  // Check if user has role
  const hasRole = (role) => {
    if (!state.user) return false;
    return state.user.role === role;
  };

  // Get user stats query
  const {
    data: userStats,
    isLoading: statsLoading,
    refetch: refetchStats,
  } = useQuery(
    ['userStats', state.user?.id],
    () => axios.get('/auth/stats').then(res => res.data),
    {
      enabled: !!state.isAuthenticated && !!state.user,
      staleTime: 5 * 60 * 1000, // 5 minutes,
      retry: false, // Don't retry on error
    }
  );

  // Context value
  const value = {
    // State
    ...state,
    userStats,
    statsLoading,

    // Actions
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    verifyEmail,
    forgotPassword,
    resetPassword,
    clearError,
    refetchStats,

    // Utility functions
    hasPermission,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Higher-order component for protected routes
export const withAuth = (Component) => {
  return (props) => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}>
          <div className="loading-spinner large"></div>
        </div>
      );
    }

    if (!isAuthenticated) {
      // Redirect to login page
      window.location.href = '/login';
      return null;
    }

    return <Component {...props} />;
  };
};

// Hook for role-based access
export const useRoleGuard = (requiredRole) => {
  const { user, hasRole } = useAuth();
  return {
    hasAccess: hasRole(requiredRole),
    user,
  };
};

// Hook for permission-based access
export const usePermissionGuard = (requiredPermission) => {
  const { user, hasPermission } = useAuth();
  return {
    hasAccess: hasPermission(requiredPermission),
    user,
  };
};

export default AuthContext;
