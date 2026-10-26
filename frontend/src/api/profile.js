import { api } from './client';

export const profileApi = {
  // Candidate Profile
  async getProfile() {
    return api.request('/profile');
  },

  async updateProfile(profileData) {
    return api.request('/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },

  // Skills
  async addSkill(skillData) {
    return api.request('/profile/skills', {
      method: 'POST',
      body: JSON.stringify(skillData),
    });
  },

  async deleteSkill(skillId) {
    return api.request(`/profile/skills/${skillId}`, {
      method: 'DELETE',
    });
  },

  // Projects
  async addProject(projectData) {
    return api.request('/profile/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  },

  async updateProject(projectId, projectData) {
    return api.request(`/profile/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
  },

  async deleteProject(projectId) {
    return api.request(`/profile/projects/${projectId}`, {
      method: 'DELETE',
    });
  },

  async extractGitHubProject(github_url) {
    return api.request('/profile/projects/extract-github', {
      method: 'POST',
      body: JSON.stringify({ github_url }),
    });
  },

  // Experiences
  async addExperience(expData) {
    return api.request('/profile/experiences', {
      method: 'POST',
      body: JSON.stringify(expData),
    });
  },

  async updateExperience(expId, expData) {
    return api.request(`/profile/experiences/${expId}`, {
      method: 'PUT',
      body: JSON.stringify(expData),
    });
  },

  async deleteExperience(expId) {
    return api.request(`/profile/experiences/${expId}`, {
      method: 'DELETE',
    });
  },

  // Educations
  async addEducation(eduData) {
    return api.request('/profile/educations', {
      method: 'POST',
      body: JSON.stringify(eduData),
    });
  },

  async updateEducation(eduId, eduData) {
    return api.request(`/profile/educations/${eduId}`, {
      method: 'PUT',
      body: JSON.stringify(eduData),
    });
  },

  async deleteEducation(eduId) {
    return api.request(`/profile/educations/${eduId}`, {
      method: 'DELETE',
    });
  },

  // Certifications
  async addCertification(certData) {
    return api.request('/profile/certifications', {
      method: 'POST',
      body: JSON.stringify(certData),
    });
  },

  async updateCertification(certId, certData) {
    return api.request(`/profile/certifications/${certId}`, {
      method: 'PUT',
      body: JSON.stringify(certData),
    });
  },

  async deleteCertification(certId) {
    return api.request(`/profile/certifications/${certId}`, {
      method: 'DELETE',
    });
  },

  // Profile Section & All Reset
  async resetSection(section) {
    return api.request(`/profile/sections/${section}`, {
      method: 'DELETE',
    });
  },

  async resetAll() {
    return api.request('/profile/reset-all', {
      method: 'DELETE',
    });
  },

  // Master Resumes
  async getResumes() {
    return api.request('/resumes');
  },

  async uploadResume(file, replace = false) {
    const formData = new FormData();
    formData.append('file', file);

    const token = api.getToken();
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const url = replace ? `${api.baseUrl}/resumes?replace=true` : `${api.baseUrl}/resumes`;
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.detail || 'Failed to upload master resume');
    }
    return data;
  },

  async deleteResume(resumeId) {
    return api.request(`/resumes/${resumeId}`, {
      method: 'DELETE',
    });
  },

  async getResumeStatus(resumeId) {
    return api.request(`/resumes/${resumeId}/status`);
  },

  async getResumeExtractedData(resumeId) {
    return api.request(`/resumes/${resumeId}/extracted-data`);
  },

  async applyExtractedData(resumeId, { sections, overwrite_existing, edited_data, item_decisions } = {}) {
    return api.request(`/resumes/${resumeId}/apply-to-profile`, {
      method: 'POST',
      body: JSON.stringify({
        sections: sections || undefined,
        overwrite_existing: !!overwrite_existing,
        edited_data: edited_data || undefined,
        item_decisions: item_decisions || undefined,
      }),
    });
  },
};
