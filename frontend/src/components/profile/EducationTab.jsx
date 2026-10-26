import React from "react";
import {
  GraduationCap,
  Plus,
  Edit3,
  Trash2,
  Save,
} from "lucide-react";

export default function EducationTab({
  newEducation,
  setNewEducation,
  handleAddEducation,
  educations,
  editingEduId,
  setEditingEduId,
  editEduForm,
  setEditEduForm,
  handleStartEditEducation,
  handleSaveEditEducation,
  handleDeleteEducation,
}) {
  return (
    <div className="space-y-3">
      {/* Education Form */}
      <form
        onSubmit={handleAddEducation}
        className="bg-cream p-3 sm:p-3.5 border border-charcoal space-y-2.5"
      >
        <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
          <GraduationCap className="w-3.5 h-3.5 text-coral" />
          <span>Add Education Record</span>
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Institution *
            </label>
            <input
              type="text"
              value={newEducation.institution}
              onChange={(e) =>
                setNewEducation({ ...newEducation, institution: e.target.value })
              }
              placeholder="e.g. Stanford University"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Degree *
            </label>
            <input
              type="text"
              value={newEducation.degree}
              onChange={(e) =>
                setNewEducation({ ...newEducation, degree: e.target.value })
              }
              placeholder="e.g. Bachelor of Science"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Field of Study
            </label>
            <input
              type="text"
              value={newEducation.field_of_study}
              onChange={(e) =>
                setNewEducation({
                  ...newEducation,
                  field_of_study: e.target.value,
                })
              }
              placeholder="e.g. Computer Science"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Grade / GPA
            </label>
            <input
              type="text"
              value={newEducation.grade}
              onChange={(e) =>
                setNewEducation({ ...newEducation, grade: e.target.value })
              }
              placeholder="e.g. 3.9 / 4.0 or First Class"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
            />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Start Date
            </label>
            <input
              type="text"
              value={newEducation.start_date || ""}
              onChange={(e) =>
                setNewEducation({ ...newEducation, start_date: e.target.value })
              }
              placeholder="e.g. 2018"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              End Date
            </label>
            <input
              type="text"
              value={newEducation.end_date || ""}
              onChange={(e) =>
                setNewEducation({ ...newEducation, end_date: e.target.value })
              }
              placeholder="e.g. 2022"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
            />
          </div>
        </div>
        <div className="flex justify-end pt-1">
          <button
            type="submit"
            className="btn-primary text-xs py-1.5 px-3.5 flex items-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Education</span>
          </button>
        </div>
      </form>

      {/* Educations List Container */}
      <div className="space-y-2">
        <h4 className="text-[11px] font-mono uppercase font-bold text-charcoal-muted">
          Recorded Education ({educations?.length || 0})
        </h4>

        {educations?.map((edu) => (
          <div key={edu.id} className="p-3 border border-charcoal bg-white">
            {editingEduId === edu.id ? (
              <form onSubmit={handleSaveEditEducation} className="space-y-2.5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Institution *
                    </label>
                    <input
                      type="text"
                      value={editEduForm.institution}
                      onChange={(e) =>
                        setEditEduForm({
                          ...editEduForm,
                          institution: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Degree *
                    </label>
                    <input
                      type="text"
                      value={editEduForm.degree}
                      onChange={(e) =>
                        setEditEduForm({
                          ...editEduForm,
                          degree: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white"
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Field of Study
                    </label>
                    <input
                      type="text"
                      value={editEduForm.field_of_study}
                      onChange={(e) =>
                        setEditEduForm({
                          ...editEduForm,
                          field_of_study: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Grade / GPA
                    </label>
                    <input
                      type="text"
                      value={editEduForm.grade}
                      onChange={(e) =>
                        setEditEduForm({
                          ...editEduForm,
                          grade: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-2 pt-1 border-t border-cream-border">
                  <button
                    type="button"
                    onClick={() => setEditingEduId(null)}
                    className="btn-secondary text-xs py-1 px-2.5"
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
            ) : (
              <div className="flex justify-between items-start gap-3">
                <div className="min-w-0">
                  <h5 className="font-bold text-xs sm:text-sm text-charcoal truncate">
                    {edu.degree}
                  </h5>
                  <div className="text-xs text-charcoal-muted mt-0.5 truncate">
                    {edu.institution}{" "}
                    {edu.field_of_study ? `• ${edu.field_of_study}` : ""}
                  </div>
                  {edu.grade && (
                    <span className="text-[11px] font-mono text-emerald-800 font-bold block mt-0.5">
                      Grade: {edu.grade}
                    </span>
                  )}
                  {(edu.start_date || edu.end_date) && (
                    <div className="text-[11px] font-mono text-charcoal-muted mt-0.5">
                      {edu.start_date || "N/A"} - {edu.end_date || "Present"}
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-1 shrink-0">
                  <button
                    type="button"
                    onClick={() => handleStartEditEducation(edu)}
                    className="p-1 border border-charcoal bg-cream hover:bg-white text-charcoal"
                    title="Edit education"
                    aria-label={`Edit ${edu.degree}`}
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDeleteEducation(edu.id)}
                    className="p-1 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                    title="Delete education"
                    aria-label={`Delete ${edu.degree}`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
        {(!educations || educations.length === 0) && (
          <p className="text-xs text-charcoal-muted">
            No education records added yet.
          </p>
        )}
      </div>
    </div>
  );
}
