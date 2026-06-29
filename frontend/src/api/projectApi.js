import api from './axios';

export default {
  list: (params) => api.get('/api/projects', { params }),
  create: (data) => api.post('/api/projects', data),
  get: (id) => api.get(`/api/projects/${id}`),
  update: (id, data) => api.put(`/api/projects/${id}`, data),
  delete: (id) => api.delete(`/api/projects/${id}`),
  addMember: (projectId, data) => api.post(`/api/projects/${projectId}/members`, data),
  removeMember: (projectId, userId) => api.delete(`/api/projects/${projectId}/members/${userId}`),
};