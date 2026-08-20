import axios from 'axios';
import { store } from '../store/store';
import { clearAuth } from '../store/slices/authSlice';

// Create axios instance
const apiClient = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach Firebase ID token
apiClient.interceptors.request.use(
  (config) => {
    // We get the token from Redux state
    const state = store.getState();
    const token = state.auth.user?.token;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 Unauthorized globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Dispatch logout action if unauthorized
      store.dispatch(clearAuth());
    }
    return Promise.reject(error);
  }
);

export default apiClient;
