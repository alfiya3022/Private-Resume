import React from 'react';
import { Briefcase, User, CheckCircle2, Shield } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, healthData, currentUser }) {
  const navItems = [
    { id: 'workspace', label: 'Workspace', icon: Briefcase },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'applications', label: 'Applications', icon: CheckCircle2 },
  ];

  const authLabel = currentUser
    ? (currentUser.full_name || currentUser.email.split('@')[0])
    : 'Sign In';

  return (
    <aside className="w-64 border-r-2 border-charcoal bg-white flex flex-col justify-between shrink-0 min-h-screen">
      {/* Top: Brand Header */}
      <div>
        <div className="p-5 border-b-2 border-charcoal flex items-center space-x-3 bg-white">
          <div className="w-9 h-9 bg-charcoal text-white flex items-center justify-center font-bold text-base shadow-brutal-sm">
            PR
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight text-charcoal block">
              PrivateResume
            </span>
          </div>
        </div>

        {/* Vertical Nav Tabs */}
        <nav className="p-4 space-y-2 flex flex-col">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 text-sm font-semibold transition-all text-left ${
                  isActive
                    ? 'bg-charcoal text-white shadow-brutal-sm border-2 border-charcoal'
                    : 'text-charcoal hover:bg-cream border-2 border-transparent hover:border-charcoal'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom: User Session / Auth Tab */}
      <div className="p-4 border-t-2 border-charcoal bg-cream">
        <button
          onClick={() => setActiveTab('auth')}
          className={`w-full flex items-center justify-between p-2.5 text-xs font-mono border-2 border-charcoal bg-white transition-all ${
            activeTab === 'auth'
              ? 'ring-2 ring-coral shadow-brutal-sm'
              : 'hover:bg-cream-muted'
          }`}
        >
          <div className="flex items-center space-x-2 truncate">
            <Shield className="w-4 h-4 text-charcoal shrink-0" />
            <span className="font-bold truncate text-charcoal">
              {authLabel}
            </span>
          </div>
          <span
            className={`w-2.5 h-2.5 rounded-full shrink-0 ${
              healthData ? 'bg-emerald-500' : 'bg-amber-500'
            }`}
            title={healthData ? 'Backend Connected' : 'Checking Connection...'}
          />
        </button>
      </div>
    </aside>
  );
}
