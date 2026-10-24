import React, { useState, useEffect } from 'react';
import Navbar from './components/layout/Navbar';
import WorkspacePage from './pages/WorkspacePage';
import ProfilePage from './pages/ProfilePage';
import ApplicationsPage from './pages/ApplicationsPage';
import AuthPage from './pages/AuthPage';
import { api } from './api/client';
import { authApi } from './api/auth';

export const PATH_TO_TAB = {
  '/': 'workspace',
  '/workspace': 'workspace',
  '/profile': 'profile',
  '/applications': 'applications',
  '/auth': 'auth',
};

export const TAB_TO_PATH = {
  workspace: '/',
  profile: '/profile',
  applications: '/applications',
  auth: '/auth',
};

export function getTabFromPath(pathname) {
  const clean = (pathname || '/').replace(/\/+$/, '') || '/';
  return PATH_TO_TAB[clean] || 'workspace';
}

export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window === 'undefined') return 'workspace';
    const tab = getTabFromPath(window.location.pathname);
    // Route guard: unauthorized users cannot directly initialize protected routes
    if ((tab === 'profile' || tab === 'applications') && !authApi.isAuthenticated()) {
      if (window.history?.replaceState) {
        window.history.replaceState(null, '', '/auth');
      }
      return 'auth';
    }
    return tab;
  });

  const [healthData, setHealthData] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(() => authApi.isAuthenticated());
  const [error, setError] = useState(null);

  const navigateToTab = (tab) => {
    // Route guard for protected tabs
    if ((tab === 'profile' || tab === 'applications') && !authApi.isAuthenticated()) {
      setActiveTab('auth');
      if (window.location.pathname !== '/auth') {
        window.history.pushState(null, '', '/auth');
      }
      return;
    }

    setActiveTab(tab);
    const targetPath = TAB_TO_PATH[tab] || '/';
    if (window.location.pathname !== targetPath) {
      window.history.pushState(null, '', targetPath);
    }
  };

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
          // If on a protected route, redirect to /auth
          setActiveTab((prev) => {
            if (prev === 'profile' || prev === 'applications') {
              window.history.replaceState(null, '', '/auth');
              return 'auth';
            }
            return prev;
          });
        })
        .finally(() => {
          setAuthLoading(false);
        });
    } else {
      setAuthLoading(false);
    }

    // Listen to browser Back/Forward navigation
    const handlePopState = () => {
      const tab = getTabFromPath(window.location.pathname);
      if ((tab === 'profile' || tab === 'applications') && !authApi.isAuthenticated()) {
        setActiveTab('auth');
        window.history.replaceState(null, '', '/auth');
      } else {
        setActiveTab(tab);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    navigateToTab('workspace');
  };

  const handleLogout = () => {
    authApi.logout();
    setCurrentUser(null);
    navigateToTab('auth');
  };

  return (
    <div className="min-h-screen bg-cream flex flex-row font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={navigateToTab}
        healthData={healthData}
        currentUser={currentUser}
      />

      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {authLoading && (activeTab === 'profile' || activeTab === 'applications') ? (
            <div className="card-brutal text-center py-12 space-y-3">
              <div className="inline-block animate-spin w-6 h-6 border-2 border-charcoal border-t-transparent rounded-full" />
              <div className="text-xs font-mono text-charcoal-muted">Verifying session...</div>
            </div>
          ) : (
            <>
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
            </>
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
