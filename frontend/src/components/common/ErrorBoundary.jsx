import React from "react";
import { AlertCircle, RefreshCw, Home } from "lucide-react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Unhandled Application Error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-cream flex items-center justify-center p-6 font-mono">
          <div className="card-brutal max-w-lg w-full bg-white p-6 space-y-4">
            <div className="flex items-center space-x-2 text-rose-600 border-b-2 border-charcoal pb-3">
              <AlertCircle className="w-6 h-6 shrink-0" />
              <h1 className="text-base font-bold text-charcoal">
                Application Encountered an Error
              </h1>
            </div>

            <p className="text-xs text-charcoal-muted leading-relaxed">
              An unexpected error occurred in this view. Your session and
              underlying data have been preserved.
            </p>

            <div className="p-3 bg-rose-50 border border-rose-300 font-mono text-[11px] text-rose-900 break-words max-h-32 overflow-y-auto">
              {this.state.error?.message ||
                "Unknown render exception occurred."}
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              <button
                onClick={() => window.location.reload()}
                className="btn-primary text-xs py-2 px-3 flex items-center space-x-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reload Page</span>
              </button>
              <button
                onClick={() => {
                  this.handleReset();
                  window.location.href = "/";
                }}
                className="btn-secondary text-xs py-2 px-3 flex items-center space-x-1.5"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Return to Workspace</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
