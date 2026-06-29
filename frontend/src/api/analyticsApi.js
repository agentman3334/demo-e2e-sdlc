import api from './axios';

export default {
  getDashboard: () => api.get('/api/analytics/dashboard'),
};