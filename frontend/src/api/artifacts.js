import { api } from './client';

export const artifactsApi = {
  async generatePdf(resumeId) {
    return api.request(`/tailored-resumes/${resumeId}/generate-pdf`, {
      method: 'POST',
    });
  },

  async getArtifacts(resumeId) {
    return api.request(`/tailored-resumes/${resumeId}/artifacts`);
  },

  getPdfUrl(resumeId) {
    return `${api.baseUrl}/tailored-resumes/${resumeId}/pdf`;
  },

  getTexUrl(resumeId) {
    return `${api.baseUrl}/tailored-resumes/${resumeId}/tex`;
  },
};
