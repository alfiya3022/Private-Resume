import React from "react";
import { Award, Plus, Edit3, ExternalLink, Trash2, Save } from "lucide-react";

export default function CertificationsTab({
  newCert,
  setNewCert,
  handleAddCert,
  certifications,
  editingCertId,
  setEditingCertId,
  editCertForm,
  setEditCertForm,
  handleStartEditCert,
  handleSaveEditCert,
  handleDeleteCert,
}) {
  return (
    <div className="space-y-3">
      {/* Add Certification Form */}
      <form
        onSubmit={handleAddCert}
        className="bg-cream p-3 sm:p-3.5 border border-charcoal space-y-2.5"
      >
        <h4 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
          <Award className="w-3.5 h-3.5 text-coral" />
          <span>Add Certification</span>
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Certification Name *
            </label>
            <input
              type="text"
              value={newCert.name}
              onChange={(e) => setNewCert({ ...newCert, name: e.target.value })}
              placeholder="e.g. AWS Solutions Architect"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Issuing Organization *
            </label>
            <input
              type="text"
              value={newCert.issuer}
              onChange={(e) =>
                setNewCert({ ...newCert, issuer: e.target.value })
              }
              placeholder="e.g. Amazon Web Services"
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Issue Date
            </label>
            <input
              type="date"
              value={newCert.issue_date}
              onChange={(e) =>
                setNewCert({ ...newCert, issue_date: e.target.value })
              }
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
            <span>Add Certification</span>
          </button>
        </div>
      </form>

      {/* Certifications List Container */}
      <div className="space-y-2">
        <h4 className="text-[11px] font-mono uppercase font-bold text-charcoal-muted">
          Recorded Certifications ({certifications?.length || 0})
        </h4>

        {certifications?.map((c) => (
          <div key={c.id} className="p-3 border border-charcoal bg-white">
            {editingCertId === c.id ? (
              <form onSubmit={handleSaveEditCert} className="space-y-2.5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Certification Name *
                    </label>
                    <input
                      type="text"
                      value={editCertForm.name}
                      onChange={(e) =>
                        setEditCertForm({
                          ...editCertForm,
                          name: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Issuer *
                    </label>
                    <input
                      type="text"
                      value={editCertForm.issuer}
                      onChange={(e) =>
                        setEditCertForm({
                          ...editCertForm,
                          issuer: e.target.value,
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
                      Issue Date
                    </label>
                    <input
                      type="date"
                      value={editCertForm.issue_date}
                      onChange={(e) =>
                        setEditCertForm({
                          ...editCertForm,
                          issue_date: e.target.value,
                        })
                      }
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                      Credential Verification URL
                    </label>
                    <input
                      type="url"
                      value={editCertForm.credential_url}
                      onChange={(e) =>
                        setEditCertForm({
                          ...editCertForm,
                          credential_url: e.target.value,
                        })
                      }
                      placeholder="https://..."
                      className="w-full border border-charcoal px-2 py-1 text-xs bg-white font-mono"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-2 pt-1 border-t border-cream-border">
                  <button
                    type="button"
                    onClick={() => setEditingCertId(null)}
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
                    {c.name}
                  </h5>
                  <div className="text-xs text-charcoal-muted mt-0.5 truncate">
                    {c.issuer} {c.issue_date ? `• ${c.issue_date}` : ""}
                  </div>
                  {c.credential_url && (
                    <a
                      href={c.credential_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center space-x-1 text-[11px] text-coral hover:underline mt-0.5"
                    >
                      <span>Verify Credential</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
                <div className="flex items-center space-x-1 shrink-0">
                  <button
                    type="button"
                    onClick={() => handleStartEditCert(c)}
                    className="p-1 border border-charcoal bg-cream hover:bg-white text-charcoal"
                    title="Edit certification"
                    aria-label={`Edit ${c.name}`}
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDeleteCert(c.id)}
                    className="p-1 border border-charcoal bg-cream hover:bg-white text-rose-600 hover:text-rose-800"
                    title="Delete certification"
                    aria-label={`Delete ${c.name}`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
        {(!certifications || certifications.length === 0) && (
          <p className="text-xs text-charcoal-muted">
            No certifications recorded yet.
          </p>
        )}
      </div>
    </div>
  );
}
