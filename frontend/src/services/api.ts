/// <reference types="vite/client" />
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://clinical-trial-matching-system-4.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds default
});

// Add a retry interceptor for cold starts
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config } = error;
    // Retry on timeout or 503 Service Unavailable (common during Render cold starts)
    if (config && !config.__isRetryRequest && (error.code === 'ECONNABORTED' || error.response?.status === 503)) {
      config.__isRetryRequest = true;
      console.warn('Backend is busy or starting up. Retrying in 5 seconds...');
      await new Promise((resolve) => setTimeout(resolve, 5000));
      return api(config);
    }
    return Promise.reject(error);
  }
);

export const patientService = {
  getPatients: async () => {
    const response = await api.get('/patient/');
    return response.data;
  },
  createPatient: async (data: any) => {
    const response = await api.post('/patient/', data);
    return response.data;
  },
  parseDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/patient/parse_document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // Allow 1 minute for document parsing
    });
    return response.data;
  },
};

export const trialService = {
  getTrials: async () => {
    const response = await api.get('/trial/');
    return response.data;
  },
  syncTrials: async (condition: string = 'cancer') => {
    const response = await api.post(`/trial/fetch_trials?condition=${encodeURIComponent(condition)}`, {}, {
      timeout: 120000, // Allow 2 minutes for API sync
    });
    return response.data;
  },
};

export const matchingService = {
  matchPatient: async (patientId: number) => {
    // Extensive timeout for AI matching to handle model loading
    const response = await api.get(`/match/${patientId}`, {
      timeout: 120000, // 120 seconds (2 minutes)
    });
    return response.data.matches;
  },
};

export default api;
