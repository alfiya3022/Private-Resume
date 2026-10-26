import React, { useState } from "react";
import {
  Briefcase,
  User,
  CheckCircle2,
  Shield,
  PanelLeftClose,
  PanelLeftOpen,
  Compass,
} from "lucide-react";

export default function Navbar({
  activeTab,
  setActiveTab,
  healthData,
  currentUser,
  onOpenWelcomeGuide,
}) {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem("pr_sidebar_collapsed") === "true";
  });

  const toggleSidebar = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("pr_sidebar_collapsed", String(next));
      return next;
    });
  };

  const navItems = [
    { id: "workspace", label: "Workspace", icon: Briefcase },
    { id: "profile", label: "Profile", icon: User },
    { id: "applications", label: "Applications", icon: CheckCircle2 },
  ];

  const authLabel = currentUser
    ? currentUser.full_name || currentUser.email.split("@")[0]
    : "Sign In";

  // Extract initials for the showcase-style user avatar
  const getInitials = () => {
    if (!currentUser) return "?";
    if (currentUser.full_name) {
      const parts = currentUser.full_name.trim().split(/\s+/);
      if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
      }
      return parts[0].slice(0, 2).toUpperCase();
    }
    return currentUser.email.slice(0, 2).toUpperCase();
  };

  return (
    <aside
      className={`border-r-2 border-charcoal bg-white flex flex-col justify-between shrink-0 min-h-screen transition-all duration-200 z-30 ${
        isCollapsed ? "w-16" : "w-60"
      }`}
    >
      {/* Top: Logo / Brand Header */}
      <div>
        <div
          className={`p-3.5 border-b-2 border-charcoal bg-cream flex items-center ${
            isCollapsed ? "justify-center" : "justify-between"
          }`}
        >
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div
              className="w-8 h-8 bg-charcoal text-white flex items-center justify-center font-bold text-sm shadow-brutal-sm shrink-0 select-none"
              title="Verity"
            >
              VR
            </div>
            {!isCollapsed && (
              <span className="font-bold text-base tracking-tight text-charcoal truncate select-none">
                Verity
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={toggleSidebar}
            className={`p-1 text-charcoal hover:bg-cream-muted border border-transparent hover:border-charcoal transition-all ${
              isCollapsed ? "hidden" : "block"
            }`}
            title="Collapse sidebar"
            aria-label="Collapse sidebar"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>

        {/* Collapsed expand toggle button */}
        {isCollapsed && (
          <div className="p-2 border-b border-cream-border flex justify-center">
            <button
              type="button"
              onClick={toggleSidebar}
              className="p-1 text-charcoal hover:bg-cream border border-transparent hover:border-charcoal transition-all"
              title="Expand sidebar"
              aria-label="Expand sidebar"
            >
              <PanelLeftOpen className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Navigation Section */}
        <nav
          className="p-2.5 space-y-1.5 flex flex-col"
          aria-label="Main Navigation"
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                title={item.label}
                aria-current={isActive ? "page" : undefined}
                className={`w-full flex items-center px-3 py-2 text-xs font-semibold transition-all text-left ${
                  isCollapsed ? "justify-center px-2" : "space-x-3"
                } ${
                  isActive
                    ? "bg-charcoal text-white shadow-brutal-sm border-2 border-charcoal"
                    : "text-charcoal hover:bg-cream border-2 border-transparent hover:border-charcoal"
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 ${isActive ? "text-coral" : "text-charcoal"}`}
                />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}

          {/* User Profile Identity (UI Showcase Style) */}
          <div className="pt-2 border-t border-cream-border mt-2">
            <button
              onClick={() => setActiveTab("auth")}
              title={currentUser ? `Signed in as ${authLabel}` : "Sign In"}
              className={`w-full flex items-center p-2 text-xs font-mono border-2 border-charcoal bg-white transition-all ${
                isCollapsed ? "justify-center p-2" : "justify-between space-x-2"
              } ${
                activeTab === "auth"
                  ? "ring-2 ring-coral shadow-brutal-sm bg-coral-light/20"
                  : "hover:bg-cream-muted"
              }`}
            >
              <div className="flex items-center space-x-2 truncate min-w-0">
                {currentUser ? (
                  <div className="w-6 h-6 rounded-full bg-blue-100 border border-blue-600 text-blue-900 font-bold flex items-center justify-center text-[10px] shrink-0 font-sans">
                    {getInitials()}
                  </div>
                ) : (
                  <Shield className="w-4 h-4 text-charcoal shrink-0" />
                )}
                {!isCollapsed && (
                  <span className="font-bold truncate text-charcoal text-[11px]">
                    {authLabel}
                  </span>
                )}
              </div>
              {!isCollapsed && (
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${
                    healthData ? "bg-emerald-500" : "bg-amber-500"
                  }`}
                  title={
                    healthData ? "API Connected" : "Checking Connection..."
                  }
                />
              )}
            </button>
          </div>
        </nav>
      </div>

      {/* Footer / System Status */}
      <div
        className={`p-2.5 border-t-2 border-charcoal bg-cream flex items-center ${
          isCollapsed
            ? "justify-center"
            : "justify-between text-[11px] font-mono text-charcoal-muted"
        }`}
      >
        {!isCollapsed ? (
          <>
            <span className="truncate">Local Privacy Mode</span>
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                healthData ? "bg-emerald-500" : "bg-amber-500"
              }`}
              title={healthData ? "API Connected" : "Checking Connection..."}
            />
          </>
        ) : (
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              healthData ? "bg-emerald-500" : "bg-amber-500"
            }`}
            title={healthData ? "API Connected" : "Checking Connection..."}
          />
        )}
      </div>
    </aside>
  );
}
