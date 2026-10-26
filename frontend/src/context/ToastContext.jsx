import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(({ message, type = 'info', duration = 2000, isCritical = false }) => {
    if (!message) return;
    const id = Date.now() + Math.random().toString(36).substring(2, 9);
    
    // Avoid duplicate identical messages stacking
    setToasts((prev) => {
      const isDuplicate = prev.some((t) => t.message === message && t.type === type);
      if (isDuplicate) return prev;
      return [...prev, { id, message, type, isCritical }];
    });

    if (!isCritical && duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }, [removeToast]);

  const showSuccess = useCallback((message, duration = 2000) => {
    addToast({ message, type: 'success', duration });
  }, [addToast]);

  const showError = useCallback((message, isCritical = false, duration = 2500) => {
    addToast({ message, type: 'error', duration: isCritical ? 0 : duration, isCritical });
  }, [addToast]);

  const showWarning = useCallback((message, duration = 2000) => {
    addToast({ message, type: 'warning', duration });
  }, [addToast]);

  const showInfo = useCallback((message, duration = 2000) => {
    addToast({ message, type: 'info', duration });
  }, [addToast]);

  return (
    <ToastContext.Provider value={{ addToast, showSuccess, showError, showWarning, showInfo, removeToast }}>
      {children}
      <div 
        className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        aria-live="polite"
      >
        {toasts.map((toast) => {
          const typeStyles = {
            success: 'bg-emerald-50 border-emerald-600 text-emerald-950',
            error: 'bg-rose-50 border-rose-600 text-rose-950',
            warning: 'bg-amber-50 border-amber-600 text-amber-950',
            info: 'bg-white border-charcoal text-charcoal',
          }[toast.type] || 'bg-white border-charcoal text-charcoal';

          const Icon = {
            success: CheckCircle2,
            error: AlertCircle,
            warning: AlertTriangle,
            info: Info,
          }[toast.type] || Info;

          const iconColor = {
            success: 'text-emerald-700',
            error: 'text-rose-700',
            warning: 'text-amber-700',
            info: 'text-charcoal',
          }[toast.type] || 'text-charcoal';

          return (
            <div
              key={toast.id}
              role={toast.type === 'error' ? 'alert' : 'status'}
              className={`border-2 shadow-brutal p-3 pointer-events-auto flex items-start justify-between gap-2.5 text-xs font-mono transition-all duration-150 animate-in fade-in slide-in-from-top-2 ${typeStyles}`}
            >
              <div className="flex items-start space-x-2 min-w-0">
                <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${iconColor}`} />
                <span className="leading-snug break-words">{toast.message}</span>
              </div>
              <button
                type="button"
                onClick={() => removeToast(toast.id)}
                className="shrink-0 p-0.5 hover:opacity-70 text-charcoal transition-opacity"
                aria-label="Close notification"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    // Graceful fallback if invoked outside provider
    return {
      addToast: () => {},
      showSuccess: (msg) => console.log('[Success]', msg),
      showError: (msg) => console.error('[Error]', msg),
      showWarning: (msg) => console.warn('[Warning]', msg),
      showInfo: (msg) => console.info('[Info]', msg),
      removeToast: () => {},
    };
  }
  return context;
}
