import React, { useState, useEffect } from "react";
import {
  Briefcase,
  Calendar,
  CheckCircle2,
  Clock,
  Download,
  ExternalLink,
  Filter,
  Layers,
  MessageSquare,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  XCircle,
  FileText,
} from "lucide-react";
import { api } from "../api/client";
import { applicationsApi } from "../api/applications";
import { artifactsApi } from "../api/artifacts";

const STATUS_CONFIG = {
  applied: {
    label: "Applied",
    color: "bg-blue-50 text-blue-800 border-blue-500",
  },
  interviewing: {
    label: "Interviewing",
    color: "bg-amber-50 text-amber-800 border-amber-500",
  },
  offer: {
    label: "Offer Received",
    color: "bg-emerald-50 text-emerald-800 border-emerald-600",
  },
  rejected: {
    label: "Declined",
    color: "bg-rose-50 text-rose-800 border-rose-500",
  },
  draft: { label: "Draft", color: "bg-gray-50 text-gray-700 border-gray-400" },
  archived: {
    label: "Archived",
    color: "bg-cream-bg text-charcoal-muted border-charcoal-muted",
  },
};

export default function ApplicationsPage({ currentUser }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Auto-dismiss green success notifications after 4 seconds
  useEffect(() => {
    if (successMsg) {
      const timer = setTimeout(() => {
        setSuccessMsg("");
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [successMsg]);

  // Editing notes state
  const [editingNotesId, setEditingNotesId] = useState(null);
  const [notesInput, setNotesInput] = useState("");
  const [savingNotes, setSavingNotes] = useState(false);
  const [downloadingId, setDownloadingId] = useState(null);

  const handleDownloadPdf = async (app) => {
    if (!app?.tailored_resume?.id) return;
    setDownloadingId(app.id);
    setErrorMsg("");
    try {
      const token = api.getToken();
      const companyClean = app.job?.company
        ? app.job.company.replace(/\s+/g, "_")
        : "Resume";
      const filename = `Application_${companyClean}.pdf`;
      const response = await fetch(
        artifactsApi.getPdfUrl(app.tailored_resume.id),
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        },
      );
      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || "Failed to download PDF");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    } catch (err) {
      setErrorMsg(err.message || "Failed to download PDF.");
    } finally {
      setDownloadingId(null);
    }
  };

  useEffect(() => {
    loadApplications();
  }, [statusFilter]);

  const loadApplications = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      const data = await applicationsApi.getApplications(
        statusFilter === "all" ? null : statusFilter,
      );
      setApplications(data || []);
    } catch (err) {
      setErrorMsg(err.message || "Failed to load applications.");
      setApplications([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (appId, newStatus) => {
    try {
      const updated = await applicationsApi.updateApplication(appId, {
        status: newStatus,
      });
      setApplications((prev) =>
        prev.map((a) => (a.id === appId ? updated : a)),
      );
      setSuccessMsg(
        `Status updated to ${STATUS_CONFIG[newStatus]?.label || newStatus}.`,
      );
    } catch (err) {
      setErrorMsg(err.message || "Failed to update status.");
    }
  };

  const handleOpenNotes = (app) => {
    setEditingNotesId(app.id);
    setNotesInput(app.notes || "");
  };

  const handleSaveNotes = async (appId) => {
    setSavingNotes(true);
    try {
      const updated = await applicationsApi.updateApplication(appId, {
        notes: notesInput,
      });
      setApplications((prev) =>
        prev.map((a) => (a.id === appId ? updated : a)),
      );
      setEditingNotesId(null);
      setSuccessMsg("Application notes saved.");
    } catch (err) {
      setErrorMsg(err.message || "Failed to save notes.");
    } finally {
      setSavingNotes(false);
    }
  };

  const handleDelete = async (appId) => {
    if (!window.confirm("Delete this application record?")) return;
    try {
      await applicationsApi.deleteApplication(appId);
      setApplications((prev) => prev.filter((a) => a.id !== appId));
      setSuccessMsg("Application deleted.");
    } catch (err) {
      setErrorMsg(err.message || "Failed to delete application.");
    }
  };

  const filteredApps = applications.filter((app) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const company = (app.job?.company || "").toLowerCase();
    const title = (app.job?.title || "").toLowerCase();
    return company.includes(q) || title.includes(q);
  });

  if (!currentUser) {
    return (
      <div className="card-brutal text-center py-12 space-y-4">
        <Briefcase className="w-12 h-12 text-coral mx-auto" />
        <h2 className="text-xl font-bold text-charcoal">Sign In Required</h2>
        <p className="text-xs text-charcoal-muted max-w-sm mx-auto">
          Sign in to view and track your submitted job applications.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-mono">
      {/* Header & Controls */}
      <div className="card-brutal bg-white p-6 border-2 border-charcoal shadow-brutal-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-bold uppercase tracking-wider text-charcoal flex items-center space-x-2">
              <Briefcase className="w-5 h-5 text-coral" />
              <span>Application Pipeline</span>
            </h1>
            <p className="text-xs text-charcoal-muted mt-1">
              Track submitted roles linked to exact, immutable resume versions.
            </p>
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <div className="relative flex-1 sm:flex-initial">
              <Search className="w-3.5 h-3.5 text-charcoal-muted absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search company or title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-brutal pl-8 pr-3 py-1.5 text-xs w-full sm:w-64"
              />
            </div>
            <button
              onClick={loadApplications}
              className="p-2 border-2 border-charcoal hover:bg-cream-bg transition-colors shrink-0"
              title="Refresh applications"
            >
              <RefreshCw className="w-3.5 h-3.5 text-charcoal" />
            </button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 border-t border-cream-border pt-3">
          {["all", "applied", "interviewing", "offer", "rejected", "draft"].map(
            (st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 text-xs border transition-all ${
                  statusFilter === st
                    ? "bg-charcoal text-white border-charcoal font-bold"
                    : "bg-white text-charcoal border-cream-border hover:border-charcoal"
                }`}
              >
                {st === "all"
                  ? "All Applications"
                  : STATUS_CONFIG[st]?.label || st}
              </button>
            ),
          )}
        </div>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-3 bg-rose-50 border-2 border-rose-600 text-rose-900 text-xs flex justify-between items-center">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg("")} className="font-bold ml-2">
            ✕
          </button>
        </div>
      )}
      {successMsg && (
        <div className="p-3 bg-emerald-50 border-2 border-emerald-600 text-emerald-900 text-xs flex justify-between items-center">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg("")} className="font-bold ml-2">
            ✕
          </button>
        </div>
      )}

      {/* Applications List */}
      {loading ? (
        <div className="card-brutal text-center py-12 space-y-2">
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-charcoal border-t-transparent mx-auto" />
          <p className="text-xs text-charcoal-muted">Loading applications...</p>
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="card-brutal bg-white text-center py-16 space-y-3 border-2 border-charcoal">
          <Briefcase className="w-8 h-8 text-charcoal-muted mx-auto" />
          <h3 className="text-sm font-bold uppercase text-charcoal">
            No Applications Found
          </h3>
          <p className="text-xs text-charcoal-muted max-w-sm mx-auto">
            {statusFilter === "all"
              ? 'Complete a resume in the Workspace and click "Log Application" to start tracking.'
              : `No applications with status "${statusFilter}".`}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredApps.map((app) => {
            const cfg = STATUS_CONFIG[app.status] || STATUS_CONFIG.applied;
            const isEditingNotes = editingNotesId === app.id;

            return (
              <div
                key={app.id}
                className="card-brutal bg-white p-5 border-2 border-charcoal shadow-brutal-sm space-y-4 hover:border-black transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-cream-border pb-3">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-sm text-charcoal">
                        {app.job?.title || "Target Role"}
                      </span>
                      <span className="text-xs text-charcoal-muted">•</span>
                      <span className="font-semibold text-xs text-charcoal">
                        {app.job?.company || "Company"}
                      </span>
                    </div>
                    {app.job?.location && (
                      <span className="text-[11px] text-charcoal-muted block mt-0.5">
                        {app.job.location}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {/* Status Dropdown */}
                    <select
                      value={app.status}
                      onChange={(e) =>
                        handleStatusChange(app.id, e.target.value)
                      }
                      className={`text-xs font-mono font-bold py-1 px-2.5 border-2 ${cfg.color} cursor-pointer`}
                    >
                      <option value="applied">Applied</option>
                      <option value="interviewing">Interviewing</option>
                      <option value="offer">Offer Received</option>
                      <option value="rejected">Declined</option>
                      <option value="draft">Draft</option>
                      <option value="archived">Archived</option>
                    </select>

                    <button
                      onClick={() => handleDelete(app.id)}
                      className="p-1.5 border border-charcoal hover:bg-rose-50 text-rose-700"
                      title="Delete record"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  {/* Applied Date */}
                  <div className="flex items-center space-x-2 text-charcoal-muted">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>
                      Applied: {new Date(app.applied_date).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Linked Resume Version & PDF Download */}
                  <div className="flex items-center space-x-2">
                    <FileText className="w-3.5 h-3.5 text-coral" />
                    {app.tailored_resume ? (
                      <div className="flex items-center space-x-1.5">
                        <span className="font-bold text-charcoal">
                          v{app.tailored_resume.version_number}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleDownloadPdf(app)}
                          disabled={downloadingId === app.id}
                          className="text-coral hover:underline inline-flex items-center space-x-0.5 text-[11px] disabled:opacity-50"
                          title="Download submitted PDF"
                        >
                          <Download className="w-3 h-3 ml-1" />
                          <span>
                            {downloadingId === app.id
                              ? "Downloading..."
                              : "PDF"}
                          </span>
                        </button>
                      </div>
                    ) : (
                      <span className="text-charcoal-muted text-[11px]">
                        No specific snapshot
                      </span>
                    )}
                  </div>

                  {/* Notes Toggle */}
                  <div className="flex items-center justify-start sm:justify-end">
                    <button
                      onClick={() => handleOpenNotes(app)}
                      className="text-xs text-charcoal hover:underline inline-flex items-center space-x-1"
                    >
                      <MessageSquare className="w-3 h-3 text-charcoal-muted" />
                      <span>{app.notes ? "Edit Notes" : "+ Add Notes"}</span>
                    </button>
                  </div>
                </div>

                {/* Notes Display / Editor */}
                {isEditingNotes ? (
                  <div className="p-3 bg-cream-bg/40 border border-charcoal space-y-2 mt-2">
                    <textarea
                      rows={3}
                      value={notesInput}
                      onChange={(e) => setNotesInput(e.target.value)}
                      placeholder="e.g. Completed technical screen. Next interview with Engineering Manager on Thursday."
                      className="input-brutal w-full text-xs"
                    />
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => setEditingNotesId(null)}
                        className="btn-secondary text-xs py-1 px-2.5"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleSaveNotes(app.id)}
                        disabled={savingNotes}
                        className="btn-primary text-xs py-1 px-3"
                      >
                        {savingNotes ? "Saving..." : "Save Notes"}
                      </button>
                    </div>
                  </div>
                ) : (
                  app.notes && (
                    <div className="p-2.5 bg-cream-bg/30 border border-cream-border text-[11px] text-charcoal leading-relaxed">
                      <strong className="text-charcoal-muted">Notes:</strong>{" "}
                      {app.notes}
                    </div>
                  )
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
