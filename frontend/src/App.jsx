import React, { useState, useEffect } from "react";
import Navbar from "./components/layout/Navbar";
import WorkspacePage from "./pages/WorkspacePage";
import ProfilePage from "./pages/ProfilePage";
import ApplicationsPage from "./pages/ApplicationsPage";
import AuthPage from "./pages/AuthPage";
import OnboardingView from "./components/onboarding/OnboardingView";
import { api } from "./api/client";
import { authApi } from "./api/auth";
import { profileApi } from "./api/profile";
import ErrorBoundary from "./components/common/ErrorBoundary";
import { ToastProvider } from "./context/ToastContext";

export const PATH_TO_TAB = {
  "/": "workspace",
  "/workspace": "workspace",
  "/profile": "profile",
  "/applications": "applications",
  "/auth": "auth",
  "/onboarding": "onboarding",
};

export const TAB_TO_PATH = {
  workspace: "/",
  profile: "/profile",
  applications: "/applications",
  auth: "/auth",
  onboarding: "/onboarding",
};

export function getTabFromPath(pathname) {
  const clean = (pathname || "/").replace(/\/+$/, "") || "/";
  return PATH_TO_TAB[clean] || "workspace";
}

export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window === "undefined") return "workspace";
    const tab = getTabFromPath(window.location.pathname);
    // Route guard: unauthorized users cannot directly initialize protected routes
    if (
      (tab === "profile" || tab === "applications" || tab === "onboarding") &&
      !authApi.isAuthenticated()
    ) {
      if (window.history?.replaceState) {
        window.history.replaceState(null, "", "/auth");
      }
      return "auth";
    }
    // Route guard: onboarding is only accessible directly after new account registration
    if (
      tab === "onboarding" &&
      sessionStorage.getItem("pr_just_registered") !== "true"
    ) {
      if (window.history?.replaceState) {
        window.history.replaceState(null, "", "/");
      }
      return "workspace";
    }
    return tab;
  });

  const [healthData, setHealthData] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(() =>
    authApi.isAuthenticated(),
  );
  const [error, setError] = useState(null);
  const [evidenceTarget, setEvidenceTarget] = useState(null);

  const navigateToTab = (tab, params = {}) => {
    // Route guard for protected tabs
    if (
      (tab === "profile" || tab === "applications" || tab === "onboarding") &&
      !authApi.isAuthenticated()
    ) {
      setActiveTab("auth");
      if (window.location.pathname !== "/auth") {
        window.history.pushState(null, "", "/auth");
      }
      return;
    }

    if (
      tab === "onboarding" &&
      sessionStorage.getItem("pr_just_registered") !== "true"
    ) {
      setActiveTab("workspace");
      if (window.location.pathname !== "/") {
        window.history.pushState(null, "", "/");
      }
      return;
    }

    setActiveTab(tab);
    const basePath = TAB_TO_PATH[tab] || "/";
    const searchParams = new URLSearchParams();

    if (tab === "workspace") {
      const stage =
        params.stage ||
        parseInt(sessionStorage.getItem("pr_workspace_stage"), 10);
      const jobId =
        params.jobId ||
        parseInt(sessionStorage.getItem("pr_workspace_job_id"), 10);
      if (stage && stage > 1) {
        searchParams.set("stage", String(stage));
        sessionStorage.setItem("pr_workspace_stage", String(stage));
      }
      if (jobId) {
        searchParams.set("jobId", String(jobId));
        sessionStorage.setItem("pr_workspace_job_id", String(jobId));
      }
    } else if (tab === "profile" && params.from) {
      searchParams.set("from", params.from);
      if (params.stage) searchParams.set("stage", String(params.stage));
      if (params.jobId) searchParams.set("jobId", String(params.jobId));
    }

    const queryStr = searchParams.toString();
    const targetPath = queryStr ? `${basePath}?${queryStr}` : basePath;
    if (window.location.pathname + window.location.search !== targetPath) {
      window.history.pushState(null, "", targetPath);
    }
  };

  const handleNavigateToProfileEvidence = (target) => {
    setEvidenceTarget(target);
    const stage = target?.stage || 3;
    const jobId = target?.jobId;
    navigateToTab("profile", { from: "workspace", stage, jobId });
  };

  const handleReturnToWorkspace = (context) => {
    const stage = context?.stage || evidenceTarget?.stage || 3;
    const jobId = context?.jobId || evidenceTarget?.jobId;
    setEvidenceTarget(null);
    navigateToTab("workspace", { stage, jobId });
  };

  useEffect(() => {
    // Probe backend health status on mount
    api
      .getHealth()
      .then((data) => {
        setHealthData(data);
        setError(null);
      })
      .catch((err) => {
        setError("Backend API is starting or not yet connected");
      });

    // If a token is in localStorage, attempt to load current user
    if (authApi.isAuthenticated()) {
      authApi
        .getMe()
        .then((user) => {
          setCurrentUser(user);
          // If the user refreshed on /onboarding but already completed onboarding or not in a fresh registration, redirect to workspace
          if (
            window.location.pathname === "/onboarding" &&
            (user.onboarding_completed ||
              sessionStorage.getItem("pr_just_registered") !== "true")
          ) {
            sessionStorage.removeItem("pr_just_registered");
            navigateToTab("workspace");
          }
        })
        .catch(() => {
          authApi.logout();
          sessionStorage.removeItem("pr_just_registered");
          setCurrentUser(null);
          // If on a protected route, redirect to /auth
          setActiveTab((prev) => {
            if (
              prev === "profile" ||
              prev === "applications" ||
              prev === "onboarding"
            ) {
              window.history.replaceState(null, "", "/auth");
              return "auth";
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
      if (
        (tab === "profile" || tab === "applications" || tab === "onboarding") &&
        !authApi.isAuthenticated()
      ) {
        setActiveTab("auth");
        window.history.replaceState(null, "", "/auth");
      } else if (
        tab === "onboarding" &&
        sessionStorage.getItem("pr_just_registered") !== "true"
      ) {
        setActiveTab("workspace");
        window.history.replaceState(null, "", "/");
      } else {
        setActiveTab(tab);
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const handleDismissOnboarding = async (targetTab = "workspace") => {
    sessionStorage.removeItem("pr_just_registered");
    if (currentUser) {
      try {
        await authApi.completeOnboarding();
        setCurrentUser((prev) =>
          prev ? { ...prev, onboarding_completed: true } : prev,
        );
      } catch {
        // Fallback gracefully
      }
    }
    navigateToTab(targetTab, { stage: 1 });
  };

  const handleAddMasterResumeFromOnboarding = async () => {
    sessionStorage.removeItem("pr_just_registered");
    if (currentUser) {
      try {
        await authApi.completeOnboarding();
        setCurrentUser((prev) =>
          prev ? { ...prev, onboarding_completed: true } : prev,
        );
      } catch {
        // Fallback gracefully
      }
    }
    navigateToTab("profile", { from: "onboarding" });
  };

  const handleAuthSuccess = (user, meta = {}) => {
    setCurrentUser(user);
    if (meta.isRegistration) {
      sessionStorage.setItem("pr_just_registered", "true");
      navigateToTab("onboarding");
      return;
    }
    sessionStorage.removeItem("pr_just_registered");
    navigateToTab("workspace");
  };

  const handleLogout = () => {
    authApi.logout();
    sessionStorage.removeItem("pr_just_registered");
    setCurrentUser(null);
    navigateToTab("auth");
  };

  return (
    <ToastProvider>
      <div className="min-h-screen bg-cream flex flex-row font-sans">
        <Navbar
          activeTab={activeTab}
          setActiveTab={navigateToTab}
          healthData={healthData}
          currentUser={currentUser}
        />

        <div className="flex-1 flex flex-col min-w-0 min-h-screen">
          <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 py-4">
            <ErrorBoundary>
              {authLoading &&
              (activeTab === "profile" ||
                activeTab === "applications" ||
                activeTab === "onboarding") ? (
                <div className="card-brutal text-center py-8 space-y-3">
                  <div className="inline-block animate-spin w-5 h-5 border-2 border-charcoal border-t-transparent rounded-full" />
                  <div className="text-xs font-mono text-charcoal-muted">
                    Verifying session...
                  </div>
                </div>
              ) : (
                <>
                  {activeTab === "workspace" && (
                    <WorkspacePage
                      currentUser={currentUser}
                      onNavigateToProfileEvidence={
                        handleNavigateToProfileEvidence
                      }
                    />
                  )}
                  {activeTab === "profile" && (
                    <ProfilePage
                      currentUser={currentUser}
                      evidenceTarget={evidenceTarget}
                      clearEvidenceTarget={() => setEvidenceTarget(null)}
                      onReturnToWorkspace={handleReturnToWorkspace}
                    />
                  )}
                  {activeTab === "applications" && (
                    <ApplicationsPage currentUser={currentUser} />
                  )}
                  {activeTab === "auth" && (
                    <AuthPage
                      currentUser={currentUser}
                      onAuthSuccess={handleAuthSuccess}
                      onLogout={handleLogout}
                    />
                  )}
                  {activeTab === "onboarding" && (
                    <OnboardingView
                      isModal={false}
                      onAddMasterResume={handleAddMasterResumeFromOnboarding}
                      onSkip={() => handleDismissOnboarding("workspace")}
                      onLater={() => handleDismissOnboarding("workspace")}
                    />
                  )}
                </>
              )}
            </ErrorBoundary>
          </main>

          <footer className="border-t-2 border-charcoal bg-white py-2.5 px-6 mt-auto">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-charcoal-muted gap-2">
              <div>Verity © 2026</div>
              <div className="flex items-center space-x-3">
                <span
                  className={
                    currentUser
                      ? "text-emerald-700 font-semibold"
                      : "text-charcoal-muted"
                  }
                >
                  {currentUser ? `User: ${currentUser.email}` : "Guest Session"}
                </span>
                <span>·</span>
                <span
                  className={
                    healthData
                      ? "text-emerald-700 font-semibold"
                      : "text-amber-700"
                  }
                >
                  {healthData ? "API Connected" : "Checking API..."}
                </span>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </ToastProvider>
  );
}
