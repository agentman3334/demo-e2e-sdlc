import api from './axios';

export default {
  getDashboard: () => api.get('/api/analytics/dashboard'),
  getProjectStats: (projectId) => api.get(`/api/analytics/project/${projectId}`),
};