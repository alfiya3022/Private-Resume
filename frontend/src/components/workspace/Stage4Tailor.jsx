// Stage 4: Tailor Resume (section editing + Ask AI consultation modal).
// All shared state and handlers live in WorkspacePage; this component renders the UI only.

import React from "react";
import {
  Sparkles,
  ArrowRight,
  Briefcase,
  Building,
  CheckCircle2,
  Check,
  X,
  Layers,
  Code2,
  Save,
  Lock,
  Plus,
  Trash2,
  GraduationCap,
  Award,
  AlertTriangle,
} from "lucide-react";

export default function Stage4Tailor({
  activeJob,
  tailoredResumes,
  activeTailoredResume,
  editableContent,
  setEditableContent,
  targetRoleInput,
  setTargetRoleInput,
  newCategoryName,
  setNewCategoryName,
  newSkillInputs,
  setNewSkillInputs,
  tailorLoading,
  tailorSaving,
  draftSaved,
  pdfArtifact,
  aiModal,
  setAiModal,
  handleTriggerTailor,
  handleSaveResume,
  handleFinalizeResume,
  handleSelectVersion,
  handleGeneratePdf,
  openAskAiModal,
  runAskAi,
  applyAiSuggestion,
  setCurrentStep,
}) {
  return (
    <>
      <div className="space-y-6">
        {!activeTailoredResume ? (
          <div className="card-brutal text-center py-12 space-y-4 font-mono">
            <div className="w-12 h-12 rounded-full border-2 border-charcoal bg-amber-50 flex items-center justify-center mx-auto text-amber-900">
              <Sparkles className="w-6 h-6 text-coral" />
            </div>
            <h2 className="text-base font-bold uppercase tracking-wider text-charcoal">
              Stage 4: Tailored Resume Generation
            </h2>
            <p className="text-xs text-charcoal-muted max-w-lg mx-auto">
              Generate an evidence-grounded resume draft aligned with{" "}
              <strong>{activeJob?.title}</strong> at{" "}
              <strong>{activeJob?.company}</strong>.
            </p>
            <div className="pt-2">
              <button
                onClick={handleTriggerTailor}
                disabled={tailorLoading}
                className="btn-primary inline-flex items-center space-x-2 text-xs"
              >
                {tailorLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                    <span>Generating Evidence-Based Draft...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate Tailored Resume (Draft v1)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6 font-mono">
            {/* Version & Control Bar */}
            <div className="card-brutal bg-white p-3 sm:p-4 flex flex-wrap items-center justify-between gap-3 border-2 border-charcoal shadow-brutal-sm">
              <div className="flex items-center space-x-2.5">
                <span className="text-xs font-bold uppercase text-charcoal tracking-wider">
                  Version:
                </span>
                <select
                  value={activeTailoredResume.id}
                  onChange={(e) => handleSelectVersion(e.target.value)}
                  className="input-brutal py-1 px-2 text-xs font-bold"
                >
                  {tailoredResumes.map((v) => (
                    <option key={v.id} value={v.id}>
                      v{v.version_number} ({v.status.toUpperCase()}) -{" "}
                      {new Date(v.created_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
                <span
                  className={`badge-tag ${
                    activeTailoredResume.status === "final"
                      ? "bg-emerald-50 text-emerald-900 border-emerald-600"
                      : draftSaved
                      ? "bg-emerald-50 text-emerald-900 border-emerald-600"
                      : "bg-amber-50 text-amber-900 border-amber-600"
                  }`}
                >
                  {activeTailoredResume.status === "final"
                    ? "FINAL (LOCKED)"
                    : draftSaved
                    ? "SAVED"
                    : "DRAFT"}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {activeTailoredResume.status !== "final" && (
                  <button
                    onClick={() => handleSaveResume(false)}
                    disabled={tailorSaving || draftSaved}
                    className={`btn-secondary text-xs flex items-center space-x-1.5 py-1 px-3 ${
                      draftSaved ? "opacity-60 cursor-not-allowed bg-cream" : ""
                    }`}
                    title={draftSaved ? "All draft changes saved" : "Save working draft in-place"}
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{draftSaved ? "Draft Saved" : "Save Working Draft"}</span>
                  </button>
                )}

                {activeTailoredResume.status !== "final" && (
                  <button
                    onClick={handleFinalizeResume}
                    disabled={tailorSaving}
                    className="btn-secondary text-xs flex items-center space-x-1.5 py-1 px-3 border-emerald-600 text-emerald-900 bg-emerald-50 hover:bg-emerald-100"
                  >
                    <Lock className="w-3.5 h-3.5 text-emerald-700" />
                    <span>Lock as Final</span>
                  </button>
                )}

                <button
                  onClick={() => handleSaveResume(true)}
                  disabled={tailorSaving}
                  className="btn-primary text-xs flex items-center space-x-1.5 py-1 px-3"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>
                    Save as New Version (v{activeTailoredResume.version_number + 1})
                  </span>
                </button>
              </div>
            </div>

            {/* Resume Content Sections (Redundant Status Banner & Resume Heading Box Removed) */}
            {editableContent && (
              <div className="space-y-4">
                {/* 1. Target Role & Professional Summary */}
                <div className="card-brutal bg-white p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <Briefcase className="w-4 h-4 text-coral shrink-0" />
                      <input
                        type="text"
                        value={
                          editableContent.section_titles?.summary ??
                          "Target Role & Professional Summary"
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            section_titles: {
                              ...(editableContent.section_titles || {}),
                              summary: e.target.value,
                            },
                          })
                        }
                        className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                        title="Click to edit section title"
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() =>
                          openAskAiModal({
                            section: "summary",
                            fieldKey: "summary",
                            currentText: editableContent.summary,
                          })
                        }
                        className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1 text-coral border-coral hover:bg-coral hover:text-white"
                      >
                        <Sparkles className="w-3 h-3" />
                        <span>Ask AI to Polish Summary</span>
                      </button>
                      <button
                        onClick={() => handleSaveResume(false)}
                        className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save Summary</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-[11px] font-bold text-charcoal-muted uppercase mb-1">
                        Resume Headline / Target Role
                      </label>
                      <input
                        type="text"
                        value={targetRoleInput}
                        onChange={(e) => setTargetRoleInput(e.target.value)}
                        className="input-brutal w-full text-xs font-bold"
                        placeholder="e.g. Lead FastAPI Backend Engineer"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-charcoal-muted uppercase mb-1">
                        Executive Professional Summary (Strictly Tailored to
                        Target JD)
                      </label>
                      <textarea
                        rows={3}
                        value={editableContent.summary || ""}
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            summary: e.target.value,
                          })
                        }
                        className="input-brutal w-full text-xs leading-relaxed"
                        placeholder="Enter summary..."
                      />
                    </div>
                  </div>
                </div>

                {/* 2. Education */}
                <div className="card-brutal bg-white p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <GraduationCap className="w-4 h-4 text-coral shrink-0" />
                      <input
                        type="text"
                        value={
                          editableContent.section_titles?.education ??
                          "Education"
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            section_titles: {
                              ...(editableContent.section_titles || {}),
                              education: e.target.value,
                            },
                          })
                        }
                        className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                        title="Click to edit section title"
                      />
                    </div>
                    <div className="flex items-center space-x-1">
                      <button
                        type="button"
                        onClick={() => {
                          const updated = { ...editableContent };
                          if (!updated.education) updated.education = [];
                          updated.education.push({
                            degree: "B.Tech in Computer Science",
                            institution: "University Name",
                            year: "2020 -- 2024",
                            gpa: "8.11",
                          });
                          setEditableContent(updated);
                        }}
                        className="btn-secondary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Add</span>
                      </button>
                      <button
                        onClick={() => handleSaveResume(false)}
                        className="btn-primary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {editableContent.education?.map((edu, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 border border-cream-border text-xs space-y-1.5 bg-cream-bg/20"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <input
                            type="text"
                            value={edu.degree || ""}
                            onChange={(e) => {
                              const updated = { ...editableContent };
                              updated.education[idx].degree = e.target.value;
                              setEditableContent(updated);
                            }}
                            placeholder="Degree / Major (e.g. B.Tech in Computer Science & Engineering)"
                            className="input-brutal text-xs font-bold py-0.5 px-1.5 flex-1"
                          />
                          <button
                            type="button"
                            onClick={() => {
                              const updated = { ...editableContent };
                              updated.education = updated.education.filter(
                                (_, i) => i !== idx,
                              );
                              setEditableContent(updated);
                            }}
                            className="text-rose-600 hover:text-rose-800 p-0.5"
                            title="Delete Education"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                          <input
                            type="text"
                            value={edu.institution || ""}
                            onChange={(e) => {
                              const updated = { ...editableContent };
                              updated.education[idx].institution =
                                e.target.value;
                              setEditableContent(updated);
                            }}
                            placeholder="Institution"
                            className="input-brutal text-[11px] py-0.5 px-1.5"
                          />
                          <input
                            type="text"
                            value={edu.year || ""}
                            onChange={(e) => {
                              const updated = { ...editableContent };
                              updated.education[idx].year = e.target.value;
                              setEditableContent(updated);
                            }}
                            placeholder="Year / Duration (e.g. 2020 -- 2024)"
                            className="input-brutal text-[11px] py-0.5 px-1.5"
                          />
                          <input
                            type="text"
                            value={edu.gpa || edu.cgpa || ""}
                            onChange={(e) => {
                              const updated = { ...editableContent };
                              updated.education[idx].gpa = e.target.value;
                              setEditableContent(updated);
                            }}
                            placeholder="CGPA / GPA (e.g. 8.11 / 10)"
                            className="input-brutal text-[11px] py-0.5 px-1.5"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 3. Core Technical Skills */}
                <div className="card-brutal bg-white p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <Code2 className="w-4 h-4 text-coral shrink-0" />
                      <input
                        type="text"
                        value={
                          editableContent.section_titles?.skills ??
                          "Technical Competencies (Evidence-Grounded)"
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            section_titles: {
                              ...(editableContent.section_titles || {}),
                              skills: e.target.value,
                            },
                          })
                        }
                        className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                        title="Click to edit section title"
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleSaveResume(false)}
                        className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save Skills</span>
                      </button>
                    </div>
                  </div>

                  {/* Add new skill category */}
                  <div className="flex items-center space-x-2 p-2 bg-cream-bg/40 border border-cream-border">
                    <input
                      type="text"
                      placeholder="New Skill Category (e.g. Cloud & DevOps)"
                      value={newCategoryName}
                      onChange={(e) => setNewCategoryName(e.target.value)}
                      className="input-brutal text-xs py-1 px-2 flex-1"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        if (!newCategoryName.trim()) return;
                        const updated = { ...editableContent };
                        if (!updated.skills) updated.skills = {};
                        if (!updated.skills[newCategoryName.trim()]) {
                          updated.skills[newCategoryName.trim()] = [];
                        }
                        setEditableContent(updated);
                        setNewCategoryName("");
                      }}
                      className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                    >
                      <Plus className="w-3 h-3" />
                      <span>Add Category</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(editableContent.skills || {}).map(
                      ([category, skillsList]) => (
                        <div
                          key={category}
                          className="border border-cream-border p-3 space-y-2 bg-cream-bg/40"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-charcoal uppercase tracking-wider block">
                              {category} ({skillsList.length})
                            </span>
                            <div className="flex items-center space-x-1">
                              <button
                                type="button"
                                onClick={() =>
                                  openAskAiModal({
                                    section: "skills",
                                    fieldKey: category,
                                    currentText: skillsList.join(", "),
                                  })
                                }
                                className="btn-secondary text-[10px] py-0.5 px-1.5 flex items-center space-x-1 text-coral border-coral hover:bg-coral hover:text-white"
                                title="Consult AI to refine this skill group"
                              >
                                <Sparkles className="w-3 h-3" />
                                <span>AI</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  const updated = { ...editableContent };
                                  delete updated.skills[category];
                                  setEditableContent(updated);
                                }}
                                className="text-rose-600 hover:text-rose-800 text-xs p-1"
                                title="Delete category"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="flex flex-wrap gap-1.5">
                            {skillsList.map((skill, sIdx) => (
                              <span
                                key={sIdx}
                                className="badge-tag bg-white text-charcoal border-charcoal flex items-center space-x-1"
                              >
                                <span>{skill}</span>
                                <button
                                  type="button"
                                  onClick={() => {
                                    const updated = { ...editableContent };
                                    updated.skills[category] = updated.skills[
                                      category
                                    ].filter((_, idx) => idx !== sIdx);
                                    setEditableContent(updated);
                                  }}
                                  className="hover:text-rose-600 ml-1 text-xs font-bold"
                                  title="Remove skill"
                                >
                                  ×
                                </button>
                              </span>
                            ))}
                          </div>

                          {/* Add skill to category */}
                          <div className="flex items-center space-x-1 pt-1 border-t border-cream-border/60">
                            <input
                              type="text"
                              placeholder="Add skill..."
                              value={newSkillInputs[category] || ""}
                              onChange={(e) =>
                                setNewSkillInputs({
                                  ...newSkillInputs,
                                  [category]: e.target.value,
                                })
                              }
                              onKeyDown={(e) => {
                                if (e.key === "Enter") {
                                  e.preventDefault();
                                  const val = (
                                    newSkillInputs[category] || ""
                                  ).trim();
                                  if (!val) return;
                                  const updated = { ...editableContent };
                                  if (
                                    !updated.skills[category].includes(val)
                                  ) {
                                    updated.skills[category] = [
                                      ...updated.skills[category],
                                      val,
                                    ];
                                  }
                                  setEditableContent(updated);
                                  setNewSkillInputs({
                                    ...newSkillInputs,
                                    [category]: "",
                                  });
                                }
                              }}
                              className="input-brutal text-[11px] py-0.5 px-1.5 flex-1"
                            />
                            <button
                              type="button"
                              onClick={() => {
                                const val = (
                                  newSkillInputs[category] || ""
                                ).trim();
                                if (!val) return;
                                const updated = { ...editableContent };
                                if (!updated.skills[category].includes(val)) {
                                  updated.skills[category] = [
                                    ...updated.skills[category],
                                    val,
                                  ];
                                }
                                setEditableContent(updated);
                                setNewSkillInputs({
                                  ...newSkillInputs,
                                  [category]: "",
                                });
                              }}
                              className="btn-secondary text-[11px] py-0.5 px-2"
                            >
                              + Add
                            </button>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                </div>

                {/* 4. Work Experience */}
                <div className="card-brutal bg-white p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <Building className="w-4 h-4 text-coral shrink-0" />
                      <input
                        type="text"
                        value={
                          editableContent.section_titles?.experience ??
                          `Work Experience (${editableContent.experience?.length || 0})`
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            section_titles: {
                              ...(editableContent.section_titles || {}),
                              experience: e.target.value,
                            },
                          })
                        }
                        className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                        title="Click to edit section title"
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={() => {
                          const updated = { ...editableContent };
                          if (!updated.experience) updated.experience = [];
                          updated.experience.push({
                            title: "Software Engineer",
                            company: "Company Name",
                            location: "Remote",
                            start_date: "2023-01",
                            end_date: "Present",
                            bullets: [
                              "Key contribution and engineering achievement aligned with target role.",
                            ],
                          });
                          setEditableContent(updated);
                        }}
                        className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Add Role</span>
                      </button>
                      <button
                        onClick={() => handleSaveResume(false)}
                        className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save Experience</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {editableContent.experience?.map((exp, expIdx) => (
                      <div
                        key={expIdx}
                        className="border-2 border-charcoal p-4 space-y-3 bg-cream-bg/20"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-2 border-b border-cream-border pb-2">
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Job Title
                            </label>
                            <input
                              type="text"
                              value={exp.title || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.experience[expIdx].title =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              className="input-brutal w-full text-xs font-bold py-1 px-2"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Company
                            </label>
                            <input
                              type="text"
                              value={exp.company || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.experience[expIdx].company =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              className="input-brutal w-full text-xs font-bold py-1 px-2"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Location
                            </label>
                            <input
                              type="text"
                              value={exp.location || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.experience[expIdx].location =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              className="input-brutal w-full text-xs py-1 px-2"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Start Date
                            </label>
                            <input
                              type="text"
                              value={exp.start_date || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.experience[expIdx].start_date =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              className="input-brutal w-full text-xs py-1 px-2"
                              placeholder="e.g. 2022-01"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              End Date
                            </label>
                            <input
                              type="text"
                              value={exp.end_date || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.experience[expIdx].end_date =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              className="input-brutal w-full text-xs py-1 px-2"
                              placeholder="e.g. Present"
                            />
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-charcoal-muted uppercase">
                            Accomplishment Bullets
                          </span>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() =>
                                openAskAiModal({
                                  section: "experience",
                                  fieldKey: "bullets",
                                  index: expIdx,
                                  currentText: (exp.bullets || []).join("\n"),
                                })
                              }
                              className="btn-secondary text-[11px] py-0.5 px-2 text-coral border-coral hover:bg-coral hover:text-white flex items-center space-x-1"
                            >
                              <Sparkles className="w-3 h-3" />
                              <span>Ask AI on Role</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                const updated = { ...editableContent };
                                updated.experience =
                                  updated.experience.filter(
                                    (_, idx) => idx !== expIdx,
                                  );
                                setEditableContent(updated);
                              }}
                              className="text-rose-600 hover:text-rose-800 text-xs p-1"
                              title="Delete Role"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          {exp.bullets?.map((bullet, bIdx) => (
                            <div
                              key={bIdx}
                              className="flex items-start space-x-2"
                            >
                              <span className="text-charcoal-muted text-xs mt-1.5">
                                •
                              </span>
                              <textarea
                                rows={2}
                                value={bullet}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.experience[expIdx].bullets[bIdx] =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal flex-1 text-xs leading-relaxed"
                              />
                              <div className="flex flex-col space-y-1">
                                <button
                                  onClick={() =>
                                    openAskAiModal({
                                      section: "experience",
                                      fieldKey: "bullet",
                                      index: expIdx,
                                      bulletIndex: bIdx,
                                      currentText: bullet,
                                    })
                                  }
                                  className="p-1 border border-charcoal hover:bg-cream-bg text-coral"
                                  title="Ask AI to refine this bullet"
                                >
                                  <Sparkles className="w-3 h-3" />
                                </button>
                                <button
                                  onClick={() => {
                                    const updated = { ...editableContent };
                                    updated.experience[expIdx].bullets =
                                      updated.experience[
                                        expIdx
                                      ].bullets.filter(
                                        (_, idx) => idx !== bIdx,
                                      );
                                    setEditableContent(updated);
                                  }}
                                  className="p-1 border border-charcoal hover:bg-rose-50 text-rose-700"
                                  title="Remove bullet"
                                >
                                  <Trash2 className="w-3 h-3" />
                                </button>
                              </div>
                            </div>
                          ))}

                          <button
                            type="button"
                            onClick={() => {
                              const updated = { ...editableContent };
                              updated.experience[expIdx].bullets = [
                                ...(updated.experience[expIdx].bullets || []),
                                "Contributed to core deliverables and team execution.",
                              ];
                              setEditableContent(updated);
                            }}
                            className="btn-secondary text-[11px] py-1 px-2.5 flex items-center space-x-1 mt-2"
                          >
                            <Plus className="w-3 h-3" />
                            <span>Add Bullet Point</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 5. Key Projects & Deliverables */}
                <div className="card-brutal bg-white p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <Layers className="w-4 h-4 text-coral shrink-0" />
                      <input
                        type="text"
                        value={
                          editableContent.section_titles?.projects ??
                          `Key Projects (${editableContent.projects?.length || 0})`
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            section_titles: {
                              ...(editableContent.section_titles || {}),
                              projects: e.target.value,
                            },
                          })
                        }
                        className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                        title="Click to edit section title"
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={() => {
                          const updated = { ...editableContent };
                          if (!updated.projects) updated.projects = [];
                          updated.projects.push({
                            name: "New Project",
                            technologies: ["Python", "FastAPI"],
                            start_date: "2025",
                            end_date: "Present",
                            is_current: true,
                            github_url: "",
                            live_url: "",
                            link: "",
                            bullets: [
                              "Built scalable service handling real-time data.",
                            ],
                          });
                          setEditableContent(updated);
                        }}
                        className="btn-secondary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Add Project</span>
                      </button>
                      <button
                        onClick={() => handleSaveResume(false)}
                        className="btn-primary text-xs py-1 px-2.5 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save Projects</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {editableContent.projects?.map((proj, pIdx) => (
                      <div
                        key={pIdx}
                        className="border-2 border-charcoal p-4 space-y-3 bg-cream-bg/20"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 border-b border-cream-border pb-3">
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Project Title
                            </label>
                            <input
                              type="text"
                              value={proj.name || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.projects[pIdx].name = e.target.value;
                                setEditableContent(updated);
                              }}
                              className="input-brutal w-full text-xs font-bold py-1 px-2"
                              placeholder="e.g. AI-Powered Resume Application"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Tech Stack (comma separated)
                            </label>
                            <input
                              type="text"
                              value={(proj.technologies || []).join(", ")}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.projects[pIdx].technologies =
                                  e.target.value
                                    .split(",")
                                    .map((t) => t.trim())
                                    .filter(Boolean);
                                setEditableContent(updated);
                              }}
                              placeholder="React, FastAPI, PostgreSQL"
                              className="input-brutal w-full text-xs py-1 px-2"
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                GitHub / Repository URL
                              </label>
                              <input
                                type="text"
                                value={proj.github_url || proj.link || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].github_url = e.target.value;
                                  updated.projects[pIdx].link = e.target.value;
                                  setEditableContent(updated);
                                }}
                                placeholder="https://github.com/..."
                                className="input-brutal w-full text-xs py-1 px-2"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Live Website URL
                              </label>
                              <input
                                type="text"
                                value={proj.live_url || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].live_url = e.target.value;
                                  setEditableContent(updated);
                                }}
                                placeholder="https://myproject.com"
                                className="input-brutal w-full text-xs py-1 px-2"
                              />
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                Start Date / Year
                              </label>
                              <input
                                type="text"
                                value={proj.start_date || ""}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].start_date = e.target.value;
                                  setEditableContent(updated);
                                }}
                                placeholder="e.g. 2025"
                                className="input-brutal w-full text-xs py-1 px-2"
                              />
                            </div>
                            <div>
                              <div className="flex items-center justify-between">
                                <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                                  End Date / Year
                                </label>
                                <label className="flex items-center space-x-1 cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={proj.is_current || proj.end_date === "Present"}
                                    onChange={(e) => {
                                      const updated = { ...editableContent };
                                      if (e.target.checked) {
                                        updated.projects[pIdx].is_current = true;
                                        updated.projects[pIdx].end_date = "Present";
                                      } else {
                                        updated.projects[pIdx].is_current = false;
                                        if (updated.projects[pIdx].end_date === "Present") {
                                          updated.projects[pIdx].end_date = "";
                                        }
                                      }
                                      setEditableContent(updated);
                                    }}
                                    className="h-3 w-3 accent-coral"
                                  />
                                  <span className="text-[10px] font-bold text-charcoal">Ongoing</span>
                                </label>
                              </div>
                              <input
                                type="text"
                                value={proj.end_date || ""}
                                disabled={proj.is_current && proj.end_date === "Present"}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].end_date = e.target.value;
                                  if (e.target.value.toLowerCase() === "present") {
                                    updated.projects[pIdx].is_current = true;
                                  }
                                  setEditableContent(updated);
                                }}
                                placeholder="e.g. 2026 or Present"
                                className="input-brutal w-full text-xs py-1 px-2 disabled:bg-cream-bg disabled:text-charcoal-muted"
                              />
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-charcoal-muted uppercase">
                            Accomplishment Bullets
                          </span>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() =>
                                openAskAiModal({
                                  section: "projects",
                                  fieldKey: "bullets",
                                  index: pIdx,
                                  currentText: (proj.bullets || []).join(
                                    "\n",
                                  ),
                                })
                              }
                              className="btn-secondary text-[11px] py-0.5 px-2 text-coral border-coral hover:bg-coral hover:text-white flex items-center space-x-1"
                            >
                              <Sparkles className="w-3 h-3" />
                              <span>Ask AI on Project</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                const updated = { ...editableContent };
                                updated.projects = updated.projects.filter(
                                  (_, idx) => idx !== pIdx,
                                );
                                setEditableContent(updated);
                              }}
                              className="text-rose-600 hover:text-rose-800 text-xs p-1"
                              title="Delete Project"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          {proj.bullets?.map((bullet, bIdx) => (
                            <div
                              key={bIdx}
                              className="flex items-start space-x-2"
                            >
                              <span className="text-charcoal-muted text-xs mt-1.5">
                                •
                              </span>
                              <textarea
                                rows={2}
                                value={bullet}
                                onChange={(e) => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].bullets[bIdx] =
                                    e.target.value;
                                  setEditableContent(updated);
                                }}
                                className="input-brutal flex-1 text-xs leading-relaxed"
                              />
                              <button
                                onClick={() => {
                                  const updated = { ...editableContent };
                                  updated.projects[pIdx].bullets =
                                    updated.projects[pIdx].bullets.filter(
                                      (_, idx) => idx !== bIdx,
                                    );
                                  setEditableContent(updated);
                                }}
                                className="p-1 border border-charcoal hover:bg-rose-50 text-rose-700"
                                title="Remove bullet"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          ))}

                          <button
                            type="button"
                            onClick={() => {
                              const updated = { ...editableContent };
                              updated.projects[pIdx].bullets = [
                                ...(updated.projects[pIdx].bullets || []),
                                "Engineered core features and optimized system performance.",
                              ];
                              setEditableContent(updated);
                            }}
                            className="btn-secondary text-[11px] py-1 px-2.5 flex items-center space-x-1 mt-2"
                          >
                            <Plus className="w-3 h-3" />
                            <span>Add Bullet Point</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 6. Certifications & Achievements */}
                <div className="card-brutal bg-white p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cream-border pb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <Award className="w-4 h-4 text-coral shrink-0" />
                      <input
                        type="text"
                        value={
                          editableContent.section_titles?.certifications ??
                          "Certifications & Achievements"
                        }
                        onChange={(e) =>
                          setEditableContent({
                            ...editableContent,
                            section_titles: {
                              ...(editableContent.section_titles || {}),
                              certifications: e.target.value,
                            },
                          })
                        }
                        className="font-bold text-xs uppercase tracking-wider text-charcoal bg-transparent border-b border-transparent hover:border-charcoal focus:border-charcoal focus:outline-hidden"
                        title="Click to edit section title"
                      />
                    </div>
                    <div className="flex items-center space-x-1">
                      <button
                        type="button"
                        onClick={() => {
                          const updated = { ...editableContent };
                          if (!updated.certifications)
                            updated.certifications = [];
                          updated.certifications.push({
                            name: "AWS Certified Solutions Architect",
                            issuer: "Amazon Web Services",
                            certificate_url: "",
                          });
                          setEditableContent(updated);
                        }}
                        className="btn-secondary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Add</span>
                      </button>
                      <button
                        onClick={() => handleSaveResume(false)}
                        className="btn-primary text-[10px] py-0.5 px-2 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {editableContent.certifications?.map((cert, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 border border-cream-border text-xs space-y-1.5 bg-cream-bg/20"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <input
                            type="text"
                            value={cert.name || ""}
                            onChange={(e) => {
                              const updated = { ...editableContent };
                              updated.certifications[idx].name =
                                e.target.value;
                              setEditableContent(updated);
                            }}
                            placeholder="Certification or Achievement Name"
                            className="input-brutal text-xs font-bold py-0.5 px-1.5 flex-1 mr-2"
                          />
                          <button
                            type="button"
                            onClick={() => {
                              const updated = { ...editableContent };
                              updated.certifications =
                                updated.certifications.filter(
                                  (_, i) => i !== idx,
                                );
                              setEditableContent(updated);
                            }}
                            className="text-rose-600 hover:text-rose-800 p-0.5"
                            title="Delete Certification"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Issuer / Organization
                            </label>
                            <input
                              type="text"
                              value={cert.issuer || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.certifications[idx].issuer =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="Issuer / Organization (e.g. AWS, Udemy, VCET)"
                              className="input-brutal text-[11px] py-0.5 px-1.5 w-full"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-charcoal-muted uppercase">
                              Certificate URL
                            </label>
                            <input
                              type="text"
                              value={cert.certificate_url || cert.credential_url || cert.link || ""}
                              onChange={(e) => {
                                const updated = { ...editableContent };
                                updated.certifications[idx].certificate_url =
                                  e.target.value;
                                setEditableContent(updated);
                              }}
                              placeholder="https://example.com/my-certificate"
                              className="input-brutal text-[11px] py-0.5 px-1.5 w-full"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Navigation CTAs */}
            <div className="flex justify-between items-center pt-3 border-t border-cream-border">
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="btn-secondary text-xs"
              >
                ← Back to Match Evidence
              </button>

              <div className="flex items-center space-x-2">
                {activeTailoredResume.status !== "final" && (
                  <button
                    type="button"
                    onClick={handleFinalizeResume}
                    disabled={tailorSaving}
                    className="btn-secondary text-xs flex items-center space-x-1.5 py-1 px-3 border-emerald-600 text-emerald-900 bg-emerald-50 hover:bg-emerald-100"
                    title="Lock this version as final and immutable"
                  >
                    <Lock className="w-3.5 h-3.5 text-emerald-700" />
                    <span>Lock as Final</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => {
                    setCurrentStep(5);
                    if (!pdfArtifact && activeTailoredResume) {
                      handleGeneratePdf();
                    }
                  }}
                  className="btn-primary flex items-center space-x-1.5 text-xs"
                >
                  <span>Next: Proceed to PDF</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Ask AI Consultation Modal */}
      {aiModal.isOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-2.5 sm:p-4">
          <div className="card-brutal bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-4 p-4 sm:p-6 border-2 border-charcoal shadow-brutal font-mono animate-in fade-in duration-150">
            <div className="flex items-center justify-between border-b-2 border-charcoal pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-coral" />
                <h3 className="font-bold text-sm uppercase tracking-wider text-charcoal">
                  Consult AI: Refine {aiModal.section.toUpperCase()}
                </h3>
              </div>
              <button
                onClick={() =>
                  setAiModal((prev) => ({ ...prev, isOpen: false }))
                }
                className="p-1 hover:bg-cream-bg border border-charcoal"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-300 text-[11px] text-amber-950">
              <strong>Anti-Fabrication Rule:</strong> AI refinement will polish
              phrasing and emphasize genuine qualifications, but will never
              invent unbacked skills or technologies.
            </div>

            {/* Current Text */}
            <div className="space-y-1">
              <label className="text-[11px] font-bold text-charcoal-muted uppercase">
                Current Content
              </label>
              <div className="p-2.5 bg-cream-bg border border-charcoal text-xs text-charcoal whitespace-pre-line max-h-32 overflow-y-auto">
                {aiModal.currentText || "(Empty)"}
              </div>
            </div>

            {/* Custom Instruction Input (Primary & Prominent) */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold text-charcoal uppercase">
                  Your Instruction / Prompt
                </label>
                <span className="text-[10px] text-charcoal-muted">
                  The model faithfully follows this request
                </span>
              </div>
              <textarea
                rows={3}
                value={aiModal.instruction}
                onChange={(e) =>
                  setAiModal((prev) => ({ ...prev, instruction: e.target.value }))
                }
                placeholder="Tell AI what to do:&#10;• Make this more concise and impactful&#10;• Rewrite in a professional active tone&#10;• Convert into 3 bullet points focusing on system scalability&#10;• Explain in simpler language without jargon&#10;• Give constructive feedback on this section"
                className="input-brutal w-full text-xs font-mono p-2.5 leading-relaxed"
              />
            </div>

            {/* Quick Prompt Suggestions (Optional Shortcuts) */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold text-charcoal-muted uppercase">
                  Suggested Prompt Shortcuts
                </label>
                <span className="text-[10px] text-charcoal-muted">
                  Click to populate prompt
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {[
                  "Make this more concise",
                  "Rewrite in a professional, active tone",
                  "Convert into bullet points",
                  "Emphasize measurable outcomes and technical metrics",
                  "Explain in simpler language",
                  "Give constructive feedback on this section",
                ].map((promptText, pIdx) => (
                  <button
                    key={pIdx}
                    type="button"
                    onClick={() => {
                      setAiModal((prev) => ({
                        ...prev,
                        instruction: prev.instruction
                          ? `${prev.instruction.trim()}. ${promptText}`
                          : promptText,
                      }));
                    }}
                    className="badge-tag bg-white hover:bg-cream-bg text-charcoal border-charcoal text-[11px] cursor-pointer transition-colors"
                    title="Click to add to your instruction"
                  >
                    💡 {promptText}
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Action Button */}
            <div className="flex justify-end pt-1">
              <button
                type="button"
                disabled={aiModal.loading || !aiModal.instruction.trim()}
                onClick={() => runAskAi(aiModal.instruction)}
                className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5"
              >
                {aiModal.loading ? (
                  <>
                    <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent" />
                    <span>Generating Revision...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Generate Revision</span>
                  </>
                )}
              </button>
            </div>

            {/* Evidence Warning / Unverified Claims Alert */}
            {aiModal.evidenceWarning && (
              <div className="p-3 bg-amber-50 border-2 border-amber-500 text-amber-950 space-y-2">
                <div className="flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                  <div className="text-xs space-y-1">
                    <div className="font-bold text-amber-900">
                      Evidence Alert: Unverified Claims Detected
                    </div>
                    <div>{aiModal.evidenceWarning}</div>
                    {aiModal.missingEvidence?.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1 pt-1">
                        <span className="font-bold text-[11px]">Unverified:</span>
                        {aiModal.missingEvidence.map((claim, cIdx) => (
                          <span
                            key={cIdx}
                            className="badge-tag bg-amber-200 border-amber-600 text-amber-950 text-[10px]"
                          >
                            {claim}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-end space-x-2 pt-1 border-t border-amber-200">
                  <button
                    type="button"
                    onClick={() => runAskAi(aiModal.instruction, true)}
                    className="btn-secondary text-xs py-1 px-3 bg-amber-100 hover:bg-amber-200 border-amber-700 text-amber-950 font-bold"
                  >
                    Acknowledge & Proceed Anyway
                  </button>
                </div>
              </div>
            )}

            {/* AI Proposed Revision */}
            {aiModal.suggestedText && (
              <div className="space-y-3 border-t border-cream-border pt-3">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-emerald-800 uppercase flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Proposed AI Revision</span>
                    </span>
                    {aiModal.hasUnsupportedContent && !aiModal.evidenceWarning && (
                      <span className="badge-tag bg-amber-100 border-amber-600 text-amber-900 text-[10px]">
                        ⚠️ Contains Acknowledged Unverified Content
                      </span>
                    )}
                  </div>
                  <div className="p-3 bg-emerald-50 border-2 border-emerald-600 text-xs text-emerald-950 whitespace-pre-line leading-relaxed font-mono">
                    {aiModal.suggestedText}
                  </div>
                </div>

                {aiModal.explanation && (
                  <div className="p-2 bg-cream-bg border border-cream-border text-[11px] text-charcoal-muted">
                    <strong>Rationale:</strong> {aiModal.explanation}
                  </div>
                )}

                <div className="flex justify-end space-x-2 pt-2">
                  <button
                    onClick={() =>
                      setAiModal((prev) => ({ ...prev, isOpen: false }))
                    }
                    className="btn-secondary text-xs"
                  >
                    Discard
                  </button>
                  <button
                    onClick={applyAiSuggestion}
                    className="btn-primary text-xs flex items-center space-x-1.5 bg-emerald-700 hover:bg-emerald-800 border-charcoal"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Accept & Apply Revision</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
