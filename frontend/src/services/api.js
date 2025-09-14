// API service for MitraVerify frontend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Update token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  // Authentication
  async login(username, password) {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(userData) {
    return this.request('/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout() {
    this.setToken(null);
    return { success: true };
  }

  // Verification
  async verifyContent(data) {
    return this.request('/verify', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async analyzeImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    return this.request('/analyze-image', {
      method: 'POST',
      headers: {
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      },
      body: formData,
    });
  }

  async getHistory(page = 1, contentType = null) {
    const params = new URLSearchParams({ page: page.toString() });
    if (contentType) params.append('content_type', contentType);
    
    return this.request(`/history?${params.toString()}`);
  }

  // Education
  async getEducationModules(difficulty = 'all', language = 'en') {
    const params = new URLSearchParams({ difficulty, language });
    return this.request(`/education/modules?${params.toString()}`);
  }

  async trackProgress(progressData) {
    return this.request('/education/progress', {
      method: 'POST',
      body: JSON.stringify(progressData),
    });
  }

  // User stats
  async getUserStats() {
    return this.request('/auth/stats');
  }

  async getUserProfile() {
    return this.request('/auth/profile');
  }

  async updateProfile(profileData) {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }
}

const apiService = new ApiService();
export default apiService;
