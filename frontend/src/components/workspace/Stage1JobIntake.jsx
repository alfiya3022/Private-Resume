import React, { useState } from "react";
import {
  FileCode,
  ListFilter,
  Briefcase,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Edit2,
  Trash2,
  Plus,
  X,
} from "lucide-react";

export default function Stage1JobIntake({
  savedJobs,
  activeJob,
  activeMasterResume,
  profile,
  loading,
  jobForm,
  setJobForm,
  formatSalaryINR,
  handleSubmitJob,
  handleSelectJob,
  handleDeleteJob,
  editingJobId,
  setEditingJobId,
  submitting,
  errorMsg,
  successMsg,
}) {
  const [jobToDelete, setJobToDelete] = useState(null);

  const onEditClick = (e, job) => {
    e.stopPropagation();
    setEditingJobId(job.id);
    handleSelectJob(job);
  };

  const onDeleteClick = (e, job) => {
    e.stopPropagation();
    setJobToDelete(job);
  };

  const confirmDelete = () => {
    if (jobToDelete) {
      handleDeleteJob(jobToDelete.id);
      setJobToDelete(null);
    }
  };

  const cancelEdit = () => {
    setEditingJobId(null);
    setJobForm({
      company: "",
      title: "",
      location: "",
      salary: "",
      job_url: "",
      raw_jd_text: "",
    });
  };

  return (
    <div className="space-y-4 font-sans">
      <div className="card-brutal space-y-4">
        {/* Header */}
        <div className="border-b border-cream-border pb-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div className="flex items-center space-x-2">
            <span className="badge-tag bg-coral-light text-coral border-coral font-bold">
              Stage 1
            </span>
            <h2 className="text-base sm:text-lg font-bold tracking-tight text-charcoal">
              Add Job Description & Master Inputs
            </h2>
          </div>
          {savedJobs.length > 0 && (
            <div className="text-xs font-mono text-charcoal-muted">
              <span>Saved Opportunities: </span>
              <span className="font-bold text-charcoal">{savedJobs.length}</span>
            </div>
          )}
        </div>

        {errorMsg && (
          <div className="bg-rose-50 border-2 border-rose-500 text-rose-900 p-2.5 text-xs font-mono">
            {errorMsg}
          </div>
        )}

        {successMsg && (
          <div className="bg-emerald-50 border-2 border-emerald-500 text-emerald-900 p-2.5 text-xs font-mono">
            {successMsg}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Column: Master Resume & Saved Jobs */}
          <div className="space-y-3">
            {/* 4.1 Active Master Resume Card */}
            <div className="border-2 border-charcoal bg-cream p-3.5 space-y-2.5">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-xs text-charcoal uppercase tracking-wider flex items-center space-x-1.5">
                  <FileCode className="w-3.5 h-3.5 text-coral" />
                  <span>Active Master Resume</span>
                </h3>
              </div>

              {activeMasterResume ? (
                <div className="bg-white border border-charcoal p-2.5 text-xs font-mono space-y-1.5">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-charcoal-muted uppercase tracking-wider">Source Document</span>
                    <span className="font-bold text-charcoal truncate" title={activeMasterResume.filename}>
                      {activeMasterResume.filename}
                    </span>
                  </div>
                  <div className="flex items-center justify-between pt-1 border-t border-cream-border text-[11px]">
                    <span className="text-emerald-700 font-semibold">
                      {profile?.skills?.length || 0} skills
                    </span>
                    <span className="text-charcoal-muted">·</span>
                    <span className="text-charcoal font-semibold">
                      {profile?.projects?.length || 0} projects
                    </span>
                  </div>
                </div>
              ) : loading ? (
                <div className="p-2.5 bg-white border border-charcoal text-xs text-charcoal-muted">
                  Loading master resume...
                </div>
              ) : (
                <div className="p-2.5 bg-white border border-charcoal text-xs text-amber-800 space-y-1">
                  <p>No master resume PDF uploaded yet.</p>
                  <p className="text-[11px] text-charcoal-muted">
                    Go to the <strong>Profile</strong> tab to upload your source resume.
                  </p>
                </div>
              )}
            </div>

            {/* 4.2 Previously Saved Jobs Selector */}
            {savedJobs.length > 0 && (
              <div className="border-2 border-charcoal bg-white p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                    <ListFilter className="w-3.5 h-3.5 text-coral" />
                    <span>Previously Saved Jobs</span>
                  </h4>
                  <span className="text-[10px] font-mono text-charcoal-muted">{savedJobs.length} total</span>
                </div>

                <div className="space-y-1 max-h-44 overflow-y-auto pr-0.5">
                  {savedJobs.map((j) => {
                    const isSelected = activeJob?.id === j.id;
                    const isEditing = editingJobId === j.id;

                    return (
                      <div
                        key={j.id}
                        onClick={() => handleSelectJob(j)}
                        className={`w-full text-left p-2 border text-xs font-mono transition-all flex items-center justify-between group cursor-pointer ${
                          isSelected
                            ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
                            : "bg-cream hover:bg-cream-muted border-cream-border hover:border-charcoal text-charcoal"
                        }`}
                      >
                        <div className="truncate flex-1 min-w-0 pr-2">
                          <span className="font-bold">{j.company}</span>
                          <span className="opacity-75 mx-1">—</span>
                          <span className="opacity-90">{j.title}</span>
                        </div>

                        <div className="flex items-center space-x-1 shrink-0">
                          <button
                            type="button"
                            onClick={(e) => onEditClick(e, j)}
                            className={`p-1 border transition-all ${
                              isSelected
                                ? "bg-white text-charcoal border-white hover:bg-cream"
                                : "bg-white text-charcoal border-charcoal hover:bg-coral hover:text-white"
                            }`}
                            title="Edit this saved job"
                            aria-label={`Edit ${j.title}`}
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                          <button
                            type="button"
                            onClick={(e) => onDeleteClick(e, j)}
                            className={`p-1 border transition-all ${
                              isSelected
                                ? "bg-rose-100 text-rose-800 border-rose-300 hover:bg-rose-200"
                                : "bg-white text-rose-700 border-charcoal hover:bg-rose-600 hover:text-white"
                            }`}
                            title="Remove this saved job"
                            aria-label={`Remove ${j.title}`}
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: 4.3 Target Job Description Form */}
          <div className="lg:col-span-2 border-2 border-charcoal bg-white p-4 sm:p-5 space-y-3.5">
            <div className="flex items-center justify-between border-b border-cream-border pb-2.5">
              <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-2">
                <Briefcase className="w-4 h-4 text-coral" />
                <span>
                  {editingJobId
                    ? `Editing Saved Opportunity`
                    : `Target Opportunity Details`}
                </span>
              </h3>
              {editingJobId && (
                <button
                  type="button"
                  onClick={cancelEdit}
                  className="text-xs font-mono text-charcoal-muted hover:text-charcoal flex items-center space-x-1"
                >
                  <X className="w-3 h-3" />
                  <span>Cancel Edit</span>
                </button>
              )}
            </div>

            <form onSubmit={handleSubmitJob} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1 font-semibold">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    value={jobForm.company}
                    onChange={(e) =>
                      setJobForm({ ...jobForm, company: e.target.value })
                    }
                    placeholder="e.g. Stripe"
                    className="w-full border-2 border-charcoal p-1.5 text-xs font-sans focus:outline-none focus:ring-1 focus:ring-coral"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1 font-semibold">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    value={jobForm.title}
                    onChange={(e) =>
                      setJobForm({ ...jobForm, title: e.target.value })
                    }
                    placeholder="e.g. Software Engineer"
                    className="w-full border-2 border-charcoal p-1.5 text-xs font-sans focus:outline-none focus:ring-1 focus:ring-coral"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Location (Optional)
                  </label>
                  <input
                    type="text"
                    value={jobForm.location}
                    onChange={(e) =>
                      setJobForm({ ...jobForm, location: e.target.value })
                    }
                    placeholder="e.g. San Francisco, CA"
                    className="w-full border-2 border-charcoal p-1.5 text-xs font-sans focus:outline-none focus:ring-1 focus:ring-coral"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
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
                    className="w-full border-2 border-charcoal p-1.5 text-xs font-sans focus:outline-none focus:ring-1 focus:ring-coral"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Job Posting URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={jobForm.job_url}
                    onChange={(e) =>
                      setJobForm({ ...jobForm, job_url: e.target.value })
                    }
                    placeholder="https://..."
                    className="w-full border-2 border-charcoal p-1.5 text-xs font-sans focus:outline-none focus:ring-1 focus:ring-coral"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1 font-semibold">
                  Raw Job Description *
                </label>
                <textarea
                  rows={6}
                  value={jobForm.raw_jd_text}
                  onChange={(e) =>
                    setJobForm({ ...jobForm, raw_jd_text: e.target.value })
                  }
                  placeholder="Paste the target job description here..."
                  className="w-full border-2 border-charcoal p-2.5 text-xs font-mono bg-cream focus:outline-none focus:ring-2 focus:ring-coral leading-relaxed"
                  required
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <div>
                  {activeJob && !editingJobId && (
                    <button
                      type="button"
                      onClick={() => setEditingJobId(activeJob.id)}
                      className="btn-secondary text-xs flex items-center space-x-1.5"
                    >
                      <Edit2 className="w-3 h-3 text-charcoal" />
                      <span>Edit Current Job</span>
                    </button>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn-primary flex items-center space-x-1.5 text-xs"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>
                      {submitting
                        ? "Saving Job..."
                        : editingJobId
                        ? "Update & Re-Analyze JD"
                        : "Save & Analyze Job Description"}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Confirmation Modal for Removing Saved Job */}
      {jobToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal/50 p-4">
          <div className="bg-white border-2 border-charcoal p-5 shadow-brutal max-w-sm w-full space-y-3 font-sans animate-in fade-in duration-150">
            <h3 className="font-bold text-sm text-charcoal">
              Remove Saved Job?
            </h3>
            <p className="text-xs text-charcoal-muted font-mono leading-relaxed">
              Are you sure you want to permanently remove{" "}
              <strong>{jobToDelete.title}</strong> at{" "}
              <strong>{jobToDelete.company}</strong>?
            </p>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setJobToDelete(null)}
                className="btn-secondary text-xs py-1 px-3"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                className="btn-primary bg-rose-600 hover:bg-rose-700 text-xs py-1 px-3"
              >
                Yes, Remove
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
