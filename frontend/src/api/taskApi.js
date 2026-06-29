import api from './axios';

export default {
  list: (params) => api.get('/api/tasks', { params }),
  create: (projectId, data) => api.post(`/api/tasks/projects/${projectId}/tasks`, data),
  get: (id) => api.get(`/api/tasks/${id}`),
  update: (id, data) => api.put(`/api/tasks/${id}`, data),
  updateStatus: (id, data) => api.patch(`/api/tasks/${id}/status`, data),
  delete: (id) => api.delete(`/api/tasks/${id}`),
};