import React from "react";
import {
  FileCode,
  ListFilter,
  Briefcase,
  Sparkles,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

export default function Stage1JobIntake({
  savedJobs,
  activeJob,
  activeMasterResume,
  profile,
  jobForm,
  setJobForm,
  formatSalaryINR,
  handleSubmitJob,
  handleSelectJob,
  submitting,
  errorMsg,
  successMsg,
}) {
  return (
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
  );
}
