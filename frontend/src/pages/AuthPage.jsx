import React, { useState } from "react";
import {
  Lock,
  Mail,
  User,
  ShieldCheck,
  LogOut,
  CheckCircle2,
  FileText,
  Sparkles,
  ArrowRight,
  Database,
  Briefcase,
} from "lucide-react";
import { authApi } from "../api/auth";

export default function AuthPage({ currentUser, onAuthSuccess, onLogout }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    setLoading(true);

    try {
      if (isRegister) {
        await authApi.register(email, password, fullName);
        setSuccessMsg("Account created successfully! Signing you in...");
        // Auto-login after registration
        await authApi.login(email, password);
        sessionStorage.setItem("pr_just_registered", "true");
      } else {
        await authApi.login(email, password);
        sessionStorage.removeItem("pr_just_registered");
      }
      const user = await authApi.getMe();
      if (onAuthSuccess) {
        onAuthSuccess(user, { isRegistration: isRegister });
      }
    } catch (err) {
      setErrorMsg(
        err.message || "Authentication failed. Please verify your details.",
      );
    } finally {
      setLoading(false);
    }
  };

  if (currentUser) {
    return (
      <div className="max-w-md mx-auto pt-8">
        <div className="card-brutal space-y-6 bg-white p-6 border-2 border-charcoal shadow-brutal">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-charcoal text-white mx-auto flex items-center justify-center font-bold text-xl shadow-brutal-sm">
              <User className="w-6 h-6 text-coral" />
            </div>
            <h2 className="text-xl font-bold tracking-tight text-charcoal">
              Active Account Session
            </h2>
            <p className="text-xs text-charcoal-muted">
              You are signed in to your local Verity workspace.
            </p>
          </div>

          <div className="bg-cream border-2 border-charcoal p-4 space-y-2.5 text-xs font-mono">
            <div className="flex justify-between items-center">
              <span className="text-charcoal-muted">Email:</span>
              <span className="font-semibold text-charcoal">
                {currentUser.email}
              </span>
            </div>
            {currentUser.full_name && (
              <div className="flex justify-between items-center">
                <span className="text-charcoal-muted">Name:</span>
                <span className="font-semibold text-charcoal">
                  {currentUser.full_name}
                </span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-charcoal-muted">User ID:</span>
              <span className="font-semibold text-charcoal">
                #{currentUser.id}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-charcoal-muted">Privacy Mode:</span>
              <span className="font-semibold text-emerald-800 bg-emerald-100 px-1.5 py-0.5 border border-emerald-400 text-[10px]">
                Local-First (Ollama)
              </span>
            </div>
          </div>

          <button
            onClick={onLogout}
            className="btn-secondary w-full py-2.5 flex items-center justify-center space-x-2 text-xs font-bold"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-6 sm:py-10">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
        {/* Left Column: Welcome & Value Propositions (UI Showcase Panel 1) */}
        <div className="md:col-span-6 space-y-6 pr-0 md:pr-4">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-coral-light border border-coral text-coral-dark text-[11px] font-mono font-bold uppercase tracking-wider mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-coral" />
              <span>Local-First & Privacy-First</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-charcoal leading-tight">
              Your Resume.
              <br />
              <span className="text-coral">Your Data.</span>
              <br />
              Your Control.
            </h1>
            <p className="text-sm font-medium text-charcoal-muted pt-1">
              Welcome to Verity. Tailor. Apply. Track.
              <br />
              All in one private, offline-capable workspace.
            </p>
          </div>

          {/* Benefits with check icons */}
          <div className="space-y-3 pt-2">
            {[
              {
                title: "AI-powered resume tailoring",
                desc: "Smart job alignment without hallucinating unverified skills",
              },
              {
                title: "Your data stays local",
                desc: "Zero third-party telemetry, tracking, or cloud data harvesting",
              },
              {
                title: "Evidence-based recommendations",
                desc: "Grounded strictly in your genuine qualifications and projects",
              },
              {
                title: "Track your applications",
                desc: "Full opportunity pipeline lifecycle and LaTeX artifact generator",
              },
            ].map((item, idx) => (
              <div key={idx} className="flex items-start space-x-3">
                <div className="w-5 h-5 rounded-full bg-emerald-100 border border-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                </div>
                <div>
                  <div className="text-xs font-bold text-charcoal">
                    {item.title}
                  </div>
                  <div className="text-[11px] text-charcoal-muted leading-tight">
                    {item.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Minimalist Neo-Brutalist Illustration Accent */}
          <div className="p-4 bg-white border-2 border-charcoal shadow-brutal-sm flex items-center space-x-4">
            <div className="relative shrink-0">
              <div className="w-12 h-14 bg-amber-100 border-2 border-charcoal rotate-[-4deg] flex items-center justify-center shadow-xs">
                <FileText className="w-6 h-6 text-charcoal-muted" />
              </div>
              <div className="w-12 h-14 bg-white border-2 border-charcoal absolute top-1 left-2 rotate-[4deg] flex items-center justify-center shadow-xs">
                <Sparkles className="w-6 h-6 text-coral" />
              </div>
            </div>
            <div className="text-xs font-mono text-charcoal-muted">
              <span className="font-bold text-charcoal block">
                Built for job seekers.
              </span>
              Complete control over your career data.
            </div>
          </div>
        </div>

        {/* Right Column: Authentication Card (UI Showcase Panel 1) */}
        <div className="md:col-span-6">
          <div className="card-brutal bg-white p-6 sm:p-7 border-2 border-charcoal shadow-brutal font-sans space-y-5">
            {/* Tab switchers: Sign In vs Create Account */}
            <div className="grid grid-cols-2 gap-2 border-b-2 border-charcoal pb-3">
              <button
                type="button"
                data-testid="auth-tab-signin"
                aria-label="Sign In Tab"
                onClick={() => {
                  setIsRegister(false);
                  setErrorMsg("");
                  setSuccessMsg("");
                }}
                className={`py-2 text-xs font-bold font-mono tracking-wider transition-all text-center border-2 ${
                  !isRegister
                    ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
                    : "bg-white text-charcoal-muted border-transparent hover:bg-cream hover:text-charcoal"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                data-testid="auth-tab-register"
                aria-label="Create Account Tab"
                onClick={() => {
                  setIsRegister(true);
                  setErrorMsg("");
                  setSuccessMsg("");
                }}
                className={`py-2 text-xs font-bold font-mono tracking-wider transition-all text-center border-2 ${
                  isRegister
                    ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
                    : "bg-white text-charcoal-muted border-transparent hover:bg-cream hover:text-charcoal"
                }`}
              >
                Create Account
              </button>
            </div>

            {errorMsg && (
              <div className="bg-rose-50 border-2 border-rose-500 text-rose-900 p-3 text-xs font-mono">
                {errorMsg}
              </div>
            )}

            {successMsg && (
              <div className="bg-emerald-50 border-2 border-emerald-500 text-emerald-900 p-3 text-xs font-mono">
                {successMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {isRegister && (
                <div>
                  <label className="block text-[11px] font-mono font-bold uppercase text-charcoal mb-1">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-charcoal-muted absolute left-3 top-3" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your name"
                      className="input-brutal w-full pl-9 py-2 text-xs font-sans"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-[11px] font-mono font-bold uppercase text-charcoal mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-charcoal-muted absolute left-3 top-3" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your Email address"
                    className="input-brutal w-full pl-9 py-2 text-xs font-sans"
                    required
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-[11px] font-mono font-bold uppercase text-charcoal">
                    Password (min. 8 characters)
                  </label>
                  {!isRegister && (
                    <span
                      title="Passwords are encrypted locally with bcrypt"
                      className="text-[10px] font-mono text-charcoal-muted cursor-help"
                    ></span>
                  )}
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-charcoal-muted absolute left-3 top-3" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="input-brutal w-full pl-9 py-2 text-xs font-sans"
                    required
                    minLength={8}
                  />
                </div>
              </div>

              <button
                type="submit"
                data-testid="auth-submit-btn"
                disabled={loading}
                className="btn-primary w-full py-2.5 mt-2 text-xs uppercase tracking-wider font-bold flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <>
                    <span>
                      {isRegister ? "Create Account & Start" : "Sign In"}
                    </span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Divider and local credentials guarantee */}
            <div className="relative text-center my-3">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-cream-border" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
