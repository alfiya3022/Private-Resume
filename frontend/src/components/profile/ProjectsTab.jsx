import React from "react";
import {
  Sparkles,
  Plus,
  FolderGit2,
  CheckCircle2,
  Edit3,
  Trash2,
  X,
  Save,
  Link as LinkIcon,
} from "lucide-react";

export default function ProjectsTab({
  projectMode,
  setProjectMode,
  githubProjectUrl,
  setGithubProjectUrl,
  extractingProject,
  handleExtractGitHubProject,
  extractedProject,
  setExtractedProject,
  handleSaveExtractedProject,
  newProject,
  setNewProject,
  handleAddManualProject,
  projects,
  editingProjectId,
  setEditingProjectId,
  editProjectForm,
  setEditProjectForm,
  handleStartEditProject,
  handleSaveEditProject,
  handleDeleteProject,
}) {
  return (
    <div className="space-y-3">
      {/* Project Mode Toggle */}
      <div className="flex items-center space-x-1.5 border-b border-cream-border pb-2">
        <button
          type="button"
          onClick={() => setProjectMode("github")}
          className={`px-2.5 py-1 text-xs font-bold border flex items-center space-x-1.5 transition-all ${
            projectMode === "github"
              ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
              : "bg-white text-charcoal border-cream-border hover:border-charcoal"
          }`}
        >
          <Sparkles className="w-3 h-3 text-coral" />
          <span>Add via GitHub Link</span>
        </button>
        <button
          type="button"
          onClick={() => setProjectMode("manual")}
          className={`px-2.5 py-1 text-xs font-bold border flex items-center space-x-1.5 transition-all ${
            projectMode === "manual"
              ? "bg-charcoal text-white border-charcoal shadow-brutal-sm"
              : "bg-white text-charcoal border-cream-border hover:border-charcoal"
          }`}
        >
          <Plus className="w-3 h-3" />
          <span>Manual Addition</span>
        </button>
      </div>

      {/* Mode A: Extract via GitHub Link */}
      {projectMode === "github" && (
        <div className="bg-cream p-3 sm:p-3.5 border border-charcoal space-y-2.5">
          <div>
            <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-coral" />
              <span>Extract Project Details from GitHub</span>
            </h4>
            <p className="text-[11px] text-charcoal-muted mt-0.5">
              Paste a public GitHub repository link. Software extracts title, tech stack, and accomplishments from Markdown files.
            </p>
          </div>

          <form
            onSubmit={handleExtractGitHubProject}
            className="flex flex-col sm:flex-row gap-2"
          >
            <input
              type="url"
              value={githubProjectUrl}
              onChange={(e) => setGithubProjectUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="flex-1 border border-charcoal px-2.5 py-1.5 text-xs font-mono bg-white focus:outline-none focus:ring-1 focus:ring-coral"
              required
            />
            <button
              type="submit"
              disabled={extractingProject || !githubProjectUrl.trim()}
              className="btn-primary flex items-center justify-center space-x-1.5 whitespace-nowrap text-xs py-1.5 px-3"
            >
              {extractingProject ? (
                <>
                  <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent" />
                  <span>Extracting Repo...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3 h-3" />
                  <span>Extract Details</span>
                </>
              )}
            </button>
          </form>

          {/* Extracted Project Preview & Customization */}
          {extractedProject && (
            <form
              onSubmit={handleSaveExtractedProject}
              className="border border-charcoal bg-white p-3 space-y-2.5"
            >
              <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                <span className="text-xs font-bold text-emerald-800 uppercase flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Extracted Repository Data (Review & Edit)</span>
                </span>
                <button
                  type="button"
                  onClick={() => setExtractedProject(null)}
                  className="text-xs text-charcoal-muted hover:text-charcoal"
                >
                  Clear
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Project Title
                  </label>
                  <input
                    type="text"
                    value={extractedProject.title}
                    onChange={(e) =>
                      setExtractedProject({
                        ...extractedProject,
                        title: e.target.value,
                      })
                    }
                    className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-medium"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Role / Position
                  </label>
                  <input
                    type="text"
                    value={extractedProject.role}
                    onChange={(e) =>
                      setExtractedProject({
                        ...extractedProject,
                        role: e.target.value,
                      })
                    }
                    placeholder="e.g. Creator / Maintainer"
                    className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-medium"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                  Technologies (comma separated)
                </label>
                <input
                  type="text"
                  value={extractedProject.technologies}
                  onChange={(e) =>
                    setExtractedProject({
                      ...extractedProject,
                      technologies: e.target.value,
                    })
                  }
                  placeholder="Python, FastAPI, Docker"
                  className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                  Description
                </label>
                <textarea
                  rows={2}
                  value={extractedProject.description}
                  onChange={(e) =>
                    setExtractedProject({
                      ...extractedProject,
                      description: e.target.value,
                    })
                  }
                  className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-sans"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                  Bullet Accomplishments (one per line)
                </label>
                <textarea
                  rows={2}
                  value={extractedProject.bullets}
                  onChange={(e) =>
                    setExtractedProject({
                      ...extractedProject,
                      bullets: e.target.value,
                    })
                  }
                  className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-1 border-t border-cream-border">
                <button
                  type="button"
                  onClick={() => setExtractedProject(null)}
                  className="btn-secondary text-xs py-1 px-2.5"
                >
                  Discard
                </button>
                <button
                  type="submit"
                  className="btn-primary text-xs py-1 px-3 flex items-center space-x-1"
                >
                  <Save className="w-3 h-3" />
                  <span>Save Extracted Project</span>
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Mode B: Manual Project Addition */}
      {projectMode === "manual" && (
        <form
          onSubmit={handleAddManualProject}
          className="bg-cream p-3 sm:p-3.5 border border-charcoal space-y-2.5"
        >
          <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
            <Plus className="w-3.5 h-3.5 text-coral" />
            <span>Add Project Manually</span>
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Project Title *
              </label>
              <input
                type="text"
                value={newProject.title}
                onChange={(e) =>
                  setNewProject({ ...newProject, title: e.target.value })
                }
                placeholder="e.g. Distributed Task Engine"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
                required
              />
            </div>
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Your Role
              </label>
              <input
                type="text"
                value={newProject.role}
                onChange={(e) =>
                  setNewProject({ ...newProject, role: e.target.value })
                }
                placeholder="e.g. Lead Architect / Creator"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Technologies (comma separated)
              </label>
              <input
                type="text"
                value={newProject.technologies}
                onChange={(e) =>
                  setNewProject({ ...newProject, technologies: e.target.value })
                }
                placeholder="e.g. Python, PostgreSQL, Docker, Redis"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
              />
            </div>
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Project URL / Repository
              </label>
              <input
                type="url"
                value={newProject.url}
                onChange={(e) =>
                  setNewProject({ ...newProject, url: e.target.value })
                }
                placeholder="https://github.com/..."
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Description
            </label>
            <textarea
              rows={2}
              value={newProject.description}
              onChange={(e) =>
                setNewProject({ ...newProject, description: e.target.value })
              }
              placeholder="Brief summary of the project goals, architecture, and personal contributions..."
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-sans"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Bullet Accomplishments (one per line)
            </label>
            <textarea
              rows={2}
              value={newProject.bullets}
              onChange={(e) =>
                setNewProject({ ...newProject, bullets: e.target.value })
              }
              placeholder="• Engineered async queue processing 50k jobs/sec&#10;• Reduced latency by 40% using Redis caching"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
            />
          </div>

          <div className="flex justify-end pt-1">
            <button
              type="submit"
              className="btn-primary text-xs py-1.5 px-3.5 flex items-center space-x-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Project</span>
            </button>
          </div>
        </form>
      )}

      {/* Projects List Container */}
      <div className="space-y-2">
        <h4 className="text-[11px] font-mono uppercase font-bold text-charcoal-muted">
          Recorded Projects ({projects?.length || 0})
        </h4>

        {projects?.map((proj) => {
          if (editingProjectId === proj.id) {
            return (
              <form
                key={proj.id}
                onSubmit={handleSaveEditProject}
                className="border border-charcoal bg-white p-3 space-y-2.5"
              >
                <div className="flex items-center justify-between border-b border-cream-border pb-1.5">
                  <span className="text-xs font-bold text-charcoal uppercase flex items-center space-x-1">
                    <Edit3 className="w-3.5 h-3.5 text-coral" />
                    <span>Editing Project: {proj.title}</span>
                  </span>
                  <button
                    type="button"
                    onClick={() => setEditingProjectId(null)}
                    className="text-xs text-charcoal-muted hover:text-charcoal"
                  >
                    Cancel
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Project Title *
                    </label>
                    <input
                      type="text"
                      value={editProjectForm.title}
                      onChange={(e) =>
                        setEditProjectForm({
                          ...editProjectForm,
                          title: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-medium"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Role / Position
                    </label>
                    <input
                      type="text"
                      value={editProjectForm.role}
                      onChange={(e) =>
                        setEditProjectForm({
                          ...editProjectForm,
                          role: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-medium"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Technologies (comma separated)
                    </label>
                    <input
                      type="text"
                      value={editProjectForm.technologies}
                      onChange={(e) =>
                        setEditProjectForm({
                          ...editProjectForm,
                          technologies: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Repository URL
                    </label>
                    <input
                      type="url"
                      value={editProjectForm.url}
                      onChange={(e) =>
                        setEditProjectForm({
                          ...editProjectForm,
                          url: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Description
                  </label>
                  <textarea
                    rows={2}
                    value={editProjectForm.description}
                    onChange={(e) =>
                      setEditProjectForm({
                        ...editProjectForm,
                        description: e.target.value,
                      })
                    }
                    className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-sans"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                    Bullet Accomplishments (one per line)
                  </label>
                  <textarea
                    rows={2}
                    value={editProjectForm.bullets}
                    onChange={(e) =>
                      setEditProjectForm({
                        ...editProjectForm,
                        bullets: e.target.value,
                      })
                    }
                    className="w-full border border-charcoal px-2 py-1 text-xs font-mono bg-white"
                  />
                </div>

                <div className="flex justify-end space-x-2 pt-1 border-t border-cream-border">
                  <button
                    type="button"
                    onClick={() => setEditingProjectId(null)}
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
              key={proj.id}
              className="border border-charcoal p-3 bg-white flex justify-between items-start gap-3"
            >
              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center space-x-2 flex-wrap">
                  <h5 className="font-bold text-xs sm:text-sm text-charcoal">
                    {proj.title}
                  </h5>
                  {proj.role && (
                    <span className="text-[11px] text-charcoal-muted font-mono">
                      • {proj.role}
                    </span>
                  )}
                  {proj.url && (
                    <a
                      href={proj.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-coral hover:underline inline-flex items-center space-x-1 text-[11px] font-mono"
                    >
                      <LinkIcon className="w-3 h-3" />
                      <span>Repo</span>
                    </a>
                  )}
                </div>
                {proj.description && (
                  <p className="text-xs text-charcoal-muted leading-relaxed">
                    {proj.description}
                  </p>
                )}
                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-0.5">
                    {proj.technologies.map((tech, i) => (
                      <span
                        key={i}
                        className="badge-tag bg-cream text-charcoal border-charcoal text-[10px]"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
                {proj.bullets && proj.bullets.length > 0 && (
                  <ul className="list-disc list-inside text-xs text-charcoal space-y-0.5 pt-0.5">
                    {proj.bullets.map((b, idx) => (
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
                  onClick={() => handleStartEditProject(proj)}
                  className="p-1 border border-charcoal bg-cream hover:bg-white text-charcoal"
                  title="Edit project"
                  aria-label={`Edit ${proj.title}`}
                >
                  <Edit3 className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleDeleteProject(proj.id)}
                  className="p-1 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                  title="Remove project"
                  aria-label={`Remove ${proj.title}`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
        {(!projects || projects.length === 0) && (
          <p className="text-xs text-charcoal-muted">
            No projects added yet. Extract from GitHub or add manually above.
          </p>
        )}
      </div>
    </div>
  );
}
