import React from "react";
import { Sparkles, CheckCircle2, ArrowRight, Check, AlertCircle } from "lucide-react";

export default function Stage3Matching({
  activeJob,
  matchData,
  matching,
  handleTriggerMatch,
  setCurrentStep,
}) {
  return (
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
  );
}
