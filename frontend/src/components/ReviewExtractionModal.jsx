import React, { useState } from 'react';
import {
  X,
  CheckCircle2,
  AlertCircle,
  FileText,
  User,
  Wrench,
  FolderGit2,
  Briefcase,
  GraduationCap,
  Award,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import { profileApi } from '../api/profile';

class SectionErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Section render error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 border-2 border-red-500 bg-red-50 text-red-800 text-xs">
          <div className="font-bold flex items-center space-x-1.5 mb-1">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <span>Unable to render this section</span>
          </div>
          <div className="font-mono text-[11px] text-red-700">
            {this.state.error?.message || 'Unexpected data structure encountered.'}
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const getSkillLabel = (skill) => {
  if (!skill) return '';
  if (typeof skill === 'string') return skill;
  if (typeof skill === 'object') return skill.name || skill.skill || '';
  return String(skill);
};

const getSkillCategory = (skill) => {
  if (!skill || typeof skill !== 'object') return null;
  return skill.category || null;
};

export default function ReviewExtractionModal({
  isOpen,
  onClose,
  resumeData,
  onApplied,
}) {
  const [activeTab, setActiveTab] = useState('personal');
  const [selectedSections, setSelectedSections] = useState({
    personal_info: true,
    skills: true,
    projects: true,
    experience: true,
    education: true,
    certifications: true,
  });
  const [overwriteExisting, setOverwriteExisting] = useState(false);
  const [applying, setApplying] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen || !resumeData) return null;

  const { resume_id, filename, extracted_data = {}, comparison = {} } = resumeData;
  const personal = extracted_data.personal_info || {};
  const personalComp = comparison.personal_info || {};
  const skillsComp = comparison.skills || {};
  const projectsComp = comparison.projects || {};
  const expComp = comparison.experience || {};
  const eduComp = comparison.education || {};
  const certComp = comparison.certifications || {};

  const toggleSection = (key) => {
    setSelectedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleApply = async () => {
    setApplying(true);
    setErrorMsg('');
    try {
      const sectionsToApply = Object.keys(selectedSections).filter(
        (k) => selectedSections[k]
      );
      if (sectionsToApply.length === 0) {
        setErrorMsg('Please select at least one section to apply.');
        setApplying(false);
        return;
      }

      const res = await profileApi.applyExtractedData(resume_id, {
        sections: sectionsToApply,
        overwrite_existing: overwriteExisting,
      });

      if (onApplied) {
        onApplied(res);
      }
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to apply extracted data to profile.');
    } finally {
      setApplying(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'new':
        return (
          <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 text-[10px]">
            New Value
          </span>
        );
      case 'conflict':
        return (
          <span className="badge-tag bg-amber-50 text-amber-900 border-amber-600 text-[10px]">
            Different from Profile
          </span>
        );
      case 'match':
        return (
          <span className="badge-tag bg-blue-50 text-blue-800 border-blue-600 text-[10px]">
            Matches Profile
          </span>
        );
      case 'current_only':
        return (
          <span className="badge-tag bg-gray-100 text-gray-700 border-gray-400 text-[10px]">
            Profile Only
          </span>
        );
      default:
        return null;
    }
  };

  const tabs = [
    { id: 'personal', label: 'Personal & Contact', icon: User, key: 'personal_info' },
    {
      id: 'skills',
      label: `Skills (${skillsComp.total_extracted || extracted_data.skills?.length || 0})`,
      icon: Wrench,
      key: 'skills',
    },
    {
      id: 'projects',
      label: `Projects (${extracted_data.projects?.length || 0})`,
      icon: FolderGit2,
      key: 'projects',
    },
    {
      id: 'experience',
      label: `Experience (${extracted_data.experience?.length || 0})`,
      icon: Briefcase,
      key: 'experience',
    },
    {
      id: 'education',
      label: `Education (${extracted_data.education?.length || 0})`,
      icon: GraduationCap,
      key: 'education',
    },
    {
      id: 'certifications',
      label: `Certifications (${extracted_data.certifications?.length || 0})`,
      icon: Award,
      key: 'certifications',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal/60 backdrop-blur-xs font-mono">
      <div className="bg-white border-2 border-charcoal shadow-brutal max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-150">
        {/* Modal Header */}
        <div className="p-4 border-b-2 border-charcoal bg-cream flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-coral" />
            <div>
              <h2 className="text-base font-bold text-charcoal tracking-tight">
                Review Extracted Resume Data
              </h2>
              <p className="text-xs text-charcoal-muted">
                Source Document: <span className="font-semibold text-charcoal">{filename}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 border border-charcoal hover:bg-white text-charcoal transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="flex border-b border-cream-border bg-cream/40 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isSelected = selectedSections[tab.key];
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2.5 px-3 text-xs font-bold border-b-2 whitespace-nowrap flex items-center space-x-1.5 transition-colors ${
                  isActive
                    ? 'border-coral text-charcoal bg-white'
                    : 'border-transparent text-charcoal-muted hover:text-charcoal hover:bg-white/50'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={(e) => {
                    e.stopPropagation();
                    toggleSection(tab.key);
                  }}
                  className="rounded-none border-charcoal accent-coral h-3.5 w-3.5 mr-1"
                  title="Check to include in Profile application"
                />
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-coral' : 'text-charcoal-muted'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Body */}
        <div className="p-5 flex-1 overflow-y-auto space-y-4">
          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-500 text-rose-900 text-xs">
              {errorMsg}
            </div>
          )}

          {/* TAB 1: Personal & Contact */}
          {activeTab === 'personal' && (
            <div className="space-y-4 text-xs">
              <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border flex justify-between items-center">
                <span>Contact & Personal Details</span>
                <span className="text-[11px] font-normal lowercase">
                  Section included: {selectedSections.personal_info ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { key: 'phone', label: 'Phone Number' },
                  { key: 'location', label: 'Location' },
                  { key: 'linkedin_url', label: 'LinkedIn Profile' },
                  { key: 'github_url', label: 'GitHub Profile' },
                  { key: 'portfolio_url', label: 'Portfolio URL' },
                ].map(({ key, label }) => {
                  const item = personalComp[key] || {
                    current: '',
                    extracted: personal[key] || '',
                    status: personal[key] ? 'new' : 'empty',
                  };
                  return (
                    <div key={key} className="p-3 border border-charcoal bg-cream/30 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-charcoal">{label}</span>
                        {getStatusBadge(item.status)}
                      </div>
                      <div className="text-[11px]">
                        <div className="text-charcoal-muted">Extracted:</div>
                        <div className="font-medium text-charcoal break-all">
                          {item.extracted || <em className="text-gray-400">None detected</em>}
                        </div>
                      </div>
                      <div className="text-[11px] pt-1 border-t border-cream-border">
                        <div className="text-charcoal-muted">Current Profile:</div>
                        <div className="text-charcoal break-all">
                          {item.current || <em className="text-gray-400">Empty</em>}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {extracted_data.summary && (
                <div className="p-3 border border-charcoal bg-cream/30 space-y-1">
                  <div className="font-bold text-charcoal">Detected Summary</div>
                  <p className="text-charcoal leading-relaxed">{extracted_data.summary}</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Skills */}
          {activeTab === 'skills' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                  Detected Skills
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="font-bold text-charcoal mb-1.5 flex items-center space-x-1.5">
                      <span className="w-2 h-2 bg-emerald-600 inline-block"></span>
                      <span>New Skills (Will be added to Profile):</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {(skillsComp.new_skills || []).length > 0 ? (
                        skillsComp.new_skills.map((skill, idx) => {
                          const label = getSkillLabel(skill);
                          const category = getSkillCategory(skill);
                          if (!label) return null;
                          return (
                            <span
                              key={idx}
                              className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 font-semibold inline-flex items-center gap-1.5"
                            >
                              <span>+ {label}</span>
                              {category && (
                                <span className="text-[10px] bg-emerald-100/90 text-emerald-900 px-1 py-0.5 rounded font-mono font-normal border border-emerald-300">
                                  {category}
                                </span>
                              )}
                            </span>
                          );
                        })
                      ) : (
                        <span className="text-charcoal-muted text-[11px]">
                          {(skillsComp.matching_skills || []).length > 0
                            ? 'All detected skills are already present in your profile.'
                            : 'No new skills detected.'}
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="font-bold text-charcoal mb-1.5 flex items-center space-x-1.5">
                      <span className="w-2 h-2 bg-gray-400 inline-block"></span>
                      <span>Already in Profile:</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {(skillsComp.matching_skills || []).length > 0 ? (
                        skillsComp.matching_skills.map((skill, idx) => {
                          const label = getSkillLabel(skill);
                          const category = getSkillCategory(skill);
                          if (!label) return null;
                          return (
                            <span
                              key={idx}
                              className="badge-tag bg-gray-100 text-gray-700 border-gray-400 inline-flex items-center gap-1.5"
                            >
                              <span>✓ {label}</span>
                              {category && (
                                <span className="text-[10px] bg-gray-200 text-gray-700 px-1 py-0.5 rounded font-mono font-normal border border-gray-300">
                                  {category}
                                </span>
                              )}
                            </span>
                          );
                        })
                      ) : (
                        <span className="text-charcoal-muted text-[11px]">
                          None of the detected skills match your existing profile yet.
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Fallback for uncompared extracted skills if comparison diff is missing */}
                  {(!skillsComp.new_skills || skillsComp.new_skills.length === 0) &&
                    (!skillsComp.matching_skills || skillsComp.matching_skills.length === 0) &&
                    (extracted_data.skills || []).length > 0 && (
                      <div className="pt-2 border-t border-cream-border">
                        <div className="font-bold text-charcoal mb-1.5">All Extracted Skills:</div>
                        <div className="flex flex-wrap gap-1.5">
                          {extracted_data.skills.map((skill, idx) => {
                            const label = getSkillLabel(skill);
                            const category = getSkillCategory(skill);
                            if (!label) return null;
                            return (
                              <span
                                key={idx}
                                className="badge-tag bg-cream text-charcoal border-charcoal-muted inline-flex items-center gap-1.5"
                              >
                                <span>{label}</span>
                                {category && (
                                  <span className="text-[10px] bg-cream-muted text-charcoal-muted px-1 py-0.5 rounded font-mono font-normal">
                                    {category}
                                  </span>
                                )}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}
                </div>
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 3: Projects */}
          {activeTab === 'projects' && (
            <div className="space-y-3 text-xs">
              <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                Extracted Projects ({extracted_data.projects?.length || 0})
              </div>
              {extracted_data.projects?.length > 0 ? (
                extracted_data.projects.map((proj, idx) => (
                  <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-charcoal">{proj.title}</span>
                      {(proj.start_date || proj.end_date || proj.dates) && (
                        <span className="text-[11px] text-charcoal-muted">
                          {proj.start_date && proj.end_date
                            ? `${proj.start_date} — ${proj.end_date}`
                            : proj.start_date || proj.end_date || proj.dates}
                        </span>
                      )}
                    </div>
                    {proj.technologies?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {proj.technologies.map((t, tidx) => (
                          <span key={tidx} className="badge-tag text-[10px] bg-white">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                    {(proj.github_url || proj.live_url) && (
                      <div className="flex flex-wrap gap-3 text-[11px]">
                        {proj.github_url && (
                          <a
                            href={proj.github_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-coral underline flex items-center space-x-1"
                          >
                            <span>GitHub: {proj.github_url}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                        {proj.live_url && (
                          <a
                            href={proj.live_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-coral underline flex items-center space-x-1"
                          >
                            <span>Live: {proj.live_url}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    )}
                    {proj.bullets?.length > 0 && (
                      <ul className="list-disc list-inside space-y-0.5 text-charcoal text-[11px]">
                        {proj.bullets.map((b, bidx) => (
                          <li key={bidx}>{b}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-charcoal-muted">
                  No projects identified in this document.
                </div>
              )}
            </div>
          )}

          {/* TAB 4: Experience */}
          {activeTab === 'experience' && (
            <div className="space-y-3 text-xs">
              <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                Extracted Work Experience ({extracted_data.experience?.length || 0})
              </div>
              {extracted_data.experience?.length > 0 ? (
                extracted_data.experience.map((exp, idx) => (
                  <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-charcoal">{exp.title}</span>
                      <span className="text-[11px] text-charcoal-muted">
                        {exp.start_date || ''} {exp.end_date ? `— ${exp.end_date}` : ''}
                      </span>
                    </div>
                    <div className="font-semibold text-charcoal-muted">
                      {exp.company} {exp.location ? `(${exp.location})` : ''}
                    </div>
                    {exp.bullets?.length > 0 && (
                      <ul className="list-disc list-inside space-y-0.5 text-charcoal text-[11px] pt-1">
                        {exp.bullets.map((b, bidx) => (
                          <li key={bidx}>{b}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-charcoal-muted">
                  No experience entries detected in this document.
                </div>
              )}
            </div>
          )}

          {/* TAB 5: Education */}
          {activeTab === 'education' && (
            <div className="space-y-3 text-xs">
              <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                Extracted Education ({extracted_data.education?.length || 0})
              </div>
              {extracted_data.education?.length > 0 ? (
                extracted_data.education.map((edu, idx) => (
                  <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-charcoal">{edu.degree}</span>
                      {(edu.end_date || edu.dates) && (
                        <span className="text-[11px] text-charcoal-muted">
                          {edu.end_date || edu.dates}
                        </span>
                      )}
                    </div>
                    <div className="text-charcoal font-medium">{edu.institution}</div>
                    {edu.grade && (
                      <div className="text-[11px] text-charcoal-muted">Grade/CGPA: {edu.grade}</div>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-charcoal-muted">
                  No education entries detected.
                </div>
              )}
            </div>
          )}

          {/* TAB 6: Certifications */}
          {activeTab === 'certifications' && (
            <div className="space-y-3 text-xs">
              <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                Extracted Certifications ({extracted_data.certifications?.length || 0})
              </div>
              {extracted_data.certifications?.length > 0 ? (
                extracted_data.certifications.map((cert, idx) => (
                  <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-charcoal">{cert.name}</span>
                      {cert.issue_date && (
                        <span className="text-[11px] text-charcoal-muted">{cert.issue_date}</span>
                      )}
                    </div>
                    {cert.issuer && (
                      <div className="text-charcoal-muted">Issuer: {cert.issuer}</div>
                    )}
                    {cert.credential_url && (
                      <div className="text-[11px] pt-1">
                        <a
                          href={cert.credential_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-coral underline flex items-center space-x-1"
                        >
                          <span>Credential Link: {cert.credential_url}</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-charcoal-muted">
                  No certifications detected.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer Controls */}
        <div className="p-4 border-t-2 border-charcoal bg-cream flex flex-col sm:flex-row items-center justify-between gap-3">
          <label className="flex items-center space-x-2 text-xs text-charcoal cursor-pointer select-none">
            <input
              type="checkbox"
              checked={overwriteExisting}
              onChange={(e) => setOverwriteExisting(e.target.checked)}
              className="rounded-none border-charcoal accent-coral h-4 w-4"
            />
            <span title="When unchecked, only fills empty fields and adds new items without touching your existing profile entries.">
              Overwrite existing profile entries if different
            </span>
          </label>

          <div className="flex items-center space-x-2">
            <button onClick={onClose} className="btn-secondary text-xs py-2 px-3">
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={applying}
              className="btn-primary text-xs py-2 px-4 flex items-center space-x-1.5"
            >
              {applying ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Applying to Profile...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Apply Selected to Profile</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
