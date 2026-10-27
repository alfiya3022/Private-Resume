import React, { useState, useEffect } from "react";
import { AlertCircle, CheckCircle2, Plus } from "lucide-react";
import { api } from "../api/client";
import { jobsApi } from "../api/jobs";
import { profileApi } from "../api/profile";
import { tailoringApi } from "../api/tailoring";
import { artifactsApi } from "../api/artifacts";
import { validationApi } from "../api/validation";
import { applicationsApi } from "../api/applications";
import { useToast } from "../context/ToastContext";
import Stage1JobIntake from "../components/workspace/Stage1JobIntake";
import Stage2Requirements from "../components/workspace/Stage2Requirements";
import Stage3Matching from "../components/workspace/Stage3Matching";
import Stage4Tailor from "../components/workspace/Stage4Tailor";
import Stage5PdfGeneration from "../components/workspace/Stage5PdfGeneration";

export default function WorkspacePage({ currentUser, onNavigateToProfileEvidence }) {
  const { showSuccess, showError, showWarning } = useToast();

  const getInitialWorkspaceState = () => {
    if (typeof window === "undefined") return { step: 1, jobId: null };
    const params = new URLSearchParams(window.location.search);
    const qStep = parseInt(params.get("stage"), 10);
    const qJobId = parseInt(params.get("jobId"), 10);

    const sStep = parseInt(sessionStorage.getItem("pr_workspace_stage"), 10);
    const sJobId = parseInt(sessionStorage.getItem("pr_workspace_job_id"), 10);

    const step =
      !isNaN(qStep) && qStep >= 1 && qStep <= 5
        ? qStep
        : !isNaN(sStep) && sStep >= 1 && sStep <= 5
        ? sStep
        : 1;

    const jobId =
      !isNaN(qJobId) && qJobId > 0
        ? qJobId
        : !isNaN(sJobId) && sJobId > 0
        ? sJobId
        : null;

    return { step, jobId };
  };

  const initialState = getInitialWorkspaceState();
  const [currentStep, setCurrentStep] = useState(initialState.step);
  const [pendingJobId, setPendingJobId] = useState(initialState.jobId);
  const [resumes, setResumes] = useState([]);
  const [profile, setProfile] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [activeJob, setActiveJob] = useState(null);
  const [editingJobId, setEditingJobId] = useState(null);
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
    { num: 1, label: "1. Add Inputs" },
    { num: 2, label: "2. Analyze JD" },
    { num: 3, label: "3. Match Evidence" },
    { num: 4, label: "4. Tailor Resume" },
    { num: 5, label: "5. PDF" },
  ];

  useEffect(() => {
    if (currentUser) {
      loadWorkspaceContext();
    }
  }, [currentUser]);

  // Clear stale banners when moving between stages (errors/successes are set after awaits, so they persist).
  useEffect(() => {
    setErrorMsg("");
    setSuccessMsg("");
  }, [currentStep]);

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
    sessionStorage.removeItem("pr_workspace_stage");
    sessionStorage.removeItem("pr_workspace_job_id");
    const url = new URL(window.location);
    url.searchParams.delete("stage");
    url.searchParams.delete("jobId");
    window.history.replaceState(
      null,
      "",
      url.pathname + (url.searchParams.toString() ? `?${url.searchParams.toString()}` : "")
    );

    if (completedJobId) {
      setSavedJobs((prev) => prev.filter((j) => j.id !== completedJobId));
    }
    setActiveJob(null);
    setPendingJobId(null);
    setEditingJobId(null);
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

  // Synchronize current stage and active job to URL query params and sessionStorage
  useEffect(() => {
    if (typeof window === "undefined") return;
    sessionStorage.setItem("pr_workspace_stage", String(currentStep));
    if (activeJob?.id) {
      sessionStorage.setItem("pr_workspace_job_id", String(activeJob.id));
    }

    const url = new URL(window.location);
    if (currentStep > 1) {
      url.searchParams.set("stage", String(currentStep));
    } else {
      url.searchParams.delete("stage");
    }

    if (activeJob?.id) {
      url.searchParams.set("jobId", String(activeJob.id));
    } else {
      url.searchParams.delete("jobId");
    }

    const newSearch = url.searchParams.toString();
    const newRelativePath = url.pathname + (newSearch ? `?${newSearch}` : "");
    if (window.location.pathname + window.location.search !== newRelativePath) {
      window.history.replaceState(null, "", newRelativePath);
    }
  }, [currentStep, activeJob?.id]);

  // Support browser Back/Forward navigation across stages and saved jobs
  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const qStep = parseInt(params.get("stage"), 10);
      const qJobId = parseInt(params.get("jobId"), 10);
      if (!isNaN(qStep) && qStep >= 1 && qStep <= 5) {
        setCurrentStep(qStep);
      }
      if (!isNaN(qJobId) && qJobId > 0 && savedJobs.length > 0) {
        const found = savedJobs.find((j) => j.id === qJobId);
        if (found) setActiveJob(found);
      }
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [savedJobs]);

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

      // Restore active job if jobId was preserved in URL or session
      const targetJobId =
        pendingJobId || parseInt(sessionStorage.getItem("pr_workspace_job_id"), 10);
      if (targetJobId && jobsData && jobsData.length > 0) {
        const found = jobsData.find((j) => j.id === targetJobId);
        if (found) {
          setActiveJob(found);
        } else {
          try {
            const specificJob = await jobsApi.getJob(targetJobId);
            if (specificJob) setActiveJob(specificJob);
          } catch {
            if (currentStep > 1) setCurrentStep(1);
          }
        }
      } else if (jobsData && jobsData.length > 0) {
        if (currentStep > 1) {
          setActiveJob(jobsData[0]);
        }
      } else if (currentStep > 1 && (!jobsData || jobsData.length === 0)) {
        setCurrentStep(1);
      }
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
      showSuccess(`ATS Pre-Flight Audit: ${report.score}/100 (${report.overall_status})`);
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
        throw new Error(
          errData?.detail || "Failed to retrieve PDF from server",
        );
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
      showSuccess(`Application for ${activeJob.company} logged successfully.`);
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
        showSuccess(`New immutable version v${saved.version_number} created.`);
      } else {
        setTailoredResumes((prev) =>
          prev.map((r) => (r.id === saved.id ? saved : r)),
        );
        setActiveTailoredResume(saved);
        setDraftSaved(true);
        setTimeout(() => setDraftSaved(false), 3000);
        setSuccessMsg(`Draft v${saved.version_number} saved.`);
        showSuccess(`Draft v${saved.version_number} saved.`);
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
      showSuccess(`Version v${finalized.version_number} locked as FINAL.`);
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
      hasUnsupportedContent: false,
      missingEvidence: [],
      evidenceWarning: null,
      loading: false,
    });
  };

  const runAskAi = async (customInstruction, acknowledge = false) => {
    const instruction = customInstruction || aiModal.instruction;
    if (!instruction || !instruction.trim()) return;
    setAiModal((prev) => ({ ...prev, loading: true, evidenceWarning: null }));
    try {
      const res = await tailoringApi.askAIEdit(activeTailoredResume.id, {
        section: aiModal.section,
        instruction,
        current_text: aiModal.currentText,
        acknowledge_unsupported: Boolean(acknowledge),
      });
      setAiModal((prev) => ({
        ...prev,
        suggestedText: res.suggested_text,
        explanation: res.explanation,
        hasUnsupportedContent: Boolean(res.has_unsupported_content),
        missingEvidence: res.missing_evidence || [],
        evidenceWarning: res.evidence_warning,
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
    } else if (aiModal.section === "skills" && aiModal.fieldKey && updated.skills?.[aiModal.fieldKey]) {
      const newSkills = aiModal.suggestedText
        .split(/[\n,]+/)
        .map((s) => s.replace(/^[•\-\*]\s*/, "").trim())
        .filter(Boolean);
      updated.skills[aiModal.fieldKey] = newSkills;
    } else if (aiModal.section === "education" && aiModal.index !== null && updated.education?.[aiModal.index]) {
      updated.education[aiModal.index].degree = aiModal.suggestedText;
    } else if (aiModal.section === "certifications" && aiModal.index !== null && updated.certifications?.[aiModal.index]) {
      updated.certifications[aiModal.index].name = aiModal.suggestedText;
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
      showSuccess(`Evidence matched: ${data.estimated_match_score}% match score.`);
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
      showError("Please fill in Company, Job Title, and the Job Description.");
      return;
    }

    setSubmitting(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      let saved;
      if (editingJobId) {
        saved = await jobsApi.updateJob(editingJobId, jobForm);
        setActiveJob(saved);
        setSavedJobs((prev) =>
          prev.map((j) => (j.id === editingJobId ? saved : j))
        );
        setEditingJobId(null);
        showSuccess(`Target job "${saved.title} at ${saved.company}" updated.`);
      } else {
        saved = await jobsApi.createJob(jobForm);
        setActiveJob(saved);
        setSavedJobs([saved, ...savedJobs]);
        showSuccess(`Target job "${saved.title} at ${saved.company}" saved.`);
      }

      // Automatically transition user to Stage 2: Analyze JD once saved successfully
      setCurrentStep(2);

      // Trigger analysis immediately on the saved job
      setAnalyzing(true);
      const anaData = await jobsApi.analyzeJob(saved.id);
      setAnalysis(anaData);
      showSuccess("Job requirements extracted successfully.");
    } catch (err) {
      showError(err.message || "Failed to save or analyze job description.");
    } finally {
      setSubmitting(false);
      setAnalyzing(false);
    }
  };

  const handleDeleteJob = async (jobId) => {
    try {
      await jobsApi.deleteJob(jobId);
      setSavedJobs((prev) => prev.filter((j) => j.id !== jobId));
      if (activeJob?.id === jobId) {
        resetWorkspaceForNewJob();
      }
      if (editingJobId === jobId) {
        setEditingJobId(null);
      }
      showSuccess("Saved job removed successfully.");
    } catch (err) {
      showError(err.message || "Failed to delete saved job.");
    }
  };

  const handleTriggerAnalysis = async () => {
    if (!activeJob) return;
    setAnalyzing(true);
    setErrorMsg("");
    try {
      const data = await jobsApi.analyzeJob(activeJob.id);
      setAnalysis(data);
      showSuccess("Job description analyzed successfully.");
    } catch (err) {
      showError(err.message || "Analysis failed.");
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

  const handleNavigateStep = (stepNum) => {
    if (stepNum === currentStep) return;
    if (stepNum === 2 && !activeJob) {
      showWarning("Please save or select a target job in Stage 1 first.");
      return;
    }
    if (stepNum === 3 && !activeJob) {
      showWarning("Please save a target job in Stage 1 first.");
      return;
    }
    if (stepNum === 4 && !activeJob) {
      showWarning("Please save a target job in Stage 1 first.");
      return;
    }
    if (stepNum === 5 && !activeTailoredResume) {
      showWarning("Please generate or save a tailored resume in Stage 4 first.");
      return;
    }
    setCurrentStep(stepNum);
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
    <div className="space-y-4 font-sans">
      {/* 3.1 Persistent Company / Opportunity Header */}
      <div className="bg-white border-2 border-charcoal p-2.5 sm:p-3 px-3 sm:px-4 shadow-brutal-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-3">
        <div className="flex items-center space-x-2.5 min-w-0 w-full sm:w-auto">
          <span className="text-[10px] sm:text-[11px] font-mono uppercase tracking-wider text-charcoal-muted shrink-0 font-bold">
            Company:
          </span>
          <span className="font-bold text-xs sm:text-base text-charcoal truncate">
            {activeJob ? (
              <>
                <span className="text-coral">{activeJob.company}</span>
                <span className="text-charcoal-muted mx-1 sm:mx-1.5">—</span>
                <span>{activeJob.title}</span>
              </>
            ) : (
              <span className="text-charcoal-muted italic text-xs sm:text-sm font-normal">
                No target job selected (Add inputs below)
              </span>
            )}
          </span>
        </div>

        <button
          type="button"
          onClick={() => {
            resetWorkspaceForNewJob();
            setCurrentStep(1);
          }}
          className="btn-secondary text-xs py-1 px-2.5 sm:px-3 flex items-center space-x-1 shrink-0 self-end sm:self-auto"
          title="Clear current job and start a new application intake"
        >
          <Plus className="w-3.5 h-3.5 text-coral" />
          <span>+ New Job</span>
        </button>
      </div>

      {/* 3.2 Persistent Horizontal Workflow Navigation */}
      <div className="bg-cream border-2 border-charcoal p-1.5 shadow-brutal-sm flex items-center space-x-1.5 overflow-x-auto scrollbar-none">
        {steps.map((s) => {
          const isActive = currentStep === s.num;
          const isCompleted =
            (s.num === 1 && Boolean(activeJob)) ||
            (s.num === 2 && Boolean(analysis)) ||
            (s.num === 3 && Boolean(matchData)) ||
            (s.num === 4 && Boolean(activeTailoredResume)) ||
            (s.num === 5 && Boolean(pdfArtifact));
          const isAccessible =
            s.num === 1 ||
            (s.num === 2 && Boolean(activeJob)) ||
            (s.num === 3 && Boolean(activeJob)) ||
            (s.num === 4 && Boolean(activeJob)) ||
            (s.num === 5 && Boolean(activeTailoredResume));

          return (
            <button
              key={s.num}
              type="button"
              onClick={() => handleNavigateStep(s.num)}
              aria-current={isActive ? "step" : undefined}
              className={`px-3 py-1.5 text-xs font-semibold border transition-all whitespace-nowrap flex items-center space-x-1.5 ${
                isActive
                  ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
                  : isAccessible
                  ? "bg-white text-charcoal border-cream-border hover:border-charcoal"
                  : "bg-white/50 text-charcoal-muted/60 border-cream-border cursor-not-allowed"
              }`}
            >
              <span>{s.label}</span>
              {isCompleted && !isActive && (
                <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
              )}
            </button>
          );
        })}
      </div>

      {/* Stage 1: Add Inputs */}
      {currentStep === 1 && (
        <Stage1JobIntake
          savedJobs={savedJobs}
          activeJob={activeJob}
          jobForm={jobForm}
          setJobForm={setJobForm}
          handleSubmitJob={handleSubmitJob}
          handleSelectJob={handleSelectJob}
          handleDeleteJob={handleDeleteJob}
          editingJobId={editingJobId}
          setEditingJobId={setEditingJobId}
          activeMasterResume={activeMasterResume}
          profile={profile}
          loading={loading}
          submitting={submitting}
          errorMsg={errorMsg}
          successMsg={successMsg}
          formatSalaryINR={formatSalaryINR}
        />
      )}

      {/* Stage 2: Job Description Analysis */}
      {currentStep === 2 && (
        <Stage2Requirements
          activeJob={activeJob}
          analysis={analysis}
          analyzing={analyzing}
          handleTriggerAnalysis={handleTriggerAnalysis}
          handleTriggerMatch={handleTriggerMatch}
          setCurrentStep={setCurrentStep}
          matchData={matchData}
        />
      )}

      {/* Stage 3: Resume-to-Job Evidence Matching */}
      {currentStep === 3 && (
        <Stage3Matching
          activeJob={activeJob}
          matchData={matchData}
          matching={matching}
          handleTriggerMatch={handleTriggerMatch}
          setCurrentStep={setCurrentStep}
          onNavigateToProfileEvidence={onNavigateToProfileEvidence}
        />
      )}

      {/* Stage 4: Tailored Resume & Section Editing */}
      {currentStep === 4 && (
        <Stage4Tailor
          activeJob={activeJob}
          activeTailoredResume={activeTailoredResume}
          tailoredResumes={tailoredResumes}
          editableContent={editableContent}
          setEditableContent={(content) => {
            setDraftSaved(false);
            setEditableContent(content);
          }}
          targetRoleInput={targetRoleInput}
          setTargetRoleInput={setTargetRoleInput}
          newCategoryName={newCategoryName}
          setNewCategoryName={setNewCategoryName}
          newSkillInputs={newSkillInputs}
          setNewSkillInputs={setNewSkillInputs}
          tailorLoading={tailorLoading}
          tailorSaving={tailorSaving}
          draftSaved={draftSaved}
          aiModal={aiModal}
          setAiModal={setAiModal}
          pdfArtifact={pdfArtifact}
          handleTriggerTailor={handleTriggerTailor}
          handleSaveResume={handleSaveResume}
          handleFinalizeResume={handleFinalizeResume}
          handleSelectVersion={handleSelectVersion}
          handleGeneratePdf={handleGeneratePdf}
          openAskAiModal={openAskAiModal}
          runAskAi={runAskAi}
          applyAiSuggestion={applyAiSuggestion}
          setCurrentStep={setCurrentStep}
        />
      )}

      {/* Stage 5: Final Resume & LaTeX Compilation */}
      {currentStep === 5 && (
        <Stage5PdfGeneration
          activeTailoredResume={activeTailoredResume}
          activeJob={activeJob}
          pdfArtifact={pdfArtifact}
          pdfLoading={pdfLoading}
          pdfRefreshKey={pdfRefreshKey}
          pdfPreviewUrl={pdfPreviewUrl}
          pdfPreviewLoading={pdfPreviewLoading}
          pdfPreviewError={pdfPreviewError}
          provenanceInfo={provenanceInfo}
          loggingApp={loggingApp}
          appLogged={appLogged}
          downloadingPdf={downloadingPdf}
          handleGeneratePdf={handleGeneratePdf}
          handleDownloadPdf={handleDownloadPdf}
          handleLogApplication={handleLogApplication}
          setCurrentStep={setCurrentStep}
          setPdfRefreshKey={setPdfRefreshKey}
        />
      )}
    </div>
  );
}
