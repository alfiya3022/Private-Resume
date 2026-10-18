import { api } from './client';

export const applicationsApi = {
  async getApplications(status) {
    const url = status ? `/applications?status=${encodeURIComponent(status)}` : '/applications';
    return api.request(url);
  },

  async getApplication(id) {
    return api.request(`/applications/${id}`);
  },

  async createApplication(data) {
    return api.request('/applications', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateApplication(id, data) {
    return api.request(`/applications/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async deleteApplication(id) {
    return api.request(`/applications/${id}`, {
      method: 'DELETE',
    });
  },
};
