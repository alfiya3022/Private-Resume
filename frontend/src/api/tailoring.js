import { api } from './client';

export const tailoringApi = {
  async tailorResumeForJob(jobId) {
    return api.request(`/jobs/${jobId}/tailor`, {
      method: 'POST',
    });
  },

  async getJobTailoredResumes(jobId) {
    return api.request(`/jobs/${jobId}/tailored-resumes`);
  },

  async getTailoredResume(resumeId) {
    return api.request(`/tailored-resumes/${resumeId}`);
  },

  async updateTailoredResume(resumeId, payload) {
    return api.request(`/tailored-resumes/${resumeId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  async askAIEdit(resumeId, request) {
    return api.request(`/tailored-resumes/${resumeId}/edit`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async finalizeTailoredResume(resumeId) {
    return api.request(`/tailored-resumes/${resumeId}/finalize`, {
      method: 'POST',
    });
  },
};
