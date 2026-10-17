import React, { useState, useEffect } from 'react';
import {
  Upload,
  Sparkles,
  ArrowRight,
  FileCode,
  Briefcase,
  AlertCircle,
  Building,
  MapPin,
  DollarSign,
  Link as LinkIcon,
  CheckCircle2,
  ListFilter,
  FileText,
} from 'lucide-react';
import { jobsApi } from '../api/jobs';
import { profileApi } from '../api/profile';

export default function WorkspacePage({ currentUser }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [resumes, setResumes] = useState([]);
  const [profile, setProfile] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [activeJob, setActiveJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Job form state
  const [jobForm, setJobForm] = useState({
    company: '',
    title: '',
    location: '',
    salary: '',
    job_url: '',
    raw_jd_text: '',
  });

  const steps = [
    { num: 1, label: '1. Add Inputs', desc: 'Master Resume & Job Description' },
    { num: 2, label: '2. Analyze JD', desc: 'Structured Requirements Extraction' },
    { num: 3, label: '3. Match Evidence', desc: 'Deterministic Skill Alignment' },
    { num: 4, label: '4. Tailor Resume', desc: 'Section Editing & AI Consultation' },
    { num: 5, label: '5. Validate & PDF', desc: 'LaTeX Compilation & Quality Gate' },
  ];

  useEffect(() => {
    if (currentUser) {
      loadWorkspaceContext();
    }
  }, [currentUser]);

  const loadWorkspaceContext = async () => {
    setLoading(true);
    try {
      const [resumesData, profileData, jobsData] = await Promise.all([
        profileApi.getResumes(),
        profileApi.getProfile(),
        jobsApi.listJobs(),
      ]);
      setResumes(resumesData);
      setProfile(profileData);
      setSavedJobs(jobsData);
      if (jobsData.length > 0 && !activeJob) {
        setActiveJob(jobsData[0]);
      }
    } catch (err) {
      setErrorMsg('Failed to load workspace data.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitJob = async (e) => {
    e.preventDefault();
    if (!jobForm.company.trim() || !jobForm.title.trim() || !jobForm.raw_jd_text.trim()) {
      setErrorMsg('Please fill in Company, Job Title, and the Job Description.');
      return;
    }

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const created = await jobsApi.createJob(jobForm);
      setActiveJob(created);
      setSavedJobs([created, ...savedJobs]);
      setSuccessMsg(`Target job "${created.title} at ${created.company}" saved successfully.`);
      // Advance to next stage (Stage 2: JD Analysis)
      setCurrentStep(2);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save job description.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSelectJob = (job) => {
    setActiveJob(job);
    setJobForm({
      company: job.company,
      title: job.title,
      location: job.location || '',
      salary: job.salary || '',
      job_url: job.job_url || '',
      raw_jd_text: job.raw_jd_text,
    });
  };

  if (!currentUser) {
    return (
      <div className="card-brutal text-center py-12 space-y-4">
        <AlertCircle className="w-12 h-12 text-coral mx-auto" />
        <h2 className="text-xl font-bold text-charcoal">Authentication Required</h2>
        <p className="text-sm text-charcoal-muted max-w-md mx-auto">
          Please sign in to access the progressive tailoring workspace.
        </p>
      </div>
    );
  }

  const activeMasterResume = resumes.length > 0 ? resumes[0] : null;

  return (
    <div className="space-y-6">
      {/* Workflow Stepper Header */}
      <div className="bg-white border-2 border-charcoal p-4 shadow-brutal-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-charcoal-muted">
              Active Workflow:
            </span>
            <span className="badge-tag bg-coral-light text-coral border-coral">
              {activeJob ? `${activeJob.title} @ ${activeJob.company}` : 'New Target Job'}
            </span>
          </div>
          <div className="flex items-center space-x-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
            {steps.map((s) => (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`px-3 py-1.5 text-xs font-medium border flex items-center space-x-1.5 transition-all whitespace-nowrap ${
                  currentStep === s.num
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stage 1: Add Inputs */}
      {currentStep === 1 && (
        <div className="space-y-6">
          <div className="card-brutal space-y-6">
            <div className="border-b border-cream-border pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div>
                <h2 className="text-xl font-bold tracking-tight text-charcoal">
                  Stage 1: Job Description & Master Resume Intake
                </h2>
                <p className="text-sm text-charcoal-muted mt-1">
                  Connect your verified candidate evidence with a target job description. The engine extracts requirements without hallucinating claims.
                </p>
              </div>
              {savedJobs.length > 0 && (
                <div className="text-xs font-mono">
                  <span className="text-charcoal-muted">Saved Jobs: </span>
                  <span className="font-bold">{savedJobs.length}</span>
                </div>
              )}
            </div>

            {errorMsg && (
              <div className="bg-rose-50 border-2 border-rose-500 text-rose-800 p-3 text-xs font-mono">
                {errorMsg}
              </div>
            )}

            {successMsg && (
              <div className="bg-emerald-50 border-2 border-emerald-500 text-emerald-800 p-3 text-xs font-mono">
                {successMsg}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Master Resume & Profile Snapshot */}
              <div className="space-y-4">
                <div className="border-2 border-charcoal bg-cream p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-xs text-charcoal uppercase tracking-wider flex items-center space-x-2">
                      <FileCode className="w-4 h-4 text-coral" />
                      <span>Active Master Resume</span>
                    </h3>
                    <span className={`badge-tag ${activeMasterResume ? 'bg-emerald-100 text-emerald-900 border-emerald-500' : 'bg-amber-100 text-amber-900 border-amber-500'}`}>
                      {activeMasterResume ? 'Ready' : 'Missing'}
                    </span>
                  </div>

                  {activeMasterResume ? (
                    <div className="bg-white border border-charcoal p-3 text-xs font-mono space-y-2">
                      <div className="flex justify-between">
                        <span className="text-charcoal-muted">File:</span>
                        <span className="font-bold truncate max-w-[150px]">{activeMasterResume.filename}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-charcoal-muted">Verified Skills:</span>
                        <span className="font-bold text-emerald-700">{profile?.skills?.length || 0} skills</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-charcoal-muted">Projects:</span>
                        <span className="font-bold">{profile?.projects?.length || 0} projects</span>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 bg-white border border-charcoal text-xs space-y-2">
                      <p className="text-amber-800">
                        No master resume PDF uploaded yet. Go to the <strong>Profile</strong> tab to upload your source resume.
                      </p>
                    </div>
                  )}
                </div>

                {/* Saved Target Jobs Selector */}
                {savedJobs.length > 0 && (
                  <div className="border-2 border-charcoal bg-white p-4 space-y-3">
                    <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1">
                      <ListFilter className="w-3.5 h-3.5" />
                      <span>Load Previously Saved Job</span>
                    </h4>
                    <div className="space-y-1.5 max-h-48 overflow-y-auto">
                      {savedJobs.map((j) => (
                        <button
                          key={j.id}
                          onClick={() => handleSelectJob(j)}
                          className={`w-full text-left p-2 border text-xs font-mono transition-all flex items-center justify-between ${
                            activeJob?.id === j.id
                              ? 'bg-charcoal text-white border-charcoal'
                              : 'bg-cream hover:bg-cream-muted border-cream-border'
                          }`}
                        >
                          <span className="truncate">{j.title} ({j.company})</span>
                          <span className="text-[10px] opacity-70">#{j.id}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column (2 cols): Target Job Description Input Form */}
              <div className="lg:col-span-2 border-2 border-charcoal bg-white p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-cream-border pb-3">
                  <h3 className="font-bold text-sm text-charcoal uppercase tracking-wider flex items-center space-x-2">
                    <Briefcase className="w-4 h-4 text-coral" />
                    <span>Target Opportunity Details</span>
                  </h3>
                  <span className="badge-tag bg-cream-muted text-charcoal">Epic 3</span>
                </div>

                <form onSubmit={handleSubmitJob} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">
                        Company Name *
                      </label>
                      <input
                        type="text"
                        value={jobForm.company}
                        onChange={(e) => setJobForm({ ...jobForm, company: e.target.value })}
                        placeholder="e.g. Stripe, OpenAI, Microsoft"
                        className="w-full border-2 border-charcoal p-2 text-sm"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">
                        Job Title *
                      </label>
                      <input
                        type="text"
                        value={jobForm.title}
                        onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })}
                        placeholder="e.g. Senior Software Engineer"
                        className="w-full border-2 border-charcoal p-2 text-sm"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">
                        Location (Optional)
                      </label>
                      <input
                        type="text"
                        value={jobForm.location}
                        onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })}
                        placeholder="e.g. San Francisco or Remote"
                        className="w-full border-2 border-charcoal p-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">
                        Salary / CTC (Optional)
                      </label>
                      <input
                        type="text"
                        value={jobForm.salary}
                        onChange={(e) => setJobForm({ ...jobForm, salary: e.target.value })}
                        placeholder="e.g. $140k - $170k"
                        className="w-full border-2 border-charcoal p-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">
                        Job Posting URL (Optional)
                      </label>
                      <input
                        type="url"
                        value={jobForm.job_url}
                        onChange={(e) => setJobForm({ ...jobForm, job_url: e.target.value })}
                        placeholder="https://company.com/jobs/..."
                        className="w-full border-2 border-charcoal p-2 text-sm"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-mono uppercase text-charcoal-muted mb-1">
                      Raw Job Description *
                    </label>
                    <textarea
                      rows={8}
                      value={jobForm.raw_jd_text}
                      onChange={(e) => setJobForm({ ...jobForm, raw_jd_text: e.target.value })}
                      placeholder="Paste full job description text here (Responsibilities, Required Skills, Preferred Qualifications, Technology Stack)..."
                      className="w-full border-2 border-charcoal p-3 text-xs font-mono bg-cream focus:outline-none focus:ring-2 focus:ring-coral"
                      required
                    />
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      disabled={submitting}
                      className="btn-primary flex items-center space-x-2"
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>{submitting ? 'Saving Job...' : 'Save & Analyze Job Description'}</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stage 2 Preview: Job Analysis (Epic 4 Anchor) */}
      {currentStep === 2 && (
        <div className="card-brutal space-y-6">
          <div className="border-b border-cream-border pb-4 flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold tracking-tight text-charcoal">
                Stage 2: Job Description Analysis (Ollama Engine)
              </h2>
              <p className="text-xs text-charcoal-muted mt-1">
                Target: <strong>{activeJob?.title}</strong> at <strong>{activeJob?.company}</strong>
              </p>
            </div>
            <button onClick={() => setCurrentStep(1)} className="btn-secondary text-xs">
              ← Back to Stage 1
            </button>
          </div>

          <div className="bg-cream border-2 border-charcoal p-6 space-y-4 font-mono text-xs">
            <div className="flex items-center space-x-2">
              <span className="badge-tag bg-coral-light text-coral border-coral">Coming in Epic 4</span>
              <span className="font-bold text-charcoal">Structured Requirements Extraction</span>
            </div>
            <p className="text-charcoal-muted">
              In Epic 4, the local Ollama provider abstraction extracts required vs preferred skills, languages, frameworks, responsibilities, and qualifications into relational entities.
            </p>
            <div className="p-3 bg-white border border-charcoal">
              <div className="font-bold mb-1">Target Raw JD Preview:</div>
              <p className="truncate text-charcoal-light">{activeJob?.raw_jd_text || 'No JD selected'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Stages 3 to 5 placeholders */}
      {currentStep > 2 && (
        <div className="card-brutal text-center py-12 space-y-3 font-mono">
          <p className="text-sm font-bold text-charcoal">Stage {currentStep}: Upcoming Epic Workflow</p>
          <p className="text-xs text-charcoal-muted">Progressive workflow stage will activate as subsequent epics are implemented.</p>
          <button onClick={() => setCurrentStep(1)} className="btn-secondary text-xs mt-2">
            Return to Stage 1
          </button>
        </div>
      )}
    </div>
  );
}
