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
  Layers,
  Code2,
  Database,
  Cloud,
  Wrench,
  Check,
} from 'lucide-react';
import { jobsApi } from '../api/jobs';
import { profileApi } from '../api/profile';

export default function WorkspacePage({ currentUser }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [resumes, setResumes] = useState([]);
  const [profile, setProfile] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [activeJob, setActiveJob] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [matchData, setMatchData] = useState(null);

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [matching, setMatching] = useState(false);
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

  useEffect(() => {
    if (activeJob) {
      loadJobAnalysis(activeJob.id);
      loadJobMatch(activeJob.id);
    }
  }, [activeJob]);

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

  const loadJobAnalysis = async (jobId) => {
    try {
      const data = await jobsApi.getJobAnalysis(jobId);
      setAnalysis(data);
    } catch (err) {
      setAnalysis(null);
    }
  };

  const loadJobMatch = async (jobId) => {
    try {
      const data = await jobsApi.getJobMatch(jobId);
      setMatchData(data);
    } catch (err) {
      setMatchData(null);
    }
  };

  const handleTriggerMatch = async () => {
    if (!activeJob) return;
    setMatching(true);
    setErrorMsg('');
    try {
      const data = await jobsApi.matchJob(activeJob.id);
      setMatchData(data);
      setSuccessMsg(`Evidence alignment complete: ${data.estimated_match_score}% Estimated Job Match.`);
    } catch (err) {
      setErrorMsg(err.message || 'Evidence matching failed.');
    } finally {
      setMatching(false);
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
      
      // Trigger analysis immediately
      setAnalyzing(true);
      setCurrentStep(2);
      const anaData = await jobsApi.analyzeJob(created.id);
      setAnalysis(anaData);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save or analyze job description.');
    } finally {
      setSubmitting(false);
      setAnalyzing(false);
    }
  };

  const handleTriggerAnalysis = async () => {
    if (!activeJob) return;
    setAnalyzing(true);
    setErrorMsg('');
    try {
      const data = await jobsApi.analyzeJob(activeJob.id);
      setAnalysis(data);
      setSuccessMsg('Job description analyzed successfully.');
    } catch (err) {
      setErrorMsg(err.message || 'Analysis failed.');
    } finally {
      setAnalyzing(false);
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

              {/* Right Column: Target Job Description Input Form */}
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

      {/* Stage 2: Job Description Analysis (Epic 4) */}
      {currentStep === 2 && (
        <div className="card-brutal space-y-6">
          <div className="border-b border-cream-border pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <span className="badge-tag bg-coral-light text-coral border-coral font-bold">Stage 2</span>
                <h2 className="text-xl font-bold tracking-tight text-charcoal">
                  Structured Job Requirements
                </h2>
              </div>
              <p className="text-xs text-charcoal-muted mt-1">
                Target: <strong>{activeJob?.title}</strong> at <strong>{activeJob?.company}</strong>
                {analysis?.experience_years ? ` · Level: ${analysis.experience_years}` : ''}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleTriggerAnalysis}
                disabled={analyzing}
                className="btn-secondary text-xs flex items-center space-x-1"
              >
                <Sparkles className="w-3.5 h-3.5 text-coral" />
                <span>{analyzing ? 'Extracting...' : 'Re-analyze JD'}</span>
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="btn-primary text-xs flex items-center space-x-1.5"
              >
                <span>Proceed to Evidence Match</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {analyzing && (
            <div className="bg-cream border-2 border-charcoal p-8 text-center space-y-3 font-mono">
              <Sparkles className="w-8 h-8 text-coral animate-spin mx-auto" />
              <div className="font-bold text-sm">Ollama Local Engine Extracting Requirements...</div>
              <p className="text-xs text-charcoal-muted">Parsing technical skills, frameworks, databases, and responsibilities without hallucinating claims.</p>
            </div>
          )}

          {!analyzing && !analysis && (
            <div className="p-8 text-center space-y-4 bg-cream border-2 border-charcoal">
              <p className="text-sm font-mono text-charcoal">No structured analysis has been generated yet for this job.</p>
              <button onClick={handleTriggerAnalysis} className="btn-primary">
                Analyze This Job Description
              </button>
            </div>
          )}

          {!analyzing && analysis && (
            <div className="space-y-6">
              {/* Top Row: Required vs Preferred Skills */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border-2 border-charcoal p-4 bg-white space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                      <span className="w-2.5 h-2.5 bg-coral inline-block"></span>
                      <span>Required Skills ({analysis.required_skills?.length || 0})</span>
                    </h3>
                    <span className="badge-tag bg-coral-light text-coral border-coral">Core</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.required_skills?.map((sk, i) => (
                      <span key={i} className="badge-tag bg-white border-charcoal font-semibold">
                        {sk}
                      </span>
                    ))}
                    {(!analysis.required_skills || analysis.required_skills.length === 0) && (
                      <p className="text-xs text-charcoal-muted">No explicit required skills listed.</p>
                    )}
                  </div>
                </div>

                <div className="border-2 border-charcoal p-4 bg-cream space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                      <span className="w-2.5 h-2.5 bg-charcoal inline-block"></span>
                      <span>Preferred / Good-to-Have Skills ({analysis.preferred_skills?.length || 0})</span>
                    </h3>
                    <span className="badge-tag bg-white">Bonus</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.preferred_skills?.map((sk, i) => (
                      <span key={i} className="badge-tag bg-white border-cream-border">
                        {sk}
                      </span>
                    ))}
                    {(!analysis.preferred_skills || analysis.preferred_skills.length === 0) && (
                      <p className="text-xs text-charcoal-muted">No preferred skills listed.</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Technical Stack Breakdown */}
              <div className="border-2 border-charcoal p-5 bg-white space-y-4">
                <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal">
                  Categorized Technical Stack
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 font-mono text-xs">
                  <div className="border border-cream-border p-3 space-y-2 bg-cream">
                    <div className="font-bold flex items-center space-x-1 text-charcoal">
                      <Code2 className="w-3.5 h-3.5 text-coral" />
                      <span>Languages</span>
                    </div>
                    <div className="space-y-1">
                      {analysis.languages?.map((item, idx) => (
                        <div key={idx} className="truncate">• {item}</div>
                      ))}
                      {(!analysis.languages || analysis.languages.length === 0) && (
                        <span className="text-charcoal-light">None listed</span>
                      )}
                    </div>
                  </div>

                  <div className="border border-cream-border p-3 space-y-2 bg-cream">
                    <div className="font-bold flex items-center space-x-1 text-charcoal">
                      <Layers className="w-3.5 h-3.5 text-coral" />
                      <span>Frameworks</span>
                    </div>
                    <div className="space-y-1">
                      {analysis.frameworks?.map((item, idx) => (
                        <div key={idx} className="truncate">• {item}</div>
                      ))}
                      {(!analysis.frameworks || analysis.frameworks.length === 0) && (
                        <span className="text-charcoal-light">None listed</span>
                      )}
                    </div>
                  </div>

                  <div className="border border-cream-border p-3 space-y-2 bg-cream">
                    <div className="font-bold flex items-center space-x-1 text-charcoal">
                      <Database className="w-3.5 h-3.5 text-coral" />
                      <span>Databases</span>
                    </div>
                    <div className="space-y-1">
                      {analysis.databases?.map((item, idx) => (
                        <div key={idx} className="truncate">• {item}</div>
                      ))}
                      {(!analysis.databases || analysis.databases.length === 0) && (
                        <span className="text-charcoal-light">None listed</span>
                      )}
                    </div>
                  </div>

                  <div className="border border-cream-border p-3 space-y-2 bg-cream">
                    <div className="font-bold flex items-center space-x-1 text-charcoal">
                      <Cloud className="w-3.5 h-3.5 text-coral" />
                      <span>Cloud & Infra</span>
                    </div>
                    <div className="space-y-1">
                      {analysis.cloud?.map((item, idx) => (
                        <div key={idx} className="truncate">• {item}</div>
                      ))}
                      {(!analysis.cloud || analysis.cloud.length === 0) && (
                        <span className="text-charcoal-light">None listed</span>
                      )}
                    </div>
                  </div>

                  <div className="border border-cream-border p-3 space-y-2 bg-cream">
                    <div className="font-bold flex items-center space-x-1 text-charcoal">
                      <Wrench className="w-3.5 h-3.5 text-coral" />
                      <span>Tools & DevOps</span>
                    </div>
                    <div className="space-y-1">
                      {analysis.tools?.map((item, idx) => (
                        <div key={idx} className="truncate">• {item}</div>
                      ))}
                      {(!analysis.tools || analysis.tools.length === 0) && (
                        <span className="text-charcoal-light">None listed</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Responsibilities & Qualifications */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border-2 border-charcoal p-4 bg-white space-y-3">
                  <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal">
                    Key Job Responsibilities
                  </h3>
                  <ul className="space-y-2 text-xs">
                    {analysis.responsibilities?.map((resp, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-coral mt-0.5">•</span>
                        <span className="text-charcoal">{resp}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="border-2 border-charcoal p-4 bg-white space-y-3">
                  <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal">
                    Minimum Qualifications & Experience
                  </h3>
                  <div className="p-2.5 bg-cream border border-charcoal font-mono text-xs font-bold text-charcoal mb-2">
                    Experience Level: {analysis.experience_years || 'Not specified'}
                  </div>
                  <ul className="space-y-2 text-xs">
                    {analysis.qualifications?.map((qual, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <Check className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                        <span className="text-charcoal">{qual}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <button onClick={() => setCurrentStep(1)} className="btn-secondary text-xs">
                  ← Back to Job Description
                </button>
                <button
                  onClick={async () => {
                    setCurrentStep(3);
                    if (activeJob && !matchData) {
                      await handleTriggerMatch();
                    }
                  }}
                  className="btn-primary flex items-center space-x-2"
                >
                  <span>Proceed to Stage 3: Evidence Matching</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Stage 3: Resume-to-Job Evidence Matching (Epic 5) */}
      {currentStep === 3 && (
        <div className="card-brutal space-y-6">
          <div className="border-b border-cream-border pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <span className="badge-tag bg-coral-light text-coral border-coral font-bold">Stage 3</span>
                <h2 className="text-xl font-bold tracking-tight text-charcoal">
                  Resume-to-Job Evidence Alignment
                </h2>
              </div>
              <p className="text-xs text-charcoal-muted mt-1">
                Comparing verified candidate profile evidence against target requirements for <strong>{activeJob?.title}</strong>.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleTriggerMatch}
                disabled={matching}
                className="btn-secondary text-xs flex items-center space-x-1"
              >
                <Sparkles className="w-3.5 h-3.5 text-coral" />
                <span>{matching ? 'Calculating...' : 'Re-run Match'}</span>
              </button>
              <button
                onClick={() => setCurrentStep(4)}
                className="btn-primary text-xs flex items-center space-x-1.5"
              >
                <span>Proceed to Tailoring</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {matching && (
            <div className="bg-cream border-2 border-charcoal p-8 text-center space-y-3 font-mono">
              <Sparkles className="w-8 h-8 text-coral animate-spin mx-auto" />
              <div className="font-bold text-sm">Deterministic Matching Engine Computing Alignment...</div>
              <p className="text-xs text-charcoal-muted">Verifying project backing, experience citations, and flagging unsupported claims.</p>
            </div>
          )}

          {!matching && !matchData && (
            <div className="p-8 text-center space-y-4 bg-cream border-2 border-charcoal">
              <p className="text-sm font-mono text-charcoal">No match analysis available yet for this target job.</p>
              <button onClick={handleTriggerMatch} className="btn-primary">
                Run Evidence Match Alignment
              </button>
            </div>
          )}

          {!matching && matchData && (
            <div className="space-y-6">
              {/* Estimated Job Match Metric Banner */}
              <div className="border-2 border-charcoal bg-white p-6 shadow-brutal flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="space-y-1">
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-charcoal-muted">
                    Deterministic Metric (Not an ATS Score)
                  </div>
                  <div className="text-2xl font-bold text-charcoal">
                    Estimated Job Match
                  </div>
                  <p className="text-xs text-charcoal-muted max-w-md">
                    Calculated by cross-referencing required (70% weight) and preferred (30% weight) job skills against candidate projects and experience.
                  </p>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-center p-4 bg-cream border-2 border-charcoal shadow-brutal-sm">
                    <div className="text-4xl font-extrabold text-coral font-mono">
                      {matchData.estimated_match_score}%
                    </div>
                    <div className="text-[10px] font-mono uppercase tracking-wider text-charcoal-muted mt-1">
                      Evidence Match
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="bg-emerald-50 border border-emerald-600 p-2 text-emerald-950">
                      <span className="font-bold">{matchData.matched_skills?.length || 0}</span> Matched
                    </div>
                    <div className="bg-amber-50 border border-amber-600 p-2 text-amber-950">
                      <span className="font-bold">{matchData.weak_skills?.length || 0}</span> Weak
                    </div>
                    <div className="bg-rose-50 border border-rose-600 p-2 text-rose-950">
                      <span className="font-bold">{matchData.missing_skills?.length || 0}</span> Missing
                    </div>
                    <div className="bg-purple-50 border border-purple-600 p-2 text-purple-950">
                      <span className="font-bold">{matchData.unsupported_claims?.length || 0}</span> Unsupported
                    </div>
                  </div>
                </div>
              </div>

              {/* 4 Categorized Columns / Sections */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 1. Matched Skills */}
                <div className="border-2 border-charcoal bg-white p-5 space-y-3">
                  <div className="flex items-center justify-between border-b border-cream-border pb-2">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-emerald-800 flex items-center space-x-1.5">
                      <Check className="w-4 h-4 text-emerald-600" />
                      <span>Matched Skills ({matchData.matched_skills?.length || 0})</span>
                    </h3>
                    <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600">Verified Evidence</span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Directly evidenced by candidate projects or verified employment records. Click to view evidence drawer:
                  </p>
                  <div className="space-y-2">
                    {matchData.matched_skills?.map((sk, i) => (
                      <div key={i} className="border border-charcoal bg-cream p-2.5 text-xs font-mono">
                        <div className="flex justify-between items-center font-bold text-charcoal">
                          <span>{sk}</span>
                          <span className="text-[10px] text-emerald-700 bg-emerald-100 px-1.5 py-0.5 border border-emerald-500">
                            Backed by Evidence
                          </span>
                        </div>
                        {matchData.evidence_map?.[sk] && (
                          <div className="mt-1 text-[11px] text-charcoal-muted border-t border-cream-border pt-1">
                            {matchData.evidence_map[sk].map((src, idx) => (
                              <div key={idx}>↳ {src}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. Weakly Represented Skills */}
                <div className="border-2 border-charcoal bg-white p-5 space-y-3">
                  <div className="flex items-center justify-between border-b border-cream-border pb-2">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-amber-800 flex items-center space-x-1.5">
                      <AlertCircle className="w-4 h-4 text-amber-600" />
                      <span>Weakly Represented Skills ({matchData.weak_skills?.length || 0})</span>
                    </h3>
                    <span className="badge-tag bg-amber-50 text-amber-900 border-amber-600">Needs Evidence</span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Present in your profile or mentioned in text, but lacks a linked project or work history accomplishment.
                  </p>
                  <div className="space-y-2">
                    {matchData.weak_skills?.map((sk, i) => (
                      <div key={i} className="border border-amber-500 bg-amber-50/50 p-2.5 text-xs font-mono">
                        <div className="font-bold text-charcoal">{sk}</div>
                        {matchData.evidence_map?.[sk] && (
                          <div className="mt-1 text-[11px] text-charcoal-muted">
                            {matchData.evidence_map[sk].map((src, idx) => (
                              <div key={idx}>↳ {src}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                    {(!matchData.weak_skills || matchData.weak_skills.length === 0) && (
                      <p className="text-xs text-charcoal-muted">None detected.</p>
                    )}
                  </div>
                </div>

                {/* 3. Missing Skills */}
                <div className="border-2 border-charcoal bg-white p-5 space-y-3">
                  <div className="flex items-center justify-between border-b border-cream-border pb-2">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-rose-800 flex items-center space-x-1.5">
                      <AlertCircle className="w-4 h-4 text-rose-600" />
                      <span>Missing Skills ({matchData.missing_skills?.length || 0})</span>
                    </h3>
                    <span className="badge-tag bg-rose-50 text-rose-900 border-rose-600">Gaps</span>
                  </div>
                  <div className="p-2.5 bg-rose-50 border border-rose-300 text-[11px] text-rose-900 font-mono">
                    <strong>Rule:</strong> Missing skills are honest gaps for this role, NOT an instruction to invent experience.
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {matchData.missing_skills?.map((sk, i) => (
                      <span key={i} className="badge-tag bg-rose-50 text-rose-950 border-rose-400">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                {/* 4. Unsupported Claims */}
                <div className="border-2 border-charcoal bg-white p-5 space-y-3">
                  <div className="flex items-center justify-between border-b border-cream-border pb-2">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-purple-800 flex items-center space-x-1.5">
                      <AlertCircle className="w-4 h-4 text-purple-600" />
                      <span>Unsupported Claims ({matchData.unsupported_claims?.length || 0})</span>
                    </h3>
                    <span className="badge-tag bg-purple-50 text-purple-900 border-purple-600">Integrity Check</span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Claims in candidate profile that lack verifiable projects or employment backing:
                  </p>
                  <div className="space-y-1.5">
                    {matchData.unsupported_claims?.map((claim, i) => (
                      <div key={i} className="p-2 bg-purple-50 border border-purple-300 text-xs font-mono text-purple-900">
                        {claim}
                      </div>
                    ))}
                    {(!matchData.unsupported_claims || matchData.unsupported_claims.length === 0) && (
                      <p className="text-xs text-charcoal-muted">Zero unsupported claims. Profile evidence is clean!</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <button onClick={() => setCurrentStep(2)} className="btn-secondary text-xs">
                  ← Back to Stage 2: JD Analysis
                </button>
                <button onClick={() => setCurrentStep(4)} className="btn-primary flex items-center space-x-2">
                  <span>Proceed to Stage 4: Resume Tailoring</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Stages 4 & 5 placeholders */}
      {currentStep > 3 && (
        <div className="card-brutal text-center py-12 space-y-3 font-mono">
          <p className="text-sm font-bold text-charcoal">Stage {currentStep}: Upcoming Epic Workflow</p>
          <p className="text-xs text-charcoal-muted">Progressive workflow stage will activate as subsequent epics are implemented.</p>
          <button onClick={() => setCurrentStep(3)} className="btn-secondary text-xs mt-2">
            Return to Stage 3: Evidence Matching
          </button>
        </div>
      )}
    </div>
  );
}

