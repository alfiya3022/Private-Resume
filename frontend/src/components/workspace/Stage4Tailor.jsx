// Stage4Tailor.jsx
// Component for Stage 4: Tailor Resume UI
// Extracted from WorkspacePage.jsx

import React from "react";
import {
  Sparkles,
  Save,
  Check,
  Edit3,
  Building,
  RefreshCw,
  X,
  Plus,
  ListFilter,
  FileCode,
  Briefcase,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";

export default function Stage4Tailor({
  activeJob,
  activeTailoredResume,
  editableContent,
  targetRoleInput,
  tailorLoading,
  tailorSaving,
  aiModal,
  errorMsg,
  successMsg,
  validationPopup,
  setActiveTailoredResume,
  setEditableContent,
  setTargetRoleInput,
  setAiModal,
  setErrorMsg,
  setSuccessMsg,
  setValidationPopup,
  handleTriggerTailor,
  handleSaveResume,
  handleFinalizeResume,
  openAskAiModal,
  applyAiSuggestion,
  runAskAi,
  loading,
}) {
  return (
    <div className="space-y-6">
      {/* Stage 4: Tailor Resume */}
      {activeJob && (
        <div className="card-brutal space-y-6">
          <div className="border-b border-cream-border pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <div>
              <h2 className="text-xl font-bold tracking-tight text-charcoal">
                Stage 4: Tailor Resume
              </h2>
              <p className="text-sm text-charcoal-muted mt-1">
                Edit sections, request AI assistance, and prepare a tailored version.
              </p>
            </div>
            <button
              type="button"
              onClick={handleTriggerTailor}
              className="btn-primary flex items-center space-x-1"
              disabled={tailorLoading}
            >
              <Sparkles className="w-4 h-4" />
              <span>{tailorLoading ? "Tailoring..." : "Run Tailor"}</span>
            </button>
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

          {/* Editable Sections */}
          <div className="grid grid-cols-1 gap-6">
            {/* Summary Section */}
            <div className="border-2 border-charcoal p-4">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-sm text-charcoal uppercase">Summary</h3>
                <button
                  type="button"
                  className="text-xs text-coral hover:underline"
                  onClick={() =>
                    openAskAiModal({
                      section: "summary",
                      currentText: editableContent?.summary || "",
                    })
                  }
                >
                  <Edit3 className="inline w-3 h-3 mr-1" />
                  Ask AI
                </button>
              </div>
              <textarea
                rows={4}
                className="w-full border-2 border-charcoal p-2 text-xs font-mono mt-2"
                value={editableContent?.summary || ""}
                onChange={(e) =>
                  setEditableContent({
                    ...editableContent,
                    summary: e.target.value,
                  })
                }
              />
            </div>

            {/* Experience Section */}
            {editableContent?.experience?.map((exp, idx) => (
              <div key={idx} className="border-2 border-charcoal p-4">
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-sm text-charcoal uppercase">Experience {idx + 1}</h3>
                  <button
                    type="button"
                    className="text-xs text-coral hover:underline"
                    onClick={() =>
                      openAskAiModal({
                        section: "experience",
                        index: idx,
                        currentText: JSON.stringify(exp, null, 2),
                      })
                    }
                  >
                    <Edit3 className="inline w-3 h-3 mr-1" />
                    Ask AI
                  </button>
                </div>
                {/* Render simple fields */}
                <input
                  type="text"
                  className="w-full border-2 border-charcoal p-1 text-xs mt-1"
                  placeholder="Company"
                  value={exp.company || ""}
                  onChange={(e) => {
                    const newExp = { ...exp, company: e.target.value };
                    const newContent = { ...editableContent };
                    newContent.experience[idx] = newExp;
                    setEditableContent(newContent);
                  }}
                />
                {/* Bullets */}
                {exp.bullets?.map((b, bIdx) => (
                  <div key={bIdx} className="flex items-center mt-1">
                    <textarea
                      rows={2}
                      className="flex-1 border-2 border-charcoal p-1 text-xs"
                      value={b}
                      onChange={(e) => {
                        const newExp = { ...exp };
                        newExp.bullets[bIdx] = e.target.value;
                        const newContent = { ...editableContent };
                        newContent.experience[idx] = newExp;
                        setEditableContent(newContent);
                      }}
                    />
                    <button
                      type="button"
                      className="ml-1 text-coral"
                      onClick={() => {
                        const newExp = { ...exp };
                        newExp.bullets.splice(bIdx, 1);
                        const newContent = { ...editableContent };
                        newContent.experience[idx] = newExp;
                        setEditableContent(newContent);
                      }}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  className="mt-2 flex items-center text-coral"
                  onClick={() => {
                    const newExp = { ...exp };
                    newExp.bullets = [...(exp.bullets || []), ""];
                    const newContent = { ...editableContent };
                    newContent.experience[idx] = newExp;
                    setEditableContent(newContent);
                  }}
                >
                  <Plus className="w-3 h-3 mr-1" /> Add Bullet
                </button>
              </div>
            ))}

            {/* Projects Section */}
            {editableContent?.projects?.map((proj, idx) => (
              <div key={idx} className="border-2 border-charcoal p-4">
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-sm text-charcoal uppercase">Project {idx + 1}</h3>
                  <button
                    type="button"
                    className="text-xs text-coral hover:underline"
                    onClick={() =>
                      openAskAiModal({
                        section: "projects",
                        index: idx,
                        currentText: JSON.stringify(proj, null, 2),
                      })
                    }
                  >
                    <Edit3 className="inline w-3 h-3 mr-1" />
                    Ask AI
                  </button>
                </div>
                <input
                  type="text"
                  className="w-full border-2 border-charcoal p-1 text-xs mt-1"
                  placeholder="Project Title"
                  value={proj.title || ""}
                  onChange={(e) => {
                    const newProj = { ...proj, title: e.target.value };
                    const newContent = { ...editableContent };
                    newContent.projects[idx] = newProj;
                    setEditableContent(newContent);
                  }}
                />
                {proj.bullets?.map((b, bIdx) => (
                  <div key={bIdx} className="flex items-center mt-1">
                    <textarea
                      rows={2}
                      className="flex-1 border-2 border-charcoal p-1 text-xs"
                      value={b}
                      onChange={(e) => {
                        const newProj = { ...proj };
                        newProj.bullets[bIdx] = e.target.value;
                        const newContent = { ...editableContent };
                        newContent.projects[idx] = newProj;
                        setEditableContent(newContent);
                      }}
                    />
                    <button
                      type="button"
                      className="ml-1 text-coral"
                      onClick={() => {
                        const newProj = { ...proj };
                        newProj.bullets.splice(bIdx, 1);
                        const newContent = { ...editableContent };
                        newContent.projects[idx] = newProj;
                        setEditableContent(newContent);
                      }}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  className="mt-2 flex items-center text-coral"
                  onClick={() => {
                    const newProj = { ...proj };
                    newProj.bullets = [...(proj.bullets || []), ""];
                    const newContent = { ...editableContent };
                    newContent.projects[idx] = newProj;
                    setEditableContent(newContent);
                  }}
                >
                  <Plus className="w-3 h-3 mr-1" /> Add Bullet
                </button>
              </div>
            ))}

            {/* Target Role Input */}
            <div className="border-2 border-charcoal p-4">
              <label className="block text-xs font-medium text-charcoal">Target Role / Title</label>
              <input
                type="text"
                className="w-full border-2 border-charcoal p-2 mt-1 text-xs"
                value={targetRoleInput}
                onChange={(e) => setTargetRoleInput(e.target.value)}
                placeholder="e.g., Senior Software Engineer"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 mt-4">
            <button
              type="button"
              className="btn-primary flex items-center"
              onClick={handleSaveResume}
              disabled={tailorSaving}
            >
              <Save className="w-4 h-4 mr-1" />
              {tailorSaving ? "Saving..." : "Save Draft"}
            </button>
            <button
              type="button"
              className="btn-success flex items-center"
              onClick={handleFinalizeResume}
              disabled={tailorSaving}
            >
              <Check className="w-4 h-4 mr-1" />
              Finalize Version
            </button>
          </div>

          {/* AI Modal */}
          {aiModal.isOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded p-6 w-96">
                <h4 className="font-bold mb-2">AI Assistance for {aiModal.section}</h4>
                <textarea
                  rows={6}
                  className="w-full border p-2 mb-2"
                  value={aiModal.suggestedText}
                  onChange={(e) =>
                    setAiModal((prev) => ({ ...prev, suggestedText: e.target.value }))
                  }
                />
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setAiModal((prev) => ({ ...prev, isOpen: false }))}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={applyAiSuggestion}
                    disabled={aiModal.loading}
                  >
                    Apply Suggestion
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
