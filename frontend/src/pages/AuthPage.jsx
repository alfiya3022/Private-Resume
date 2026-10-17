import React, { useState } from 'react';
import { Lock, Mail, User, ShieldCheck, LogOut, CheckCircle2 } from 'lucide-react';
import { authApi } from '../api/auth';

export default function AuthPage({ currentUser, onAuthSuccess, onLogout }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');
    setLoading(true);

    try {
      if (isRegister) {
        await authApi.register(email, password, fullName);
        setSuccessMsg('Account created successfully! Signing you in...');
        // Auto-login after registration
        await authApi.login(email, password);
      } else {
        await authApi.login(email, password);
      }
      const user = await authApi.getMe();
      if (onAuthSuccess) {
        onAuthSuccess(user);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed. Please verify your details.');
    } finally {
      setLoading(false);
    }
  };

  if (currentUser) {
    return (
      <div className="max-w-md mx-auto pt-6">
        <div className="card-brutal space-y-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-charcoal text-white mx-auto flex items-center justify-center font-bold text-xl shadow-brutal-sm">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-charcoal">
              Authenticated Session
            </h2>
            <p className="text-xs text-charcoal-muted">
              Your candidate data is isolated and protected under your local session.
            </p>
          </div>

          <div className="bg-cream border-2 border-charcoal p-4 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-charcoal-muted">Email:</span>
              <span className="font-semibold text-charcoal">{currentUser.email}</span>
            </div>
            {currentUser.full_name && (
              <div className="flex justify-between">
                <span className="text-charcoal-muted">Name:</span>
                <span className="font-semibold text-charcoal">{currentUser.full_name}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-charcoal-muted">User ID:</span>
              <span className="font-semibold text-charcoal">#{currentUser.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-charcoal-muted">Status:</span>
              <span className="text-emerald-700 font-bold">Active & Verified</span>
            </div>
          </div>

          <button
            onClick={onLogout}
            className="btn-secondary w-full py-2.5 flex items-center justify-center space-x-2"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto pt-6">
      <div className="card-brutal space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-charcoal text-white mx-auto flex items-center justify-center font-bold text-xl shadow-brutal-sm">
            <Lock className="w-6 h-6 text-coral" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-charcoal">
            {isRegister ? 'Create Your Account' : 'Welcome to PrivateResume'}
          </h2>
          <p className="text-xs text-charcoal-muted">
            All candidate resumes and Ollama inference remain strictly local to your machine.
          </p>
        </div>

        {errorMsg && (
          <div className="bg-rose-50 border-2 border-rose-500 text-rose-800 p-3 text-xs font-mono">
            {errorMsg}
          </div>
        )}

        {successMsg && (
          <div className="bg-emerald-50 border-2 border-emerald-500 text-emerald-800 p-3 text-xs font-mono">
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-mono font-medium uppercase text-charcoal-muted mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full border-2 border-charcoal p-2.5 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-coral"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-mono font-medium uppercase text-charcoal-muted mb-1">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="candidate@privateresume.local"
              className="w-full border-2 border-charcoal p-2.5 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-coral"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-medium uppercase text-charcoal-muted mb-1">
              Password (min. 8 characters)
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full border-2 border-charcoal p-2.5 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-coral"
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-2.5 mt-2"
          >
            {loading
              ? 'Processing...'
              : isRegister
              ? 'Register Account'
              : 'Sign In'}
          </button>
        </form>

        <div className="border-t border-cream-border pt-4 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setErrorMsg('');
              setSuccessMsg('');
            }}
            className="text-xs font-mono text-charcoal hover:underline"
          >
            {isRegister
              ? 'Already registered? Sign in here'
              : "Don't have an account yet? Create one"}
          </button>
        </div>
      </div>
    </div>
  );
}
