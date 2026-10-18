import React, { useState, useEffect } from 'react';
import Navbar from './components/layout/Navbar';
import WorkspacePage from './pages/WorkspacePage';
import ProfilePage from './pages/ProfilePage';
import ApplicationsPage from './pages/ApplicationsPage';
import AuthPage from './pages/AuthPage';
import { api } from './api/client';
import { authApi } from './api/auth';

export default function App() {
  const [activeTab, setActiveTab] = useState('workspace');
  const [healthData, setHealthData] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Probe backend health status on mount
    api.getHealth()
      .then((data) => {
        setHealthData(data);
        setError(null);
      })
      .catch((err) => {
        setError('Backend API is starting or not yet connected');
      });

    // If a token is in localStorage, attempt to load current user
    if (authApi.isAuthenticated()) {
      authApi.getMe()
        .then((user) => setCurrentUser(user))
        .catch(() => {
          authApi.logout();
          setCurrentUser(null);
        });
    }
  }, []);

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    setActiveTab('workspace');
  };

  const handleLogout = () => {
    authApi.logout();
    setCurrentUser(null);
    setActiveTab('auth');
  };

  return (
    <div className="min-h-screen bg-cream flex flex-row font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthData={healthData}
        currentUser={currentUser}
      />

      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'workspace' && <WorkspacePage currentUser={currentUser} />}
          {activeTab === 'profile' && <ProfilePage currentUser={currentUser} />}
          {activeTab === 'applications' && <ApplicationsPage currentUser={currentUser} />}
          {activeTab === 'auth' && (
            <AuthPage
              currentUser={currentUser}
              onAuthSuccess={handleAuthSuccess}
              onLogout={handleLogout}
            />
          )}
        </main>

        <footer className="border-t-2 border-charcoal bg-white py-3 px-6 mt-auto">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-charcoal-muted gap-2">
            <div>
              PrivateResume © 2026
            </div>
            <div className="flex items-center space-x-3">
              <span className={currentUser ? 'text-emerald-700 font-semibold' : 'text-charcoal-muted'}>
                {currentUser ? `User: ${currentUser.email}` : 'Guest Session'}
              </span>
              <span>·</span>
              <span className={healthData ? 'text-emerald-700 font-semibold' : 'text-amber-700'}>
                {healthData ? 'API Connected' : 'Checking API...'}
              </span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
