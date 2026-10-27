import React from "react";
import { Edit3, ExternalLink, X, Save } from "lucide-react";

export const COUNTRY_CODES = [
  { code: "+91", label: "IN (+91)" },
  { code: "+1", label: "US/CA (+1)" },
  { code: "+44", label: "UK (+44)" },
  { code: "+61", label: "AU (+61)" },
  { code: "+49", label: "DE (+49)" },
  { code: "+33", label: "FR (+33)" },
  { code: "+65", label: "SG (+65)" },
  { code: "+971", label: "UAE (+971)" },
  { code: "+81", label: "JP (+81)" },
];

export default function PersonalInfoTab({
  isEditingPersonal,
  setIsEditingPersonal,
  personalForm,
  setPersonalForm,
  phoneCountryCode,
  setPhoneCountryCode,
  phoneDigits,
  setPhoneDigits,
  handleUpdatePersonal,
  handleCancelPersonalEdit,
  countryCodes = COUNTRY_CODES,
}) {
  return (
    <div className="space-y-3">
      {!isEditingPersonal ? (
        /* View Mode: Compact Candidate Overview Card */
        <div className="bg-cream border border-charcoal p-3.5 sm:p-4 space-y-3">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-charcoal/20 pb-2.5">
            <div>
              <h3 className="font-bold text-base text-charcoal">
                {personalForm.headline || "Candidate Overview"}
              </h3>
              {personalForm.location && (
                <p className="text-xs text-charcoal-muted mt-0.5">
                  {personalForm.location}
                </p>
              )}
            </div>
            <button
              onClick={() => setIsEditingPersonal(true)}
              className="btn-primary text-xs flex items-center space-x-1.5 py-1 px-3 self-end sm:self-auto"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Personal Info</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 sm:gap-3 text-xs font-mono">
            <div className="px-2.5 py-2 bg-white border border-charcoal">
              <span className="text-charcoal-muted uppercase text-[10px] block">
                Contact
              </span>
              <span className="font-bold text-charcoal mt-0.5 block truncate">
                {personalForm.phone || "Not provided"}
              </span>
            </div>

            <div className="px-2.5 py-2 bg-white border border-charcoal">
              <span className="text-charcoal-muted uppercase text-[10px] block">
                LinkedIn
              </span>
              {personalForm.linkedin_url ? (
                <a
                  href={personalForm.linkedin_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-coral hover:underline mt-0.5 truncate block flex items-center space-x-1"
                >
                  <span className="truncate">{personalForm.linkedin_url}</span>
                  <ExternalLink className="w-3 h-3 shrink-0" />
                </a>
              ) : (
                <span className="text-charcoal-muted mt-0.5 block">
                  Not provided
                </span>
              )}
            </div>

            <div className="px-2.5 py-2 bg-white border border-charcoal">
              <span className="text-charcoal-muted uppercase text-[10px] block">
                GitHub
              </span>
              {personalForm.github_url ? (
                <a
                  href={personalForm.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-coral hover:underline mt-0.5 truncate block flex items-center space-x-1"
                >
                  <span className="truncate">{personalForm.github_url}</span>
                  <ExternalLink className="w-3 h-3 shrink-0" />
                </a>
              ) : (
                <span className="text-charcoal-muted mt-0.5 block">
                  Not provided
                </span>
              )}
            </div>
          </div>

          <div className="bg-white border border-charcoal p-3 space-y-1">
            <span className="text-[10px] font-mono uppercase font-bold text-charcoal-muted block">
              Professional Summary
            </span>
            <p className="text-xs text-charcoal leading-relaxed">
              {personalForm.summary || "No professional summary provided."}
            </p>
          </div>
        </div>
      ) : (
        /* Edit Mode: Compact Form */
        <form
          onSubmit={handleUpdatePersonal}
          className="space-y-2.5 max-w-3xl bg-cream p-3.5 sm:p-4 border border-charcoal"
        >
          <div className="flex items-center justify-between border-b border-charcoal/20 pb-2">
            <h3 className="font-bold text-xs uppercase tracking-wider text-charcoal flex items-center space-x-1.5">
              <Edit3 className="w-3.5 h-3.5 text-coral" />
              <span>Edit Personal Information</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Headline / Role
              </label>
              <input
                type="text"
                value={personalForm.headline}
                onChange={(e) =>
                  setPersonalForm({ ...personalForm, headline: e.target.value })
                }
                placeholder="e.g. Senior Full-Stack Engineer"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              />
            </div>
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Location
              </label>
              <input
                type="text"
                value={personalForm.location}
                onChange={(e) =>
                  setPersonalForm({ ...personalForm, location: e.target.value })
                }
                placeholder="e.g. San Francisco, CA"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
              Professional Summary
            </label>
            <textarea
              rows={3}
              value={personalForm.summary}
              onChange={(e) =>
                setPersonalForm({ ...personalForm, summary: e.target.value })
              }
              placeholder="Brief factual summary of candidate career, technologies, and achievements..."
              className="w-full border border-charcoal px-2.5 py-1.5 text-xs sm:text-sm bg-white font-sans"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                Contact
              </label>
              <div className="flex border border-charcoal bg-white">
                <select
                  value={phoneCountryCode}
                  onChange={(e) => setPhoneCountryCode(e.target.value)}
                  className="bg-cream px-2 py-1 text-xs font-mono font-bold border-r border-charcoal focus:outline-none"
                >
                  {countryCodes.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.label}
                    </option>
                  ))}
                </select>
                <input
                  type="tel"
                  value={phoneDigits}
                  onChange={(e) => setPhoneDigits(e.target.value)}
                  placeholder="98765 43210"
                  className="w-full px-2 py-1 text-xs sm:text-sm bg-white focus:outline-none font-mono"
                />
              </div>
            </div>
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                LinkedIn URL
              </label>
              <input
                type="url"
                value={personalForm.linkedin_url}
                onChange={(e) =>
                  setPersonalForm({
                    ...personalForm,
                    linkedin_url: e.target.value,
                  })
                }
                placeholder="https://linkedin.com/in/username"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
              />
            </div>
            <div>
              <label className="block text-[11px] font-mono uppercase text-charcoal-muted mb-1">
                GitHub URL
              </label>
              <input
                type="url"
                value={personalForm.github_url}
                onChange={(e) =>
                  setPersonalForm({
                    ...personalForm,
                    github_url: e.target.value,
                  })
                }
                placeholder="https://github.com/username"
                className="w-full border border-charcoal px-2.5 py-1.5 text-xs bg-white font-mono"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-2 pt-2 border-t border-charcoal/20">
            <button
              type="button"
              onClick={handleCancelPersonalEdit}
              className="btn-secondary text-xs py-1.5 px-3 flex items-center justify-center space-x-1"
            >
              <X className="w-3 h-3" />
              <span>Cancel</span>
            </button>
            <button
              type="submit"
              className="btn-primary text-xs py-1.5 px-3.5 flex items-center justify-center space-x-1.5"
            >
              <Save className="w-3 h-3" />
              <span>Save Personal Details</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
