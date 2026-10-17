import React from 'react';
import { FileText, Briefcase, User, CheckCircle2, Shield } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, healthData }) {
  const navItems = [
    { id: 'workspace', label: 'Workspace', icon: Briefcase },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'applications', label: 'Applications', icon: CheckCircle2 },
    { id: 'auth', label: 'Auth', icon: Shield },
  ];

  return (
    <header className="border-b-2 border-charcoal bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 bg-charcoal text-white flex items-center justify-center font-bold text-lg shadow-brutal-sm">
              PR
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-charcoal">
                  PrivateResume
                </span>
                <span className="badge-tag bg-coral-light text-coral border-coral">
                  Local-First V1
                </span>
              </div>
              <p className="text-xs text-charcoal-muted hidden sm:block">
                AI recommends · Candidate approves · System compiles
              </p>
            </div>
          </div>

          {/* Navigation Links (Four Locked Areas) */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-charcoal text-white shadow-brutal-sm'
                      : 'text-charcoal hover:bg-cream-muted border border-transparent'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Subsystem Health Indicator */}
          <div className="hidden lg:flex items-center space-x-2 text-xs font-mono">
            <span
              title={`Database: ${healthData?.subsystems?.database || 'checking'}`}
              className={`inline-block w-2.5 h-2.5 rounded-full ${
                healthData?.subsystems?.database === 'connected' ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
            />
            <span className="text-charcoal-muted">
              {healthData?.subsystems?.ollama === 'connected' ? 'Ollama Ready' : 'Ollama Local'}
            </span>
            <span className="text-cream-border">|</span>
            <span className="text-charcoal-muted">
              {healthData?.subsystems?.latex === 'available' ? 'LaTeX Ready' : 'LaTeX Standby'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
