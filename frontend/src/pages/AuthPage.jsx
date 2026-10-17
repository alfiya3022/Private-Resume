import React, { useState } from 'react';
import { Lock, Mail, User, ShieldCheck } from 'lucide-react';

export default function AuthPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
  };

  return (
    <div className="max-w-md mx-auto pt-6">
      <div className="card-brutal space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-charcoal text-white mx-auto flex items-center justify-center font-bold text-xl shadow-brutal-sm">
            <Lock className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-charcoal">
            {isRegister ? 'Create Your Account' : 'Welcome to PrivateResume'}
          </h2>
          <p className="text-xs text-charcoal-muted">
            All candidate resumes and Ollama inference remain strictly local to your machine.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
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
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full border-2 border-charcoal p-2.5 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-coral"
              required
            />
          </div>

          <button type="submit" className="btn-primary w-full py-2.5 mt-2">
            {isRegister ? 'Register Account' : 'Sign In'}
          </button>
        </form>

        <div className="border-t border-cream-border pt-4 text-center">
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
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
