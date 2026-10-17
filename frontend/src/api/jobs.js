import { api } from './client';

export const jobsApi = {
  async createJob(jobData) {
    return api.request('/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  },

  async listJobs(status = null) {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return api.request(`/jobs${query}`);
  },

  async getJob(jobId) {
    return api.request(`/jobs/${jobId}`);
  },

  async updateJob(jobId, jobData) {
    return api.request(`/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify(jobData),
    });
  },

  async deleteJob(jobId) {
    return api.request(`/jobs/${jobId}`, {
      method: 'DELETE',
    });
  },
};
