import React, { useState } from 'react';
import { User, GraduationCap, Briefcase, FolderGit2, Wrench, Award, FileText, Check } from 'lucide-react';

export default function ProfilePage() {
  const [activeSection, setActiveSection] = useState('personal');

  const sections = [
    { id: 'personal', label: 'Personal Info', icon: User },
    { id: 'experience', label: 'Experience', icon: Briefcase },
    { id: 'projects', label: 'Projects', icon: FolderGit2 },
    { id: 'skills', label: 'Skills', icon: Wrench },
    { id: 'education', label: 'Education', icon: GraduationCap },
    { id: 'certifications', label: 'Certifications', icon: Award },
    { id: 'template', label: 'Resume Template (LaTeX)', icon: FileText },
  ];

  return (
    <div className="space-y-6">
      <div className="card-brutal">
        <div className="border-b border-cream-border pb-4 mb-6">
          <h2 className="text-xl font-bold tracking-tight text-charcoal">
            Candidate Master Profile
          </h2>
          <p className="text-sm text-charcoal-muted mt-1">
            Structured candidate source of truth. All tailored resumes draw evidence from this profile without inventing qualifications.
          </p>
        </div>

        {/* Section Tabs */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 border-b border-cream-border pb-4 mb-6">
          {sections.map((sec) => {
            const Icon = sec.icon;
            const isCurrent = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => setActiveSection(sec.id)}
                className={`p-2.5 text-xs font-medium border flex flex-col items-center justify-center space-y-1.5 transition-all text-center ${
                  isCurrent
                    ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                    : 'bg-white text-charcoal border-cream-border hover:border-charcoal'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="truncate w-full">{sec.label}</span>
              </button>
            );
          })}
        </div>

        {/* Active Tab Content Area */}
        <div className="bg-cream p-6 border-2 border-charcoal">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-base text-charcoal capitalize">
              {activeSection} Configuration
            </h3>
            <span className="badge-tag bg-white">Saved</span>
          </div>

          <div className="space-y-4 max-w-xl">
            <div className="space-y-1">
              <label className="text-xs font-mono font-medium text-charcoal-muted uppercase">
                Section Overview
              </label>
              <p className="text-sm text-charcoal">
                Structured candidate records will be edited, uploaded via PDF parser, or verified in Epic 2.
              </p>
            </div>

            {activeSection === 'template' ? (
              <div className="bg-white border-2 border-charcoal p-4 space-y-3 font-mono text-xs">
                <div className="font-bold text-sm text-charcoal">LaTeX Package Manager</div>
                <p className="text-charcoal-muted">
                  Supports ZIP template uploads with <code className="bg-cream px-1">main.tex</code> and styling assets.
                </p>
                <div className="flex space-x-2">
                  <button className="btn-secondary">Upload ZIP Template</button>
                  <button className="btn-primary">Compile Test PDF</button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
