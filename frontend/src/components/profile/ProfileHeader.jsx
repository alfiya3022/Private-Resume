import React from "react";
import { RotateCcw } from "lucide-react";

export default function ProfileHeader({ handleResetAll, savingTab }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-cream-border pb-2.5">
      <h2 className="text-base sm:text-lg font-bold tracking-tight text-charcoal">
        Candidate Profile
      </h2>
      <button
        type="button"
        onClick={handleResetAll}
        disabled={savingTab}
        className="btn-secondary text-xs py-1.5 px-3 flex items-center space-x-1.5 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 transition-colors shadow-sm"
        title="Discard all unsaved edits across all profile tabs"
      >
        <RotateCcw className="w-3.5 h-3.5 text-coral" />
        <span className="font-semibold">Reset All</span>
      </button>
    </div>
  );
}
