import React from "react";
import { Plus } from "lucide-react";

export default function SkillsTab({
  newSkill,
  setNewSkill,
  handleAddSkill,
  skills,
  handleDeleteSkill,
}) {
  return (
    <div className="space-y-3">
      {/* Add Skill Form - Compact single row on desktop */}
      <form
        onSubmit={handleAddSkill}
        className="bg-cream p-2.5 sm:p-3 border border-charcoal flex flex-col sm:flex-row gap-2.5 items-end"
      >
        <div className="flex-1 w-full">
          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
            Skill Name *
          </label>
          <input
            type="text"
            value={newSkill.name}
            onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
            placeholder="e.g. Python, Docker, PostgreSQL"
            className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
            required
          />
        </div>
        <div className="w-full sm:w-56">
          <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
            Category *
          </label>
          <select
            value={newSkill.category}
            onChange={(e) =>
              setNewSkill({ ...newSkill, category: e.target.value })
            }
            className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white font-sans"
            required
          >
            <option value="" disabled>
              Select Category
            </option>
            <option value="Languages">Languages</option>
            <option value="Frameworks & Libraries">
              Frameworks & Libraries
            </option>
            <option value="Databases">Databases</option>
            <option value="Cloud & Infrastructure">
              Cloud & Infrastructure
            </option>
            <option value="DevOps & Tools">DevOps & Tools</option>
            <option value="Technical Competencies">
              Technical Competencies
            </option>
            <option value="Soft Skills">Soft Skills</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <button
          type="submit"
          className="btn-primary text-xs py-1.5 px-3 flex items-center space-x-1 whitespace-nowrap self-stretch sm:self-auto justify-center"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Skill</span>
        </button>
      </form>

      {/* Verified Skills Container */}
      <div className="border border-charcoal p-3 bg-white space-y-2">
        <h4 className="text-[11px] font-mono uppercase font-bold text-charcoal-muted">
          Verified Candidate Skills ({skills?.length || 0})
        </h4>
        <div className="flex flex-wrap gap-1.5">
          {skills?.map((s) => (
            <span
              key={s.id}
              className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-cream border border-charcoal text-xs font-mono"
            >
              <span className="font-semibold text-charcoal">{s.name}</span>
              <span className="text-charcoal-muted text-[10px]">
                ({s.category || "Skill"})
              </span>
              <button
                type="button"
                onClick={() => handleDeleteSkill(s.id)}
                className="text-rose-600 hover:text-rose-800 ml-1 font-bold leading-none"
                title="Remove skill"
              >
                ×
              </button>
            </span>
          ))}
          {(!skills || skills.length === 0) && (
            <p className="text-xs text-charcoal-muted">
              No skills recorded yet. Add skills using the form above or upload a resume.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
