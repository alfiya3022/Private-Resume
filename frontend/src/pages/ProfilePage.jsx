import React, { useState, useEffect } from 'react';
import {
  User,
  GraduationCap,
  Briefcase,
  FolderGit2,
  Wrench,
  Award,
  FileText,
  Upload,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  FileCheck,
} from 'lucide-react';
import { profileApi } from '../api/profile';

export default function ProfilePage({ currentUser }) {
  const [activeSection, setActiveSection] = useState('personal');
  const [profile, setProfile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState({ type: '', text: '' });

  // Form states for adding items
  const [personalForm, setPersonalForm] = useState({
    headline: '',
    summary: '',
    phone: '',
    location: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
  });

  const [newSkill, setNewSkill] = useState({ name: '', category: 'Technical', proficiency: 'Intermediate' });
  const [newProject, setNewProject] = useState({ title: '', role: '', description: '', technologies: '', bullets: '' });
  const [newExperience, setNewExperience] = useState({ company: '', title: '', location: '', description: '', bullets: '', is_current: false });
  const [newEducation, setNewEducation] = useState({ institution: '', degree: '', field_of_study: '', grade: '' });
  const [newCert, setNewCert] = useState({ name: '', issuer: '', issue_date: '' });

  useEffect(() => {
    if (currentUser) {
      loadProfileAndResumes();
    }
  }, [currentUser]);

  const loadProfileAndResumes = async () => {
    setLoading(true);
    try {
      const [profData, resumesData] = await Promise.all([
        profileApi.getProfile(),
        profileApi.getResumes(),
      ]);
      setProfile(profData);
      setResumes(resumesData);
      setPersonalForm({
        headline: profData.headline || '',
        summary: profData.summary || '',
        phone: profData.phone || '',
        location: profData.location || '',
        linkedin_url: profData.linkedin_url || '',
        github_url: profData.github_url || '',
        portfolio_url: profData.portfolio_url || '',
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to load profile data.' });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePersonal = async (e) => {
    e.preventDefault();
    try {
      const updated = await profileApi.updateProfile(personalForm);
      setProfile(updated);
      setFeedbackMsg({ type: 'success', text: 'Personal info saved successfully.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to save personal info.' });
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkill.name.trim()) return;
    try {
      await profileApi.addSkill(newSkill);
      setNewSkill({ name: '', category: 'Technical', proficiency: 'Intermediate' });
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Skill added to profile.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add skill.' });
    }
  };

  const handleDeleteSkill = async (id) => {
    try {
      await profileApi.deleteSkill(id);
      await loadProfileAndResumes();
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete skill.' });
    }
  };

  const handleAddProject = async (e) => {
    e.preventDefault();
    if (!newProject.title.trim()) return;
    try {
      const payload = {
        title: newProject.title,
        role: newProject.role,
        description: newProject.description,
        technologies: newProject.technologies ? newProject.technologies.split(',').map((s) => s.trim()) : [],
        bullets: newProject.bullets ? newProject.bullets.split('\n').filter(Boolean) : [],
      };
      await profileApi.addProject(payload);
      setNewProject({ title: '', role: '', description: '', technologies: '', bullets: '' });
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Project added to profile.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add project.' });
    }
  };

  const handleDeleteProject = async (id) => {
    try {
      await profileApi.deleteProject(id);
      await loadProfileAndResumes();
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete project.' });
    }
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setFeedbackMsg({ type: '', text: '' });
    try {
      const result = await profileApi.uploadResume(file);
      setFeedbackMsg({
        type: 'success',
        text: `Parsed "${result.filename}" with PyMuPDF. ${result.extracted_skills.length} skills added to profile!`,
      });
      await loadProfileAndResumes();
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to upload resume.' });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDeleteResume = async (id) => {
    try {
      await profileApi.deleteResume(id);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Master resume removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete resume.' });
    }
  };

  const sections = [
    { id: 'personal', label: 'Personal Info', icon: User, count: null },
    { id: 'skills', label: 'Skills', icon: Wrench, count: profile?.skills?.length },
    { id: 'projects', label: 'Projects', icon: FolderGit2, count: profile?.projects?.length },
    { id: 'experience', label: 'Experience', icon: Briefcase, count: profile?.experiences?.length },
    { id: 'education', label: 'Education', icon: GraduationCap, count: profile?.educations?.length },
    { id: 'certifications', label: 'Certifications', icon: Award, count: profile?.certifications?.length },
    { id: 'template', label: 'LaTeX Template', icon: FileText, count: null },
  ];

  if (!currentUser) {
    return (
      <div className="card-brutal text-center py-12 space-y-4">
        <AlertCircle className="w-12 h-12 text-coral mx-auto" />
        <h2 className="text-xl font-bold text-charcoal">Authentication Required</h2>
        <p className="text-sm text-charcoal-muted max-w-md mx-auto">
          Please sign in or create an account in the Auth tab to access and edit your candidate master profile.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Master Resume Parsing Banner */}
      <div className="bg-white border-2 border-charcoal p-6 shadow-brutal space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-charcoal flex items-center space-x-2">
              <FileCheck className="w-5 h-5 text-coral" />
              <span>Master Resume PDF Parser (PyMuPDF)</span>
            </h2>
            <p className="text-xs text-charcoal-muted mt-1">
              Upload your existing PDF resume. Text and skills are extracted locally without sending data to external APIs.
            </p>
          </div>

          <label className="btn-primary cursor-pointer flex items-center space-x-2">
            <Upload className="w-4 h-4" />
            <span>{uploading ? 'Parsing PDF...' : 'Upload Master PDF'}</span>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleResumeUpload}
              disabled={uploading}
            />
          </label>
        </div>

        {/* Uploaded Resumes List */}
        {resumes.length > 0 && (
          <div className="border-t border-cream-border pt-4">
            <div className="text-xs font-mono font-bold text-charcoal-muted uppercase mb-2">
              Parsed Source Resumes:
            </div>
            <div className="space-y-2">
              {resumes.map((r) => (
                <div
                  key={r.id}
                  className="flex items-center justify-between p-3 bg-cream border border-charcoal text-xs font-mono"
                >
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-coral" />
                    <span className="font-semibold text-charcoal">{r.filename}</span>
                    <span className="text-charcoal-muted">({Math.round(r.file_size / 1024)} KB)</span>
                    <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600">Active</span>
                  </div>
                  <button
                    onClick={() => handleDeleteResume(r.id)}
                    className="text-rose-600 hover:text-rose-800 p-1"
                    title="Remove Resume"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {feedbackMsg.text && (
          <div
            className={`p-3 text-xs font-mono border-2 ${
              feedbackMsg.type === 'success'
                ? 'bg-emerald-50 border-emerald-500 text-emerald-900'
                : 'bg-rose-50 border-rose-500 text-rose-900'
            }`}
          >
            {feedbackMsg.text}
          </div>
        )}
      </div>

      {/* Main Profile Tabs & Editor */}
      <div className="card-brutal space-y-6">
        <div className="border-b border-cream-border pb-4">
          <h2 className="text-xl font-bold tracking-tight text-charcoal">
            Candidate Evidence & Source of Truth
          </h2>
          <p className="text-sm text-charcoal-muted mt-1">
            Structured candidate source of truth. All tailored resumes draw evidence from this profile without inventing qualifications.
          </p>
        </div>

        {/* Section Tabs */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 border-b border-cream-border pb-4">
          {sections.map((sec) => {
            const Icon = sec.icon;
            const isCurrent = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => setActiveSection(sec.id)}
                className={`p-2.5 text-xs font-medium border flex flex-col items-center justify-center space-y-1.5 transition-all text-center ${
                  isCurrent
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="truncate w-full">{sec.label}</span>
                {sec.count !== null && sec.count !== undefined && (
                  <span className="text-[10px] font-mono opacity-80">({sec.count})</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab 1: Personal Info */}
        {activeSection === 'personal' && (
          <form onSubmit={handleUpdatePersonal} className="space-y-4 max-w-2xl bg-cream p-6 border-2 border-charcoal">
            <h3 className="font-bold text-sm uppercase tracking-wider text-charcoal">
              Candidate Overview
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Headline / Role</label>
                <input
                  type="text"
                  value={personalForm.headline}
                  onChange={(e) => setPersonalForm({ ...personalForm, headline: e.target.value })}
                  placeholder="e.g. Senior Full-Stack Engineer"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>
              <div>
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Location</label>
                <input
                  type="text"
                  value={personalForm.location}
                  onChange={(e) => setPersonalForm({ ...personalForm, location: e.target.value })}
                  placeholder="e.g. San Francisco, CA (or Remote)"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Professional Summary</label>
              <textarea
                rows={4}
                value={personalForm.summary}
                onChange={(e) => setPersonalForm({ ...personalForm, summary: e.target.value })}
                placeholder="High-level factual summary of candidate career and competencies..."
                className="w-full border-2 border-charcoal p-2 text-sm bg-white font-sans"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Phone</label>
                <input
                  type="text"
                  value={personalForm.phone}
                  onChange={(e) => setPersonalForm({ ...personalForm, phone: e.target.value })}
                  placeholder="+1 (555) 000-0000"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>
              <div>
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">LinkedIn URL</label>
                <input
                  type="url"
                  value={personalForm.linkedin_url}
                  onChange={(e) => setPersonalForm({ ...personalForm, linkedin_url: e.target.value })}
                  placeholder="https://linkedin.com/in/..."
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>
              <div>
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">GitHub URL</label>
                <input
                  type="url"
                  value={personalForm.github_url}
                  onChange={(e) => setPersonalForm({ ...personalForm, github_url: e.target.value })}
                  placeholder="https://github.com/..."
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button type="submit" className="btn-primary">
                Save Personal Details
              </button>
            </div>
          </form>
        )}

        {/* Tab 2: Skills */}
        {activeSection === 'skills' && (
          <div className="space-y-6">
            <form onSubmit={handleAddSkill} className="bg-cream p-4 border-2 border-charcoal flex flex-col sm:flex-row gap-3 items-end">
              <div className="flex-1 w-full">
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Skill Name</label>
                <input
                  type="text"
                  value={newSkill.name}
                  onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
                  placeholder="e.g. Python, Docker, PostgreSQL"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  required
                />
              </div>
              <div className="w-full sm:w-48">
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Category</label>
                <select
                  value={newSkill.category}
                  onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value })}
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                >
                  <option value="Language">Language</option>
                  <option value="Framework">Framework</option>
                  <option value="Database">Database</option>
                  <option value="Tool">Tool / DevOps</option>
                  <option value="Cloud">Cloud</option>
                  <option value="Technical">Technical</option>
                </select>
              </div>
              <button type="submit" className="btn-primary flex items-center space-x-1 whitespace-nowrap">
                <Plus className="w-4 h-4" />
                <span>Add Skill</span>
              </button>
            </form>

            <div className="border-2 border-charcoal p-4 bg-white">
              <h4 className="text-xs font-mono uppercase font-bold text-charcoal-muted mb-3">
                Verified Candidate Skills ({profile?.skills?.length || 0})
              </h4>
              <div className="flex flex-wrap gap-2">
                {profile?.skills?.map((s) => (
                  <span
                    key={s.id}
                    className="inline-flex items-center space-x-2 px-3 py-1 bg-cream border border-charcoal text-xs font-mono"
                  >
                    <span className="font-semibold text-charcoal">{s.name}</span>
                    <span className="text-charcoal-muted text-[10px]">({s.category || 'Skill'})</span>
                    <button
                      onClick={() => handleDeleteSkill(s.id)}
                      className="text-rose-600 hover:text-rose-800 ml-1"
                    >
                      ×
                    </button>
                  </span>
                ))}
                {(!profile?.skills || profile.skills.length === 0) && (
                  <p className="text-xs text-charcoal-muted">No skills recorded yet. Upload a PDF resume above or add skills manually.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Projects */}
        {activeSection === 'projects' && (
          <div className="space-y-6">
            <form onSubmit={handleAddProject} className="bg-cream p-4 border-2 border-charcoal space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal">Add Project Evidence</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  type="text"
                  value={newProject.title}
                  onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                  placeholder="Project Title (e.g. PrivateResume)"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  required
                />
                <input
                  type="text"
                  value={newProject.technologies}
                  onChange={(e) => setNewProject({ ...newProject, technologies: e.target.value })}
                  placeholder="Tech Stack comma-separated (e.g. Python, FastAPI, Docker)"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>
              <textarea
                rows={2}
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                placeholder="High-level description of what the project accomplished..."
                className="w-full border-2 border-charcoal p-2 text-sm bg-white"
              />
              <textarea
                rows={2}
                value={newProject.bullets}
                onChange={(e) => setNewProject({ ...newProject, bullets: e.target.value })}
                placeholder="Accomplishment bullet points (one per line)..."
                className="w-full border-2 border-charcoal p-2 text-sm bg-white"
              />
              <button type="submit" className="btn-primary flex items-center space-x-1">
                <Plus className="w-4 h-4" />
                <span>Add Project</span>
              </button>
            </form>

            <div className="space-y-3">
              {profile?.projects?.map((proj) => (
                <div key={proj.id} className="border-2 border-charcoal p-4 bg-white flex justify-between items-start">
                  <div>
                    <h5 className="font-bold text-sm text-charcoal">{proj.title}</h5>
                    {proj.description && <p className="text-xs text-charcoal-muted mt-1">{proj.description}</p>}
                    <div className="flex flex-wrap gap-1 mt-2">
                      {proj.technologies?.map((tech, i) => (
                        <span key={i} className="badge-tag bg-cream">{tech}</span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteProject(proj.id)}
                    className="text-rose-600 hover:text-rose-800 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 7: Resume Template (LaTeX) */}
        {activeSection === 'template' && (
          <div className="bg-cream border-2 border-charcoal p-6 space-y-4 font-mono text-xs">
            <h3 className="font-bold text-sm text-charcoal uppercase">LaTeX Template Package Manager</h3>
            <p className="text-charcoal-muted">
              PrivateResume uses candidate LaTeX ZIP packages containing <code className="bg-white px-1">main.tex</code>, section templates, and custom fonts/styling to deterministically render PDFs.
            </p>
            <div className="p-4 bg-white border border-charcoal space-y-2">
              <div className="flex justify-between">
                <span className="text-charcoal-muted">Default Template:</span>
                <span className="font-bold text-emerald-800">Modern Editorial (main.tex)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-charcoal-muted">Compiler Engine:</span>
                <span className="font-bold text-charcoal">pdflatex (Local Host / Docker)</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button className="btn-secondary">Upload Custom ZIP Package</button>
              <button className="btn-primary">Download Sample Template</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
