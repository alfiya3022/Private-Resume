import React, { useState, useEffect } from "react";
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
  Save,
  Lock,
  Plus,
  Trash2,
  Edit3,
  RefreshCw,
  X,
  Download,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  GraduationCap,
  Award,
} from "lucide-react";
import { api } from "../api/client";
import { jobsApi } from "../api/jobs";
import { profileApi } from "../api/profile";
import { tailoringApi } from "../api/tailoring";
import { artifactsApi } from "../api/artifacts";
import { validationApi } from "../api/validation";
import { applicationsApi } from "../api/applications";
import PdfPreviewer from "../components/PdfPreviewer";

export default function WorkspacePage({ currentUser }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [resumes, setResumes] = useState([]);
  const [profile, setProfile] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [activeJob, setActiveJob] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [matchData, setMatchData] = useState(null);

  // Stage 4 Tailoring state
  const [tailoredResumes, setTailoredResumes] = useState([]);
  const [activeTailoredResume, setActiveTailoredResume] = useState(null);
  const [editableContent, setEditableContent] = useState(null);
  const [targetRoleInput, setTargetRoleInput] = useState("");
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newSkillInputs, setNewSkillInputs] = useState({});
  const [tailorLoading, setTailorLoading] = useState(false);
  const [tailorSaving, setTailorSaving] = useState(false);
  const [aiModal, setAiModal] = useState({
    isOpen: false,
    section: "",
    fieldKey: "",
    index: null,
    bulletIndex: null,
    currentText: "",
    suggestedText: "",
    explanation: "",
    instruction: "",
    loading: false,
  });

  // Stage 5 PDF & Validation state
  const [pdfArtifact, setPdfArtifact] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [provenanceInfo, setProvenanceInfo] = useState(null);
  const [pdfRefreshKey, setPdfRefreshKey] = useState(0);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState("");
  const [pdfPreviewLoading, setPdfPreviewLoading] = useState(false);
  const [pdfPreviewError, setPdfPreviewError] = useState("");
  const [validationReport, setValidationReport] = useState(null);
  const [validating, setValidating] = useState(false);
  const [loggingApp, setLoggingApp] = useState(false);

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [matching, setMatching] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [validationPopup, setValidationPopup] = useState(null);
  const [draftSaved, setDraftSaved] = useState(false);
  const [appLogged, setAppLogged] = useState(false);

  // Job form state
  const [jobForm, setJobForm] = useState({
    company: "",
    title: "",
    location: "",
    salary: "",
    job_url: "",
    raw_jd_text: "",
  });

  const formatSalaryINR = (val) => {
    if (!val) return "";
    const digits = val.replace(/[^0-9]/g, "");
    if (!digits) return "";
    const lastThree = digits.substring(digits.length - 3);
    const otherNumbers = digits.substring(0, digits.length - 3);
    const formatted =
      otherNumbers !== ""
        ? otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + lastThree
        : lastThree;
    return `₹ ${formatted}`;
  };

  const steps = [
    { num: 1, label: "1. Add Inputs", desc: "Master Resume & Job Description" },
    {
      num: 2,
      label: "2. Analyze JD",
      desc: "Structured Requirements Extraction",
    },
    {
      num: 3,
      label: "3. Match Evidence",
      desc: "Deterministic Skill Alignment",
    },
    {
      num: 4,
      label: "4. Tailor Resume",
      desc: "Section Editing & AI Consultation",
    },
    { num: 5, label: "5. PDF", desc: "ATS PDF Generation & Download" },
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
      loadJobTailoredResumes(activeJob.id);
    }
  }, [activeJob]);

  // Load the PDF with the Authorization header instead of exposing the JWT in the URL.
  useEffect(() => {
    let cancelled = false;
    let objectUrl = "";

    const loadPdfPreview = async () => {
      if (!activeTailoredResume?.id || !pdfArtifact) {
        setPdfPreviewUrl("");
        setPdfPreviewLoading(false);
        setPdfPreviewError("");
        return;
      }

      setPdfPreviewUrl("");
      setPdfPreviewError("");
      setPdfPreviewLoading(true);

      try {
        const token = api.getToken();
        const response = await fetch(
          artifactsApi.getPdfUrl(activeTailoredResume.id),
          {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          },
        );

        if (!response.ok) {
          throw new Error("The server could not load the PDF preview.");
        }

        const blob = await response.blob();
        if (cancelled) return;

        objectUrl = window.URL.createObjectURL(blob);
        setPdfPreviewUrl(objectUrl);
      } catch {
        if (!cancelled) {
          setPdfPreviewUrl("");
          setPdfPreviewError(
            "Unable to load the PDF preview. Please compile the PDF again or try refreshing the preview.",
          );
        }
      } finally {
        if (!cancelled) {
          setPdfPreviewLoading(false);
        }
      }
    };

    loadPdfPreview();

    return () => {
      cancelled = true;
      if (objectUrl) {
        window.URL.revokeObjectURL(objectUrl);
      }
    };
  }, [activeTailoredResume?.id, pdfArtifact?.id, pdfRefreshKey]);

  const resetWorkspaceForNewJob = (completedJobId = null) => {
    if (completedJobId) {
      setSavedJobs((prev) => prev.filter((j) => j.id !== completedJobId));
    }
    setActiveJob(null);
    setJobForm({
      company: "",
      title: "",
      location: "",
      salary: "",
      job_url: "",
      raw_jd_text: "",
    });
    setAnalysis(null);
    setMatchData(null);
    setTailoredResumes([]);
    setActiveTailoredResume(null);
    setEditableContent(null);
    setPdfArtifact(null);
    setValidationReport(null);
    setAppLogged(false);
    setCurrentStep(1);
    setSuccessMsg("");
    setErrorMsg("");
  };

  const loadWorkspaceContext = async () => {
    setLoading(true);
    try {
      const [resumesData, profileData, jobsData] = await Promise.all([
        profileApi.getResumes(),
        profileApi.getProfile(),
        jobsApi.listJobs("active"),
      ]);
      setResumes(resumesData);
      setProfile(profileData);
      setSavedJobs(jobsData || []);
      // Do not auto-select previous jobs, so the workspace defaults to a clean page for new entry
    } catch (err) {
      setErrorMsg("Failed to load workspace data.");
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

  const loadJobTailoredResumes = async (jobId) => {
    try {
      const data = await tailoringApi.getJobTailoredResumes(jobId);
      setTailoredResumes(data || []);
      if (data && data.length > 0) {
        const latest = data[data.length - 1];
        setActiveTailoredResume(latest);
        setEditableContent(JSON.parse(JSON.stringify(latest.content || {})));
        setTargetRoleInput(latest.target_role || "");
        loadPdfArtifact(latest.id);
      } else {
        setActiveTailoredResume(null);
        setEditableContent(null);
        setTargetRoleInput("");
        setPdfArtifact(null);
      }
    } catch (err) {
      setTailoredResumes([]);
    }
  };

  const loadPdfArtifact = async (resumeId) => {
    if (!resumeId) return;
    try {
      const artifacts = await artifactsApi.getArtifacts(resumeId);
      const pdf = artifacts.find((a) => a.artifact_type === "pdf");
      setPdfArtifact(pdf || null);
      if (pdf) {
        loadValidationReport(resumeId);
      } else {
        setValidationReport(null);
      }
    } catch {
      setPdfArtifact(null);
      setValidationReport(null);
    }
  };

  const loadValidationReport = async (resumeId) => {
    if (!resumeId) return;
    try {
      const report = await validationApi.getValidation(resumeId);
      setValidationReport(report);
    } catch {
      setValidationReport(null);
    }
  };

  const handleRunValidation = async () => {
    if (!activeTailoredResume) return;
    setValidating(true);
    setErrorMsg("");
    try {
      const report = await validationApi.validateResume(
        activeTailoredResume.id,
      );
      setValidationReport(report);
      setSuccessMsg(
        `ATS Pre-Flight Audit completed: ${report.overall_status} (${report.score}/100)`,
      );
      setValidationPopup({
        title: "ATS Audit Passed",
        message: `ATS Pre-Flight Audit score: ${report.score}/100 (${report.overall_status}).`,
      });
    } catch (err) {
      setErrorMsg(err.message || "Validation failed. Compile PDF first.");
    } finally {
      setValidating(false);
    }
  };

  const handleGeneratePdf = async () => {
    if (!activeTailoredResume) return;
    setPdfLoading(true);
    setErrorMsg("");
    try {
      const res = await artifactsApi.generatePdf(activeTailoredResume.id);
      setPdfArtifact(res.pdf_artifact);
      if (res.provenance) {
        setProvenanceInfo(res.provenance);
      }
      setPdfRefreshKey((k) => k + 1);
      try {
        const report = await validationApi.validateResume(
          activeTailoredResume.id,
        );
        setValidationReport(report);
        setSuccessMsg("Resume compiled into ATS-ready PDF and validated.");
      } catch {
        setSuccessMsg("Resume compiled into ATS-ready PDF successfully.");
      }
    } catch (err) {
      setErrorMsg(err.message || "LaTeX compilation failed.");
    } finally {
      setPdfLoading(false);
    }
  };

  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleDownloadPdf = async () => {
    if (!activeTailoredResume) return;
    setDownloadingPdf(true);
    setErrorMsg("");
    const completedJob = activeJob;
    try {
      const token = api.getToken();
      const filename = `Resume_${activeJob?.company?.replace(/\s+/g, "_") || "Tailored"}.pdf`;
      const response = await fetch(
        artifactsApi.getPdfUrl(activeTailoredResume.id),
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        },
      );
      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || "Failed to retrieve PDF from server");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      // Give the browser time to begin consuming the Blob before releasing it.
      window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);

      setSuccessMsg(`Resume PDF "${filename}" downloaded successfully.`);
    } catch (err) {
      setErrorMsg(err.message || "Failed to download PDF.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleLogApplication = async () => {
    if (!activeJob || !activeTailoredResume) return;
    setLoggingApp(true);
    setErrorMsg("");
    try {
      await applicationsApi.createApplication({
        job_id: activeJob.id,
        tailored_resume_id: activeTailoredResume.id,
        status: "applied",
        notes: `Submitted application with Tailored v${activeTailoredResume.version_number}. Verified ATS compliance.`,
      });
      setAppLogged(true);
      setSuccessMsg(
        `Application for ${activeJob.company} logged successfully! View in Applications pipeline.`,
      );
      setValidationPopup({
        title: "Application Logged",
        message: `Application for ${activeJob.company} (${activeJob.title}) has been logged in your Applications pipeline.`,
      });
    } catch (err) {
      setErrorMsg(err.message || "Failed to log application.");
    } finally {
      setLoggingApp(false);
    }
  };

  const handleSelectVersion = (versionId) => {
    const selected = tailoredResumes.find(
      (r) => r.id === parseInt(versionId, 10),
    );
    if (selected) {
      setActiveTailoredResume(selected);
      setEditableContent(JSON.parse(JSON.stringify(selected.content || {})));
      setTargetRoleInput(selected.target_role || "");
      loadPdfArtifact(selected.id);
    }
  };

  const handleTriggerTailor = async () => {
    if (!activeJob) return;
    setTailorLoading(true);
    setErrorMsg("");
    try {
      const created = await tailoringApi.tailorResumeForJob(activeJob.id);
      setTailoredResumes((prev) => [...prev, created]);
      setActiveTailoredResume(created);
      setEditableContent(JSON.parse(JSON.stringify(created.content || {})));
      setTargetRoleInput(created.target_role || "");
      setSuccessMsg(
        `Draft v${created.version_number} tailored successfully from candidate evidence.`,
      );
    } catch (err) {
      setErrorMsg(err.message || "Failed to tailor resume.");
    } finally {
      setTailorLoading(false);
    }
  };

  const handleSaveResume = async (saveAsNewVersion = false) => {
    if (!activeTailoredResume || !editableContent) return;
    setTailorSaving(true);
    setErrorMsg("");
    try {
      const saved = await tailoringApi.updateTailoredResume(
        activeTailoredResume.id,
        {
          content: editableContent,
          target_role: targetRoleInput,
          save_as_new_version: saveAsNewVersion,
        },
      );
      if (saveAsNewVersion || activeTailoredResume.status === "final") {
        setTailoredResumes((prev) => [...prev, saved]);
        setActiveTailoredResume(saved);
        setEditableContent(JSON.parse(JSON.stringify(saved.content || {})));
        setTargetRoleInput(saved.target_role || "");
        setSuccessMsg(
          `New immutable version v${saved.version_number} created.`,
        );
        setValidationPopup({
          title: "New Version Created",
          message: `Created immutable tailored resume version v${saved.version_number}.`,
        });
      } else {
        setTailoredResumes((prev) =>
          prev.map((r) => (r.id === saved.id ? saved : r)),
        );
        setActiveTailoredResume(saved);
        setDraftSaved(true);
        setTimeout(() => setDraftSaved(false), 3000);
        setSuccessMsg(`Draft v${saved.version_number} saved.`);
        setValidationPopup({
          title: "Draft Saved",
          message: `Draft v${saved.version_number} saved successfully.`,
        });
      }
    } catch (err) {
      setErrorMsg(err.message || "Failed to save resume.");
    } finally {
      setTailorSaving(false);
    }
  };

  const handleFinalizeResume = async () => {
    if (!activeTailoredResume) return;
    setTailorSaving(true);
    setErrorMsg("");
    try {
      const finalized = await tailoringApi.finalizeTailoredResume(
        activeTailoredResume.id,
      );
      setTailoredResumes((prev) =>
        prev.map((r) => (r.id === finalized.id ? finalized : r)),
      );
      setActiveTailoredResume(finalized);
      setSuccessMsg(
        `Version v${finalized.version_number} approved and locked as FINAL.`,
      );
      setValidationPopup({
        title: "Version Finalized",
        message: `Version v${finalized.version_number} is locked as FINAL. No further edits can be made to this immutable version.`,
      });
    } catch (err) {
      setErrorMsg(err.message || "Failed to finalize resume.");
    } finally {
      setTailorSaving(false);
    }
  };

  const openAskAiModal = ({
    section,
    fieldKey,
    index = null,
    bulletIndex = null,
    currentText = "",
  }) => {
    setAiModal({
      isOpen: true,
      section,
      fieldKey,
      index,
      bulletIndex,
      currentText,
      suggestedText: "",
      explanation: "",
      instruction: "",
      loading: false,
    });
  };

  const runAskAi = async (customInstruction) => {
    const instruction = customInstruction || aiModal.instruction;
    if (!instruction || !instruction.trim()) return;
    setAiModal((prev) => ({ ...prev, loading: true }));
    try {
      const res = await tailoringApi.askAIEdit(activeTailoredResume.id, {
        section: aiModal.section,
        instruction,
        current_text: aiModal.currentText,
      });
      setAiModal((prev) => ({
        ...prev,
        suggestedText: res.suggested_text,
        explanation: res.explanation,
        instruction,
        loading: false,
      }));
    } catch (err) {
      setErrorMsg(err.message || "AI refinement request failed.");
      setAiModal((prev) => ({ ...prev, loading: false }));
    }
  };

  const applyAiSuggestion = () => {
    if (!aiModal.suggestedText || !editableContent) return;
    const updated = JSON.parse(JSON.stringify(editableContent));

    if (aiModal.section === "summary") {
      updated.summary = aiModal.suggestedText;
    } else if (aiModal.section === "experience" && aiModal.index !== null) {
      if (aiModal.bulletIndex !== null) {
        updated.experience[aiModal.index].bullets[aiModal.bulletIndex] =
          aiModal.suggestedText.replace(/^[•\-\*]\s*/, "");
      } else {
        const lines = aiModal.suggestedText
          .split("\n")
          .map((l) => l.replace(/^[•\-\*]\s*/, "").trim())
          .filter(Boolean);
        updated.experience[aiModal.index].bullets = lines;
      }
    } else if (aiModal.section === "projects" && aiModal.index !== null) {
      if (aiModal.bulletIndex !== null) {
        updated.projects[aiModal.index].bullets[aiModal.bulletIndex] =
          aiModal.suggestedText.replace(/^[•\-\*]\s*/, "");
      } else {
        const lines = aiModal.suggestedText
          .split("\n")
          .map((l) => l.replace(/^[•\-\*]\s*/, "").trim())
          .filter(Boolean);
        updated.projects[aiModal.index].bullets = lines;
      }
    }
    setEditableContent(updated);
    setAiModal((prev) => ({ ...prev, isOpen: false }));
    setSuccessMsg(
      `AI refinement applied to ${aiModal.section}. Review and save version.`,
    );
  };

  const handleTriggerMatch = async () => {
    if (!activeJob) return;
    setMatching(true);
    setErrorMsg("");
    try {
      const data = await jobsApi.matchJob(activeJob.id);
      setMatchData(data);
      setSuccessMsg(
        `Evidence alignment complete: ${data.estimated_match_score}% Estimated Job Match.`,
      );
      setValidationPopup({
        title: "Evidence Matched",
        message: `Calculated alignment: ${data.estimated_match_score}% match with ${data.matched_skills?.length || 0} matched skills.`,
      });
    } catch (err) {
      setErrorMsg(err.message || "Evidence matching failed.");
    } finally {
      setMatching(false);
    }
  };

  const handleSubmitJob = async (e) => {
    e.preventDefault();
    if (
      !jobForm.company.trim() ||
      !jobForm.title.trim() ||
      !jobForm.raw_jd_text.trim()
    ) {
      setErrorMsg(
        "Please fill in Company, Job Title, and the Job Description.",
      );
      return;
    }

    setSubmitting(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const created = await jobsApi.createJob(jobForm);
      setActiveJob(created);
      setSavedJobs([created, ...savedJobs]);
      setSuccessMsg(
        `Target job "${created.title} at ${created.company}" saved successfully.`,
      );
      setValidationPopup({
        title: "Job Saved & Analyzed",
        message: `Target job "${created.title} at ${created.company}" saved. Requirements extracted.`,
      });

      // Trigger analysis immediately
      setAnalyzing(true);
      setCurrentStep(2);
      const anaData = await jobsApi.analyzeJob(created.id);
      setAnalysis(anaData);
    } catch (err) {
      setErrorMsg(err.message || "Failed to save or analyze job description.");
    } finally {
      setSubmitting(false);
      setAnalyzing(false);
    }
  };

  const handleTriggerAnalysis = async () => {
    if (!activeJob) return;
    setAnalyzing(true);
    setErrorMsg("");
    try {
      const data = await jobsApi.analyzeJob(activeJob.id);
      setAnalysis(data);
      setSuccessMsg("Job description analyzed successfully.");
    } catch (err) {
      setErrorMsg(err.message || "Analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectJob = (job) => {
    setActiveJob(job);
    setJobForm({
      company: job.company,
      title: job.title,
      location: job.location || "",
      salary: job.salary || "",
      job_url: job.job_url || "",
      raw_jd_text: job.raw_jd_text,
    });
  };

  if (!currentUser) {
    return (
      <div className="card-brutal text-center py-12 space-y-4">
        <AlertCircle className="w-12 h-12 text-coral mx-auto" />
        <h2 className="text-xl font-bold text-charcoal">
          Authentication Required
        </h2>
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
              {activeJob
                ? `${activeJob.title} @ ${activeJob.company}`
                : "New Target Job"}
            </span>
            {activeJob && (
              <button
                type="button"
                onClick={() => resetWorkspaceForNewJob()}
                className="btn-secondary text-[11px] py-1 px-2.5 flex items-center space-x-1 border-dashed"
                title="Clear current job and start a new application intake"
              >
                <Plus className="w-3 h-3" />
                <span>New Job Intake</span>
              </button>
            )}
          </div>
          <div className="flex items-center space-x-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
            {steps.map((s) => (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`px-3 py-1.5 text-xs font-medium border flex items-center space-x-1.5 transition-all whitespace-nowrap ${
                  currentStep === s.num
                    ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
                    : "bg-white text-charcoal border-cream-border hover:border-charcoal"
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
                  Add a target job description to match against your master
                  resume.
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
                    <span
                      className={`badge-tag ${activeMasterResume ? "bg-emerald-100 text-emerald-900 border-emerald-500" : "bg-amber-100 text-amber-900 border-amber-500"}`}
                    >
                      {activeMasterResume ? "Ready" : "Missing"}
                    </span>
                  </div>

                  {activeMasterResume ? (
                    <div className="bg-white border border-charcoal p-3 text-xs font-mono space-y-2">
                      <div className="flex justify-between">
                        <span className="text-charcoal-muted">File:</span>
                        <span className="font-bold truncate max-w-[150px]">
                          {activeMasterResume.filename}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-charcoal-muted">
                          Verified Skills:
                        </span>
                        <span className="font-bold text-emerald-700">
                          {profile?.skills?.length || 0} skills
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-charcoal-muted">Projects:</span>
                        <span className="font-bold">
                          {profile?.projects?.length || 0} projects
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 bg-white border border-charcoal text-xs space-y-2">
                      <p className="text-amber-800">
                        No master resume PDF uploaded yet. Go to the{" "}
                        <strong>Profile</strong> tab to upload your source
                        resume.
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
                              ? "bg-charcoal text-white border-charcoal"
                              : "bg-cream hover:bg-cream-muted border-cream-border"
                          }`}
                        >
                          <span className="truncate">
                            {j.title} ({j.company})
                          </span>
                          <span className="text-[10px] opacity-70">
                            #{j.id}
                          </span>
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
                        onChange={(e) =>
                          setJobForm({ ...jobForm, company: e.target.value })
                        }
                        placeholder="e.g. Stripe"
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
                        onChange={(e) =>
                          setJobForm({ ...jobForm, title: e.target.value })
                        }
                        placeholder="e.g. Software Engineer"
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
                        onChange={(e) =>
                          setJobForm({ ...jobForm, location: e.target.value })
                        }
                        placeholder="e.g. San Francisco, CA"
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
                        onChange={(e) =>
                          setJobForm({
                            ...jobForm,
                            salary: formatSalaryINR(e.target.value),
                          })
                        }
                        placeholder="e.g. ₹ 12,00,000"
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
                        onChange={(e) =>
                          setJobForm({ ...jobForm, job_url: e.target.value })
                        }
                        placeholder="https://company.com/jobs/123"
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
                      onChange={(e) =>
                        setJobForm({ ...jobForm, raw_jd_text: e.target.value })
                      }
                      placeholder="Paste the target job description here..."
                      className="w-full border-2 border-charcoal p-3 text-xs font-mono bg-cream focus:outline-none focus:ring-2 focus:ring-coral"
                      required
                    />
                  </div>

                  <div className="flex justify-end pt-2">
                    {activeJob &&
                    jobForm.company === activeJob.company &&
                    jobForm.title === activeJob.title ? (
                      <button
                        type="button"
                        disabled
                        className="btn-secondary opacity-80 cursor-default flex items-center space-x-2"
                      >
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Job Saved & Analyzed</span>
                      </button>
                    ) : (
                      <button
                        type="submit"
                        disabled={submitting}
                        className="btn-primary flex items-center space-x-2"
                      >
                        <Sparkles className="w-4 h-4" />
                        <span>
                          {submitting
                            ? "Saving Job..."
                            : "Save & Analyze Job Description"}
                        </span>
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    )}
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
                <span className="badge-tag bg-coral-light text-coral border-coral font-bold">
                  Stage 2
                </span>
                <h2 className="text-xl font-bold tracking-tight text-charcoal">
                  Structured Job Requirements
                </h2>
              </div>
              <p className="text-xs text-charcoal-muted mt-1">
                Target: <strong>{activeJob?.title}</strong> at{" "}
                <strong>{activeJob?.company}</strong>
                {analysis?.experience_years
                  ? ` · Level: ${analysis.experience_years}`
                  : ""}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleTriggerAnalysis}
                disabled={analyzing}
                className="btn-secondary text-xs flex items-center space-x-1"
              >
                {analyzing ? (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-coral animate-spin" />
                    <span>Extracting...</span>
                  </>
                ) : analysis ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Analysis Complete</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-coral" />
                    <span>Analyze JD</span>
                  </>
                )}
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
              <div className="font-bold text-sm">
                Ollama Local Engine Extracting Requirements...
              </div>
              <p className="text-xs text-charcoal-muted">
                Parsing technical skills, frameworks, databases, and
                responsibilities without hallucinating claims.
              </p>
            </div>
          )}

          {!analyzing && !analysis && (
            <div className="p-8 text-center space-y-4 bg-cream border-2 border-charcoal">
              <p className="text-sm font-mono text-charcoal">
                No structured analysis has been generated yet for this job.
              </p>
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
                      <span>
                        Required Skills ({analysis.required_skills?.length || 0}
                        )
                      </span>
                    </h3>
                    <span className="badge-tag bg-coral-light text-coral border-coral">
                      Core
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.required_skills?.map((sk, i) => (
                      <span
                        key={i}
                        className="badge-tag bg-white border-charcoal font-semibold"
                      >
                        {sk}
                      </span>
                    ))}
                    {(!analysis.required_skills ||
                      analysis.required_skills.length === 0) && (
                      <p className="text-xs text-charcoal-muted">
                        No explicit required skills listed.
                      </p>
                    )}
                  </div>
                </div>

                <div className="border-2 border-charcoal p-4 bg-cream space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                      <span className="w-2.5 h-2.5 bg-charcoal inline-block"></span>
                      <span>
                        Preferred / Good-to-Have Skills (
                        {analysis.preferred_skills?.length || 0})
                      </span>
                    </h3>
                    <span className="badge-tag bg-white">Bonus</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.preferred_skills?.map((sk, i) => (
                      <span
                        key={i}
                        className="badge-tag bg-white border-cream-border"
                      >
                        {sk}
                      </span>
                    ))}
                    {(!analysis.preferred_skills ||
                      analysis.preferred_skills.length === 0) && (
                      <p className="text-xs text-charcoal-muted">
                        No preferred skills listed.
                      </p>
                    )}
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
                    Experience Level:{" "}
                    {analysis.experience_years || "Not specified"}
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
                <button
                  onClick={() => setCurrentStep(1)}
                  className="btn-secondary text-xs"
                >
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
                <span className="badge-tag bg-coral-light text-coral border-coral font-bold">
                  Stage 3
                </span>
                <h2 className="text-xl font-bold tracking-tight text-charcoal">
                  Resume-to-Job Evidence Alignment
                </h2>
              </div>
              <p className="text-xs text-charcoal-muted mt-1">
                Comparing verified candidate profile evidence against target
                requirements for <strong>{activeJob?.title}</strong>.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleTriggerMatch}
                disabled={matching}
                className="btn-secondary text-xs flex items-center space-x-1"
              >
                {matching ? (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-coral animate-spin" />
                    <span>Calculating...</span>
                  </>
                ) : matchData ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>
                      Evidence Matched ({matchData.estimated_match_score}%)
                    </span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-coral" />
                    <span>Run Match Alignment</span>
                  </>
                )}
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
              <div className="font-bold text-sm">
                Deterministic Matching Engine Computing Alignment...
              </div>
              <p className="text-xs text-charcoal-muted">
                Verifying project backing, experience citations, and flagging
                unsupported claims.
              </p>
            </div>
          )}

          {!matching && !matchData && (
            <div className="p-8 text-center space-y-4 bg-cream border-2 border-charcoal">
              <p className="text-sm font-mono text-charcoal">
                No match analysis available yet for this target job.
              </p>
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
                    Calculated by cross-referencing required (70% weight) and
                    preferred (30% weight) job skills against candidate projects
                    and experience.
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
                      <span className="font-bold">
                        {matchData.matched_skills?.length || 0}
                      </span>{" "}
                      Matched
                    </div>
                    <div className="bg-amber-50 border border-amber-600 p-2 text-amber-950">
                      <span className="font-bold">
                        {matchData.weak_skills?.length || 0}
                      </span>{" "}
                      Weak
                    </div>
                    <div className="bg-rose-50 border border-rose-600 p-2 text-rose-950">
                      <span className="font-bold">
                        {matchData.missing_skills?.length || 0}
                      </span>{" "}
                      Missing
                    </div>
                    <div className="bg-purple-50 border border-purple-600 p-2 text-purple-950">
                      <span className="font-bold">
                        {matchData.unsupported_claims?.length || 0}
                      </span>{" "}
                      Unsupported
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
                      <span>
                        Matched Skills ({matchData.matched_skills?.length || 0})
                      </span>
                    </h3>
                    <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600">
                      Verified Evidence
                    </span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Directly evidenced by candidate projects or verified
                    employment records. Click to view evidence drawer:
                  </p>
                  <div className="space-y-2">
                    {matchData.matched_skills?.map((sk, i) => (
                      <div
                        key={i}
                        className="border border-charcoal bg-cream p-2.5 text-xs font-mono"
                      >
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
                      <span>
                        Weakly Represented Skills (
                        {matchData.weak_skills?.length || 0})
                      </span>
                    </h3>
                    <span className="badge-tag bg-amber-50 text-amber-900 border-amber-600">
                      Needs Evidence
                    </span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Present in your profile or mentioned in text, but lacks a
                    linked project or work history accomplishment.
                  </p>
                  <div className="space-y-2">
                    {matchData.weak_skills?.map((sk, i) => (
                      <div
                        key={i}
                        className="border border-amber-500 bg-amber-50/50 p-2.5 text-xs font-mono"
                      >
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
                    {(!matchData.weak_skills ||
                      matchData.weak_skills.length === 0) && (
                      <p className="text-xs text-charcoal-muted">
                        None detected.
                      </p>
                    )}
                  </div>
                </div>

                {/* 3. Missing Skills */}
                <div className="border-2 border-charcoal bg-white p-5 space-y-3">
                  <div className="flex items-center justify-between border-b border-cream-border pb-2">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-rose-800 flex items-center space-x-1.5">
                      <AlertCircle className="w-4 h-4 text-rose-600" />
                      <span>
                        Missing Skills ({matchData.missing_skills?.length || 0})
                      </span>
                    </h3>
                    <span className="badge-tag bg-rose-50 text-rose-900 border-rose-600">
                      Gaps
                    </span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Missing job requirements excluded from resume generation:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {matchData.missing_skills?.map((sk, i) => (
                      <span
                        key={i}
                        className="badge-tag bg-rose-50 text-rose-950 border-rose-400"
                      >
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
                      <span>
                        Unsupported Claims (
                        {matchData.unsupported_claims?.length || 0})
                      </span>
                    </h3>
                    <span className="badge-tag bg-purple-50 text-purple-900 border-purple-600">
                      Integrity Check
                    </span>
                  </div>
                  <p className="text-xs text-charcoal-muted">
                    Claims in candidate profile that lack verifiable projects or
                    employment backing:
                  </p>
                  <div className="space-y-1.5">
                    {matchData.unsupported_claims?.map((claim, i) => (
                      <div
                        key={i}
                        className="p-2 bg-purple-50 border border-purple-300 text-xs font-mono text-purple-900"
                      >
                        {claim}
                      </div>
                    ))}
                    {(!matchData.unsupported_claims ||
                      matchData.unsupported_claims.length === 0) && (
                      <p className="text-xs text-charcoal-muted">
                        Zero unsupported claims. Profile evidence is clean!
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={() => setCurrentStep(2)}
                  className="btn-secondary text-xs"
                >
                  ← Back to Stage 2: JD Analysis
                </button>
                <button
                  onClick={() => setCurrentStep(4)}
                  className="btn-primary flex items-center space-x-2"
                >
                  <span>Proceed to Stage 4: Resume Tailoring</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Stage 4: Tailored Resume & Section Editing */}
      {currentStep === 4 && (
        <div className="space-y-6">
          {!activeTailoredResume ? (
            <div className="card-brutal text-center py-12 space-y-4 font-mono">
              <div className="w-12 h-12 rounded-full border-2 border-charcoal bg-amber-50 flex items-center justify-center mx-auto text-amber-900">
                <Sparkles className="w-6 h-6 text-coral" />
              </div>
              <h2 className="text-base font-bold uppercase tracking-wider text-charcoal">
                Stage 4: Tailored Resume Generation
              </h2>
              <p className="text-xs text-charcoal-muted max-w-lg mx-auto">
                Generate an evidence-grounded resume draft aligned with{" "}
                <strong>{activeJob?.title}</strong> at{" "}
                <strong>{activeJob?.company}</strong>.
              </p>
              <div className="pt-2">
                <button
                  onClick={handleTriggerTailor}
                  disabled={tailorLoading}
                  className="btn-primary inline-flex items-center space-x-2 text-xs"
                >
                  {tailorLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                      <span>Generating Evidence-Based Draft...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Generate Tailored Resume (Draft v1)</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6 font-mono">
              {/* Version & Control Bar */}
              <div className="card-brutal bg-white p-4 flex flex-wrap items-center justify-between gap-4 border-2 border-charcoal shadow-brutal-sm">
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-bold uppercase text-charcoal tracking-wider">
                    Version:
                  </span>
                  <select
                    value={activeTailoredResume.id}
                    onChange={(e) => handleSelectVersion(e.target.value)}
                    className="input-brutal py-1 px-2.5 text-xs font-bold"
                  >
                    {tailoredResumes.map((v) => (
                      <option key={v.id} value={v.id}>
                        v{v.version_number} ({v.status.toUpperCase()}) -{" "}
                        {new Date(v.created_at).toLocaleDateString()}
                      </option>
                    ))}
                  </select>
                  <span
                    className={`badge-tag ${
                      activeTailoredResume.status === "final"
                        ? "bg-emerald-50 text-emerald-900 border-emerald-600"
                        : "bg-amber-50 text-amber-900 border-amber-600"
                    }`}
                  >
                    {activeTailoredResume.status.toUpperCase()}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => handleSaveResume(false)}
                    disabled={
                      tailorSaving ||
                      activeTailoredResume.status === "final" ||
                      draftSaved
                    }
                    className={`btn-secondary text-xs flex items-center space-x-1.5 py-1.5 px-3 ${
                      draftSaved
                        ? "border-emerald-600 text-emerald-800 bg-emerald-50"
                        : ""
                    }`}
                    title={
                      activeTailoredResume.status === "final"
                        ? "Final versions are immutable. Use Save as New Version."
                        : "Save draft in-place"
                    }
                  >
                    {draftSaved ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Draft Saved</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-3.5 h-3.5" />
                        <span>Save Working Draft</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => handleSaveResume(true)}
                    disabled={tailorSaving}
                    className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>
                      Save as New Version (v
                      {activeTailoredResume.version_number + 1})
                    </span>
                  </button>

                  {activeTailoredResume.status !== "final" && (
                    <button
                      onClick={handleFinalizeResume}
                      disabled={tailorSaving}
                      className="btn-secondary text-xs flex items-center space-x-1.5 py-1.5 px-3 border-emerald-600 text-emerald-900 bg-emerald-50 hover:bg-emerald-100"
                    >
                      <Lock className="w-3.5 h-3.5 text-emerald-700" />
                      <span>Lock as Final</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Status & Integrity Notice */}
              <div className="px-3 py-2 bg-cream-bg border border-charcoal text-xs text-charcoal-muted flex items-center justify-between">
                <span className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>
                    Evidence-grounded • Zero fabrication • Candidate approved
                  </span>
                </span>
                <span className="text-[11px] font-mono">Stage 4 of 5</span>
              </div>

              {/* Resume Content Sections */}
              {editableContent && (
                <div className="space-y-6">
                  {/* Master Heading Edit Bar */}
                  <div className="card-brutal bg-white p-3 flex flex-wrap items-center justify-between gap-3 border border-charcoal">
                    <div className="flex items-center space-x-2 flex-1 min-w-[280px]">
                      <span className="text-xs font-bold text-charcoal uppercase tracking-wider shrink-0">
                        Resume Heading:
                      </span>
                      <input
                        type="text"
                        value={
                          editableContent.resume_heading ?? "Tailored Resume"
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            resume_heading: e.target.value,
                          })
                        }
                        className="input-brutal text-xs font-bold py-1 px-2 flex-1"
                        placeholder="e.g. Tailored Professional Resume"
                      />
                    </div>
                    <button
                      onClick={() => handleSaveResume(false)}
                      className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                    >
                      <Save className="w-3 h-3" />
                      <span>Save Heading</span>
                    </button>
                  </div>

                  {/* 1. Target Role & Professional Summary */}
                  <div className="card-brutal bg-white p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                      <div className="flex items-center space-x-2 flex-1">
                        <Briefcase className="w-4 h-4 text-coral shrink-0" />
                        <input
                          type="text"
                          value={
                            editableContent.section_titles?.summary ??
                            "Target Role & Professional Summary"
                          }
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              section_titles: {
                                ...(editableContent.section_titles || {}),
                                summary: e.target.value,
                              },
                            })
                          }
                          className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                          title="Click to edit section title"
                        />
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() =>
                            openAskAiModal({
                              section: "summary",
                              fieldKey: "summary",
                              currentText: editableContent.summary,
                            })
                          }
                          className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1 text-coral border-coral hover:bg-coral hover:text-white"
                        >
                          <Sparkles className="w-3 h-3" />
                          <span>Ask AI to Polish Summary</span>
                        </button>
                        <button
                          onClick={() => handleSaveResume(false)}
                          className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                        >
                          <Save className="w-3 h-3" />
                          <span>Save Summary</span>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <label className="block text-[11px] font-bold text-charcoal-muted uppercase mb-1">
                          Resume Headline / Target Role
                        </label>
                        <input
                          type="text"
                          value={targetRoleInput}
                          onChange={(e) => setTargetRoleInput(e.target.value)}
                          className="input-brutal w-full text-xs font-bold"
                          placeholder="e.g. Lead FastAPI Backend Engineer"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-charcoal-muted uppercase mb-1">
                          Executive Professional Summary (Strictly Tailored to
                          Target JD)
                        </label>
                        <textarea
                          rows={3}
                          value={editableContent.summary || ""}
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              summary: e.target.value,
                            })
                          }
                          className="input-brutal w-full text-xs leading-relaxed"
                          placeholder="Enter summary..."
                        />
                      </div>
                    </div>
                  </div>

                  {/* 2. Education */}
                  <div className="card-brutal bg-white p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                      <div className="flex items-center space-x-2 flex-1">
                        <GraduationCap className="w-4 h-4 text-coral shrink-0" />
                        <input
                          type="text"
                          value={
                            editableContent.section_titles?.education ??
                            "Education"
                          }
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              section_titles: {
                                ...(editableContent.section_titles || {}),
                                education: e.target.value,
                              },
                            })
                          }
                          className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                          title="Click to edit section title"
                        />
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          type="button"
                          onClick={() => {
                            const updated = { ...editableContent };
                            if (!updated.education) updated.education = [];
                            updated.education.push({
                              degree: "B.Tech in Computer Science",
                              institution: "University Name",
                              year: "2020 -- 2024",
                              gpa: "8.11",
                            });
                            setEditableContent(updated);
                          }}
                          className="btn-secondary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Add</span>
                        </button>
                        <button
                          onClick={() => handleSaveResume(false)}
                          className="btn-primary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                        >
                          <Save className="w-3 h-3" />
                          <span>Save</span>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {editableContent.education?.map((edu, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 border border-cream-border text-xs space-y-1.5 bg-cream-bg/20"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <input
                              type="text"
                              value={edu.degree || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.education[idx].degree = e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="Degree / Major (e.g. B.Tech in Computer Science & Engineering)"
                              className="input-brutal text-xs font-bold py-0.5 px-1.5 flex-1"
                            />
                            <button
                              type="button"
                              onClick={() => {
                                const updated = { ...editableContent };
                                updated.education = updated.education.filter(
                                  (_, i) => i !== idx,
                                );
                                setEditableContent(updated);
                              }}
                              className="text-rose-600 hover:text-rose-800 p-0.5"
                              title="Delete Education"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                            <input
                              type="text"
                              value={edu.institution || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.education[idx].institution =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="Institution"
                              className="input-brutal text-[11px] py-0.5 px-1.5"
                            />
                            <input
                              type="text"
                              value={edu.year || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.education[idx].year = e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="Year / Duration (e.g. 2020 -- 2024)"
                              className="input-brutal text-[11px] py-0.5 px-1.5"
                            />
                            <input
                              type="text"
                              value={edu.gpa || edu.cgpa || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.education[idx].gpa = e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="CGPA / GPA (e.g. 8.11 / 10)"
                              className="input-brutal text-[11px] py-0.5 px-1.5"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 3. Core Technical Skills */}
                  <div className="card-brutal bg-white p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                      <div className="flex items-center space-x-2 flex-1">
                        <Code2 className="w-4 h-4 text-coral shrink-0" />
                        <input
                          type="text"
                          value={
                            editableContent.section_titles?.skills ??
                            "Technical Competencies (Evidence-Grounded)"
                          }
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              section_titles: {
                                ...(editableContent.section_titles || {}),
                                skills: e.target.value,
                              },
                            })
                          }
                          className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                          title="Click to edit section title"
                        />
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleSaveResume(false)}
                          className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                        >
                          <Save className="w-3 h-3" />
                          <span>Save Skills</span>
                        </button>
                      </div>
                    </div>

                    {/* Add new skill category */}
                    <div className="flex items-center space-x-2 p-2 bg-cream-bg/40 border border-cream-border">
                      <input
                        type="text"
                        placeholder="New Skill Category (e.g. Cloud & DevOps)"
                        value={newCategoryName}
                        onChange={(e) => setNewCategoryName(e.target.value)}
                        className="input-brutal text-xs py-1 px-2 flex-1"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          if (!newCategoryName.trim()) return;
                          const updated = { ...editableContent };
                          if (!updated.skills) updated.skills = {};
                          if (!updated.skills[newCategoryName.trim()]) {
                            updated.skills[newCategoryName.trim()] = [];
                          }
                          setEditableContent(updated);
                          setNewCategoryName("");
                        }}
                        className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Add Category</span>
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(editableContent.skills || {}).map(
                        ([category, skillsList]) => (
                          <div
                            key={category}
                            className="border border-cream-border p-3 space-y-2 bg-cream-bg/40"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-charcoal uppercase tracking-wider block">
                                {category} ({skillsList.length})
                              </span>
                              <button
                                type="button"
                                onClick={() => {
                                  const updated = { ...editableContent };
                                  delete updated.skills[category];
                                  setEditableContent(updated);
                                }}
                                className="text-rose-600 hover:text-rose-800 text-xs"
                                title="Delete category"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>

                            <div className="flex flex-wrap gap-1.5">
                              {skillsList.map((skill, sIdx) => (
                                <span
                                  key={sIdx}
                                  className="badge-tag bg-white text-charcoal border-charcoal flex items-center space-x-1"
                                >
                                  <span>{skill}</span>
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const updated = { ...editableContent };
                                      updated.skills[category] = updated.skills[
                                        category
                                      ].filter((_, idx) => idx !== sIdx);
                                      setEditableContent(updated);
                                    }}
                                    className="hover:text-rose-600 ml-1 text-xs font-bold"
                                    title="Remove skill"
                                  >
                                    ×
                                  </button>
                                </span>
                              ))}
                            </div>

                            {/* Add skill to category */}
                            <div className="flex items-center space-x-1 pt-1 border-t border-cream-border/60">
                              <input
                                type="text"
                                placeholder="Add skill..."
                                value={newSkillInputs[category] || ""}
                                onChange={(e) =>
                                  setNewSkillInputs({
                                    ...newSkillInputs,
                                    [category]: e.target.value,
                                  })
                                }
                                onKeyDown={(e) => {
                                  if (e.key === "Enter") {
                                    e.preventDefault();
                                    const val = (
                                      newSkillInputs[category] || ""
                                    ).trim();
                                    if (!val) return;
                                    const updated = { ...editableContent };
                                    if (
                                      !updated.skills[category].includes(val)
                                    ) {
                                      updated.skills[category] = [
                                        ...updated.skills[category],
                                        val,
                                      ];
                                    }
                                    setEditableContent(updated);
                                    setNewSkillInputs({
                                      ...newSkillInputs,
                                      [category]: "",
                                    });
                                  }
                                }}
                                className="input-brutal text-[11px] py-0.5 px-1.5 flex-1"
                              />
                              <button
                                type="button"
                                onClick={() => {
                                  const val = (
                                    newSkillInputs[category] || ""
                                  ).trim();
                                  if (!val) return;
                                  const updated = { ...editableContent };
                                  if (!updated.skills[category].includes(val)) {
                                    updated.skills[category] = [
                                      ...updated.skills[category],
                                      val,
                                    ];
                                  }
                                  setEditableContent(updated);
                                  setNewSkillInputs({
                                    ...newSkillInputs,
                                    [category]: "",
                                  });
                                }}
                                className="btn-secondary text-[11px] py-0.5 px-2"
                              >
                                + Add
                              </button>
                            </div>
                          </div>
                        ),
                      )}
                    </div>
                  </div>

                  {/* 4. Work Experience */}
                  <div className="card-brutal bg-white p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                      <div className="flex items-center space-x-2 flex-1">
                        <Building className="w-4 h-4 text-coral shrink-0" />
                        <input
                          type="text"
                          value={
                            editableContent.section_titles?.experience ??
                            `Work Experience (${editableContent.experience?.length || 0})`
                          }
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              section_titles: {
                                ...(editableContent.section_titles || {}),
                                experience: e.target.value,
                              },
                            })
                          }
                          className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                          title="Click to edit section title"
                        />
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => {
                            const updated = { ...editableContent };
                            if (!updated.experience) updated.experience = [];
                            updated.experience.push({
                              title: "Software Engineer",
                              company: "Company Name",
                              location: "Remote",
                              start_date: "2023-01",
                              end_date: "Present",
                              bullets: [
                                "Key contribution and engineering achievement aligned with target role.",
                              ],
                            });
                            setEditableContent(updated);
                          }}
                          className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Add Role</span>
                        </button>
                        <button
                          onClick={() => handleSaveResume(false)}
                          className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                        >
                          <Save className="w-3 h-3" />
                          <span>Save Experience</span>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {editableContent.experience?.map((exp, expIdx) => (
                        <div
                          key={expIdx}
                          className="border-2 border-charcoal p-4 space-y-3 bg-cream-bg/20"
                        >
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-2 border-b border-cream-border pb-2">
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Job Title
                              </label>
                              <input
                                type="text"
                                value={exp.title || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.experience[expIdx].title =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal w-full text-xs font-bold py-1 px-2"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Company
                              </label>
                              <input
                                type="text"
                                value={exp.company || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.experience[expIdx].company =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal w-full text-xs font-bold py-1 px-2"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Location
                              </label>
                              <input
                                type="text"
                                value={exp.location || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.experience[expIdx].location =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal w-full text-xs py-1 px-2"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Start Date
                              </label>
                              <input
                                type="text"
                                value={exp.start_date || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.experience[expIdx].start_date =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal w-full text-xs py-1 px-2"
                                placeholder="e.g. 2022-01"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                End Date
                              </label>
                              <input
                                type="text"
                                value={exp.end_date || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.experience[expIdx].end_date =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal w-full text-xs py-1 px-2"
                                placeholder="e.g. Present"
                              />
                            </div>
                          </div>

                          <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-charcoal-muted uppercase">
                              Accomplishment Bullets
                            </span>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() =>
                                  openAskAiModal({
                                    section: "experience",
                                    fieldKey: "bullets",
                                    index: expIdx,
                                    currentText: (exp.bullets || []).join("\n"),
                                  })
                                }
                                className="btn-secondary text-[11px] py-0.5 px-2 text-coral border-coral hover:bg-coral hover:text-white flex items-center space-x-1"
                              >
                                <Sparkles className="w-3 h-3" />
                                <span>Ask AI on Role</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  const updated = { ...editableContent };
                                  updated.experience =
                                    updated.experience.filter(
                                      (_, idx) => idx !== expIdx,
                                    );
                                  setEditableContent(updated);
                                }}
                                className="text-rose-600 hover:text-rose-800 text-xs p-1"
                                title="Delete Role"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="space-y-2">
                            {exp.bullets?.map((bullet, bIdx) => (
                              <div
                                key={bIdx}
                                className="flex items-start space-x-2"
                              >
                                <span className="text-charcoal-muted text-xs mt-1.5">
                                  •
                                </span>
                                <textarea
                                  rows={2}
                                  value={bullet}
                                  onChange={(e) => {
                                    const updated = { ...editableContent };
                                    updated.experience[expIdx].bullets[bIdx] =
                                      e.target.value;
                                    setEditableContent(updated);
                                  }}
                                  className="input-brutal flex-1 text-xs leading-relaxed"
                                />
                                <div className="flex flex-col space-y-1">
                                  <button
                                    onClick={() =>
                                      openAskAiModal({
                                        section: "experience",
                                        fieldKey: "bullet",
                                        index: expIdx,
                                        bulletIndex: bIdx,
                                        currentText: bullet,
                                      })
                                    }
                                    className="p-1 border border-charcoal hover:bg-cream-bg text-coral"
                                    title="Ask AI to refine this bullet"
                                  >
                                    <Sparkles className="w-3 h-3" />
                                  </button>
                                  <button
                                    onClick={() => {
                                      const updated = { ...editableContent };
                                      updated.experience[expIdx].bullets =
                                        updated.experience[
                                          expIdx
                                        ].bullets.filter(
                                          (_, idx) => idx !== bIdx,
                                        );
                                      setEditableContent(updated);
                                    }}
                                    className="p-1 border border-charcoal hover:bg-rose-50 text-rose-700"
                                    title="Remove bullet"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </button>
                                </div>
                              </div>
                            ))}

                            <button
                              type="button"
                              onClick={() => {
                                const updated = { ...editableContent };
                                updated.experience[expIdx].bullets = [
                                  ...(updated.experience[expIdx].bullets || []),
                                  "Contributed to core deliverables and team execution.",
                                ];
                                setEditableContent(updated);
                              }}
                              className="btn-secondary text-[11px] py-1 px-2.5 flex items-center space-x-1 mt-2"
                            >
                              <Plus className="w-3 h-3" />
                              <span>Add Bullet Point</span>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 5. Key Projects & Deliverables */}
                  <div className="card-brutal bg-white p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                      <div className="flex items-center space-x-2 flex-1">
                        <Layers className="w-4 h-4 text-coral shrink-0" />
                        <input
                          type="text"
                          value={
                            editableContent.section_titles?.projects ??
                            `Key Projects (${editableContent.projects?.length || 0})`
                          }
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              section_titles: {
                                ...(editableContent.section_titles || {}),
                                projects: e.target.value,
                              },
                            })
                          }
                          className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                          title="Click to edit section title"
                        />
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => {
                            const updated = { ...editableContent };
                            if (!updated.projects) updated.projects = [];
                            updated.projects.push({
                              name: "New Project",
                              technologies: ["Python", "FastAPI"],
                              start_date: "2025",
                              end_date: "Present",
                              is_current: true,
                              github_url: "",
                              live_url: "",
                              link: "",
                              bullets: [
                                "Built scalable service handling real-time data.",
                              ],
                            });
                            setEditableContent(updated);
                          }}
                          className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Add Project</span>
                        </button>
                        <button
                          onClick={() => handleSaveResume(false)}
                          className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                        >
                          <Save className="w-3 h-3" />
                          <span>Save Projects</span>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {editableContent.projects?.map((proj, pIdx) => (
                        <div
                          key={pIdx}
                          className="border-2 border-charcoal p-4 space-y-3 bg-cream-bg/20"
                        >
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 border-b border-cream-border pb-3">
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Project Title
                              </label>
                              <input
                                type="text"
                                value={proj.name || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].name = e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal w-full text-xs font-bold py-1 px-2"
                                placeholder="e.g. AI-Powered Resume Application"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Tech Stack (comma separated)
                              </label>
                              <input
                                type="text"
                                value={(proj.technologies || []).join(", ")}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].technologies =
                                    e.target.value
                                      .split(",")
                                      .map((t) => t.trim())
                                      .filter(Boolean);
                                  setEditableContent(updated);
                                }}
                                placeholder="React, FastAPI, PostgreSQL"
                                className="input-brutal w-full text-xs py-1 px-2"
                              />
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                  GitHub / Repository URL
                                </label>
                                <input
                                  type="text"
                                  value={proj.github_url || proj.link || ""}
                                  onChange={(e) => {
                                    const updated = { ...editableContent };
                                    updated.projects[pIdx].github_url = e.target.value;
                                    updated.projects[pIdx].link = e.target.value;
                                    setEditableContent(updated);
                                  }}
                                  placeholder="https://github.com/..."
                                  className="input-brutal w-full text-xs py-1 px-2"
                                />
                              </div>
                              <div>
                                <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                  Live Website URL
                                </label>
                                <input
                                  type="text"
                                  value={proj.live_url || ""}
                                  onChange={(e) => {
                                    const updated = { ...editableContent };
                                    updated.projects[pIdx].live_url = e.target.value;
                                    setEditableContent(updated);
                                  }}
                                  placeholder="https://myproject.com"
                                  className="input-brutal w-full text-xs py-1 px-2"
                                />
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                  Start Date / Year
                                </label>
                                <input
                                  type="text"
                                  value={proj.start_date || ""}
                                  onChange={(e) => {
                                    const updated = { ...editableContent };
                                    updated.projects[pIdx].start_date = e.target.value;
                                    setEditableContent(updated);
                                  }}
                                  placeholder="e.g. 2025"
                                  className="input-brutal w-full text-xs py-1 px-2"
                                />
                              </div>
                              <div>
                                <div className="flex items-center justify-between">
                                  <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                    End Date / Year
                                  </label>
                                  <label className="flex items-center space-x-1 cursor-pointer">
                                    <input
                                      type="checkbox"
                                      checked={proj.is_current || proj.end_date === "Present"}
                                      onChange={(e) => {
                                        const updated = { ...editableContent };
                                        if (e.target.checked) {
                                          updated.projects[pIdx].is_current = true;
                                          updated.projects[pIdx].end_date = "Present";
                                        } else {
                                          updated.projects[pIdx].is_current = false;
                                          if (updated.projects[pIdx].end_date === "Present") {
                                            updated.projects[pIdx].end_date = "";
                                          }
                                        }
                                        setEditableContent(updated);
                                      }}
                                      className="h-3 w-3 accent-coral"
                                    />
                                    <span className="text-[10px] font-bold text-charcoal">Ongoing</span>
                                  </label>
                                </div>
                                <input
                                  type="text"
                                  value={proj.end_date || ""}
                                  disabled={proj.is_current && proj.end_date === "Present"}
                                  onChange={(e) => {
                                    const updated = { ...editableContent };
                                    updated.projects[pIdx].end_date = e.target.value;
                                    if (e.target.value.toLowerCase() === "present") {
                                      updated.projects[pIdx].is_current = true;
                                    }
                                    setEditableContent(updated);
                                  }}
                                  placeholder="e.g. 2026 or Present"
                                  className="input-brutal w-full text-xs py-1 px-2 disabled:bg-cream-bg disabled:text-charcoal-muted"
                                />
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-charcoal-muted uppercase">
                              Accomplishment Bullets
                            </span>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() =>
                                  openAskAiModal({
                                    section: "projects",
                                    fieldKey: "bullets",
                                    index: pIdx,
                                    currentText: (proj.bullets || []).join(
                                      "\n",
                                    ),
                                  })
                                }
                                className="btn-secondary text-[11px] py-0.5 px-2 text-coral border-coral hover:bg-coral hover:text-white flex items-center space-x-1"
                              >
                                <Sparkles className="w-3 h-3" />
                                <span>Ask AI on Project</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  const updated = { ...editableContent };
                                  updated.projects = updated.projects.filter(
                                    (_, idx) => idx !== pIdx,
                                  );
                                  setEditableContent(updated);
                                }}
                                className="text-rose-600 hover:text-rose-800 text-xs p-1"
                                title="Delete Project"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="space-y-2">
                            {proj.bullets?.map((bullet, bIdx) => (
                              <div
                                key={bIdx}
                                className="flex items-start space-x-2"
                              >
                                <span className="text-charcoal-muted text-xs mt-1.5">
                                  •
                                </span>
                                <textarea
                                  rows={2}
                                  value={bullet}
                                  onChange={(e) => {
                                    const updated = { ...editableContent };
                                    updated.projects[pIdx].bullets[bIdx] =
                                      e.target.value;
                                    setEditableContent(updated);
                                  }}
                                  className="input-brutal flex-1 text-xs leading-relaxed"
                                />
                                <button
                                  onClick={() => {
                                    const updated = { ...editableContent };
                                    updated.projects[pIdx].bullets =
                                      updated.projects[pIdx].bullets.filter(
                                        (_, idx) => idx !== bIdx,
                                      );
                                    setEditableContent(updated);
                                  }}
                                  className="p-1 border border-charcoal hover:bg-rose-50 text-rose-700"
                                  title="Remove bullet"
                                >
                                  <Trash2 className="w-3 h-3" />
                                </button>
                              </div>
                            ))}

                            <button
                              type="button"
                              onClick={() => {
                                const updated = { ...editableContent };
                                updated.projects[pIdx].bullets = [
                                  ...(updated.projects[pIdx].bullets || []),
                                  "Engineered core features and optimized system performance.",
                                ];
                                setEditableContent(updated);
                              }}
                              className="btn-secondary text-[11px] py-1 px-2.5 flex items-center space-x-1 mt-2"
                            >
                              <Plus className="w-3 h-3" />
                              <span>Add Bullet Point</span>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 6. Certifications & Achievements */}
                  <div className="card-brutal bg-white p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                      <div className="flex items-center space-x-2 flex-1">
                        <Award className="w-4 h-4 text-coral shrink-0" />
                        <input
                          type="text"
                          value={
                            editableContent.section_titles?.certifications ??
                            "Certifications & Achievements"
                          }
                          onChange={(e) =>
                            setEditableContent({
                              ...editableContent,
                              section_titles: {
                                ...(editableContent.section_titles || {}),
                                certifications: e.target.value,
                              },
                            })
                          }
                          className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                          title="Click to edit section title"
                        />
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          type="button"
                          onClick={() => {
                            const updated = { ...editableContent };
                            if (!updated.certifications)
                              updated.certifications = [];
                            updated.certifications.push({
                              name: "AWS Certified Solutions Architect",
                              issuer: "Amazon Web Services",
                              certificate_url: "",
                            });
                            setEditableContent(updated);
                          }}
                          className="btn-secondary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Add</span>
                        </button>
                        <button
                          onClick={() => handleSaveResume(false)}
                          className="btn-primary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                        >
                          <Save className="w-3 h-3" />
                          <span>Save</span>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {editableContent.certifications?.map((cert, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 border border-cream-border text-xs space-y-1.5 bg-cream-bg/20"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <input
                              type="text"
                              value={cert.name || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.certifications[idx].name =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="Certification or Achievement Name"
                              className="input-brutal text-xs font-bold py-0.5 px-1.5 flex-1 mr-2"
                            />
                            <button
                              type="button"
                              onClick={() => {
                                const updated = { ...editableContent };
                                updated.certifications =
                                  updated.certifications.filter(
                                    (_, i) => i !== idx,
                                  );
                                setEditableContent(updated);
                              }}
                              className="text-rose-600 hover:text-rose-800 p-0.5"
                              title="Delete Certification"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Issuer / Organization
                              </label>
                              <input
                                type="text"
                                value={cert.issuer || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.certifications[idx].issuer =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                placeholder="Issuer / Organization (e.g. AWS, Udemy, VCET)"
                                className="input-brutal text-[11px] py-0.5 px-1.5 w-full"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Certificate URL
                              </label>
                              <input
                                type="text"
                                value={cert.certificate_url || cert.credential_url || cert.link || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.certifications[idx].certificate_url =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                placeholder="https://example.com/my-certificate"
                                className="input-brutal text-[11px] py-0.5 px-1.5 w-full"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Navigation CTAs */}
              <div className="flex justify-between items-center pt-4 border-t border-cream-border">
                <button
                  onClick={() => setCurrentStep(3)}
                  className="btn-secondary text-xs"
                >
                  ← Back to Stage 3: Match Evidence
                </button>
                <button
                  onClick={() => {
                    setCurrentStep(5);
                    if (!pdfArtifact && activeTailoredResume) {
                      handleGeneratePdf();
                    }
                  }}
                  className="btn-primary flex items-center space-x-2"
                >
                  <span>Proceed to Stage 5: PDF</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Stage 5: Final Resume & LaTeX Compilation */}
      {currentStep === 5 && (
        <div className="space-y-6 font-mono">
          {!activeTailoredResume ? (
            <div className="card-brutal text-center py-12 space-y-4">
              <p className="text-xs text-charcoal-muted">
                No tailored resume selected. Please generate a tailored draft in
                Stage 4 first.
              </p>
              <button
                onClick={() => setCurrentStep(4)}
                className="btn-secondary text-xs"
              >
                ← Return to Stage 4: Tailor Resume
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Stage 5 Top Control Bar */}
              <div className="card-brutal bg-white p-4 flex flex-wrap items-center justify-between gap-4 border-2 border-charcoal shadow-brutal-sm">
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-bold uppercase text-charcoal tracking-wider">
                    Target: {activeJob?.title} (v
                    {activeTailoredResume.version_number})
                  </span>
                  <span
                    className={`badge-tag ${
                      activeTailoredResume.status === "final"
                        ? "bg-emerald-50 text-emerald-900 border-emerald-600"
                        : "bg-amber-50 text-amber-900 border-amber-600"
                    }`}
                  >
                    {activeTailoredResume.status.toUpperCase()}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {!pdfArtifact ? (
                    <button
                      onClick={handleGeneratePdf}
                      disabled={pdfLoading}
                      className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                    >
                      {pdfLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent" />
                          <span>Compiling LaTeX...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Compile ATS PDF</span>
                        </>
                      )}
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={handleDownloadPdf}
                        disabled={downloadingPdf}
                        className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                      >
                        {downloadingPdf ? (
                          <>
                            <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent" />
                            <span>Downloading...</span>
                          </>
                        ) : (
                          <>
                            <Download className="w-3.5 h-3.5 text-white" />
                            <span>Download PDF</span>
                          </>
                        )}
                      </button>

                      {!appLogged ? (
                        <button
                          type="button"
                          onClick={handleLogApplication}
                          disabled={loggingApp || !activeJob}
                          className="btn-secondary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                          title="Log this application in your Applications tracker"
                        >
                          {loggingApp ? (
                            <>
                              <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-charcoal border-t-transparent" />
                              <span>Logging...</span>
                            </>
                          ) : (
                            <>
                              <Briefcase className="w-3.5 h-3.5" />
                              <span>Log to Tracker</span>
                            </>
                          )}
                        </button>
                      ) : (
                        <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 text-xs flex items-center space-x-1 py-1 px-2.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Application Logged</span>
                        </span>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Safe Metadata Recovery Provenance Banner */}
              {provenanceInfo && Object.keys(provenanceInfo).some((k) => provenanceInfo[k] !== 'tailored_resume') && (
                <div className="card-brutal bg-cream border-2 border-charcoal p-3 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>
                      <strong>Missing Metadata Safely Recovered:</strong>{' '}
                      {Object.keys(provenanceInfo)
                        .filter((k) => provenanceInfo[k] !== 'tailored_resume')
                        .map((k) => `${k.replace('contact.', '').replace(/\.\d+\./, ' ')} (from ${provenanceInfo[k].replace('_', ' ')})`)
                        .join(', ')}
                    </span>
                  </div>
                  <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 text-[10px]">
                    Candidate Evidence Retained
                  </span>
                </div>
              )}

              {/* Main PDF Preview Window */}
              {pdfArtifact ? (
                <div className="card-brutal bg-white p-2 border-2 border-charcoal shadow-brutal space-y-2">
                  <div className="flex items-center justify-between px-3 py-1.5 border-b border-cream-border text-[11px] text-charcoal-muted">
                    <span className="flex items-center space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span className="font-bold text-charcoal">
                        Resume PDF Preview
                      </span>
                    </span>
                    <span>
                      File Size:{" "}
                      {Math.round((pdfArtifact.file_size || 0) / 1024)} KB
                    </span>
                  </div>

                  {pdfPreviewUrl ? (
                    <PdfPreviewer
                      key={pdfRefreshKey}
                      pdfUrl={pdfPreviewUrl}
                      onRefresh={() => setPdfRefreshKey((key) => key + 1)}
                      title={pdfArtifact.file_name || "Compiled ATS PDF"}
                    />
                  ) : pdfPreviewLoading ? (
                    <div
                      role="status"
                      className="flex h-[780px] items-center justify-center border border-charcoal bg-white text-sm text-charcoal-muted"
                    >
                      Loading PDF preview...
                    </div>
                  ) : (
                    <div
                      role="alert"
                      className="flex h-[780px] flex-col items-center justify-center gap-3 border border-charcoal bg-white px-6 text-center text-sm text-charcoal-muted"
                    >
                      <p>{pdfPreviewError || "PDF preview is not available yet."}</p>
                      <button
                        type="button"
                        onClick={() => setPdfRefreshKey((key) => key + 1)}
                        className="btn-secondary"
                      >
                        Retry preview
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="card-brutal text-center py-16 space-y-4 bg-white border-2 border-charcoal">
                  <div className="w-12 h-12 rounded-full border-2 border-charcoal bg-cream-bg flex items-center justify-center mx-auto text-charcoal">
                    <FileCode className="w-6 h-6 text-coral" />
                  </div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-charcoal">
                    ATS Resume Not Yet Compiled
                  </h3>
                  <p className="text-xs text-charcoal-muted max-w-md mx-auto">
                    Click compile below to transform your tailored resume into
                    an ATS-parsable PDF document.
                  </p>
                  <button
                    onClick={handleGeneratePdf}
                    disabled={pdfLoading}
                    className="btn-primary inline-flex items-center space-x-2 text-xs py-2 px-4"
                  >
                    {pdfLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                        <span>Compiling LaTeX...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Compile ATS PDF</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Navigation CTAs */}
              <div className="flex justify-between items-center pt-4 border-t border-cream-border">
                <button
                  onClick={() => setCurrentStep(4)}
                  className="btn-secondary text-xs"
                >
                  ← Back to Stage 4: Resume Tailoring
                </button>
                <div className="text-xs text-charcoal-muted font-mono">
                  Stage 5: Final Resume Ready
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ask AI Consultation Modal */}
      {aiModal.isOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="card-brutal bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-4 p-6 border-2 border-charcoal shadow-brutal font-mono animate-in fade-in duration-150">
            <div className="flex items-center justify-between border-b-2 border-charcoal pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-coral" />
                <h3 className="font-bold text-sm uppercase tracking-wider text-charcoal">
                  Consult AI: Refine {aiModal.section.toUpperCase()}
                </h3>
              </div>
              <button
                onClick={() =>
                  setAiModal((prev) => ({ ...prev, isOpen: false }))
                }
                className="p-1 hover:bg-cream-bg border border-charcoal"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-300 text-[11px] text-amber-950">
              <strong>Anti-Fabrication Rule:</strong> AI refinement will polish
              phrasing and emphasize genuine qualifications, but will never
              invent unbacked skills or technologies.
            </div>

            {/* Current Text */}
            <div className="space-y-1">
              <label className="text-[11px] font-bold text-charcoal-muted uppercase">
                Current Content
              </label>
              <div className="p-2.5 bg-cream-bg border border-charcoal text-xs text-charcoal whitespace-pre-line max-h-32 overflow-y-auto">
                {aiModal.currentText || "(Empty)"}
              </div>
            </div>

            {/* Quick Prompt Suggestions */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-bold text-charcoal-muted uppercase">
                Refinement Directives
              </label>
              <div className="flex flex-wrap gap-1.5">
                {[
                  "Emphasize measurable outcomes and technical metrics",
                  "Tighten phrasing with strong active engineering verbs",
                  "Align terminology with job requirements without inventing skills",
                  "Be concise, direct, and eliminate passive voice",
                ].map((promptText, pIdx) => (
                  <button
                    key={pIdx}
                    type="button"
                    onClick={() => {
                      setAiModal((prev) => ({
                        ...prev,
                        instruction: promptText,
                      }));
                      runAskAi(promptText);
                    }}
                    className="badge-tag bg-white hover:bg-cream-bg text-charcoal border-charcoal text-[11px] cursor-pointer"
                  >
                    ⚡ {promptText}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Instruction Input */}
            <div className="space-y-1">
              <label className="text-[11px] font-bold text-charcoal-muted uppercase">
                Custom Instruction (Optional)
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={aiModal.instruction}
                  onChange={(e) =>
                    setAiModal({ ...aiModal, instruction: e.target.value })
                  }
                  placeholder="e.g. Focus on high-throughput distributed system design..."
                  className="input-brutal flex-1 text-xs"
                />
                <button
                  type="button"
                  disabled={aiModal.loading || !aiModal.instruction.trim()}
                  onClick={() => runAskAi()}
                  className="btn-primary text-xs py-1.5 px-3 flex items-center space-x-1"
                >
                  {aiModal.loading ? (
                    <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent" />
                  ) : (
                    <Sparkles className="w-3.5 h-3.5" />
                  )}
                  <span>Generate</span>
                </button>
              </div>
            </div>

            {/* AI Proposed Revision */}
            {aiModal.suggestedText && (
              <div className="space-y-3 border-t border-cream-border pt-3">
                <div className="space-y-1">
                  <span className="text-[11px] font-bold text-emerald-800 uppercase flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Proposed AI Revision</span>
                  </span>
                  <div className="p-3 bg-emerald-50 border-2 border-emerald-600 text-xs text-emerald-950 whitespace-pre-line leading-relaxed font-mono">
                    {aiModal.suggestedText}
                  </div>
                </div>

                {aiModal.explanation && (
                  <div className="p-2 bg-cream-bg border border-cream-border text-[11px] text-charcoal-muted">
                    <strong>Rationale:</strong> {aiModal.explanation}
                  </div>
                )}

                <div className="flex justify-end space-x-2 pt-2">
                  <button
                    onClick={() =>
                      setAiModal((prev) => ({ ...prev, isOpen: false }))
                    }
                    className="btn-secondary text-xs"
                  >
                    Discard
                  </button>
                  <button
                    onClick={applyAiSuggestion}
                    className="btn-primary text-xs flex items-center space-x-1.5 bg-emerald-700 hover:bg-emerald-800 border-charcoal"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Accept & Apply Revision</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Validation Pop-up Modal */}
      {validationPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal/50 p-4">
          <div className="bg-white border-2 border-charcoal p-6 shadow-brutal max-w-sm w-full space-y-4 font-sans">
            <div className="flex items-center space-x-2.5 text-emerald-600">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <h3 className="font-bold text-base text-charcoal">
                {validationPopup.title}
              </h3>
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
