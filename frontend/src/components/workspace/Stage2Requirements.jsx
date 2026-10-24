import React from "react";
import { Sparkles, CheckCircle2, ArrowRight, Check } from "lucide-react";

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
                    Required Skills ({analysis.required_skills?.length || 0})
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
  );
}
