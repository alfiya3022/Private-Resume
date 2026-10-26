import React from "react";
import { Sparkles, ArrowRight, ArrowLeft, RotateCw, Check } from "lucide-react";

export default function Stage2Requirements({
  activeJob,
  analysis,
  analyzing,
  handleTriggerAnalysis,
  matchData,
  handleTriggerMatch,
  setCurrentStep,
}) {
  return (
    <div className="card-brutal space-y-4 font-sans">
      {/* Stage Header */}
      <div className="border-b border-cream-border pb-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <span className="badge-tag bg-coral-light text-coral border-coral font-bold">
              Stage 2
            </span>
            <h2 className="text-base sm:text-lg font-bold tracking-tight text-charcoal">
              Structured Job Requirements
            </h2>
          </div>
          <p className="text-xs text-charcoal-muted mt-0.5">
            Requirements extracted from target posting for <strong>{activeJob?.title}</strong> at{" "}
            <strong>{activeJob?.company}</strong>
            {analysis?.experience_years ? ` · Level: ${analysis.experience_years}` : ""}
          </p>
        </div>

        {/* Single Analysis Trigger / Retry Control */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={handleTriggerAnalysis}
            disabled={analyzing}
            className="btn-secondary text-xs flex items-center space-x-1.5 py-1 px-3"
            title={analysis ? "Rerun analysis on this job description" : "Analyze job description"}
          >
            {analyzing ? (
              <>
                <Sparkles className="w-3.5 h-3.5 text-coral animate-spin" />
                <span>Extracting Requirements...</span>
              </>
            ) : analysis ? (
              <>
                <RotateCw className="w-3.5 h-3.5 text-coral" />
                <span>Retry Analysis</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5 text-coral" />
                <span>Analyze JD</span>
              </>
            )}
          </button>
        </div>
      </div>

      {analyzing && (
        <div className="bg-cream border-2 border-charcoal p-6 text-center space-y-2.5 font-mono">
          <Sparkles className="w-6 h-6 text-coral animate-spin mx-auto" />
          <div className="font-bold text-xs uppercase tracking-wider text-charcoal">
            Extracting Structured Requirements...
          </div>
          <p className="text-[11px] text-charcoal-muted max-w-sm mx-auto">
            Classifying required skills, preferred qualifications, and core responsibilities.
          </p>
        </div>
      )}

      {!analyzing && !analysis && (
        <div className="p-6 text-center space-y-3 bg-cream border-2 border-charcoal">
          <p className="text-xs font-mono text-charcoal">
            No structured analysis generated yet for this job description.
          </p>
          <button
            type="button"
            onClick={handleTriggerAnalysis}
            className="btn-primary text-xs"
          >
            Analyze This Job Description
          </button>
        </div>
      )}

      {!analyzing && analysis && (
        <div className="space-y-4">
          {/* Top Row: Required vs Preferred Skills */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border-2 border-charcoal p-3.5 bg-white space-y-2.5">
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                  <span className="w-2 h-2 bg-coral inline-block"></span>
                  <span>
                    Required Skills ({analysis.required_skills?.length || 0})
                  </span>
                </h3>
                <span className="badge-tag bg-coral-light text-coral border-coral text-[10px]">
                  Core
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {analysis.required_skills?.map((sk, i) => (
                  <span
                    key={i}
                    className="badge-tag bg-white border-charcoal text-[11px] font-semibold"
                  >
                    {sk}
                  </span>
                ))}
                {(!analysis.required_skills || analysis.required_skills.length === 0) && (
                  <p className="text-xs text-charcoal-muted">
                    No explicit required skills identified.
                  </p>
                )}
              </div>
            </div>

            <div className="border-2 border-charcoal p-3.5 bg-cream space-y-2.5">
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
                  <span className="w-2 h-2 bg-charcoal inline-block"></span>
                  <span>
                    Preferred Skills ({analysis.preferred_skills?.length || 0})
                  </span>
                </h3>
                <span className="badge-tag bg-white text-[10px]">Bonus</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {analysis.preferred_skills?.map((sk, i) => (
                  <span
                    key={i}
                    className="badge-tag bg-white border-cream-border text-[11px]"
                  >
                    {sk}
                  </span>
                ))}
                {(!analysis.preferred_skills || analysis.preferred_skills.length === 0) && (
                  <p className="text-xs text-charcoal-muted">
                    No preferred skills specified.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Row: Responsibilities & Qualifications */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border-2 border-charcoal p-3.5 bg-white space-y-2">
              <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal border-b border-cream-border pb-1.5">
                Key Responsibilities
              </h3>
              <ul className="space-y-1.5 text-xs">
                {analysis.responsibilities?.map((resp, i) => (
                  <li key={i} className="flex items-start space-x-2 leading-relaxed">
                    <span className="text-coral shrink-0">•</span>
                    <span className="text-charcoal">{resp}</span>
                  </li>
                ))}
                {(!analysis.responsibilities || analysis.responsibilities.length === 0) && (
                  <p className="text-xs text-charcoal-muted">No explicit responsibilities parsed.</p>
                )}
              </ul>
            </div>

            <div className="border-2 border-charcoal p-3.5 bg-white space-y-2">
              <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal border-b border-cream-border pb-1.5">
                Minimum Qualifications
              </h3>
              <div className="p-2 bg-cream border border-charcoal font-mono text-[11px] font-bold text-charcoal mb-1.5">
                Experience Level: {analysis.experience_years || "Not specified"}
              </div>
              <ul className="space-y-1.5 text-xs">
                {analysis.qualifications?.map((qual, i) => (
                  <li key={i} className="flex items-start space-x-2 leading-relaxed">
                    <Check className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                    <span className="text-charcoal">{qual}</span>
                  </li>
                ))}
                {(!analysis.qualifications || analysis.qualifications.length === 0) && (
                  <p className="text-xs text-charcoal-muted">No specific qualifications listed.</p>
                )}
              </ul>
            </div>
          </div>

          {/* Single Clear Navigation Path at Bottom */}
          <div className="flex justify-between items-center pt-3 border-t border-cream-border">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="btn-secondary text-xs flex items-center space-x-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Job Description</span>
            </button>
            <button
              type="button"
              onClick={async () => {
                setCurrentStep(3);
                if (activeJob && !matchData) {
                  await handleTriggerMatch();
                }
              }}
              className="btn-primary flex items-center space-x-1.5 text-xs"
            >
              <span>Next</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
