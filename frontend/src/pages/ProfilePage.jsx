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
  Edit3,
  Save,
  X,
  ExternalLink,
  Sparkles,
  Link as LinkIcon,
} from 'lucide-react';
import { profileApi } from '../api/profile';

const COUNTRY_CODES = [
  { code: '+91', label: 'IN (+91)' },
  { code: '+1', label: 'US/CA (+1)' },
  { code: '+44', label: 'UK (+44)' },
  { code: '+61', label: 'AU (+61)' },
  { code: '+49', label: 'DE (+49)' },
  { code: '+33', label: 'FR (+33)' },
  { code: '+65', label: 'SG (+65)' },
  { code: '+971', label: 'UAE (+971)' },
  { code: '+81', label: 'JP (+81)' },
];

export default function ProfilePage({ currentUser }) {
  const [activeSection, setActiveSection] = useState('personal');
  const [profile, setProfile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState({ type: '', text: '' });
  const [validationPopup, setValidationPopup] = useState(null);

  // Personal Info state
  const [isEditingPersonal, setIsEditingPersonal] = useState(false);
  const [phoneCountryCode, setPhoneCountryCode] = useState('+91');
  const [phoneDigits, setPhoneDigits] = useState('');
  const [personalForm, setPersonalForm] = useState({
    headline: '',
    summary: '',
    phone: '',
    location: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
  });

  // Skills state
  const [newSkill, setNewSkill] = useState({ name: '', category: '', proficiency: 'Intermediate' });

  // Projects state
  const [projectMode, setProjectMode] = useState('github'); // 'github' | 'manual'
  const [githubProjectUrl, setGithubProjectUrl] = useState('');
  const [extractingProject, setExtractingProject] = useState(false);
  const [extractedProject, setExtractedProject] = useState(null);
  const [newProject, setNewProject] = useState({
    title: '',
    role: '',
    description: '',
    technologies: '',
    bullets: '',
    url: '',
  });

  // Experience state
  const [experienceMode, setExperienceMode] = useState('manual'); // 'manual' | 'github'
  const [githubExpUrl, setGithubExpUrl] = useState('');
  const [extractingExp, setExtractingExp] = useState(false);
  const [newExperience, setNewExperience] = useState({
    company: '',
    title: '',
    location: '',
    description: '',
    bullets: '',
    start_date: '',
    end_date: '',
    is_current: false,
  });

  // Editing existing project state
  const [editingProjectId, setEditingProjectId] = useState(null);
  const [editProjectForm, setEditProjectForm] = useState({
    title: '',
    role: '',
    technologies: '',
    url: '',
    description: '',
    bullets: '',
  });

  // Editing existing experience state
  const [editingExpId, setEditingExpId] = useState(null);
  const [editExpForm, setEditExpForm] = useState({
    company: '',
    title: '',
    location: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
    bullets: '',
  });

  // Custom template packages state
  const [templateInfo, setTemplateInfo] = useState(null);
  const [uploadingTemplate, setUploadingTemplate] = useState(false);

  // Education & Certification state
  const [newEducation, setNewEducation] = useState({ institution: '', degree: '', field_of_study: '', grade: '' });
  const [editingEduId, setEditingEduId] = useState(null);
  const [editEduForm, setEditEduForm] = useState({
    institution: '',
    degree: '',
    field_of_study: '',
    grade: '',
    start_date: '',
    end_date: '',
  });

  const [newCert, setNewCert] = useState({ name: '', issuer: '', issue_date: '' });
  const [editingCertId, setEditingCertId] = useState(null);
  const [editCertForm, setEditCertForm] = useState({
    name: '',
    issuer: '',
    issue_date: '',
    credential_url: '',
  });

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

      // Parse phone into country code and number
      if (profData.phone) {
        const matched = COUNTRY_CODES.find((c) => profData.phone.startsWith(c.code));
        if (matched) {
          setPhoneCountryCode(matched.code);
          setPhoneDigits(profData.phone.slice(matched.code.length).trim());
        } else {
          setPhoneCountryCode('+91');
          setPhoneDigits(profData.phone.trim());
        }
      } else {
        setPhoneCountryCode('+91');
        setPhoneDigits('');
      }

      // If personal info has no fields filled, start in edit mode
      if (!profData.headline && !profData.summary && !profData.location && !profData.phone) {
        setIsEditingPersonal(true);
      }

      // Load active custom template info
      try {
        const tpl = await profileApi.getTemplate();
        setTemplateInfo(tpl);
      } catch (e) {}
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to load profile data.' });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePersonal = async (e) => {
    e.preventDefault();
    try {
      const fullPhone = phoneDigits.trim() ? `${phoneCountryCode} ${phoneDigits.trim()}` : '';
      const payload = { ...personalForm, phone: fullPhone };
      const updated = await profileApi.updateProfile(payload);
      setProfile(updated);
      setIsEditingPersonal(false);
      setFeedbackMsg({ type: 'success', text: 'Personal info saved successfully.' });
      setValidationPopup({
        title: 'Personal Info Saved',
        message: 'Your personal information and contact details have been successfully saved.',
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to save personal info.' });
    }
  };

  const handleCancelPersonalEdit = () => {
    if (profile) {
      setPersonalForm({
        headline: profile.headline || '',
        summary: profile.summary || '',
        phone: profile.phone || '',
        location: profile.location || '',
        linkedin_url: profile.linkedin_url || '',
        github_url: profile.github_url || '',
        portfolio_url: profile.portfolio_url || '',
      });
      if (profile.phone) {
        const matched = COUNTRY_CODES.find((c) => profile.phone.startsWith(c.code));
        if (matched) {
          setPhoneCountryCode(matched.code);
          setPhoneDigits(profile.phone.slice(matched.code.length).trim());
        } else {
          setPhoneCountryCode('+91');
          setPhoneDigits(profile.phone.trim());
        }
      } else {
        setPhoneDigits('');
      }
    }
    setIsEditingPersonal(false);
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkill.name.trim()) {
      setFeedbackMsg({ type: 'error', text: 'Please enter a skill name.' });
      return;
    }
    if (!newSkill.category) {
      setFeedbackMsg({ type: 'error', text: 'Please select a skill category from the dropdown.' });
      return;
    }
    try {
      const added = await profileApi.addSkill(newSkill);
      const skillName = added.name;
      const skillCat = added.category || 'Technical';
      setNewSkill({ name: '', category: '', proficiency: 'Intermediate' });
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: `Successfully added "${skillName}"!` });
      setValidationPopup({
        title: 'Skill Successfully Added',
        message: `"${skillName}" was added under ${skillCat} in your candidate profile.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add skill.' });
    }
  };

  const handleDeleteSkill = async (id) => {
    try {
      await profileApi.deleteSkill(id);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Skill removed from profile.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete skill.' });
    }
  };

  // GitHub extraction for Projects
  const handleExtractGitHubProject = async (e) => {
    e.preventDefault();
    if (!githubProjectUrl.trim()) {
      setFeedbackMsg({ type: 'error', text: 'Please enter a valid GitHub repository URL.' });
      return;
    }
    setExtractingProject(true);
    setFeedbackMsg({ type: '', text: '' });
    try {
      const data = await profileApi.extractGitHubProject(githubProjectUrl.trim());
      setExtractedProject({
        title: data.title || '',
        role: data.role || 'Creator / Maintainer',
        description: data.description || '',
        technologies: (data.technologies || []).join(', '),
        bullets: (data.bullets || []).join('\n'),
        url: data.url || githubProjectUrl.trim(),
      });
      setValidationPopup({
        title: 'GitHub Data Extracted',
        message: `Extracted project "${data.title}" from GitHub repository. You can review or edit accomplishments before saving.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to extract GitHub repository details.' });
    } finally {
      setExtractingProject(false);
    }
  };

  const handleSaveExtractedProject = async (e) => {
    e.preventDefault();
    if (!extractedProject?.title.trim()) return;
    try {
      const payload = {
        title: extractedProject.title.trim(),
        role: extractedProject.role || 'Creator / Maintainer',
        description: extractedProject.description || '',
        technologies: extractedProject.technologies
          ? extractedProject.technologies.split(',').map((s) => s.trim()).filter(Boolean)
          : [],
        bullets: extractedProject.bullets
          ? extractedProject.bullets.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        url: extractedProject.url || githubProjectUrl.trim(),
      };
      await profileApi.addProject(payload);
      setExtractedProject(null);
      setGithubProjectUrl('');
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'GitHub project added to profile!' });
      setValidationPopup({
        title: 'Project Successfully Added',
        message: `Project "${payload.title}" has been added to your candidate profile.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to save project.' });
    }
  };

  const handleAddManualProject = async (e) => {
    e.preventDefault();
    if (!newProject.title.trim()) return;
    try {
      const payload = {
        title: newProject.title.trim(),
        role: newProject.role || 'Developer',
        description: newProject.description || '',
        technologies: newProject.technologies
          ? newProject.technologies.split(',').map((s) => s.trim()).filter(Boolean)
          : [],
        bullets: newProject.bullets
          ? newProject.bullets.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        url: newProject.url || '',
      };
      await profileApi.addProject(payload);
      setNewProject({ title: '', role: '', description: '', technologies: '', bullets: '', url: '' });
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Project added to profile.' });
      setValidationPopup({
        title: 'Project Successfully Added',
        message: `Project "${payload.title}" has been added to your candidate profile.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add project.' });
    }
  };

  const handleDeleteProject = async (id) => {
    try {
      await profileApi.deleteProject(id);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Project removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete project.' });
    }
  };

  const handleStartEditProject = (proj) => {
    setEditingProjectId(proj.id);
    setEditProjectForm({
      title: proj.title || '',
      role: proj.role || '',
      technologies: (proj.technologies || []).join(', '),
      url: proj.url || '',
      description: proj.description || '',
      bullets: (proj.bullets || []).join('\n'),
    });
  };

  const handleSaveEditProject = async (e) => {
    e.preventDefault();
    if (!editProjectForm.title.trim()) return;
    try {
      const payload = {
        title: editProjectForm.title.trim(),
        role: editProjectForm.role.trim() || null,
        technologies: editProjectForm.technologies
          ? editProjectForm.technologies.split(',').map((s) => s.trim()).filter(Boolean)
          : [],
        description: editProjectForm.description.trim(),
        bullets: editProjectForm.bullets
          ? editProjectForm.bullets.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        url: editProjectForm.url.trim() || null,
      };
      await profileApi.updateProject(editingProjectId, payload);
      setEditingProjectId(null);
      await loadProfileAndResumes();
      setValidationPopup({
        title: 'Project Saved',
        message: `Changes to "${payload.title}" have been successfully saved.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to update project.' });
    }
  };

  // GitHub extraction for Experience
  const handleExtractGitHubExp = async (e) => {
    e.preventDefault();
    if (!githubExpUrl.trim()) {
      setFeedbackMsg({ type: 'error', text: 'Please enter a valid GitHub repository URL.' });
      return;
    }
    setExtractingExp(true);
    setFeedbackMsg({ type: '', text: '' });
    try {
      const data = await profileApi.extractGitHubProject(githubExpUrl.trim());
      setNewExperience({
        company: `GitHub / ${data.title}`,
        title: data.role || 'Open Source Contributor',
        location: 'Remote',
        description: data.description || '',
        bullets: (data.bullets || []).join('\n'),
        start_date: '2023',
        end_date: 'Present',
        is_current: true,
      });
      setValidationPopup({
        title: 'Experience Details Extracted',
        message: `Extracted project details from GitHub for experience role. Review and save below.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to extract GitHub repository details.' });
    } finally {
      setExtractingExp(false);
    }
  };

  const handleAddExperience = async (e) => {
    e.preventDefault();
    if (!newExperience.company.trim() || !newExperience.title.trim()) return;
    try {
      const payload = {
        company: newExperience.company.trim(),
        title: newExperience.title.trim(),
        location: newExperience.location.trim(),
        description: newExperience.description.trim(),
        bullets: newExperience.bullets
          ? newExperience.bullets.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        start_date: newExperience.start_date.trim() || null,
        end_date: newExperience.end_date.trim() || null,
        is_current: newExperience.is_current,
      };
      await profileApi.addExperience(payload);
      setNewExperience({
        company: '',
        title: '',
        location: '',
        description: '',
        bullets: '',
        start_date: '',
        end_date: '',
        is_current: false,
      });
      setGithubExpUrl('');
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Experience record added.' });
      setValidationPopup({
        title: 'Experience Successfully Added',
        message: `Role "${payload.title} at ${payload.company}" added to profile.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add experience.' });
    }
  };

  const handleDeleteExperience = async (id) => {
    try {
      await profileApi.deleteExperience(id);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Experience record removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete experience.' });
    }
  };

  const handleStartEditExperience = (exp) => {
    setEditingExpId(exp.id);
    setEditExpForm({
      company: exp.company || '',
      title: exp.title || '',
      location: exp.location || '',
      start_date: exp.start_date || '',
      end_date: exp.end_date || '',
      is_current: exp.is_current || false,
      description: exp.description || '',
      bullets: (exp.bullets || []).join('\n'),
    });
  };

  const handleSaveEditExperience = async (e) => {
    e.preventDefault();
    if (!editExpForm.company.trim() || !editExpForm.title.trim()) return;
    try {
      const payload = {
        company: editExpForm.company.trim(),
        title: editExpForm.title.trim(),
        location: editExpForm.location.trim(),
        description: editExpForm.description.trim(),
        bullets: editExpForm.bullets
          ? editExpForm.bullets.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        start_date: editExpForm.start_date || null,
        end_date: editExpForm.is_current ? null : (editExpForm.end_date || null),
        is_current: editExpForm.is_current,
      };
      await profileApi.updateExperience(editingExpId, payload);
      setEditingExpId(null);
      await loadProfileAndResumes();
      setValidationPopup({
        title: 'Experience Saved',
        message: `Work experience at "${payload.company}" updated successfully.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to update experience.' });
    }
  };

  // Template handlers
  const handleUploadTemplate = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const lower = file.name.toLowerCase();
    if (!lower.endsWith('.tex') && !lower.endsWith('.zip')) {
      setFeedbackMsg({ type: 'error', text: 'Template file must be a .tex file or .zip package.' });
      return;
    }
    setUploadingTemplate(true);
    setFeedbackMsg({ type: '', text: '' });
    try {
      const res = await profileApi.uploadTemplate(file);
      const tpl = await profileApi.getTemplate();
      setTemplateInfo(tpl);
      setFeedbackMsg({ type: 'success', text: res.message || 'Custom LaTeX template activated!' });
      setValidationPopup({
        title: 'Custom LaTeX Template Active',
        message: `Template "${file.name}" has been uploaded and activated. Resumes will now be rendered strictly using this template.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to upload template.' });
    } finally {
      setUploadingTemplate(false);
      e.target.value = '';
    }
  };

  const handleDeleteTemplate = async () => {
    try {
      await profileApi.deleteTemplate();
      const tpl = await profileApi.getTemplate();
      setTemplateInfo(tpl);
      setFeedbackMsg({ type: 'success', text: 'Reverted to default LaTeX template.' });
      setValidationPopup({
        title: 'Reverted to Default Template',
        message: 'Custom template removed. The system base template is now active.',
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to revert template.' });
    }
  };

  // Education & Certification handlers
  const handleAddEducation = async (e) => {
    e.preventDefault();
    if (!newEducation.institution.trim() || !newEducation.degree.trim()) return;
    try {
      await profileApi.addEducation(newEducation);
      setNewEducation({ institution: '', degree: '', field_of_study: '', grade: '' });
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Education record added.' });
      setValidationPopup({
        title: 'Education Added',
        message: `Record for ${newEducation.degree} at ${newEducation.institution} added to profile.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add education.' });
    }
  };

  const handleStartEditEducation = (edu) => {
    setEditingEduId(edu.id);
    setEditEduForm({
      institution: edu.institution || '',
      degree: edu.degree || '',
      field_of_study: edu.field_of_study || '',
      grade: edu.grade || '',
      start_date: edu.start_date || '',
      end_date: edu.end_date || '',
    });
  };

  const handleSaveEditEducation = async (e) => {
    e.preventDefault();
    if (!editEduForm.institution.trim() || !editEduForm.degree.trim()) return;
    try {
      await profileApi.updateEducation(editingEduId, editEduForm);
      setEditingEduId(null);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Education record updated.' });
      setValidationPopup({
        title: 'Education Updated',
        message: `Successfully updated record for ${editEduForm.degree} at ${editEduForm.institution}.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to update education.' });
    }
  };

  const handleDeleteEducation = async (id) => {
    try {
      await profileApi.deleteEducation(id);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Education record removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete education.' });
    }
  };

  const handleAddCert = async (e) => {
    e.preventDefault();
    if (!newCert.name.trim() || !newCert.issuer.trim()) return;
    try {
      await profileApi.addCertification(newCert);
      setNewCert({ name: '', issuer: '', issue_date: '' });
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Certification added.' });
      setValidationPopup({
        title: 'Certification Added',
        message: `Certification "${newCert.name}" from ${newCert.issuer} added to profile.`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to add certification.' });
    }
  };

  const handleStartEditCert = (cert) => {
    setEditingCertId(cert.id);
    setEditCertForm({
      name: cert.name || '',
      issuer: cert.issuer || '',
      issue_date: cert.issue_date || '',
      credential_url: cert.credential_url || '',
    });
  };

  const handleSaveEditCert = async (e) => {
    e.preventDefault();
    if (!editCertForm.name.trim() || !editCertForm.issuer.trim()) return;
    try {
      await profileApi.updateCertification(editingCertId, editCertForm);
      setEditingCertId(null);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Certification updated.' });
      setValidationPopup({
        title: 'Certification Updated',
        message: `Successfully updated certification "${editCertForm.name}".`,
      });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to update certification.' });
    }
  };

  const handleDeleteCert = async (id) => {
    try {
      await profileApi.deleteCertification(id);
      await loadProfileAndResumes();
      setFeedbackMsg({ type: 'success', text: 'Certification removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete certification.' });
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
        text: `Parsed "${result.filename}". ${result.extracted_skills.length} skills added to profile!`,
      });
      setValidationPopup({
        title: 'Resume Parsed',
        message: `Extracted ${result.extracted_skills.length} skills and candidate records from "${result.filename}".`,
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
      {/* Master Resume Upload Banner */}
      <div className="bg-white border-2 border-charcoal p-6 shadow-brutal space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-charcoal flex items-center space-x-2">
              <FileCheck className="w-5 h-5 text-coral" />
              <span>Master Resume PDF</span>
            </h2>
            <p className="text-xs text-charcoal-muted mt-1">
              Upload your existing PDF resume
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
            Candidate Profile
          </h2>
          <p className="text-sm text-charcoal-muted mt-1">
            Manage your structured experience, projects, and skills.
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
          <div className="space-y-4">
            {!isEditingPersonal ? (
              /* View Mode */
              <div className="bg-cream border-2 border-charcoal p-6 space-y-5">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-charcoal/20 pb-4">
                  <div>
                    <h3 className="font-bold text-lg text-charcoal">
                      {personalForm.headline || 'Candidate Overview'}
                    </h3>
                    {personalForm.location && (
                      <p className="text-xs text-charcoal-muted mt-0.5">{personalForm.location}</p>
                    )}
                  </div>
                  <button
                    onClick={() => setIsEditingPersonal(true)}
                    className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Edit Personal Info</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
                  <div className="p-3 bg-white border border-charcoal">
                    <span className="text-charcoal-muted uppercase text-[10px] block">Phone Number</span>
                    <span className="font-bold text-charcoal mt-1 block">
                      {personalForm.phone || 'Not provided'}
                    </span>
                  </div>

                  <div className="p-3 bg-white border border-charcoal">
                    <span className="text-charcoal-muted uppercase text-[10px] block">LinkedIn</span>
                    {personalForm.linkedin_url ? (
                      <a
                        href={personalForm.linkedin_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-coral hover:underline mt-1 truncate block flex items-center space-x-1"
                      >
                        <span className="truncate">{personalForm.linkedin_url}</span>
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>
                    ) : (
                      <span className="text-charcoal-muted mt-1 block">Not provided</span>
                    )}
                  </div>

                  <div className="p-3 bg-white border border-charcoal">
                    <span className="text-charcoal-muted uppercase text-[10px] block">GitHub</span>
                    {personalForm.github_url ? (
                      <a
                        href={personalForm.github_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-coral hover:underline mt-1 truncate block flex items-center space-x-1"
                      >
                        <span className="truncate">{personalForm.github_url}</span>
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>
                    ) : (
                      <span className="text-charcoal-muted mt-1 block">Not provided</span>
                    )}
                  </div>
                </div>

                <div className="bg-white border border-charcoal p-4 space-y-1.5">
                  <span className="text-[10px] font-mono uppercase font-bold text-charcoal-muted block">
                    Professional Summary
                  </span>
                  <p className="text-xs text-charcoal leading-relaxed whitespace-pre-line font-sans">
                    {personalForm.summary || 'No professional summary added yet. Click "Edit Personal Info" to add one.'}
                  </p>
                </div>
              </div>
            ) : (
              /* Edit Mode */
              <form onSubmit={handleUpdatePersonal} className="space-y-4 max-w-2xl bg-cream p-6 border-2 border-charcoal">
                <div className="flex items-center justify-between border-b border-charcoal/20 pb-2">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-charcoal flex items-center space-x-2">
                    <Edit3 className="w-4 h-4 text-coral" />
                    <span>Edit Personal Information</span>
                  </h3>
                </div>

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
                      placeholder="e.g. San Francisco, CA"
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
                    placeholder="Brief factual summary of candidate career, technologies, and achievements..."
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white font-sans"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Phone Number</label>
                    <div className="flex border-2 border-charcoal bg-white">
                      <select
                        value={phoneCountryCode}
                        onChange={(e) => setPhoneCountryCode(e.target.value)}
                        className="bg-cream px-2 py-2 text-xs font-mono font-bold border-r-2 border-charcoal focus:outline-none"
                      >
                        {COUNTRY_CODES.map((c) => (
                          <option key={c.code} value={c.code}>
                            {c.label}
                          </option>
                        ))}
                      </select>
                      <input
                        type="tel"
                        value={phoneDigits}
                        onChange={(e) => setPhoneDigits(e.target.value)}
                        placeholder="98765 43210"
                        className="w-full p-2 text-sm bg-white focus:outline-none font-mono"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">LinkedIn URL</label>
                    <input
                      type="url"
                      value={personalForm.linkedin_url}
                      onChange={(e) => setPersonalForm({ ...personalForm, linkedin_url: e.target.value })}
                      placeholder="https://linkedin.com/in/username"
                      className="w-full border-2 border-charcoal p-2 text-sm bg-white font-mono text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">GitHub URL</label>
                    <input
                      type="url"
                      value={personalForm.github_url}
                      onChange={(e) => setPersonalForm({ ...personalForm, github_url: e.target.value })}
                      placeholder="https://github.com/username"
                      className="w-full border-2 border-charcoal p-2 text-sm bg-white font-mono text-xs"
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-2 pt-3 border-t border-charcoal/20">
                  <button
                    type="button"
                    onClick={handleCancelPersonalEdit}
                    className="btn-secondary text-xs py-2 px-3 flex items-center space-x-1"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Cancel</span>
                  </button>
                  <button
                    type="submit"
                    className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Save Personal Details</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Tab 2: Skills */}
        {activeSection === 'skills' && (
          <div className="space-y-6">
            <form onSubmit={handleAddSkill} className="bg-cream p-4 border-2 border-charcoal flex flex-col sm:flex-row gap-3 items-end">
              <div className="flex-1 w-full">
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Skill Name *</label>
                <input
                  type="text"
                  value={newSkill.name}
                  onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
                  placeholder="e.g. Python, Docker, PostgreSQL"
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  required
                />
              </div>
              <div className="w-full sm:w-60">
                <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">Category *</label>
                <select
                  value={newSkill.category}
                  onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value })}
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white font-sans"
                  required
                >
                  <option value="" disabled>Select Category</option>
                  <option value="Languages">Languages</option>
                  <option value="Frameworks & Libraries">Frameworks & Libraries</option>
                  <option value="Databases">Databases</option>
                  <option value="Cloud & Infrastructure">Cloud & Infrastructure</option>
                  <option value="DevOps & Tools">DevOps & Tools</option>
                  <option value="Technical Competencies">Technical Competencies</option>
                  <option value="Soft Skills">Soft Skills</option>
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
                      className="text-rose-600 hover:text-rose-800 ml-1 font-bold"
                      title="Remove skill"
                    >
                      ×
                    </button>
                  </span>
                ))}
                {(!profile?.skills || profile.skills.length === 0) && (
                  <p className="text-xs text-charcoal-muted">No skills recorded yet. Add skills using the form above or upload a resume.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Projects */}
        {activeSection === 'projects' && (
          <div className="space-y-6">
            {/* Project Mode Toggle */}
            <div className="flex items-center space-x-2 border-b border-cream-border pb-3">
              <button
                type="button"
                onClick={() => setProjectMode('github')}
                className={`px-3 py-1.5 text-xs font-bold border flex items-center space-x-1.5 transition-all ${
                  projectMode === 'github'
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-coral" />
                <span>Add via GitHub Link</span>
              </button>
              <button
                type="button"
                onClick={() => setProjectMode('manual')}
                className={`px-3 py-1.5 text-xs font-bold border flex items-center space-x-1.5 transition-all ${
                  projectMode === 'manual'
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Manual Addition</span>
              </button>
            </div>

            {/* Mode A: Extract via GitHub Link */}
            {projectMode === 'github' && (
              <div className="bg-cream p-5 border-2 border-charcoal space-y-4">
                <div>
                  <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-coral" />
                    <span>Extract Project Details from GitHub</span>
                  </h4>
                  <p className="text-xs text-charcoal-muted mt-1">
                    Paste a public GitHub repository link. The software automatically extracts title, tech stack, description, and key accomplishments from Markdown files.
                  </p>
                </div>

                <form onSubmit={handleExtractGitHubProject} className="flex flex-col sm:flex-row gap-2">
                  <input
                    type="url"
                    value={githubProjectUrl}
                    onChange={(e) => setGithubProjectUrl(e.target.value)}
                    placeholder="https://github.com/username/repository"
                    className="flex-1 border-2 border-charcoal p-2.5 text-xs font-mono bg-white focus:outline-none focus:ring-2 focus:ring-coral"
                    required
                  />
                  <button
                    type="submit"
                    disabled={extractingProject || !githubProjectUrl.trim()}
                    className="btn-primary flex items-center justify-center space-x-2 whitespace-nowrap text-xs py-2 px-4"
                  >
                    {extractingProject ? (
                      <>
                        <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent" />
                        <span>Extracting Repo...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Extract Details</span>
                      </>
                    )}
                  </button>
                </form>

                {/* Extracted Project Preview & Customization */}
                {extractedProject && (
                  <form onSubmit={handleSaveExtractedProject} className="border-2 border-charcoal bg-white p-4 space-y-3 pt-4">
                    <div className="flex items-center justify-between border-b border-cream-border pb-2">
                      <span className="text-xs font-bold text-emerald-800 uppercase flex items-center space-x-1">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Extracted Repository Data (Review & Edit)</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => setExtractedProject(null)}
                        className="text-xs text-charcoal-muted hover:text-charcoal"
                      >
                        Clear
                      </button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Project Title</label>
                        <input
                          type="text"
                          value={extractedProject.title}
                          onChange={(e) => setExtractedProject({ ...extractedProject, title: e.target.value })}
                          className="w-full border-2 border-charcoal p-2 text-xs bg-white font-bold"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Tech Stack (comma-separated)</label>
                        <input
                          type="text"
                          value={extractedProject.technologies}
                          onChange={(e) => setExtractedProject({ ...extractedProject, technologies: e.target.value })}
                          placeholder="e.g. Python, FastAPI, Docker"
                          className="w-full border-2 border-charcoal p-2 text-xs bg-white"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Project Description (Extracted from README)</label>
                      <textarea
                        rows={2}
                        value={extractedProject.description}
                        onChange={(e) => setExtractedProject({ ...extractedProject, description: e.target.value })}
                        className="w-full border-2 border-charcoal p-2 text-xs bg-white"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                        Accomplishment Bullets (One per line - add or edit as needed)
                      </label>
                      <textarea
                        rows={3}
                        value={extractedProject.bullets}
                        onChange={(e) => setExtractedProject({ ...extractedProject, bullets: e.target.value })}
                        placeholder="Bullet points describing achievements, performance gains, or features..."
                        className="w-full border-2 border-charcoal p-2 text-xs bg-white font-mono"
                      />
                    </div>

                    <div className="flex justify-end pt-2">
                      <button type="submit" className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5">
                        <Plus className="w-3.5 h-3.5" />
                        <span>Add Extracted Project to Profile</span>
                      </button>
                    </div>
                  </form>
                )}
              </div>
            )}

            {/* Mode B: Manual Project Addition */}
            {projectMode === 'manual' && (
              <form onSubmit={handleAddManualProject} className="bg-cream p-5 border-2 border-charcoal space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                  <FolderGit2 className="w-4 h-4 text-coral" />
                  <span>Manual Project Addition</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Project Title *</label>
                    <input
                      type="text"
                      value={newProject.title}
                      onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                      placeholder="e.g. Distributed Task Engine"
                      className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Tech Stack (comma-separated)</label>
                    <input
                      type="text"
                      value={newProject.technologies}
                      onChange={(e) => setNewProject({ ...newProject, technologies: e.target.value })}
                      placeholder="e.g. Python, PostgreSQL, Docker, Redis"
                      className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Repository / Project URL (Optional)</label>
                    <input
                      type="url"
                      value={newProject.url}
                      onChange={(e) => setNewProject({ ...newProject, url: e.target.value })}
                      placeholder="https://github.com/username/project"
                      className="w-full border-2 border-charcoal p-2 text-xs font-mono bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Role in Project (Optional)</label>
                    <input
                      type="text"
                      value={newProject.role}
                      onChange={(e) => setNewProject({ ...newProject, role: e.target.value })}
                      placeholder="e.g. Lead Architect / Creator"
                      className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Project Description</label>
                  <textarea
                    rows={2}
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    placeholder="High-level description of what the project accomplished..."
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Accomplishment Bullets (One per line)
                  </label>
                  <textarea
                    rows={3}
                    value={newProject.bullets}
                    onChange={(e) => setNewProject({ ...newProject, bullets: e.target.value })}
                    placeholder="Architected async task queues reducing job latency by 45%&#10;Integrated PostgreSQL full-text search with automated migration pipeline"
                    className="w-full border-2 border-charcoal p-2 text-xs font-mono bg-white"
                  />
                </div>

                <div className="flex justify-end pt-1">
                  <button type="submit" className="btn-primary flex items-center space-x-1.5 text-xs py-2 px-4">
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Project</span>
                  </button>
                </div>
              </form>
            )}

            {/* List of Existing Projects */}
            <div className="space-y-3">
              <h4 className="text-xs font-mono uppercase font-bold text-charcoal-muted">
                Candidate Projects ({profile?.projects?.length || 0})
              </h4>
              {profile?.projects?.map((proj) => {
                const isEditing = editingProjectId === proj.id;
                if (isEditing) {
                  return (
                    <form
                      key={proj.id}
                      onSubmit={handleSaveEditProject}
                      className="border-2 border-charcoal p-4 bg-cream space-y-3 shadow-brutal-sm"
                    >
                      <div className="flex justify-between items-center border-b border-cream-border pb-2">
                        <span className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                          <Edit3 className="w-3.5 h-3.5 text-coral" />
                          <span>Edit Project: {proj.title}</span>
                        </span>
                        <button
                          type="button"
                          onClick={() => setEditingProjectId(null)}
                          className="text-charcoal-muted hover:text-charcoal p-1"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Project Title *</label>
                          <input
                            type="text"
                            value={editProjectForm.title}
                            onChange={(e) => setEditProjectForm({ ...editProjectForm, title: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Tech Stack (comma-separated)</label>
                          <input
                            type="text"
                            value={editProjectForm.technologies}
                            onChange={(e) => setEditProjectForm({ ...editProjectForm, technologies: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Role in Project</label>
                          <input
                            type="text"
                            value={editProjectForm.role}
                            onChange={(e) => setEditProjectForm({ ...editProjectForm, role: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Repository URL</label>
                          <input
                            type="url"
                            value={editProjectForm.url}
                            onChange={(e) => setEditProjectForm({ ...editProjectForm, url: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs font-mono bg-white"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Description</label>
                        <textarea
                          rows={2}
                          value={editProjectForm.description}
                          onChange={(e) => setEditProjectForm({ ...editProjectForm, description: e.target.value })}
                          className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                          Accomplishment Bullets (One per line)
                        </label>
                        <textarea
                          rows={3}
                          value={editProjectForm.bullets}
                          onChange={(e) => setEditProjectForm({ ...editProjectForm, bullets: e.target.value })}
                          className="w-full border-2 border-charcoal p-2 text-xs font-mono bg-white"
                        />
                      </div>

                      <div className="flex justify-end space-x-2 pt-1">
                        <button
                          type="button"
                          onClick={() => setEditingProjectId(null)}
                          className="btn-secondary text-xs py-1.5 px-3 bg-white"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="btn-primary text-xs py-1.5 px-4 flex items-center space-x-1.5"
                        >
                          <Save className="w-3.5 h-3.5" />
                          <span>Save Changes</span>
                        </button>
                      </div>
                    </form>
                  );
                }

                return (
                  <div key={proj.id} className="border-2 border-charcoal p-4 bg-white flex justify-between items-start gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center space-x-2">
                        <h5 className="font-bold text-sm text-charcoal">{proj.title}</h5>
                        {proj.role && <span className="text-xs text-charcoal-muted font-mono">• {proj.role}</span>}
                        {proj.url && (
                          <a
                            href={proj.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-coral hover:underline inline-flex items-center space-x-1 text-xs font-mono"
                          >
                            <LinkIcon className="w-3 h-3" />
                            <span>Repository</span>
                          </a>
                        )}
                      </div>
                      {proj.description && <p className="text-xs text-charcoal-muted">{proj.description}</p>}
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {proj.technologies.map((tech, i) => (
                            <span key={i} className="badge-tag bg-cream text-charcoal border-charcoal text-[10px]">
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                      {proj.bullets && proj.bullets.length > 0 && (
                        <ul className="list-disc list-inside text-xs text-charcoal space-y-0.5 pt-1">
                          {proj.bullets.map((b, idx) => (
                            <li key={idx} className="leading-relaxed">{b}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <div className="flex items-center space-x-1.5 shrink-0">
                      <button
                        onClick={() => handleStartEditProject(proj)}
                        className="p-1.5 border border-charcoal bg-cream hover:bg-white text-charcoal"
                        title="Edit project"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteProject(proj.id)}
                        className="p-1.5 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                        title="Remove project"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
              {(!profile?.projects || profile.projects.length === 0) && (
                <p className="text-xs text-charcoal-muted">No projects added yet. Extract from GitHub or add manually above.</p>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Experience */}
        {activeSection === 'experience' && (
          <div className="space-y-6">
            {/* Experience Mode Toggle */}
            <div className="flex items-center space-x-2 border-b border-cream-border pb-3">
              <button
                type="button"
                onClick={() => setExperienceMode('manual')}
                className={`px-3 py-1.5 text-xs font-bold border flex items-center space-x-1.5 transition-all ${
                  experienceMode === 'manual'
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Manual Addition</span>
              </button>
              <button
                type="button"
                onClick={() => setExperienceMode('github')}
                className={`px-3 py-1.5 text-xs font-bold border flex items-center space-x-1.5 transition-all ${
                  experienceMode === 'github'
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-coral" />
                <span>Extract via GitHub Link</span>
              </button>
            </div>

            {/* GitHub Extraction for Experience */}
            {experienceMode === 'github' && (
              <div className="bg-cream p-5 border-2 border-charcoal space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-coral" />
                  <span>Extract Experience from GitHub Repository</span>
                </h4>
                <p className="text-xs text-charcoal-muted">
                  Import an open source contribution or project repository as an experience entry.
                </p>
                <div className="flex flex-col sm:flex-row gap-2">
                  <input
                    type="url"
                    value={githubExpUrl}
                    onChange={(e) => setGithubExpUrl(e.target.value)}
                    placeholder="https://github.com/organization/repository"
                    className="flex-1 border-2 border-charcoal p-2.5 text-xs font-mono bg-white focus:outline-none focus:ring-2 focus:ring-coral"
                  />
                  <button
                    type="button"
                    onClick={handleExtractGitHubExp}
                    disabled={extractingExp || !githubExpUrl.trim()}
                    className="btn-primary text-xs py-2 px-4 whitespace-nowrap"
                  >
                    {extractingExp ? 'Extracting...' : 'Extract Experience'}
                  </button>
                </div>
              </div>
            )}

            {/* Experience Form */}
            <form onSubmit={handleAddExperience} className="bg-cream p-5 border-2 border-charcoal space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                <Briefcase className="w-4 h-4 text-coral" />
                <span>Add Work Experience</span>
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Company / Organization *</label>
                  <input
                    type="text"
                    value={newExperience.company}
                    onChange={(e) => setNewExperience({ ...newExperience, company: e.target.value })}
                    placeholder="e.g. Acme Corporation"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Job Title / Role *</label>
                  <input
                    type="text"
                    value={newExperience.title}
                    onChange={(e) => setNewExperience({ ...newExperience, title: e.target.value })}
                    placeholder="e.g. Senior Software Engineer"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Location</label>
                  <input
                    type="text"
                    value={newExperience.location}
                    onChange={(e) => setNewExperience({ ...newExperience, location: e.target.value })}
                    placeholder="e.g. San Francisco, CA (or Remote)"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Start Date</label>
                  <input
                    type="date"
                    value={newExperience.start_date}
                    onChange={(e) => setNewExperience({ ...newExperience, start_date: e.target.value })}
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">End Date</label>
                  <input
                    type="date"
                    value={newExperience.end_date}
                    onChange={(e) => setNewExperience({ ...newExperience, end_date: e.target.value })}
                    disabled={newExperience.is_current}
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white disabled:bg-cream-muted"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="is_current"
                  checked={newExperience.is_current}
                  onChange={(e) => setNewExperience({ ...newExperience, is_current: e.target.checked })}
                  className="rounded border-charcoal text-coral focus:ring-coral"
                />
                <label htmlFor="is_current" className="text-xs font-mono text-charcoal">
                  I currently work here
                </label>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Role Description</label>
                <textarea
                  rows={2}
                  value={newExperience.description}
                  onChange={(e) => setNewExperience({ ...newExperience, description: e.target.value })}
                  placeholder="Overview of organizational scope and team responsibilities..."
                  className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                  Accomplishment Bullets (One per line)
                </label>
                <textarea
                  rows={3}
                  value={newExperience.bullets}
                  onChange={(e) => setNewExperience({ ...newExperience, bullets: e.target.value })}
                  placeholder="Built microservice architecture handling 10M events daily&#10;Mentored 4 junior engineers on distributed systems best practices"
                  className="w-full border-2 border-charcoal p-2 text-xs font-mono bg-white"
                />
              </div>

              <div className="flex justify-end pt-1">
                <button type="submit" className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5">
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Experience</span>
                </button>
              </div>
            </form>

            {/* List of Existing Experiences */}
            <div className="space-y-3">
              <h4 className="text-xs font-mono uppercase font-bold text-charcoal-muted">
                Candidate Work Experience ({profile?.experiences?.length || 0})
              </h4>
              {profile?.experiences?.map((exp) => {
                const isEditing = editingExpId === exp.id;
                if (isEditing) {
                  return (
                    <form
                      key={exp.id}
                      onSubmit={handleSaveEditExperience}
                      className="border-2 border-charcoal p-4 bg-cream space-y-3 shadow-brutal-sm"
                    >
                      <div className="flex justify-between items-center border-b border-cream-border pb-2">
                        <span className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                          <Edit3 className="w-3.5 h-3.5 text-coral" />
                          <span>Edit Work Experience: {exp.company}</span>
                        </span>
                        <button
                          type="button"
                          onClick={() => setEditingExpId(null)}
                          className="text-charcoal-muted hover:text-charcoal p-1"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Company *</label>
                          <input
                            type="text"
                            value={editExpForm.company}
                            onChange={(e) => setEditExpForm({ ...editExpForm, company: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Job Title *</label>
                          <input
                            type="text"
                            value={editExpForm.title}
                            onChange={(e) => setEditExpForm({ ...editExpForm, title: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Location</label>
                          <input
                            type="text"
                            value={editExpForm.location}
                            onChange={(e) => setEditExpForm({ ...editExpForm, location: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Start Date</label>
                          <input
                            type="date"
                            value={editExpForm.start_date}
                            onChange={(e) => setEditExpForm({ ...editExpForm, start_date: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">End Date</label>
                          <input
                            type="date"
                            value={editExpForm.end_date}
                            onChange={(e) => setEditExpForm({ ...editExpForm, end_date: e.target.value })}
                            disabled={editExpForm.is_current}
                            className="w-full border-2 border-charcoal p-2 text-sm bg-white disabled:bg-cream-muted"
                          />
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 pt-1">
                        <input
                          type="checkbox"
                          id={`edit_is_current_${exp.id}`}
                          checked={editExpForm.is_current}
                          onChange={(e) => setEditExpForm({ ...editExpForm, is_current: e.target.checked })}
                          className="rounded border-charcoal text-coral focus:ring-coral"
                        />
                        <label htmlFor={`edit_is_current_${exp.id}`} className="text-xs font-mono text-charcoal">
                          I currently work here
                        </label>
                      </div>

                      <div>
                        <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Role Description</label>
                        <textarea
                          rows={2}
                          value={editExpForm.description}
                          onChange={(e) => setEditExpForm({ ...editExpForm, description: e.target.value })}
                          className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                          Accomplishment Bullets (One per line)
                        </label>
                        <textarea
                          rows={3}
                          value={editExpForm.bullets}
                          onChange={(e) => setEditExpForm({ ...editExpForm, bullets: e.target.value })}
                          className="w-full border-2 border-charcoal p-2 text-xs font-mono bg-white"
                        />
                      </div>

                      <div className="flex justify-end space-x-2 pt-1">
                        <button
                          type="button"
                          onClick={() => setEditingExpId(null)}
                          className="btn-secondary text-xs py-1.5 px-3 bg-white"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="btn-primary text-xs py-1.5 px-4 flex items-center space-x-1.5"
                        >
                          <Save className="w-3.5 h-3.5" />
                          <span>Save Changes</span>
                        </button>
                      </div>
                    </form>
                  );
                }

                return (
                  <div key={exp.id} className="border-2 border-charcoal p-4 bg-white flex justify-between items-start gap-4">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center space-x-2">
                        <h5 className="font-bold text-sm text-charcoal">{exp.title}</h5>
                        <span className="text-xs text-charcoal-muted">at</span>
                        <span className="font-semibold text-xs text-charcoal">{exp.company}</span>
                        {exp.location && <span className="text-xs text-charcoal-muted">• {exp.location}</span>}
                      </div>
                      <div className="text-xs font-mono text-charcoal-muted">
                        {exp.start_date || 'Start'} – {exp.is_current ? 'Present' : exp.end_date || 'End'}
                      </div>
                      {exp.description && <p className="text-xs text-charcoal-muted pt-1">{exp.description}</p>}
                      {exp.bullets && exp.bullets.length > 0 && (
                        <ul className="list-disc list-inside text-xs text-charcoal space-y-0.5 pt-1">
                          {exp.bullets.map((b, idx) => (
                            <li key={idx} className="leading-relaxed">{b}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <div className="flex items-center space-x-1.5 shrink-0">
                      <button
                        onClick={() => handleStartEditExperience(exp)}
                        className="p-1.5 border border-charcoal bg-cream hover:bg-white text-charcoal"
                        title="Edit experience"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteExperience(exp.id)}
                        className="p-1.5 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                        title="Remove experience"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
              {(!profile?.experiences || profile.experiences.length === 0) && (
                <p className="text-xs text-charcoal-muted">No experience records added yet.</p>
              )}
            </div>
          </div>
        )}

        {/* Tab 5: Education */}
        {activeSection === 'education' && (
          <div className="space-y-6">
            <form onSubmit={handleAddEducation} className="bg-cream p-5 border-2 border-charcoal space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                <GraduationCap className="w-4 h-4 text-coral" />
                <span>Add Education Record</span>
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Institution *</label>
                  <input
                    type="text"
                    value={newEducation.institution}
                    onChange={(e) => setNewEducation({ ...newEducation, institution: e.target.value })}
                    placeholder="e.g. Stanford University"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Degree *</label>
                  <input
                    type="text"
                    value={newEducation.degree}
                    onChange={(e) => setNewEducation({ ...newEducation, degree: e.target.value })}
                    placeholder="e.g. Bachelor of Science"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Field of Study</label>
                  <input
                    type="text"
                    value={newEducation.field_of_study}
                    onChange={(e) => setNewEducation({ ...newEducation, field_of_study: e.target.value })}
                    placeholder="e.g. Computer Science"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Grade / GPA</label>
                  <input
                    type="text"
                    value={newEducation.grade}
                    onChange={(e) => setNewEducation({ ...newEducation, grade: e.target.value })}
                    placeholder="e.g. 3.9 / 4.0 or First Class"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  />
                </div>
              </div>
              <div className="flex justify-end pt-1">
                <button type="submit" className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5">
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Education</span>
                </button>
              </div>
            </form>

            <div className="space-y-3">
              <h4 className="text-xs font-mono uppercase font-bold text-charcoal-muted">
                Candidate Education Records ({profile?.educations?.length || 0})
              </h4>
              {profile?.educations?.map((edu) => (
                <div key={edu.id} className="border-2 border-charcoal p-4 bg-white">
                  {editingEduId === edu.id ? (
                    <form onSubmit={handleSaveEditEducation} className="space-y-3">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Degree *</label>
                          <input
                            type="text"
                            value={editEduForm.degree}
                            onChange={(e) => setEditEduForm({ ...editEduForm, degree: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Institution *</label>
                          <input
                            type="text"
                            value={editEduForm.institution}
                            onChange={(e) => setEditEduForm({ ...editEduForm, institution: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                            required
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Field of Study</label>
                          <input
                            type="text"
                            value={editEduForm.field_of_study}
                            onChange={(e) => setEditEduForm({ ...editEduForm, field_of_study: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Grade / GPA</label>
                          <input
                            type="text"
                            value={editEduForm.grade}
                            onChange={(e) => setEditEduForm({ ...editEduForm, grade: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Start Date</label>
                          <input
                            type="date"
                            value={editEduForm.start_date || ''}
                            onChange={(e) => setEditEduForm({ ...editEduForm, start_date: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">End Date</label>
                          <input
                            type="date"
                            value={editEduForm.end_date || ''}
                            onChange={(e) => setEditEduForm({ ...editEduForm, end_date: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                          />
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2 pt-1">
                        <button
                          type="button"
                          onClick={() => setEditingEduId(null)}
                          className="px-3 py-1.5 border border-charcoal text-xs font-mono hover:bg-cream"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="btn-primary text-xs py-1.5 px-3 flex items-center space-x-1"
                        >
                          <Save className="w-3.5 h-3.5" />
                          <span>Save Changes</span>
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="flex justify-between items-start">
                      <div>
                        <h5 className="font-bold text-sm text-charcoal">{edu.degree}</h5>
                        <div className="text-xs text-charcoal-muted mt-0.5">
                          {edu.institution} {edu.field_of_study ? `• ${edu.field_of_study}` : ''}
                        </div>
                        {edu.grade && <span className="text-xs font-mono text-emerald-800 font-bold block mt-1">Grade: {edu.grade}</span>}
                        {(edu.start_date || edu.end_date) && (
                          <div className="text-[11px] font-mono text-charcoal-muted mt-1">
                            {edu.start_date || 'N/A'} - {edu.end_date || 'Present'}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => handleStartEditEducation(edu)}
                          className="p-1.5 border border-charcoal bg-cream hover:bg-white text-charcoal text-xs flex items-center space-x-1"
                          title="Edit education"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline">Edit</span>
                        </button>
                        <button
                          onClick={() => handleDeleteEducation(edu.id)}
                          className="p-1.5 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                          title="Delete education"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {(!profile?.educations || profile.educations.length === 0) && (
                <p className="text-xs text-charcoal-muted">No education records added yet.</p>
              )}
            </div>
          </div>
        )}

        {/* Tab 6: Certifications */}
        {activeSection === 'certifications' && (
          <div className="space-y-6">
            <form onSubmit={handleAddCert} className="bg-cream p-5 border-2 border-charcoal space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                <Award className="w-4 h-4 text-coral" />
                <span>Add Certification</span>
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Certification Name *</label>
                  <input
                    type="text"
                    value={newCert.name}
                    onChange={(e) => setNewCert({ ...newCert, name: e.target.value })}
                    placeholder="e.g. AWS Certified Solutions Architect"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Issuing Organization *</label>
                  <input
                    type="text"
                    value={newCert.issuer}
                    onChange={(e) => setNewCert({ ...newCert, issuer: e.target.value })}
                    placeholder="e.g. Amazon Web Services"
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">Issue Date</label>
                  <input
                    type="date"
                    value={newCert.issue_date}
                    onChange={(e) => setNewCert({ ...newCert, issue_date: e.target.value })}
                    className="w-full border-2 border-charcoal p-2 text-sm bg-white"
                  />
                </div>
              </div>
              <div className="flex justify-end pt-1">
                <button type="submit" className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5">
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Certification</span>
                </button>
              </div>
            </form>

            <div className="space-y-3">
              <h4 className="text-xs font-mono uppercase font-bold text-charcoal-muted">
                Candidate Certifications ({profile?.certifications?.length || 0})
              </h4>
              {profile?.certifications?.map((c) => (
                <div key={c.id} className="border-2 border-charcoal p-4 bg-white">
                  {editingCertId === c.id ? (
                    <form onSubmit={handleSaveEditCert} className="space-y-3">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Certification Name *</label>
                          <input
                            type="text"
                            value={editCertForm.name}
                            onChange={(e) => setEditCertForm({ ...editCertForm, name: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Issuing Organization *</label>
                          <input
                            type="text"
                            value={editCertForm.issuer}
                            onChange={(e) => setEditCertForm({ ...editCertForm, issuer: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                            required
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Issue Date</label>
                          <input
                            type="date"
                            value={editCertForm.issue_date || ''}
                            onChange={(e) => setEditCertForm({ ...editCertForm, issue_date: e.target.value })}
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono uppercase text-charcoal-muted mb-1">Credential URL</label>
                          <input
                            type="url"
                            value={editCertForm.credential_url || ''}
                            onChange={(e) => setEditCertForm({ ...editCertForm, credential_url: e.target.value })}
                            placeholder="https://..."
                            className="w-full border-2 border-charcoal p-2 text-xs bg-cream-bg"
                          />
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2 pt-1">
                        <button
                          type="button"
                          onClick={() => setEditingCertId(null)}
                          className="px-3 py-1.5 border border-charcoal text-xs font-mono hover:bg-cream"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="btn-primary text-xs py-1.5 px-3 flex items-center space-x-1"
                        >
                          <Save className="w-3.5 h-3.5" />
                          <span>Save Changes</span>
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="flex justify-between items-start">
                      <div>
                        <h5 className="font-bold text-sm text-charcoal">{c.name}</h5>
                        <div className="text-xs text-charcoal-muted mt-0.5">
                          {c.issuer} {c.issue_date ? `• ${c.issue_date}` : ''}
                        </div>
                        {c.credential_url && (
                          <a
                            href={c.credential_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center space-x-1 text-[11px] text-coral hover:underline mt-1"
                          >
                            <span>Verify Credential</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => handleStartEditCert(c)}
                          className="p-1.5 border border-charcoal bg-cream hover:bg-white text-charcoal text-xs flex items-center space-x-1"
                          title="Edit certification"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline">Edit</span>
                        </button>
                        <button
                          onClick={() => handleDeleteCert(c.id)}
                          className="p-1.5 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                          title="Delete certification"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {(!profile?.certifications || profile.certifications.length === 0) && (
                <p className="text-xs text-charcoal-muted">No certifications recorded yet.</p>
              )}
            </div>
          </div>
        )}

        {/* Tab 7: Resume Template (LaTeX) */}
        {activeSection === 'template' && (
          <div className="bg-cream border-2 border-charcoal p-6 space-y-5 font-mono text-xs">
            <div>
              <h3 className="font-bold text-sm text-charcoal uppercase">LaTeX Template Package Manager</h3>
              <p className="text-charcoal-muted mt-1">
                Upload your preferred custom LaTeX template (.tex file or .zip package). When provided, PrivateResume compiles your PDF strictly with this template.
              </p>
            </div>

            <div className="p-4 bg-white border-2 border-charcoal space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-cream-border pb-3">
                <span className="text-charcoal-muted font-bold uppercase text-[11px]">Active LaTeX Engine Template:</span>
                {templateInfo?.has_custom_template ? (
                  <span className="inline-flex items-center px-2 py-0.5 text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-400">
                    Custom Template Active: {templateInfo.template_name || 'main.tex'}
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2 py-0.5 text-xs font-bold bg-cream text-charcoal border border-charcoal">
                    System Default Template (Modern Editorial)
                  </span>
                )}
              </div>

              {/* Upload New Template (.tex or .zip) */}
              <div className="space-y-2">
                <label className="block text-[11px] font-bold uppercase text-charcoal">
                  Upload Custom LaTeX Template (.tex or .zip package)
                </label>
                <div className="flex flex-col sm:flex-row items-center gap-3">
                  <input
                    type="file"
                    accept=".tex,.zip"
                    onChange={handleUploadTemplate}
                    disabled={uploadingTemplate}
                    className="w-full text-xs file:mr-3 file:py-2 file:px-3 file:border-2 file:border-charcoal file:text-xs file:font-bold file:bg-white file:text-charcoal hover:file:bg-cream cursor-pointer disabled:opacity-50"
                  />
                  {uploadingTemplate && (
                    <span className="text-xs text-coral font-bold shrink-0 animate-pulse">Uploading...</span>
                  )}
                </div>
                <p className="text-[10px] text-charcoal-muted">
                  Accepts a single <code>.tex</code> document or a <code>.zip</code> package containing style files (<code>.cls</code>, <code>.sty</code>) alongside <code>main.tex</code>.
                </p>
              </div>

              {/* Active Template Controls */}
              {templateInfo?.has_custom_template && (
                <div className="pt-3 border-t border-cream-border flex justify-between items-center">
                  <div className="space-y-0.5">
                    <div className="font-bold text-xs text-charcoal flex items-center space-x-1.5">
                      <FileText className="w-3.5 h-3.5 text-coral" />
                      <span>{templateInfo.template_name || 'Custom LaTeX Template'}</span>
                    </div>
                    {templateInfo.template_size && (
                      <div className="text-[10px] text-charcoal-muted">
                        Size: {(templateInfo.template_size / 1024).toFixed(1)} KB
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleDeleteTemplate}
                    className="px-3 py-1.5 border border-charcoal bg-rose-50 text-rose-700 hover:bg-rose-100 font-bold text-xs flex items-center space-x-1"
                    title="Remove custom template and revert to default"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Revert to Default Template</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Validation Pop-up Modal */}
      {validationPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal/50 p-4">
          <div className="bg-white border-2 border-charcoal p-6 shadow-brutal max-w-sm w-full space-y-4 font-sans">
            <div className="flex items-center space-x-2.5 text-emerald-600">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <h3 className="font-bold text-base text-charcoal">{validationPopup.title}</h3>
            </div>
            <p className="text-xs text-charcoal-muted leading-relaxed font-mono">
              {validationPopup.message}
            </p>
            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setValidationPopup(null)}
                className="btn-primary w-full py-2 text-xs"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
