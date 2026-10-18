import { api } from './client';

export const validationApi = {
  async validateResume(resumeId) {
    return api.request(`/tailored-resumes/${resumeId}/validate`, {
      method: 'POST',
    });
  },

  async getValidation(resumeId) {
    return api.request(`/tailored-resumes/${resumeId}/validation`);
  },
};
