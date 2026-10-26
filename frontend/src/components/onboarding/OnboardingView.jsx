import React from "react";
import {
  FileText,
  UserCheck,
  Briefcase,
  GitCompare,
  Sparkles,
  FileCheck,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  X,
  Compass,
} from "lucide-react";

export default function OnboardingView({
  onAddMasterResume,
  onSkip,
  onLater,
  onClose,
  isModal = false,
}) {
  const steps = [
    {
      num: 1,
      icon: FileText,
      title: "Add your Master Resume",
      badge: "Core Evidence",
    },
    {
      num: 2,
      icon: UserCheck,
      title: "Build or review your profile",
      badge: "Human Verified",
    },
    {
      num: 3,
      icon: Briefcase,
      title: "Add a job description",
      badge: "Opportunity",
    },
    {
      num: 4,
      icon: GitCompare,
      title: "Analyze & match skills",
      badge: "Zero Fabrication",
    },
    {
      num: 5,
      icon: Sparkles,
      title: "Tailor your resume",
      badge: "ASK AI",
    },
    {
      num: 6,
      icon: FileCheck,
      title: "Generate & validate PDF",
      badge: "ATS Ready",
    },
  ];

  const content = (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="bg-white border-2 border-charcoal p-6 shadow-brutal space-y-3 relative overflow-hidden">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-coral-light border border-coral text-coral-dark text-[11px] font-mono font-bold uppercase tracking-wider">
              <Compass className="w-3.5 h-3.5 text-coral" />
              <span>Getting Started Guide</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-charcoal tracking-tight">
              Welcome to Verity!
            </h1>
            <p className="text-xs sm:text-sm text-charcoal-muted font-medium max-w-2xl leading-relaxed">
              Your private workspace for building, tailoring, and tracking
              resumes. Let’s get your profile ready with our 6-step workflow.
            </p>
          </div>

          {isModal && onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-cream border border-charcoal transition-colors"
              title="Close guide"
            >
              <X className="w-4 h-4 text-charcoal" />
            </button>
          )}
        </div>

        {/* Local Guarantee Badge */}
        <div className="flex flex-wrap items-center gap-3 pt-2 text-[11px] font-mono text-charcoal-muted border-t border-cream-border">
          <div className="flex items-center space-x-1 text-emerald-800">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
            <span className="font-semibold">Local-First Storage</span>
          </div>
          <span>•</span>
          <div className="flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-coral" />
            <span>AI Recommends, You Approve</span>
          </div>
          <span>•</span>
          <div className="flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-charcoal" />
            <span>Never Fabricates Experience</span>
          </div>
        </div>
      </div>

      {/* 6-Step Workflow Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {steps.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.num}
              className="card-brutal bg-white p-4 space-y-2.5 border-2 border-charcoal hover:border-coral transition-colors flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="w-8 h-8 rounded-none bg-charcoal text-white font-bold text-xs flex items-center justify-center font-mono shadow-brutal-sm">
                    0{s.num}
                  </div>
                  <span className="badge-tag bg-cream text-charcoal-muted border-charcoal/30 text-[10px] font-mono">
                    {s.badge}
                  </span>
                </div>
                <div className="flex items-center space-x-2 pt-1">
                  <Icon className="w-4 h-4 text-coral shrink-0" />
                  <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal">
                    {s.title}
                  </h3>
                </div>
                <p className="text-[11px] text-charcoal-muted leading-relaxed">
                  {s.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Footer */}
      <div className="bg-white border-2 border-charcoal p-4 sm:p-5 shadow-brutal flex flex-col sm:flex-row items-center justify-between gap-3 font-sans">
        <div className="flex items-center space-x-2 text-xs font-mono text-charcoal-muted">
          <span>Ready to begin?</span>
          <span className="text-charcoal font-bold">
            Start with your Master Resume PDF:
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto justify-end">
          <button
            type="button"
            data-testid="onboarding-later-btn"
            onClick={onLater || onSkip}
            className="btn-secondary text-xs py-2 px-3.5 font-mono"
            title="Enter workspace and upload later"
          >
            I'll do this later
          </button>
          <button
            type="button"
            data-testid="onboarding-skip-btn"
            onClick={onSkip}
            className="btn-secondary text-xs py-2 px-3.5 font-mono text-charcoal-muted hover:text-charcoal"
            title="Skip onboarding for now"
          >
            Skip for now
          </button>
          <button
            type="button"
            data-testid="onboarding-add-resume-btn"
            onClick={onAddMasterResume}
            className="btn-primary text-xs py-2 px-4.5 font-bold uppercase tracking-wider flex items-center space-x-1.5 shadow-brutal-sm"
          >
            <span>Add Master Resume</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  if (isModal) {
    return (
      <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
        <div className="w-full max-w-4xl my-auto animate-in fade-in duration-150">
          {content}
        </div>
      </div>
    );
  }

  return <div className="py-2 sm:py-4">{content}</div>;
}
