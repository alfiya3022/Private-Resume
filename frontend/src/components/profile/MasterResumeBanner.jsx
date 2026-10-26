import React from "react";
import {
  FileCheck,
  Upload,
  FileText,
  Eye,
  Trash2,
  RefreshCw,
} from "lucide-react";

export default function MasterResumeBanner({
  resumes,
  uploading,
  uploadStage,
  loadingReview,
  handleResumeUpload,
  handleOpenReview,
  handleDeleteResume,
  feedbackMsg,
  setFeedbackMsg,
}) {
  return (
    <div className="card-brutal p-3.5 sm:p-4 space-y-2.5">
      {/* Header and Upload action if no resume uploaded */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5">
        <h2 className="text-base sm:text-lg font-bold tracking-tight text-charcoal flex items-center space-x-2">
          <FileCheck className="w-4 h-4 text-coral shrink-0" />
          <span>Master Resume PDF</span>
        </h2>

        {resumes.length === 0 && (
          <label className="btn-primary cursor-pointer flex items-center space-x-1.5 py-1.5 px-3 text-xs">
            <Upload className="w-3.5 h-3.5" />
            <span>{uploading ? "Parsing PDF..." : "Upload Master PDF"}</span>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => handleResumeUpload(e, false)}
              disabled={uploading}
            />
          </label>
        )}
      </div>

      {/* Processing State Feedback Indicator */}
      {uploading && (
        <div className="p-2.5 border border-coral bg-coral-subtle/20 space-y-1.5 animate-in fade-in text-xs font-mono">
          <div className="flex items-center space-x-2 text-charcoal font-bold uppercase tracking-wider text-[11px]">
            <RefreshCw className="w-3.5 h-3.5 text-coral animate-spin" />
            <span>Processing</span>
          </div>
          <div className="text-xs text-charcoal font-semibold flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-coral animate-pulse"></span>
            <span>{uploadStage || "Processing your resume..."}</span>
          </div>
          <p className="text-[11px] text-charcoal-muted">
            Please wait while the system parses the PDF. Do not refresh or submit again.
          </p>
        </div>
      )}

      {/* Active Resume Row - Clean, Compact Single Row on Desktop */}
      {resumes.length > 0 && (
        <div className="border-t border-cream-border pt-2.5 space-y-2">
          {resumes.map((r) => (
            <div
              key={r.id}
              className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-2 sm:p-2.5 bg-cream border border-charcoal text-xs font-mono"
            >
              <div className="flex items-center space-x-2 min-w-0 truncate">
                <span className="text-[10px] font-bold uppercase tracking-wider text-charcoal-muted bg-white border border-charcoal/20 px-1.5 py-0.5 shrink-0">
                  Active
                </span>
                <FileText className="w-3.5 h-3.5 text-coral shrink-0" />
                <span className="font-semibold text-charcoal truncate">
                  {r.filename}
                </span>
                <span className="text-charcoal-muted shrink-0 text-[11px]">
                  ({Math.round(r.file_size / 1024)} KB)
                </span>
              </div>

              <div className="flex items-center space-x-1.5 shrink-0 self-end sm:self-auto">
                <button
                  type="button"
                  onClick={() => handleOpenReview(r.id)}
                  disabled={loadingReview}
                  className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1 bg-white hover:bg-cream"
                  title="Review Extracted Details"
                >
                  <Eye className="w-3 h-3 text-coral" />
                  <span>Review Extraction</span>
                </button>

                <label
                  className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1 cursor-pointer bg-white hover:bg-cream"
                  title="Replace Master Resume PDF"
                >
                  <Upload className="w-3 h-3 text-coral" />
                  <span>{uploading ? "Replacing..." : "Replace PDF"}</span>
                  <input
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => handleResumeUpload(e, true)}
                    disabled={uploading}
                  />
                </label>

                <button
                  onClick={() => handleDeleteResume(r.id)}
                  className="p-1 text-rose-600 hover:text-rose-800 border border-transparent hover:border-rose-300 transition-colors"
                  title="Remove Resume"
                  aria-label="Remove Resume"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {feedbackMsg.text && (
        <div
          className={`p-2.5 text-xs font-mono border flex items-center justify-between ${
            feedbackMsg.type === "success"
              ? "bg-emerald-50 border-emerald-500 text-emerald-900"
              : "bg-rose-50 border-rose-500 text-rose-900"
          }`}
        >
          <span>{feedbackMsg.text}</span>
          <button
            type="button"
            onClick={() => setFeedbackMsg({ type: "", text: "" })}
            className="font-bold ml-2 text-charcoal hover:text-coral"
            title="Dismiss"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
