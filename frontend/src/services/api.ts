/// <reference types="vite/client" />
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://clinical-trial-matching-system-4.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a retry interceptor for cold starts
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    if (!response && config && !config.__isRetryRequest) {
      config.__isRetryRequest = true;
      console.warn('Backend might be starting up (cold start). Retrying in 3 seconds...');
      await new Promise((resolve) => setTimeout(resolve, 3000));
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
    const response = await api.post(`/trial/fetch_trials?condition=${encodeURIComponent(condition)}`);
    return response.data;
  },
};

export const matchingService = {
  matchPatient: async (patientId: number) => {
    const response = await api.get(`/match/${patientId}`);
    return response.data.matches;
  },
};

export default api;
