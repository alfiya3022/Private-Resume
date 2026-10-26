import React from "react";
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
  AlertCircle,
  ExternalLink,
  HelpCircle,
} from "lucide-react";

export default function Stage3Matching({
  activeJob,
  matchData,
  matching,
  handleTriggerMatch,
  setCurrentStep,
  onNavigateToProfileEvidence,
}) {
  const handleEvidenceClick = (section, itemValue, extra = {}) => {
    if (!onNavigateToProfileEvidence) return;
    onNavigateToProfileEvidence({
      section,
      itemValue,
      jobId: activeJob?.id,
      jobTitle: activeJob?.title,
      company: activeJob?.company,
      stage: 3,
      ...extra,
    });
  };

  return (
    <div className="card-brutal space-y-4 font-sans">
      {/* Header with redundant top action buttons removed */}
      <div className="border-b border-cream-border pb-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <span className="badge-tag bg-coral-light text-coral border-coral font-bold">
              Stage 3
            </span>
            <h2 className="text-base sm:text-lg font-bold tracking-tight text-charcoal">
              Resume-to-Job Evidence Alignment
            </h2>
          </div>
          <p className="text-xs text-charcoal-muted mt-0.5">
            Cross-referencing candidate profile evidence against target
            requirements for <strong>{activeJob?.title}</strong>.
          </p>
        </div>

        {/* Lightweight Match Trigger / Refresh */}
        <button
          type="button"
          onClick={handleTriggerMatch}
          disabled={matching}
          className="btn-secondary text-xs flex items-center space-x-1.5 py-1 px-3"
          title="Recalculate evidence alignment"
        >
          {matching ? (
            <>
              <Sparkles className="w-3.5 h-3.5 text-coral animate-spin" />
              <span>Matching...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 text-coral" />
              <span>Re-run Alignment</span>
            </>
          )}
        </button>
      </div>

      {matching && (
        <div className="bg-cream border-2 border-charcoal p-6 text-center space-y-2 font-mono">
          <Sparkles className="w-6 h-6 text-coral animate-spin mx-auto" />
          <div className="font-bold text-xs uppercase tracking-wider text-charcoal">
            Computing Deterministic Evidence Alignment...
          </div>
          <p className="text-[11px] text-charcoal-muted max-w-sm mx-auto">
            Verifying project backing, employment citations, and candidate
            profile records.
          </p>
        </div>
      )}

      {!matching && !matchData && (
        <div className="p-6 text-center space-y-3 bg-cream border-2 border-charcoal">
          <p className="text-xs font-mono text-charcoal">
            No evidence alignment generated yet for this target job.
          </p>
          <button
            type="button"
            onClick={handleTriggerMatch}
            className="btn-primary text-xs"
          >
            Run Evidence Match Alignment
          </button>
        </div>
      )}

      {!matching && matchData && (
        <div className="space-y-4">
          {/* Estimated Job Match Metric Banner (Compact) */}
          <div className="border-2 border-charcoal bg-white p-4 shadow-brutal-sm flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="space-y-0.5">
              <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-charcoal-muted">
                Deterministic Alignment Metric
              </div>
              <div className="text-xl font-bold text-charcoal">
                Estimated Job Match
              </div>
              <p className="text-xs text-charcoal-muted max-w-md">
                Required skills (70% weight) and preferred skills (30% weight)
                cross-referenced against profile evidence.
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-center p-3 bg-cream border-2 border-charcoal shadow-brutal-sm shrink-0">
                <div className="text-3xl font-extrabold text-coral font-mono">
                  {matchData.estimated_match_score}%
                </div>
                <div className="text-[9px] font-mono uppercase tracking-wider text-charcoal-muted mt-0.5">
                  Evidence Match
                </div>
              </div>

              <div className="grid grid-cols-2 gap-1.5 text-xs font-mono">
                <div className="bg-emerald-50 border border-emerald-600 px-2 py-1 text-emerald-950 flex items-center justify-between gap-1.5">
                  <span className="text-charcoal-muted text-[10px]">
                    Matched:
                  </span>
                  <span className="font-bold">
                    {matchData.matched_skills?.length || 0}
                  </span>
                </div>
                <div className="bg-amber-50 border border-amber-600 px-2 py-1 text-amber-950 flex items-center justify-between gap-1.5">
                  <span className="text-charcoal-muted text-[10px]">Weak:</span>
                  <span className="font-bold">
                    {matchData.weak_skills?.length || 0}
                  </span>
                </div>
                <div className="bg-rose-50 border border-rose-600 px-2 py-1 text-rose-950 flex items-center justify-between gap-1.5">
                  <span className="text-charcoal-muted text-[10px]">
                    Missing:
                  </span>
                  <span className="font-bold">
                    {matchData.missing_skills?.length || 0}
                  </span>
                </div>
                <div className="bg-purple-50 border border-purple-600 px-2 py-1 text-purple-950 flex items-center justify-between gap-1.5">
                  <span className="text-charcoal-muted text-[10px]">
                    Unchecked:
                  </span>
                  <span className="font-bold">
                    {matchData.unsupported_claims?.length || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 4 Categorized Columns with Navigable Evidence Links */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 1. Matched Skills (Navigable) */}
            <div className="border-2 border-charcoal bg-white p-3.5 space-y-2.5">
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <h3 className="font-bold text-xs uppercase tracking-wider text-emerald-800 flex items-center space-x-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span>
                    Matched Skills ({matchData.matched_skills?.length || 0})
                  </span>
                </h3>
                <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 text-[10px]">
                  Verified
                </span>
              </div>
              <p className="text-[11px] text-charcoal-muted">
                Evidenced by projects or work history. Click an item to inspect
                in Profile:
              </p>
              <div className="space-y-1.5 max-h-52 overflow-y-auto pr-0.5">
                {matchData.matched_skills?.map((sk, i) => (
                  <div
                    key={i}
                    onClick={() => handleEvidenceClick("skills", sk)}
                    className="border border-charcoal bg-cream p-2 text-xs font-mono hover:bg-cream-muted transition-colors cursor-pointer group"
                    title="Click to view evidence in Profile"
                  >
                    <div className="flex justify-between items-center font-bold text-charcoal">
                      <span className="group-hover:text-coral transition-colors flex items-center space-x-1">
                        <span>{sk}</span>
                        <ExternalLink className="w-2.5 h-2.5 opacity-60 group-hover:opacity-100" />
                      </span>
                      <span className="text-[9px] text-emerald-700 bg-emerald-100 px-1 py-0.2 border border-emerald-500">
                        Backed
                      </span>
                    </div>
                    {matchData.evidence_map?.[sk] && (
                      <div className="mt-1 text-[10px] text-charcoal-muted border-t border-cream-border pt-0.5 space-y-0.5">
                        {matchData.evidence_map[sk].map((src, idx) => (
                          <div
                            key={idx}
                            onClick={(e) => {
                              e.stopPropagation();
                              const isProj = src
                                .toLowerCase()
                                .includes("project");
                              const isExp =
                                src.toLowerCase().includes("experience") ||
                                src.toLowerCase().includes("work");
                              handleEvidenceClick(
                                isProj
                                  ? "projects"
                                  : isExp
                                    ? "experience"
                                    : "skills",
                                src,
                              );
                            }}
                            className="hover:underline text-charcoal flex items-center space-x-1"
                          >
                            <span>↳ {src}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 2. Weakly Represented Skills (Navigable) */}
            <div className="border-2 border-charcoal bg-white p-3.5 space-y-2.5">
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <h3 className="font-bold text-xs uppercase tracking-wider text-amber-800 flex items-center space-x-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                  <span>
                    Weakly Represented Skills (
                    {matchData.weak_skills?.length || 0})
                  </span>
                </h3>
                <span className="badge-tag bg-amber-50 text-amber-900 border-amber-600 text-[10px]">
                  Needs Backing
                </span>
              </div>
              <p className="text-[11px] text-charcoal-muted">
                Listed in profile but lacks a linked project or accomplishment
                citation:
              </p>
              <div className="space-y-1.5 max-h-52 overflow-y-auto pr-0.5">
                {matchData.weak_skills?.map((sk, i) => (
                  <div
                    key={i}
                    onClick={() => handleEvidenceClick("skills", sk)}
                    className="border border-amber-500 bg-amber-50/50 p-2 text-xs font-mono hover:bg-amber-100/50 transition-colors cursor-pointer group"
                    title="Click to view and add evidence in Profile"
                  >
                    <div className="flex justify-between items-center font-bold text-charcoal">
                      <span className="group-hover:text-coral transition-colors flex items-center space-x-1">
                        <span>{sk}</span>
                        <ExternalLink className="w-2.5 h-2.5 opacity-60 group-hover:opacity-100" />
                      </span>
                      <span className="text-[9px] text-amber-800 bg-amber-100 px-1 py-0.2 border border-amber-400">
                        Add Evidence
                      </span>
                    </div>
                  </div>
                ))}
                {(!matchData.weak_skills ||
                  matchData.weak_skills.length === 0) && (
                  <p className="text-xs text-charcoal-muted">
                    None detected. Every claimed skill is substantiated!
                  </p>
                )}
              </div>
            </div>

            {/* 3. Missing Skills (Clear Explanation, Never Fabricates Destination) */}
            <div className="border-2 border-charcoal bg-white p-3.5 space-y-2.5">
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <h3 className="font-bold text-xs uppercase tracking-wider text-rose-800 flex items-center space-x-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                  <span>
                    Missing Skills ({matchData.missing_skills?.length || 0})
                  </span>
                </h3>
                <span className="badge-tag bg-rose-50 text-rose-900 border-rose-600 text-[10px]">
                  Excluded
                </span>
              </div>
              <div className="p-2 bg-rose-50/60 border border-rose-200 text-[11px] text-rose-950 font-mono flex items-start space-x-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                <span>
                  No supporting evidence found in candidate profile. Verity
                  adheres strictly to zero-fabrication and excludes missing
                  skills from generation.
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {matchData.missing_skills?.map((sk, i) => (
                  <span
                    key={i}
                    className="badge-tag bg-rose-50 text-rose-950 border-rose-400 text-[11px]"
                    title="Missing job requirement — excluded from resume generation"
                  >
                    {sk}
                  </span>
                ))}
                {(!matchData.missing_skills ||
                  matchData.missing_skills.length === 0) && (
                  <p className="text-xs text-charcoal-muted">
                    No skill gaps identified!
                  </p>
                )}
              </div>
            </div>

            {/* 4. Unsupported Claims (Navigable) */}
            <div className="border-2 border-charcoal bg-white p-3.5 space-y-2.5">
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <h3 className="font-bold text-xs uppercase tracking-wider text-purple-800 flex items-center space-x-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-purple-600" />
                  <span>
                    Unsupported Claims (
                    {matchData.unsupported_claims?.length || 0})
                  </span>
                </h3>
                <span className="badge-tag bg-purple-50 text-purple-900 border-purple-600 text-[10px]">
                  Integrity
                </span>
              </div>
              <p className="text-[11px] text-charcoal-muted">
                Profile claims that lack verifiable projects or work evidence:
              </p>
              <div className="space-y-1 max-h-52 overflow-y-auto pr-0.5">
                {matchData.unsupported_claims?.map((claim, i) => (
                  <div
                    key={i}
                    onClick={() => handleEvidenceClick("skills", claim)}
                    className="p-2 bg-purple-50 border border-purple-300 text-xs font-mono text-purple-950 hover:bg-purple-100 transition-colors cursor-pointer group flex items-start justify-between gap-1.5"
                    title="Click to inspect this claim in Profile"
                  >
                    <span className="break-words leading-relaxed">{claim}</span>
                    <ExternalLink className="w-3 h-3 text-purple-700 shrink-0 mt-0.5 opacity-60 group-hover:opacity-100" />
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

          {/* Single Clear Navigation Path at Bottom */}
          <div className="flex justify-between items-center pt-3 border-t border-cream-border">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="btn-secondary text-xs flex items-center space-x-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to JD Analysis</span>
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="btn-primary flex items-center space-x-1.5 text-xs"
            >
              <span>Next: Tailor Resume</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
