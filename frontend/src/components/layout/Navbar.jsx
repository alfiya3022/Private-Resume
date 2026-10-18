import React from 'react';
import { Briefcase, User, CheckCircle2, Shield } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, currentUser }) {
  const navItems = [
    { id: 'workspace', label: 'Workspace', icon: Briefcase },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'applications', label: 'Applications', icon: CheckCircle2 },
  ];

  return (
    <header className="border-b-2 border-charcoal bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Brand Logo & Navigation Tabs */}
          <div className="flex items-center space-x-4 sm:space-x-8">
            <div
              onClick={() => setActiveTab('workspace')}
              className="flex items-center space-x-2.5 cursor-pointer select-none"
            >
              <div className="w-8 h-8 bg-charcoal text-white flex items-center justify-center font-bold text-base shadow-brutal-sm">
                PR
              </div>
              <span className="font-bold text-lg tracking-tight text-charcoal">
                PrivateResume
              </span>
            </div>

            {/* Navigation Tabs aligned to the left */}
            <nav className="flex space-x-1 sm:space-x-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center space-x-2 px-3 py-1.5 text-xs sm:text-sm font-medium transition-all ${
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
          </div>

          {/* Right: Auth / Candidate Session */}
          <div className="flex items-center">
            <button
              onClick={() => setActiveTab('auth')}
              className={`flex items-center space-x-2 px-3 py-1.5 text-xs sm:text-sm font-medium transition-all border ${
                activeTab === 'auth'
                  ? 'bg-charcoal text-white border-charcoal shadow-brutal-sm'
                  : 'bg-white text-charcoal border-charcoal hover:bg-cream-muted'
              }`}
            >
              <Shield className="w-3.5 h-3.5 text-coral" />
              <span>
                {currentUser ? (currentUser.full_name || currentUser.email.split('@')[0]) : 'Sign In'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
