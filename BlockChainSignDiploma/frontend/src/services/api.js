import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only redirect to login if 401 AND request was NOT to /login endpoint
    if (error.response?.status === 401 && !error.config.url.includes('/auth/login')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/api/v1/auth/register', data),
  login: (data) => api.post('/api/v1/auth/login', data),
};

// Crypto APIs
export const cryptoAPI = {
  generateKeypair: () => api.post('/api/v1/crypto/generate-keypair'),
  signFile: (formData) => {
    return api.post('/api/v1/crypto/sign-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  verifySignature: (formData) => {
    return api.post('/api/v1/crypto/verify-signature', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// CSR APIs
export const csrAPI = {
  submit: (formData) => {
    return api.post('/api/v1/school/csr/submit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getStatus: () => api.get('/api/v1/school/csr/status'),
};

// Ministry APIs
export const ministryAPI = {
  listCSR: (statusFilter) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    return api.get('/api/v1/ministry/csr/list', { params });
  },
  getCSRDetail: (csrId) => api.get(`/api/v1/ministry/csr/${csrId}`),
  approveCSR: (csrId, data) => api.post(`/api/v1/ministry/csr/${csrId}/approve`, data),
  rejectCSR: (csrId, data) => api.post(`/api/v1/ministry/csr/${csrId}/reject`, data),
  listSchools: () => api.get('/api/v1/ministry/schools'),
  revokeSchool: (schoolId, reason) => api.post(`/api/v1/ministry/schools/${schoolId}/revoke`, { reason }),
};

// School APIs
export const schoolAPI = {
  pushToFabric: (formData) => {
    return api.post('/api/v1/school/push-to-fabric', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getDiplomas: (limit = 20, offset = 0) => {
    return api.get('/api/v1/school/diplomas', { params: { limit, offset } });
  },
  revokeDiploma: (formData) => {
    return api.post('/api/v1/school/diplomas/revoke', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Verify APIs
export const verifyAPI = {
  verifyByFile: (formData) => {
    return api.post('/api/v1/verify/diploma', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  verifyByHash: (fileHash) => api.get(`/api/v1/verify/diploma/${fileHash}`),
};

export default api;
