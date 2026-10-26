import React from "react";
import {
  Briefcase,
  Plus,
  Edit3,
  Trash2,
  Save,
} from "lucide-react";

export default function ExperienceTab({
  experienceMode,
  setExperienceMode,
  githubExpUrl,
  setGithubExpUrl,
  extractingExp,
  handleExtractGitHubExp,
  newExperience,
  setNewExperience,
  handleAddExperience,
  experiences,
  editingExpId,
  setEditingExpId,
  editExpForm,
  setEditExpForm,
  handleStartEditExperience,
  handleSaveEditExperience,
  handleDeleteExperience,
}) {
  return (
    <div className="space-y-3">
      {/* Experience Form */}
      <form
        onSubmit={handleAddExperience}
        className="bg-cream p-3 sm:p-3.5 border border-charcoal space-y-2.5"
      >
        <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
          <Briefcase className="w-3.5 h-3.5 text-coral" />
          <span>Add Work Experience</span>
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Company / Organization *
            </label>
            <input
              type="text"
              value={newExperience.company}
              onChange={(e) =>
                setNewExperience({ ...newExperience, company: e.target.value })
              }
              placeholder="e.g. Acme Corporation"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Job Title / Role *
            </label>
            <input
              type="text"
              value={newExperience.title}
              onChange={(e) =>
                setNewExperience({ ...newExperience, title: e.target.value })
              }
              placeholder="e.g. Staff Infrastructure Engineer"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Location
            </label>
            <input
              type="text"
              value={newExperience.location}
              onChange={(e) =>
                setNewExperience({ ...newExperience, location: e.target.value })
              }
              placeholder="e.g. New York, NY (Hybrid)"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white"
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Start Date
            </label>
            <input
              type="text"
              value={newExperience.start_date}
              onChange={(e) =>
                setNewExperience({ ...newExperience, start_date: e.target.value })
              }
              placeholder="e.g. Jan 2021"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              End Date
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={newExperience.end_date}
                disabled={newExperience.is_current}
                onChange={(e) =>
                  setNewExperience({ ...newExperience, end_date: e.target.value })
                }
                placeholder={newExperience.is_current ? "Present" : "e.g. Present"}
                className={`w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono ${
                  newExperience.is_current ? "opacity-50" : ""
                }`}
              />
              <label className="flex items-center space-x-1 text-[11px] font-mono whitespace-nowrap cursor-pointer">
                <input
                  type="checkbox"
                  checked={newExperience.is_current}
                  onChange={(e) =>
                    setNewExperience({
                      ...newExperience,
                      is_current: e.target.checked,
                    })
                  }
                  className="rounded border-charcoal text-charcoal focus:ring-coral"
                />
                <span>Current</span>
              </label>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
            General Role Description
          </label>
          <textarea
            rows={2}
            value={newExperience.description}
            onChange={(e) =>
              setNewExperience({
                ...newExperience,
                description: e.target.value,
              })
            }
            placeholder="High-level description of scope, team, or responsibilities..."
            className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-sans"
          />
        </div>

        <div>
          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
            Key Accomplishments / Bullets (one per line)
          </label>
          <textarea
            rows={2}
            value={newExperience.bullets}
            onChange={(e) =>
              setNewExperience({ ...newExperience, bullets: e.target.value })
            }
            placeholder="• Designed and deployed multi-region Kubernetes clusters&#10;• Mentored 6 junior engineers on distributed systems best practices"
            className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
          />
        </div>

        <div className="flex justify-end pt-1">
          <button
            type="submit"
            className="btn-primary text-xs py-1.5 px-3.5 flex items-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Experience</span>
          </button>
        </div>
      </form>

      {/* Experience List Container */}
      <div className="space-y-2">
        <h4 className="text-[11px] font-mono uppercase font-bold text-charcoal-muted">
          Recorded Experience Roles ({experiences?.length || 0})
        </h4>

        {experiences?.map((exp) => {
          if (editingExpId === exp.id) {
            return (
              <form
                key={exp.id}
                onSubmit={handleSaveEditExperience}
                className="border border-charcoal bg-white p-3 space-y-2.5"
              >
                <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                  <span className="text-xs font-bold text-charcoal uppercase flex items-center space-x-1">
                    <Edit3 className="w-3.5 h-3.5 text-coral" />
                    <span>
                      Editing: {exp.title} at {exp.company}
                    </span>
                  </span>
                  <button
                    type="button"
                    onClick={() => setEditingExpId(null)}
                    className="text-xs text-charcoal-muted hover:text-charcoal"
                  >
                    Cancel
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Company *
                    </label>
                    <input
                      type="text"
                      value={editExpForm.company}
                      onChange={(e) =>
                        setEditExpForm({
                          ...editExpForm,
                          company: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-medium"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Job Title *
                    </label>
                    <input
                      type="text"
                      value={editExpForm.title}
                      onChange={(e) =>
                        setEditExpForm({
                          ...editExpForm,
                          title: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-medium"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Location
                    </label>
                    <input
                      type="text"
                      value={editExpForm.location}
                      onChange={(e) =>
                        setEditExpForm({
                          ...editExpForm,
                          location: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Start Date
                    </label>
                    <input
                      type="text"
                      value={editExpForm.start_date}
                      onChange={(e) =>
                        setEditExpForm({
                          ...editExpForm,
                          start_date: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      End Date
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={editExpForm.end_date}
                        disabled={editExpForm.is_current}
                        onChange={(e) =>
                          setEditExpForm({
                            ...editExpForm,
                            end_date: e.target.value,
                          })
                        }
                        placeholder={
                          editExpForm.is_current ? "Present" : "End Date"
                        }
                        className={`w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono ${
                          editExpForm.is_current ? "opacity-50" : ""
                        }`}
                      />
                      <label className="flex items-center space-x-1 text-[11px] font-mono whitespace-nowrap cursor-pointer">
                        <input
                          type="checkbox"
                          checked={editExpForm.is_current}
                          onChange={(e) =>
                            setEditExpForm({
                              ...editExpForm,
                              is_current: e.target.checked,
                            })
                          }
                        />
                        <span>Current</span>
                      </label>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Role Description
                  </label>
                  <textarea
                    rows={2}
                    value={editExpForm.description}
                    onChange={(e) =>
                      setEditExpForm({
                        ...editExpForm,
                        description: e.target.value,
                      })
                    }
                    className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-sans"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Accomplishments (one bullet per line)
                  </label>
                  <textarea
                    rows={2}
                    value={editExpForm.bullets}
                    onChange={(e) =>
                      setEditExpForm({
                        ...editExpForm,
                        bullets: e.target.value,
                      })
                    }
                    className="w-full border border-charcoal px-2 py-1 text-xs font-mono bg-white"
                  />
                </div>

                <div className="flex justify-end space-x-2 pt-1 border-t border-cream-border">
                  <button
                    type="button"
                    onClick={() => setEditingExpId(null)}
                    className="btn-secondary text-xs py-1 px-2.5 bg-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary text-xs py-1 px-3 flex items-center space-x-1"
                  >
                    <Save className="w-3 h-3" />
                    <span>Save Changes</span>
                  </button>
                </div>
              </form>
            );
          }

          return (
            <div
              key={exp.id}
              className="border border-charcoal p-3 bg-white flex justify-between items-start gap-3"
            >
              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center space-x-2 flex-wrap">
                  <h5 className="font-bold text-xs sm:text-sm text-charcoal">
                    {exp.title}
                  </h5>
                  <span className="text-[11px] text-charcoal-muted">at</span>
                  <span className="font-semibold text-xs text-charcoal">
                    {exp.company}
                  </span>
                  {exp.location && (
                    <span className="text-[11px] text-charcoal-muted">
                      • {exp.location}
                    </span>
                  )}
                </div>
                <div className="text-[11px] font-mono text-charcoal-muted">
                  {exp.start_date || "Start"} –{" "}
                  {exp.is_current ? "Present" : exp.end_date || "End"}
                </div>
                {exp.description && (
                  <p className="text-xs text-charcoal-muted leading-relaxed pt-0.5">
                    {exp.description}
                  </p>
                )}
                {exp.bullets && exp.bullets.length > 0 && (
                  <ul className="list-disc list-inside text-xs text-charcoal space-y-0.5 pt-0.5">
                    {exp.bullets.map((b, idx) => (
                      <li key={idx} className="leading-relaxed">
                        {b}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="flex items-center space-x-1 shrink-0">
                <button
                  type="button"
                  onClick={() => handleStartEditExperience(exp)}
                  className="p-1 border border-charcoal bg-cream hover:bg-white text-charcoal"
                  title="Edit experience"
                  aria-label={`Edit ${exp.title}`}
                >
                  <Edit3 className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleDeleteExperience(exp.id)}
                  className="p-1 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                  title="Remove experience"
                  aria-label={`Remove ${exp.title}`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
        {(!experiences || experiences.length === 0) && (
          <p className="text-xs text-charcoal-muted">
            No experience records added yet.
          </p>
        )}
      </div>
    </div>
  );
}
