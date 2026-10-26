import React, { useState, useEffect } from 'react';
import {
  User,
  GraduationCap,
  Briefcase,
  FolderGit2,
  Wrench,
  Award,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  Compass,
} from 'lucide-react';
import { profileApi } from '../api/profile';
import ReviewExtractionModal from '../components/ReviewExtractionModal';
import MasterResumeBanner from '../components/profile/MasterResumeBanner';
import ProfileHeader from '../components/profile/ProfileHeader';
import ProfileTabs from '../components/profile/ProfileTabs';
import PersonalInfoTab, { COUNTRY_CODES } from '../components/profile/PersonalInfoTab';
import SkillsTab from '../components/profile/SkillsTab';
import ProjectsTab from '../components/profile/ProjectsTab';
import ExperienceTab from '../components/profile/ExperienceTab';
import EducationTab from '../components/profile/EducationTab';
import CertificationsTab from '../components/profile/CertificationsTab';
import { useToast } from '../context/ToastContext';

export default function ProfilePage({
  currentUser,
  evidenceTarget,
  clearEvidenceTarget,
  onReturnToWorkspace,
}) {
  const { showSuccess, showError, showInfo } = useToast();
  const [activeSection, setActiveSection] = useState('personal');
  const [profile, setProfile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStage, setUploadStage] = useState('');
  const [feedbackMsg, setFeedbackMsg] = useState({ type: '', text: '' });

  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const isFromWorkspace = searchParams && searchParams.get('from') === 'workspace';
  const isFromOnboarding = searchParams && searchParams.get('from') === 'onboarding';
  const urlStage = searchParams ? parseInt(searchParams.get('stage'), 10) || 3 : 3;
  const urlJobId = searchParams ? parseInt(searchParams.get('jobId'), 10) || null : null;
  const effectiveEvidenceTarget = evidenceTarget || (isFromWorkspace ? {
    section: searchParams?.get('section') || 'personal',
    stage: urlStage,
    jobId: urlJobId,
    itemValue: 'Workspace Context',
  } : null);

  useEffect(() => {
    if (effectiveEvidenceTarget?.section) {
      setActiveSection(effectiveEvidenceTarget.section);
    }
  }, [effectiveEvidenceTarget?.section]);

  // Extraction review modal state
  const [reviewResumeData, setReviewResumeData] = useState(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [loadingReview, setLoadingReview] = useState(false);

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

  // Saved baseline & Reset/Save tracking state
  const [savedBaseline, setSavedBaseline] = useState({
    personal: null,
    skills: [],
    projects: [],
    experiences: [],
    educations: [],
    certifications: [],
  });
  const [savingTab, setSavingTab] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState(null);

  useEffect(() => {
    if (currentUser) {
      loadProfileAndResumes();
    }
  }, [currentUser]);

  // Auto-dismiss green success notifications after 4 seconds with timer cleanup
  useEffect(() => {
    if (feedbackMsg?.type === 'success' && feedbackMsg?.text) {
      const timer = setTimeout(() => {
        setFeedbackMsg({ type: '', text: '' });
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [feedbackMsg]);

  const loadProfileAndResumes = async (preserveForms = false) => {
    setLoading(true);
    try {
      const [profData, resumesData] = await Promise.all([
        profileApi.getProfile(),
        profileApi.getResumes(),
      ]);
      setProfile(profData);
      setResumes(resumesData);

      const baselinePersonal = {
        headline: profData.headline || '',
        summary: profData.summary || '',
        phone: profData.phone || '',
        location: profData.location || '',
        linkedin_url: profData.linkedin_url || '',
        github_url: profData.github_url || '',
        portfolio_url: profData.portfolio_url || '',
      };

      setSavedBaseline({
        personal: baselinePersonal,
        skills: profData.skills ? JSON.parse(JSON.stringify(profData.skills)) : [],
        projects: profData.projects ? JSON.parse(JSON.stringify(profData.projects)) : [],
        experiences: profData.experiences ? JSON.parse(JSON.stringify(profData.experiences)) : [],
        educations: profData.educations ? JSON.parse(JSON.stringify(profData.educations)) : [],
        certifications: profData.certifications ? JSON.parse(JSON.stringify(profData.certifications)) : [],
      });

      if (!preserveForms) {
        setPersonalForm({ ...baselinePersonal });

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
      }
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to load profile data.' });
    } finally {
      setLoading(false);
    }
  };

  const hasTabActiveContent = (tabId) => {
    if (tabId === 'personal') {
      return !!(
        (personalForm.headline || '').trim() ||
        (personalForm.summary || '').trim() ||
        (personalForm.location || '').trim() ||
        (phoneDigits || '').trim() ||
        (personalForm.linkedin_url || '').trim() ||
        (personalForm.github_url || '').trim() ||
        (personalForm.portfolio_url || '').trim()
      );
    }
    if (tabId === 'skills') {
      return !!((newSkill.name || '').trim() || newSkill.category);
    }
    if (tabId === 'projects') {
      if (editingProjectId !== null) return true;
      if (extractedProject !== null) return true;
      if ((githubProjectUrl || '').trim() !== '') return true;
      return !!(
        (newProject.title || '').trim() ||
        (newProject.role || '').trim() ||
        (newProject.description || '').trim() ||
        (newProject.technologies || '').trim() ||
        (newProject.bullets || '').trim() ||
        (newProject.url || '').trim() ||
        (editProjectForm.title || '').trim() ||
        (editProjectForm.role || '').trim() ||
        (editProjectForm.description || '').trim() ||
        (editProjectForm.technologies || '').trim() ||
        (editProjectForm.bullets || '').trim() ||
        (editProjectForm.url || '').trim()
      );
    }
    if (tabId === 'experience') {
      if (editingExpId !== null) return true;
      if ((githubExpUrl || '').trim() !== '') return true;
      return !!(
        (newExperience.company || '').trim() ||
        (newExperience.title || '').trim() ||
        (newExperience.location || '').trim() ||
        (newExperience.description || '').trim() ||
        (newExperience.bullets || '').trim() ||
        (newExperience.start_date || '').trim() ||
        (newExperience.end_date || '').trim() ||
        newExperience.is_current ||
        (editExpForm.company || '').trim() ||
        (editExpForm.title || '').trim() ||
        (editExpForm.location || '').trim() ||
        (editExpForm.description || '').trim() ||
        (editExpForm.bullets || '').trim() ||
        (editExpForm.start_date || '').trim() ||
        (editExpForm.end_date || '').trim() ||
        editExpForm.is_current
      );
    }
    if (tabId === 'education') {
      if (editingEduId !== null) return true;
      return !!(
        (newEducation.institution || '').trim() ||
        (newEducation.degree || '').trim() ||
        (newEducation.field_of_study || '').trim() ||
        (newEducation.grade || '').trim() ||
        (editEduForm.institution || '').trim() ||
        (editEduForm.degree || '').trim() ||
        (editEduForm.field_of_study || '').trim() ||
        (editEduForm.grade || '').trim()
      );
    }
    if (tabId === 'certifications') {
      if (editingCertId !== null) return true;
      return !!(
        (newCert.name || '').trim() ||
        (newCert.issuer || '').trim() ||
        (newCert.issue_date || '').trim() ||
        (editCertForm.name || '').trim() ||
        (editCertForm.issuer || '').trim() ||
        (editCertForm.issue_date || '').trim() ||
        (editCertForm.credential_url || '').trim()
      );
    }
    return false;
  };

  const hasTabPersistedContent = (tabId) => {
    if (tabId === 'personal') {
      return !!(
        profile?.headline ||
        profile?.summary ||
        profile?.location ||
        profile?.phone ||
        profile?.linkedin_url ||
        profile?.github_url ||
        profile?.portfolio_url
      );
    }
    if (tabId === 'skills') {
      return !!(profile?.skills && profile.skills.length > 0);
    }
    if (tabId === 'projects') {
      return !!(profile?.projects && profile.projects.length > 0);
    }
    if (tabId === 'experience') {
      return !!(profile?.experiences && profile.experiences.length > 0);
    }
    if (tabId === 'education') {
      return !!(profile?.educations && profile.educations.length > 0);
    }
    if (tabId === 'certifications') {
      return !!(profile?.certifications && profile.certifications.length > 0);
    }
    return false;
  };

  const hasTabAnyData = (tabId) => {
    return hasTabPersistedContent(tabId) || hasTabActiveContent(tabId);
  };

  const hasAnyProfileData = () => {
    return sections.some((s) => hasTabAnyData(s.id));
  };

  const performTabReset = (tabId) => {
    if (tabId === 'personal') {
      setPersonalForm({
        headline: '',
        summary: '',
        phone: '',
        location: '',
        linkedin_url: '',
        github_url: '',
        portfolio_url: '',
      });
      setPhoneCountryCode('+91');
      setPhoneDigits('');
      setIsEditingPersonal(true);
    } else if (tabId === 'skills') {
      setNewSkill({ name: '', category: '', proficiency: 'Intermediate' });
    } else if (tabId === 'projects') {
      setEditingProjectId(null);
      setEditProjectForm({ title: '', role: '', technologies: '', url: '', description: '', bullets: '' });
      setNewProject({ title: '', role: '', description: '', technologies: '', bullets: '', url: '' });
      setExtractedProject(null);
      setGithubProjectUrl('');
    } else if (tabId === 'experience') {
      setEditingExpId(null);
      setEditExpForm({ company: '', title: '', location: '', start_date: '', end_date: '', is_current: false, description: '', bullets: '' });
      setNewExperience({ company: '', title: '', location: '', description: '', bullets: '', start_date: '', end_date: '', is_current: false });
      setGithubExpUrl('');
    } else if (tabId === 'education') {
      setEditingEduId(null);
      setEditEduForm({ institution: '', degree: '', field_of_study: '', grade: '', start_date: '', end_date: '' });
      setNewEducation({ institution: '', degree: '', field_of_study: '', grade: '' });
    } else if (tabId === 'certifications') {
      setEditingCertId(null);
      setEditCertForm({ name: '', issuer: '', issue_date: '', credential_url: '' });
      setNewCert({ name: '', issuer: '', issue_date: '' });
    }
  };

  const handleTabReset = (tabId) => {
    const hasData = hasTabAnyData(tabId);
    const tabLabel = sections.find((s) => s.id === tabId)?.label || tabId;

    if (!hasData) {
      performTabReset(tabId);
      setFeedbackMsg({ type: 'info', text: `${tabLabel} is already empty.` });
      return;
    }

    setConfirmDialog({
      title: `Reset ${tabLabel}`,
      message: `Permanently delete all saved ${tabLabel.toLowerCase()} records from your candidate profile and clear unsaved drafts? This action cannot be undone.`,
      confirmLabel: 'Reset & Delete',
      onConfirm: async () => {
        setSavingTab(true);
        setFeedbackMsg({ type: '', text: '' });
        try {
          const updated = await profileApi.resetSection(tabId);
          setProfile(updated);
          performTabReset(tabId);
          await loadProfileAndResumes(false);
          setFeedbackMsg({
            type: 'success',
            text: `Successfully reset ${tabLabel} and deleted all saved records.`,
          });
        } catch (err) {
          setFeedbackMsg({
            type: 'error',
            text: err?.message || `Failed to reset ${tabLabel}.`,
          });
          await loadProfileAndResumes(true);
        } finally {
          setSavingTab(false);
        }
      },
    });
  };

  const handleResetAll = () => {
    const hasData = hasAnyProfileData();

    if (!hasData) {
      sections.forEach((s) => performTabReset(s.id));
      setFeedbackMsg({ type: 'info', text: 'All profile sections are already empty.' });
      return;
    }

    setConfirmDialog({
      title: 'Reset All Profile Data',
      message: 'Permanently delete all saved records across all six Profile sections (Personal Info, Skills, Projects, Experience, Education, Certifications) and clear all unsaved drafts? Your uploaded Master Resume PDF will NOT be deleted.',
      confirmLabel: 'Reset All Sections',
      onConfirm: async () => {
        setSavingTab(true);
        setFeedbackMsg({ type: '', text: '' });
        try {
          const updated = await profileApi.resetAll();
          setProfile(updated);
          sections.forEach((s) => performTabReset(s.id));
          await loadProfileAndResumes(false);
          setFeedbackMsg({
            type: 'success',
            text: 'Successfully reset all Profile sections and deleted all saved records.',
          });
        } catch (err) {
          setFeedbackMsg({
            type: 'error',
            text: err?.message || 'Failed to reset profile sections.',
          });
          await loadProfileAndResumes(true);
        } finally {
          setSavingTab(false);
        }
      },
    });
  };

  const handleTabSave = async (tabId) => {
    setSavingTab(true);
    setFeedbackMsg({ type: '', text: '' });
    try {
      if (tabId === 'personal') {
        const fullPhone = phoneDigits.trim() ? `${phoneCountryCode} ${phoneDigits.trim()}` : '';
        const payload = { ...personalForm, phone: fullPhone };
        const updated = await profileApi.updateProfile(payload);
        setProfile(updated);
        const baselinePersonal = {
          headline: updated.headline || '',
          summary: updated.summary || '',
          phone: updated.phone || '',
          location: updated.location || '',
          linkedin_url: updated.linkedin_url || '',
          github_url: updated.github_url || '',
          portfolio_url: updated.portfolio_url || '',
        };
        setSavedBaseline((prev) => ({
          ...prev,
          personal: baselinePersonal,
        }));
        setIsEditingPersonal(false);
        setFeedbackMsg({ type: 'success', text: 'Personal info saved successfully.' });
        showSuccess('Personal information saved.');
      } else if (tabId === 'skills') {
        if (!newSkill.name.trim()) {
          setFeedbackMsg({ type: 'error', text: 'Please enter a skill name.' });
          return;
        }
        if (!newSkill.category) {
          setFeedbackMsg({ type: 'error', text: 'Please select a skill category from the dropdown.' });
          return;
        }
        const added = await profileApi.addSkill(newSkill);
        const skillName = added.name;
        const skillCat = added.category || 'Technical';
        setNewSkill({ name: '', category: '', proficiency: 'Intermediate' });
        await loadProfileAndResumes(true);
        setFeedbackMsg({ type: 'success', text: `Successfully added "${skillName}"!` });
        showSuccess(`Skill "${skillName}" added to candidate profile.`);
      } else if (tabId === 'projects') {
        if (editingProjectId) {
          if (!editProjectForm.title.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Project title is required.' });
            return;
          }
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
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: `Changes to "${payload.title}" have been successfully saved.` });
          showSuccess(`Changes to "${payload.title}" saved.`);
        } else if (newProject.title.trim()) {
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
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'Project added to profile.' });
          showSuccess(`Project "${payload.title}" added to profile.`);
        } else if (extractedProject?.title?.trim()) {
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
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'GitHub project added to profile!' });
          showSuccess(`Project "${payload.title}" added to profile.`);
        } else {
          setFeedbackMsg({ type: 'error', text: 'No unsaved project changes to save. Enter a project title or edit an existing project.' });
        }
      } else if (tabId === 'experience') {
        if (editingExpId) {
          if (!editExpForm.company.trim() || !editExpForm.title.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Company and Job Title are required.' });
            return;
          }
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
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: `Work experience at "${payload.company}" updated successfully.` });
          showSuccess(`Work experience at "${payload.company}" updated.`);
        } else if (newExperience.company.trim() || newExperience.title.trim()) {
          if (!newExperience.company.trim() || !newExperience.title.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Both Company and Job Title are required.' });
            return;
          }
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
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'Experience record added.' });
          showSuccess(`Role "${payload.title} at ${payload.company}" added to profile.`);
        } else {
          setFeedbackMsg({ type: 'error', text: 'No unsaved experience changes to save. Enter company and title or edit a role.' });
        }
      } else if (tabId === 'education') {
        if (editingEduId) {
          if (!editEduForm.institution.trim() || !editEduForm.degree.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Institution and Degree are required.' });
            return;
          }
          await profileApi.updateEducation(editingEduId, editEduForm);
          setEditingEduId(null);
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'Education record updated.' });
          showSuccess(`Record for ${editEduForm.degree} at ${editEduForm.institution} updated.`);
        } else if (newEducation.institution.trim() || newEducation.degree.trim()) {
          if (!newEducation.institution.trim() || !newEducation.degree.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Both Institution and Degree are required.' });
            return;
          }
          await profileApi.addEducation(newEducation);
          setNewEducation({ institution: '', degree: '', field_of_study: '', grade: '' });
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'Education record added.' });
          showSuccess(`Record for ${newEducation.degree} at ${newEducation.institution} added.`);
        } else {
          setFeedbackMsg({ type: 'error', text: 'No unsaved education changes to save.' });
        }
      } else if (tabId === 'certifications') {
        if (editingCertId) {
          if (!editCertForm.name.trim() || !editCertForm.issuer.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Certification Name and Issuer are required.' });
            return;
          }
          await profileApi.updateCertification(editingCertId, editCertForm);
          setEditingCertId(null);
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'Certification updated.' });
          showSuccess(`Certification "${editCertForm.name}" updated.`);
        } else if (newCert.name.trim() || newCert.issuer.trim()) {
          if (!newCert.name.trim() || !newCert.issuer.trim()) {
            setFeedbackMsg({ type: 'error', text: 'Both Certification Name and Issuing Organization are required.' });
            return;
          }
          await profileApi.addCertification(newCert);
          setNewCert({ name: '', issuer: '', issue_date: '' });
          await loadProfileAndResumes(true);
          setFeedbackMsg({ type: 'success', text: 'Certification added.' });
          showSuccess(`Certification "${newCert.name}" from ${newCert.issuer} added.`);
        } else {
          setFeedbackMsg({ type: 'error', text: 'No unsaved certification changes to save.' });
        }
      }
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err?.message || `Failed to save ${tabId}.` });
    } finally {
      setSavingTab(false);
    }
  };

  const handleUpdatePersonal = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('personal');
  };

  const handleCancelPersonalEdit = () => {
    if (savedBaseline?.personal && (savedBaseline.personal.headline || savedBaseline.personal.summary || savedBaseline.personal.location || savedBaseline.personal.phone)) {
      setPersonalForm({ ...savedBaseline.personal });
      if (savedBaseline.personal.phone) {
        const matched = COUNTRY_CODES.find((c) => savedBaseline.personal.phone.startsWith(c.code));
        if (matched) {
          setPhoneCountryCode(matched.code);
          setPhoneDigits(savedBaseline.personal.phone.slice(matched.code.length).trim());
        } else {
          setPhoneCountryCode('+91');
          setPhoneDigits(savedBaseline.personal.phone.trim());
        }
      } else {
        setPhoneCountryCode('+91');
        setPhoneDigits('');
      }
      setIsEditingPersonal(false);
    } else {
      performTabReset('personal');
    }
  };

  const handleAddSkill = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('skills');
  };

  const handleDeleteSkill = async (id) => {
    try {
      await profileApi.deleteSkill(id);
      await loadProfileAndResumes(true);
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
      showSuccess(`Extracted project "${data.title}" from GitHub.`);
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to extract GitHub repository details.' });
    } finally {
      setExtractingProject(false);
    }
  };

  const handleSaveExtractedProject = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('projects');
  };

  const handleAddManualProject = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('projects');
  };

  const handleDeleteProject = async (id) => {
    try {
      await profileApi.deleteProject(id);
      await loadProfileAndResumes(true);
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
    e?.preventDefault?.();
    await handleTabSave('projects');
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
      showSuccess(`Extracted role "${data.role || 'Open Source Contributor'}" from GitHub.`);
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to extract GitHub repository details.' });
    } finally {
      setExtractingExp(false);
    }
  };

  const handleAddExperience = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('experience');
  };

  const handleDeleteExperience = async (id) => {
    try {
      await profileApi.deleteExperience(id);
      await loadProfileAndResumes(true);
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
    e?.preventDefault?.();
    await handleTabSave('experience');
  };

  // Education & Certification handlers
  const handleAddEducation = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('education');
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
    e?.preventDefault?.();
    await handleTabSave('education');
  };

  const handleDeleteEducation = async (id) => {
    try {
      await profileApi.deleteEducation(id);
      await loadProfileAndResumes(true);
      setFeedbackMsg({ type: 'success', text: 'Education record removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete education.' });
    }
  };

  const handleAddCert = async (e) => {
    e?.preventDefault?.();
    await handleTabSave('certifications');
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
    e?.preventDefault?.();
    await handleTabSave('certifications');
  };

  const handleDeleteCert = async (id) => {
    try {
      await profileApi.deleteCertification(id);
      await loadProfileAndResumes(true);
      setFeedbackMsg({ type: 'success', text: 'Certification removed.' });
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Failed to delete certification.' });
    }
  };

  const handleOpenReview = async (resumeId) => {
    setLoadingReview(true);
    try {
      const data = await profileApi.getResumeExtractedData(resumeId);
      setReviewResumeData(data);
      setIsReviewModalOpen(true);
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to load extraction details.' });
    } finally {
      setLoadingReview(false);
    }
  };

  const handleResumeUpload = async (e, replace = false) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setFeedbackMsg({
        type: 'error',
        text: 'Only PDF resume files are accepted. Please select a .pdf document.',
      });
      e.target.value = '';
      return;
    }

    setUploading(true);
    setUploadStage('Uploading resume file...');
    setFeedbackMsg({ type: '', text: '' });

    try {
      const result = await profileApi.uploadResume(file, replace);
      const resumeId = result.resume_id;
      setUploadStage('Queued for processing...');

      // Poll real processing stages from backend
      let statusData = null;
      const startTime = Date.now();
      const MAX_POLL_TIME = 90000; // 90 seconds timeout

      while (Date.now() - startTime < MAX_POLL_TIME) {
        await new Promise((r) => setTimeout(r, 1200));
        statusData = await profileApi.getResumeStatus(resumeId);
        if (statusData?.parse_stage) {
          setUploadStage(statusData.parse_stage);
        }
        if (statusData?.parse_status === 'complete') {
          break;
        }
        if (statusData?.parse_status === 'failed') {
          throw new Error(statusData.parse_error || 'Failed to parse resume PDF.');
        }
      }

      if (!statusData || statusData.parse_status !== 'complete') {
        throw new Error('Resume parsing timed out. Please try again.');
      }

      setUploadStage('Complete! Loading review...');
      setFeedbackMsg({
        type: 'success',
        text: replace
          ? `Replaced Master Resume with "${result.filename}". Review extracted information below.`
          : `Parsed "${result.filename}". Review extracted information below.`,
      });
      await loadProfileAndResumes();

      if (isFromOnboarding) {
        showSuccess('Master resume uploaded and processed successfully! Welcome to your Workspace.');
        if (onReturnToWorkspace) {
          onReturnToWorkspace({ stage: 1 });
        }
        return;
      }

      const extData = await profileApi.getResumeExtractedData(resumeId);
      if (extData?.extracted_data) {
        setReviewResumeData(extData);
        setIsReviewModalOpen(true);
      }
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to upload resume.' });
    } finally {
      setUploading(false);
      setUploadStage('');
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
    <div className="space-y-3 sm:space-y-3.5">
      {/* Onboarding Welcome Navigation Notice if from onboarding */}
      {isFromOnboarding && (
        <div className="card-brutal bg-coral-subtle/30 border-coral p-2.5 sm:p-3 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="font-bold text-coral-dark uppercase tracking-wide">First-Time Setup:</span>
            <span className="text-charcoal font-medium">Upload your Master Resume PDF below to populate your profile.</span>
          </div>
          <button
            onClick={() => {
              if (onReturnToWorkspace) onReturnToWorkspace({ stage: 1 });
            }}
            className="btn-secondary text-xs px-2.5 py-1 bg-white hover:bg-cream flex items-center space-x-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>← Go to Workspace (Stage 1)</span>
          </button>
        </div>
      )}

      {/* Evidence Target Navigation Banner */}
      {effectiveEvidenceTarget && (
        <div className="card-brutal bg-amber-50 border-amber-300 p-2.5 sm:p-3 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="font-bold text-amber-900 uppercase tracking-wide">Evidence Review:</span>
            <span className="text-charcoal font-medium">{effectiveEvidenceTarget.itemValue}</span>
            {effectiveEvidenceTarget.jobTitle && (
              <span className="text-charcoal-muted">
                for {effectiveEvidenceTarget.jobTitle}{effectiveEvidenceTarget.company ? ` @ ${effectiveEvidenceTarget.company}` : ''}
              </span>
            )}
          </div>
          <button
            onClick={() => {
              const returnContext = {
                stage: effectiveEvidenceTarget?.stage || 3,
                jobId: effectiveEvidenceTarget?.jobId || null,
              };
              if (clearEvidenceTarget) clearEvidenceTarget();
              if (onReturnToWorkspace) onReturnToWorkspace(returnContext);
            }}
            className="btn-secondary text-xs px-2.5 py-1 bg-white hover:bg-amber-100 flex items-center space-x-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>← Return to Workspace (Stage {effectiveEvidenceTarget?.stage || 3})</span>
          </button>
        </div>
      )}

      {/* Master Resume Upload Banner */}
      <MasterResumeBanner
        resumes={resumes}
        uploading={uploading}
        uploadStage={uploadStage}
        loadingReview={loadingReview}
        handleResumeUpload={handleResumeUpload}
        handleOpenReview={handleOpenReview}
        handleDeleteResume={handleDeleteResume}
        feedbackMsg={feedbackMsg}
        setFeedbackMsg={setFeedbackMsg}
      />

      {/* Main Profile Tabs & Editor */}
      <div className="card-brutal p-3.5 sm:p-4 space-y-3">
        <ProfileHeader
          handleResetAll={handleResetAll}
          savingTab={savingTab}
        />

        <ProfileTabs
          sections={sections}
          activeSection={activeSection}
          setActiveSection={setActiveSection}
          hasTabActiveContent={hasTabActiveContent}
          handleTabReset={handleTabReset}
          handleTabSave={handleTabSave}
          savingTab={savingTab}
        />

        {/* Tab 1: Personal Info */}
        {activeSection === 'personal' && (
          <PersonalInfoTab
            isEditingPersonal={isEditingPersonal}
            setIsEditingPersonal={setIsEditingPersonal}
            personalForm={personalForm}
            setPersonalForm={setPersonalForm}
            phoneCountryCode={phoneCountryCode}
            setPhoneCountryCode={setPhoneCountryCode}
            phoneDigits={phoneDigits}
            setPhoneDigits={setPhoneDigits}
            handleUpdatePersonal={handleUpdatePersonal}
            handleCancelPersonalEdit={handleCancelPersonalEdit}
            countryCodes={COUNTRY_CODES}
          />
        )}

        {/* Tab 2: Skills */}
        {activeSection === 'skills' && (
          <SkillsTab
            newSkill={newSkill}
            setNewSkill={setNewSkill}
            handleAddSkill={handleAddSkill}
            skills={profile?.skills}
            handleDeleteSkill={handleDeleteSkill}
          />
        )}

        {/* Tab 3: Projects */}
        {activeSection === 'projects' && (
          <ProjectsTab
            projectMode={projectMode}
            setProjectMode={setProjectMode}
            githubProjectUrl={githubProjectUrl}
            setGithubProjectUrl={setGithubProjectUrl}
            extractingProject={extractingProject}
            handleExtractGitHubProject={handleExtractGitHubProject}
            extractedProject={extractedProject}
            setExtractedProject={setExtractedProject}
            handleSaveExtractedProject={handleSaveExtractedProject}
            newProject={newProject}
            setNewProject={setNewProject}
            handleAddManualProject={handleAddManualProject}
            projects={profile?.projects}
            editingProjectId={editingProjectId}
            setEditingProjectId={setEditingProjectId}
            editProjectForm={editProjectForm}
            setEditProjectForm={setEditProjectForm}
            handleStartEditProject={handleStartEditProject}
            handleSaveEditProject={handleSaveEditProject}
            handleDeleteProject={handleDeleteProject}
          />
        )}

        {/* Tab 4: Experience */}
        {activeSection === 'experience' && (
          <ExperienceTab
            experienceMode={experienceMode}
            setExperienceMode={setExperienceMode}
            githubExpUrl={githubExpUrl}
            setGithubExpUrl={setGithubExpUrl}
            extractingExp={extractingExp}
            handleExtractGitHubExp={handleExtractGitHubExp}
            newExperience={newExperience}
            setNewExperience={setNewExperience}
            handleAddExperience={handleAddExperience}
            experiences={profile?.experiences}
            editingExpId={editingExpId}
            setEditingExpId={setEditingExpId}
            editExpForm={editExpForm}
            setEditExpForm={setEditExpForm}
            handleStartEditExperience={handleStartEditExperience}
            handleSaveEditExperience={handleSaveEditExperience}
            handleDeleteExperience={handleDeleteExperience}
          />
        )}

        {/* Tab 5: Education */}
        {activeSection === 'education' && (
          <EducationTab
            newEducation={newEducation}
            setNewEducation={setNewEducation}
            handleAddEducation={handleAddEducation}
            educations={profile?.educations}
            editingEduId={editingEduId}
            setEditingEduId={setEditingEduId}
            editEduForm={editEduForm}
            setEditEduForm={setEditEduForm}
            handleStartEditEducation={handleStartEditEducation}
            handleSaveEditEducation={handleSaveEditEducation}
            handleDeleteEducation={handleDeleteEducation}
          />
        )}

        {/* Tab 6: Certifications */}
        {activeSection === 'certifications' && (
          <CertificationsTab
            newCert={newCert}
            setNewCert={setNewCert}
            handleAddCert={handleAddCert}
            certifications={profile?.certifications}
            editingCertId={editingCertId}
            setEditingCertId={setEditingCertId}
            editCertForm={editCertForm}
            setEditCertForm={setEditCertForm}
            handleStartEditCert={handleStartEditCert}
            handleSaveEditCert={handleSaveEditCert}
            handleDeleteCert={handleDeleteCert}
          />
        )}
      </div>

      {/* Reset Confirmation Dialog Modal */}
      {confirmDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal/50 p-4">
          <div className="bg-white border-2 border-charcoal p-6 shadow-brutal max-w-sm sm:max-w-md w-full space-y-4 font-sans">
            <div className="flex items-center space-x-2.5 text-charcoal">
              <AlertCircle className="w-5 h-5 text-amber-500 shrink-0" />
              <h3 className="font-bold text-base text-charcoal">{confirmDialog.title}</h3>
            </div>
            <p className="text-xs text-charcoal-muted leading-relaxed font-mono">
              {confirmDialog.message}
            </p>
            <div className="pt-2 flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setConfirmDialog(null)}
                className="btn-secondary text-xs py-2 px-4"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  const action = confirmDialog.onConfirm;
                  setConfirmDialog(null);
                  if (action) action();
                }}
                className="btn-primary bg-coral hover:bg-coral-dark text-white text-xs py-2 px-4"
              >
                {confirmDialog.confirmLabel || 'Confirm Reset'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Review Extraction Modal */}
      <ReviewExtractionModal
        isOpen={isReviewModalOpen}
        onClose={() => setIsReviewModalOpen(false)}
        resumeData={reviewResumeData}
        onApplied={async (summary) => {
          await loadProfileAndResumes();
          setFeedbackMsg({
            type: 'success',
            text: summary.message || 'Extracted data successfully applied to candidate profile.',
          });
          showSuccess(
            `Profile updated: Added ${summary.counts?.skills_added || 0} skills, ${summary.counts?.projects_added || 0} projects, and updated contact info.`
          );
        }}
      />
    </div>
  );
}
