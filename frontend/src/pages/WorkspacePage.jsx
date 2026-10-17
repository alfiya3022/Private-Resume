import React, { useState } from 'react';
import { Upload, Sparkles, CheckCircle, ArrowRight, FileCode, Sliders } from 'lucide-react';

export default function WorkspacePage() {
  const [currentStep, setCurrentStep] = useState(1);
  const steps = [
    { num: 1, label: '1. Add Inputs', desc: 'Master Resume & Job Description' },
    { num: 2, label: '2. Analyze JD', desc: 'Structured Requirements Extraction' },
    { num: 3, label: '3. Match Evidence', desc: 'Deterministic Skill & Claim Alignment' },
    { num: 4, label: '4. Tailor Resume', desc: 'Section Editing & AI Consultation' },
    { num: 5, label: '5. Validate & PDF', desc: 'LaTeX Compilation & Quality Gate' },
  ];

  return (
    <div className="space-y-6">
      {/* Workflow Stepper Header */}
      <div className="bg-white border-2 border-charcoal p-4 shadow-brutal-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-charcoal-muted">
              Workflow State:
            </span>
            <span className="badge-tag bg-cream-muted text-charcoal">
              Progressive Workspace
            </span>
          </div>
          <div className="flex items-center space-x-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
            {steps.map((s) => (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`px-3 py-1.5 text-xs font-medium border flex items-center space-x-1.5 transition-all whitespace-nowrap ${
                  currentStep === s.num
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Workspace Active Stage Container */}
      <div className="card-brutal space-y-6">
        <div className="border-b border-cream-border pb-4">
          <h2 className="text-xl font-bold tracking-tight text-charcoal flex items-center space-x-2">
            <span>Stage 1: Job Description & Candidate Context</span>
          </h2>
          <p className="text-sm text-charcoal-muted mt-1">
            Provide the target job description. The AI engine will extract structured technical requirements without fabricating experience.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Master Resume Summary Box */}
          <div className="border-2 border-charcoal bg-cream p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-charcoal uppercase tracking-wider flex items-center space-x-2">
                <FileCode className="w-4 h-4 text-coral" />
                <span>Active Master Resume</span>
              </h3>
              <span className="badge-tag bg-white">Verified</span>
            </div>
            <p className="text-xs text-charcoal-muted">
              Source candidate data loaded from your verified master profile.
            </p>
            <div className="bg-white border border-charcoal p-3 text-xs space-y-1 font-mono">
              <div className="flex justify-between">
                <span className="text-charcoal-muted">Profile:</span>
                <span className="font-semibold">Candidate Profile Active</span>
              </div>
              <div className="flex justify-between">
                <span className="text-charcoal-muted">LaTeX Template:</span>
                <span className="text-emerald-700 font-semibold">Standard Modern (main.tex)</span>
              </div>
            </div>
          </div>

          {/* Target Job Input Box */}
          <div className="border-2 border-charcoal bg-white p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-charcoal uppercase tracking-wider flex items-center space-x-2">
                <Upload className="w-4 h-4 text-coral" />
                <span>Target Job Description</span>
              </h3>
              <span className="badge-tag bg-coral-light text-coral border-coral">Required</span>
            </div>
            <textarea
              rows={6}
              placeholder="Paste raw job description here (e.g. responsibilities, required qualifications, technical stack)..."
              className="w-full border-2 border-charcoal p-3 text-sm font-mono placeholder:text-charcoal-light focus:outline-none focus:ring-2 focus:ring-coral"
              defaultValue=""
            />
            <div className="flex justify-end">
              <button className="btn-primary flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>Analyze Job Description</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
