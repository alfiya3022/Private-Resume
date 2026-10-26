import React from "react";
import { RotateCcw, Save } from "lucide-react";

export default function ProfileTabs({
  sections,
  activeSection,
  setActiveSection,
  hasTabActiveContent,
  handleTabReset,
  handleTabSave,
  savingTab,
}) {
  const currentSectionMeta = sections.find((s) => s.id === activeSection);

  return (
    <div className="space-y-2.5">
      {/* Section Tabs - Compact, Readable, Responsive Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-1.5 border-b border-cream-border pb-2.5">
        {sections.map((sec) => {
          const Icon = sec.icon;
          const isCurrent = activeSection === sec.id;
          const hasContent = hasTabActiveContent(sec.id);
          return (
            <button
              key={sec.id}
              onClick={() => setActiveSection(sec.id)}
              className={`relative px-2.5 py-1.5 sm:py-2 text-xs font-semibold border flex items-center justify-center space-x-1.5 transition-all text-center min-h-[38px] ${
                isCurrent
                  ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
                  : "bg-white text-charcoal border-cream-border hover:border-charcoal hover:bg-cream"
              }`}
            >
              {hasContent && (
                <span
                  aria-hidden="true"
                  className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-amber-500 ring-1 ring-white"
                  title="Form has active content"
                />
              )}
              <Icon className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate">{sec.label}</span>
              {sec.count !== null && sec.count !== undefined && (
                <span className="text-[10px] font-mono opacity-80 shrink-0">
                  ({sec.count})
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Active Tab Controls - Slim Single Row Bar */}
      <div className="flex items-center justify-between gap-2 bg-cream/70 border border-charcoal px-3 py-1.5">
        <div className="flex items-center space-x-2 min-w-0">
          <span className="font-bold text-xs uppercase tracking-wider text-charcoal font-mono truncate">
            {currentSectionMeta?.label} Controls
          </span>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            type="button"
            onClick={() => handleTabReset(activeSection)}
            disabled={savingTab}
            className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1.5 hover:border-charcoal bg-white"
            title={`Clear all editable fields in ${currentSectionMeta?.label}`}
          >
            <RotateCcw className="w-3 h-3 text-charcoal-muted" />
            <span>Reset</span>
          </button>
          <button
            type="button"
            onClick={() => handleTabSave(activeSection)}
            disabled={savingTab}
            className="btn-primary text-xs py-1 px-3 flex items-center space-x-1.5"
            title={`Save changes in ${currentSectionMeta?.label}`}
          >
            {savingTab ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-3 h-3" />
                <span>Save</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
