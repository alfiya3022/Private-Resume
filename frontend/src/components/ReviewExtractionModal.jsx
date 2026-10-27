import React, { useState, useEffect, useMemo } from 'react';
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
  Search,
  Plus,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Info,
  HelpCircle,
  Layers,
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

export const getSkillLabel = (skill) => {
  if (!skill) return '';
  if (typeof skill === 'string') return skill.trim();
  if (typeof skill === 'object') {
    const val = skill.name ?? skill.skill ?? '';
    if (typeof val === 'string') return val.trim();
    if (typeof val === 'object' && val !== null) {
      return String(val.name || val.skill || '').trim();
    }
    return String(val || '').trim();
  }
  return String(skill).trim();
};

export const getSkillCategory = (skill) => {
  if (!skill || typeof skill !== 'object') return 'Other';
  const cat = skill.category;
  if (typeof cat === 'string' && cat.trim()) return cat.trim();
  if (typeof cat === 'object' && cat !== null) {
    return String(cat.name || cat.label || 'Other').trim();
  }
  return 'Other';
};

export const getSkillEvidence = (skill) => {
  if (!skill || typeof skill !== 'object') return null;
  const ev = skill.source_evidence;
  if (typeof ev === 'string' && ev.trim()) return ev.trim();
  return null;
};

const SKILL_CATEGORIES = [
  'All',
  'Programming Language',
  'Languages',
  'Frontend',
  'Backend',
  'Database',
  'DevOps',
  'AI & Machine Learning',
  'Tools & Platforms',
  'Soft Skills',
  'Uncategorized',
  'Other',
];

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
  const [rememberCorrections, setRememberCorrections] = useState(true);
  const [applying, setApplying] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Per-item duplicate consent choices: { "projects:0": "replace_with_new", "skills:sql": "keep_existing", ... }
  const [itemDecisions, setItemDecisions] = useState({});

  // Editable state preserved across tab transitions
  const [editedData, setEditedData] = useState(() => ({
    personal_info: {},
    summary: '',
    skills: [],
    projects: [],
    experience: [],
    education: [],
    certifications: [],
    custom_sections: {},
  }));

  // Skills interactive controls state
  const [skillSearch, setSkillSearch] = useState('');
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('All');
  const [newSkillInput, setNewSkillInput] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('Programming Language');

  // Sync internal state when resumeData updates or modal opens
  useEffect(() => {
    if (resumeData?.extracted_data) {
      const ext = resumeData.extracted_data;
      const rawSkills = Array.isArray(ext.skills) ? ext.skills : [];
      const normalizedSkills = rawSkills
        .map((s) => ({
          name: getSkillLabel(s),
          category: getSkillCategory(s),
          source_evidence: getSkillEvidence(s),
        }))
        .filter((s) => s.name.length > 0);

      setEditedData({
        personal_info: { ...(ext.personal_info || {}) },
        summary: ext.summary || ext.personal_info?.summary || '',
        skills: normalizedSkills,
        projects: Array.isArray(ext.projects) ? ext.projects.map((p) => ({ ...p })) : [],
        experience: Array.isArray(ext.experience) ? ext.experience.map((e) => ({ ...e })) : [],
        education: Array.isArray(ext.education) ? ext.education.map((ed) => ({ ...ed })) : [],
        certifications: Array.isArray(ext.certifications) ? ext.certifications.map((c) => ({ ...c })) : [],
        custom_sections: { ...(ext.custom_sections || {}) },
      });
      setActiveTab('personal');
      setErrorMsg('');
      setSkillSearch('');
      setSelectedCategoryFilter('All');
      setItemDecisions({});
    }
  }, [resumeData, isOpen]);

  const comparison = resumeData?.comparison || {};
  const skillsComp = comparison.skills || {};
  const projectsComp = comparison.projects || {};

  // Set of skills already present in the existing candidate profile
  const existingProfileSkills = useMemo(() => {
    const set = new Set();
    const matching = skillsComp.matching_skills || [];
    matching.forEach((s) => {
      const lbl = getSkillLabel(s).toLowerCase();
      if (lbl) set.add(lbl);
    });
    return set;
  }, [skillsComp.matching_skills]);

  // Set of skills identified as possible duplicate or alias
  const possibleDuplicateSkills = useMemo(() => {
    const map = new Map();
    const dups = skillsComp.possible_duplicates || [];
    dups.forEach((d) => {
      const lbl = getSkillLabel(d.skill || d).toLowerCase();
      if (lbl) map.set(lbl, d);
    });
    return map;
  }, [skillsComp.possible_duplicates]);

  // Map of project matches / possible duplicates by incoming index
  const projectMatchesByIndex = useMemo(() => {
    const map = new Map();
    (projectsComp.matching_items || []).forEach((item) => {
      if (item.incoming_index !== undefined) {
        map.set(item.incoming_index, { type: 'match', ...item.match });
      }
    });
    (projectsComp.possible_duplicates || []).forEach((item) => {
      if (item.incoming_index !== undefined) {
        map.set(item.incoming_index, { type: 'possible_duplicate', ...item.match });
      }
    });
    return map;
  }, [projectsComp]);

  // Filtered skills based on category and search query
  const filteredSkills = useMemo(() => {
    const list = editedData.skills || [];
    return list.filter((skill) => {
      const name = (getSkillLabel(skill) || '').toLowerCase();
      const cat = (getSkillCategory(skill) || 'Other').toLowerCase();
      const matchesSearch = !skillSearch || name.includes(skillSearch.toLowerCase().trim());
      const matchesCat =
        selectedCategoryFilter === 'All' ||
        cat === selectedCategoryFilter.toLowerCase();
      return matchesSearch && matchesCat;
    });
  }, [editedData.skills, skillSearch, selectedCategoryFilter]);

  const newSkillsList = useMemo(() => {
    return filteredSkills.filter(
      (s) =>
        !existingProfileSkills.has(getSkillLabel(s).toLowerCase()) &&
        !possibleDuplicateSkills.has(getSkillLabel(s).toLowerCase())
    );
  }, [filteredSkills, existingProfileSkills, possibleDuplicateSkills]);

  const reviewSkillsList = useMemo(() => {
    return filteredSkills.filter((s) =>
      possibleDuplicateSkills.has(getSkillLabel(s).toLowerCase())
    );
  }, [filteredSkills, possibleDuplicateSkills]);

  const matchingSkillsList = useMemo(() => {
    return filteredSkills.filter((s) =>
      existingProfileSkills.has(getSkillLabel(s).toLowerCase())
    );
  }, [filteredSkills, existingProfileSkills]);

  // Early return if modal is closed or no resumeData — AFTER all hooks
  if (!isOpen || !resumeData) return null;

  const { resume_id, filename } = resumeData;
  const personalComp = comparison.personal_info || {};

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

      const correctionsList = [];
      if (rememberCorrections && resumeData?.extracted_data) {
        const orig = resumeData.extracted_data;
        // Collect skill corrections
        const origSkills = Array.isArray(orig.skills) ? orig.skills.map((s) => (typeof s === 'string' ? s : s.name)) : [];
        (editedData.skills || []).forEach((sk) => {
          if (!origSkills.includes(sk.name)) {
            correctionsList.push({
              field_name: 'skill',
              original_value: origSkills[0] || sk.name,
              corrected_value: sk.name,
              category: sk.category || 'skill',
            });
          }
        });
        // Collect duplicate decisions as corrections
        Object.entries(itemDecisions).forEach(([key, decision]) => {
          correctionsList.push({
            field_name: key,
            original_value: key,
            corrected_value: decision,
            category: decision,
          });
        });
      }

      const res = await profileApi.applyExtractedData(resume_id, {
        sections: sectionsToApply,
        overwrite_existing: overwriteExisting,
        edited_data: editedData,
        item_decisions: itemDecisions,
        remember_corrections: correctionsList,
      });

      if (onApplied) {
        onApplied(res);
      }
      onClose();
    } catch (err) {
      const serverDetail = err?.data?.detail || err?.detail || err?.message;
      const displayMsg = typeof serverDetail === 'string'
        ? serverDetail
        : (Array.isArray(serverDetail)
          ? serverDetail.map((d) => d.msg || JSON.stringify(d)).join('; ')
          : JSON.stringify(serverDetail));
      setErrorMsg(displayMsg || 'Failed to apply extracted data to profile.');
    } finally {
      setApplying(false);
    }
  };

  const handleRemoveSkill = (skillNameToRemove) => {
    setEditedData((prev) => ({
      ...prev,
      skills: prev.skills.filter(
        (s) => s.name.toLowerCase() !== skillNameToRemove.toLowerCase()
      ),
    }));
  };

  const handleAddSkill = (e) => {
    e?.preventDefault();
    const trimmed = newSkillInput.trim();
    if (!trimmed) return;

    const exists = editedData.skills.some(
      (s) => s.name.toLowerCase() === trimmed.toLowerCase()
    );
    if (exists) {
      setErrorMsg(`Skill "${trimmed}" is already in the list.`);
      return;
    }

    setEditedData((prev) => ({
      ...prev,
      skills: [
        ...prev.skills,
        {
          name: trimmed,
          category: newSkillCategory || 'Other',
          source_evidence: 'Manually added by candidate during review',
        },
      ],
    }));
    setNewSkillInput('');
    setErrorMsg('');
  };

  const setItemDecision = (key, decision) => {
    setItemDecisions((prev) => ({
      ...prev,
      [key]: decision,
    }));
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

  const customSections = editedData.custom_sections || {};
  const customSectionKeys = Object.keys(customSections);

  const tabs = [
    { id: 'personal', label: 'Contact Info', icon: User, key: 'personal_info' },
    {
      id: 'skills',
      label: `Skills (${editedData.skills.length})`,
      icon: Wrench,
      key: 'skills',
    },
    {
      id: 'projects',
      label: `Projects (${editedData.projects.length})`,
      icon: FolderGit2,
      key: 'projects',
    },
    {
      id: 'experience',
      label: `Experience (${editedData.experience.length})`,
      icon: Briefcase,
      key: 'experience',
    },
    {
      id: 'education',
      label: `Education (${editedData.education.length})`,
      icon: GraduationCap,
      key: 'education',
    },
    {
      id: 'certifications',
      label: `Certifications (${editedData.certifications.length})`,
      icon: Award,
      key: 'certifications',
    },
  ];

  if (customSectionKeys.length > 0) {
    tabs.push({
      id: 'custom_sections',
      label: `Preserved Sections (${customSectionKeys.length})`,
      icon: FileText,
      key: 'custom_sections',
    });
  }

  const currentTabIndex = tabs.findIndex((t) => t.id === activeTab);
  const handlePrevTab = () => {
    if (currentTabIndex > 0) {
      setActiveTab(tabs[currentTabIndex - 1].id);
    }
  };
  const handleNextTab = () => {
    if (currentTabIndex < tabs.length - 1) {
      setActiveTab(tabs[currentTabIndex + 1].id);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2.5 sm:p-4 bg-charcoal/60 backdrop-blur-xs font-mono">
      <div className="bg-white border-2 border-charcoal shadow-brutal max-w-4xl w-full max-h-[92vh] sm:max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-150">
        {/* Modal Header */}
        <div className="p-3 sm:p-4 border-b-2 border-charcoal bg-cream flex items-center justify-between">
          <div className="flex items-center space-x-2 min-w-0 pr-2">
            <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-coral shrink-0" />
            <div className="min-w-0">
              <h2 className="text-sm sm:text-base font-bold text-charcoal tracking-tight truncate">
                Review Extracted Resume Data
              </h2>
              <p className="text-[11px] sm:text-xs text-charcoal-muted truncate max-w-xs sm:max-w-md">
                Source Document: <span className="font-semibold text-charcoal">{filename}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 border border-charcoal hover:bg-white text-charcoal transition-colors cursor-pointer shrink-0"
            title="Close review modal"
          >
            <X className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>
        </div>

        {/* Modal Tabs Bar */}
        <div className="flex border-b border-cream-border bg-cream/40 overflow-x-auto scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isSelected = selectedSections[tab.key];
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2.5 px-3 text-xs font-bold border-b-2 whitespace-nowrap flex items-center space-x-1.5 transition-colors cursor-pointer ${
                  isActive
                    ? 'border-coral text-charcoal bg-white'
                    : 'border-transparent text-charcoal-muted hover:text-charcoal hover:bg-white/50'
                }`}
              >
                <input
                  type="checkbox"
                  checked={!!isSelected}
                  onChange={(e) => {
                    e.stopPropagation();
                    toggleSection(tab.key);
                  }}
                  className="rounded-none border-charcoal accent-coral h-3.5 w-3.5 mr-1 cursor-pointer"
                  title="Check to include section in Profile application"
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
            <div className="p-3 bg-rose-50 border border-rose-500 text-rose-900 text-xs flex items-center justify-between">
              <span>{errorMsg}</span>
              <button
                onClick={() => setErrorMsg('')}
                className="text-rose-700 hover:text-rose-900 ml-2 font-bold cursor-pointer"
              >
                ×
              </button>
            </div>
          )}

          {/* TAB 1: Contact Information */}
          {activeTab === 'personal' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border flex justify-between items-center">
                  <span>Contact & Personal Details</span>
                  <span className="text-[11px] font-normal lowercase">
                    Section included: {selectedSections.personal_info ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    { key: 'name', label: 'Full Name' },
                    { key: 'email', label: 'Email Address' },
                    { key: 'headline', label: 'Headline / Role' },
                    { key: 'phone', label: 'Phone Number' },
                    { key: 'location', label: 'Location' },
                    { key: 'linkedin_url', label: 'LinkedIn Profile' },
                    { key: 'github_url', label: 'GitHub Profile' },
                    { key: 'portfolio_url', label: 'Portfolio URL' },
                  ].map(({ key, label }) => {
                    const item = personalComp[key] || {
                      current: '',
                      extracted: editedData.personal_info[key] || '',
                      status: editedData.personal_info[key] ? 'new' : 'empty',
                    };
                    return (
                      <div key={key} className="p-3 border border-charcoal bg-cream/30 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-charcoal">{label}</span>
                          {getStatusBadge(item.status)}
                        </div>
                        <div className="text-[11px]">
                          <div className="text-charcoal-muted">Extracted Value:</div>
                          <input
                            type="text"
                            value={editedData.personal_info[key] || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => ({
                                ...prev,
                                personal_info: {
                                  ...prev.personal_info,
                                  [key]: val,
                                },
                              }));
                            }}
                            className="w-full mt-1 px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal focus:outline-none focus:ring-1 focus:ring-coral"
                            placeholder="None detected"
                          />
                        </div>
                        <div className="text-[11px] pt-1 border-t border-cream-border">
                          <div className="text-charcoal-muted">Current Profile:</div>
                          <div className="text-charcoal break-all font-sans">
                            {item.current || <em className="text-gray-400">Empty</em>}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="p-3 border border-charcoal bg-cream/30 space-y-1.5">
                  <div className="font-bold text-charcoal">Professional Summary</div>
                  <textarea
                    rows={3}
                    value={editedData.summary || ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      setEditedData((prev) => ({ ...prev, summary: val }));
                    }}
                    placeholder="Candidate summary detected from resume..."
                    className="w-full p-2 bg-white border border-charcoal text-xs font-sans text-charcoal focus:outline-none focus:ring-1 focus:ring-coral"
                  />
                </div>
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 2: Skills (Review, Search, Filter, Add, and Remove) */}
          {activeTab === 'skills' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-cream-border">
                  <div className="font-bold uppercase tracking-wider text-charcoal-muted">
                    Extracted Skills ({editedData.skills.length} Total)
                  </div>
                  <div className="text-[11px] text-charcoal-muted">
                    {newSkillsList.length} new · {matchingSkillsList.length} in profile ·{' '}
                    {reviewSkillsList.length} needs review
                  </div>
                </div>

                {/* Search & Filter Toolbar */}
                <div className="space-y-2.5 bg-cream/20 p-3 border border-charcoal">
                  <div className="flex flex-col sm:flex-row gap-2">
                    <div className="relative flex-1">
                      <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-charcoal-muted" />
                      <input
                        type="text"
                        value={skillSearch}
                        onChange={(e) => setSkillSearch(e.target.value)}
                        placeholder="Search detected skills..."
                        className="w-full pl-8 pr-3 py-1.5 bg-white border border-charcoal text-xs font-mono text-charcoal placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-coral"
                      />
                      {skillSearch && (
                        <button
                          onClick={() => setSkillSearch('')}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-charcoal-muted hover:text-charcoal font-bold cursor-pointer"
                        >
                          ×
                        </button>
                      )}
                    </div>

                    {/* Add Missing Skill Inline Form */}
                    <form onSubmit={handleAddSkill} className="flex gap-1.5 items-center">
                      <input
                        type="text"
                        value={newSkillInput}
                        onChange={(e) => setNewSkillInput(e.target.value)}
                        placeholder="Add missing skill..."
                        className="px-2 py-1.5 bg-white border border-charcoal text-xs font-mono text-charcoal placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-coral w-36 sm:w-44"
                      />
                      <select
                        value={newSkillCategory}
                        onChange={(e) => setNewSkillCategory(e.target.value)}
                        className="px-2 py-1.5 bg-white border border-charcoal text-xs font-mono text-charcoal focus:outline-none focus:ring-1 focus:ring-coral"
                      >
                        {SKILL_CATEGORIES.filter((c) => c !== 'All').map((cat) => (
                          <option key={cat} value={cat}>
                            {cat}
                          </option>
                        ))}
                      </select>
                      <button
                        type="submit"
                        className="btn-primary text-xs py-1.5 px-2.5 flex items-center space-x-1 cursor-pointer shrink-0"
                        title="Add skill to extraction review"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        <span>Add</span>
                      </button>
                    </form>
                  </div>

                  {/* Category Filter Chips */}
                  <div className="flex flex-wrap gap-1 pt-1">
                    {SKILL_CATEGORIES.map((cat) => {
                      const count =
                        cat === 'All'
                          ? editedData.skills.length
                          : editedData.skills.filter(
                              (s) => s.category.toLowerCase() === cat.toLowerCase()
                            ).length;
                      const isSelected = selectedCategoryFilter === cat;
                      return (
                        <button
                          key={cat}
                          type="button"
                          onClick={() => setSelectedCategoryFilter(cat)}
                          className={`text-[10px] px-2 py-0.5 border transition-colors cursor-pointer ${
                            isSelected
                              ? 'bg-charcoal text-white border-charcoal font-bold'
                              : 'bg-white text-charcoal-muted border-charcoal hover:bg-cream hover:text-charcoal'
                          }`}
                        >
                          {cat} ({count})
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Skills Rendering Groups */}
                {filteredSkills.length === 0 ? (
                  <div className="p-6 text-center border border-dashed border-charcoal-muted/50 bg-cream/10 space-y-1">
                    <p className="font-bold text-charcoal">No skills match the selected filter</p>
                    <p className="text-charcoal-muted text-[11px]">
                      {editedData.skills.length === 0
                        ? 'No skills were detected from this document. Use the input above to add skills.'
                        : 'Try searching for a different keyword or selecting "All" categories.'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Needs Review / Possible Duplicate Skills */}
                    {reviewSkillsList.length > 0 && (
                      <div className="p-3 bg-amber-50 border border-amber-400 space-y-2">
                        <div className="font-bold text-amber-900 flex items-center space-x-1.5">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
                          <span>Needs Review (Possible duplicate or alias with existing profile skill)</span>
                        </div>
                        <div className="space-y-2">
                          {reviewSkillsList.map((skill, idx) => {
                            const sName = getSkillLabel(skill);
                            const dupInfo = possibleDuplicateSkills.get(sName.toLowerCase()) || {};
                            const decision = itemDecisions[`skills:${sName.toLowerCase()}`] || 'keep_existing';
                            return (
                              <div
                                key={`review-${sName}-${idx}`}
                                className="p-2 bg-white border border-amber-300 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                              >
                                <div>
                                  <span className="font-bold text-charcoal">{sName}</span>
                                  <span className="text-charcoal-muted ml-2 text-[11px]">
                                    (Similar to: <strong className="text-amber-800">{dupInfo.matched_with}</strong>, {dupInfo.relationship})
                                  </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <button
                                    type="button"
                                    onClick={() => setItemDecision(`skills:${sName.toLowerCase()}`, 'keep_existing')}
                                    className={`text-[10px] px-2 py-0.5 border cursor-pointer ${
                                      decision === 'keep_existing'
                                        ? 'bg-charcoal text-white font-bold'
                                        : 'bg-white text-charcoal border-charcoal'
                                    }`}
                                  >
                                    Keep Existing
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => setItemDecision(`skills:${sName.toLowerCase()}`, 'replace_with_new')}
                                    className={`text-[10px] px-2 py-0.5 border cursor-pointer ${
                                      decision === 'replace_with_new'
                                        ? 'bg-charcoal text-white font-bold'
                                        : 'bg-white text-charcoal border-charcoal'
                                    }`}
                                  >
                                    Replace
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => setItemDecision(`skills:${sName.toLowerCase()}`, 'discard')}
                                    className={`text-[10px] px-2 py-0.5 border cursor-pointer ${
                                      decision === 'discard'
                                        ? 'bg-rose-700 text-white font-bold'
                                        : 'bg-white text-rose-700 border-rose-300'
                                    }`}
                                  >
                                    Discard
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Group 1: New Skills to Add */}
                    {newSkillsList.length > 0 && (
                      <div>
                        <div className="font-bold text-charcoal mb-2 flex items-center space-x-1.5">
                          <span className="w-2 h-2 bg-emerald-600 inline-block" />
                          <span>New Skills (Will be added to Candidate Profile):</span>
                          <span className="text-[11px] font-normal text-emerald-800">
                            ({newSkillsList.length})
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {newSkillsList.map((skill, idx) => {
                            const isUncat =
                              !skill.category ||
                              skill.category.toLowerCase() === 'other';
                            return (
                              <span
                                key={`${skill.name}-${idx}`}
                                className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 font-semibold inline-flex items-center gap-1.5 pl-2 pr-1.5 py-1"
                                title={skill.source_evidence ? `Evidence: ${skill.source_evidence}` : ''}
                              >
                                <span>+ {skill.name}</span>
                                {skill.category && (
                                  <span
                                    className={`text-[9px] px-1 py-0.2 rounded font-mono font-normal border ${
                                      isUncat
                                        ? 'bg-blue-50 text-blue-800 border-blue-300'
                                        : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                                    }`}
                                  >
                                    {isUncat ? 'Uncategorized' : skill.category}
                                  </span>
                                )}
                                <button
                                  type="button"
                                  onClick={() => handleRemoveSkill(skill.name)}
                                  className="ml-1 text-emerald-700 hover:text-red-700 hover:bg-emerald-200/50 rounded p-0.5 transition-colors cursor-pointer"
                                  title={`Remove "${skill.name}" from review`}
                                >
                                  <X className="w-3 h-3" />
                                </button>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Group 2: Already in Profile */}
                    {matchingSkillsList.length > 0 && (
                      <div>
                        <div className="font-bold text-charcoal mb-2 flex items-center space-x-1.5">
                          <span className="w-2 h-2 bg-gray-400 inline-block" />
                          <span>Already Present in Profile:</span>
                          <span className="text-[11px] font-normal text-charcoal-muted">
                            ({matchingSkillsList.length})
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {matchingSkillsList.map((skill, idx) => (
                            <span
                              key={`${skill.name}-${idx}`}
                              className="badge-tag bg-gray-100 text-gray-700 border-gray-400 inline-flex items-center gap-1.5 pl-2 pr-1.5 py-1"
                              title={skill.source_evidence ? `Evidence: ${skill.source_evidence}` : ''}
                            >
                              <span>✓ {skill.name}</span>
                              {skill.category && (
                                <span className="text-[9px] bg-gray-200 text-gray-700 px-1 py-0.2 rounded font-mono font-normal border border-gray-300">
                                  {skill.category}
                                </span>
                              )}
                              <button
                                type="button"
                                onClick={() => handleRemoveSkill(skill.name)}
                                className="ml-1 text-gray-500 hover:text-red-700 hover:bg-gray-200 rounded p-0.5 transition-colors cursor-pointer"
                                title={`Remove "${skill.name}" from review`}
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 3: Projects (Full Editing + Duplicate Consent Resolution) */}
          {activeTab === 'projects' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border flex justify-between items-center">
                  <span>Extracted Projects ({editedData.projects.length})</span>
                  <span className="text-[11px] font-normal text-charcoal-muted">
                    Edit project attributes or resolve duplicate conflicts below
                  </span>
                </div>
                {editedData.projects.length > 0 ? (
                  editedData.projects.map((proj, idx) => {
                    const matchInfo = projectMatchesByIndex.get(idx);
                    const decision = itemDecisions[`projects:${idx}`] || (matchInfo ? 'keep_existing' : 'replace_with_new');

                    return (
                      <div key={idx} className="p-4 border-2 border-charcoal bg-cream/20 space-y-3">
                        {/* Duplicate Alert Card if matched */}
                        {matchInfo && (
                          <div className="p-3 border-2 border-amber-500 bg-amber-50/70 space-y-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-1.5 font-bold text-amber-900">
                                <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
                                <span>
                                  {matchInfo.type === 'same'
                                    ? 'Matching Profile Project Detected'
                                    : 'Possible Duplicate Project Detected'}
                                </span>
                              </div>
                              <span className="text-[10px] bg-amber-200 text-amber-900 px-1.5 py-0.5 font-bold border border-amber-400">
                                {matchInfo.reason || 'Existing profile project matches'}
                              </span>
                            </div>
                            <div className="text-[11px] text-amber-900">
                              Matched with profile project:{' '}
                              <strong className="text-charcoal">{matchInfo.existing_title}</strong>
                            </div>

                            {/* 4 Candidate Decision Choices */}
                            <div className="pt-1 border-t border-amber-300">
                              <div className="font-bold text-[11px] text-amber-950 mb-1">
                                Choose resolution for this project:
                              </div>
                              <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                                {[
                                  { key: 'keep_existing', label: 'Keep Existing', desc: 'Retain profile version' },
                                  { key: 'replace_with_new', label: 'Replace with New', desc: 'Overwrite profile' },
                                  { key: 'save_separate', label: 'Save as Separate', desc: 'Keep both projects' },
                                  { key: 'discard', label: 'Discard', desc: 'Do not import' },
                                ].map((choice) => (
                                  <button
                                    key={choice.key}
                                    type="button"
                                    onClick={() => setItemDecision(`projects:${idx}`, choice.key)}
                                    className={`p-1.5 text-left border text-[11px] cursor-pointer transition-colors ${
                                      decision === choice.key
                                        ? 'bg-charcoal text-white border-charcoal font-bold'
                                        : 'bg-white text-charcoal border-charcoal hover:bg-cream'
                                    }`}
                                  >
                                    <div className="font-bold">{choice.label}</div>
                                    <div className="text-[9px] opacity-80">{choice.desc}</div>
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Editable Project Fields */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                          <div>
                            <label className="font-bold text-charcoal block mb-0.5">Project Title</label>
                            <input
                              type="text"
                              value={proj.title || ''}
                              onChange={(e) => {
                                const val = e.target.value;
                                setEditedData((prev) => {
                                  const list = [...prev.projects];
                                  list[idx] = { ...list[idx], title: val };
                                  return { ...prev, projects: list };
                                });
                              }}
                              className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                            />
                          </div>

                          <div>
                            <label className="font-bold text-charcoal block mb-0.5">Role / Contribution</label>
                            <input
                              type="text"
                              value={proj.role || ''}
                              onChange={(e) => {
                                const val = e.target.value;
                                setEditedData((prev) => {
                                  const list = [...prev.projects];
                                  list[idx] = { ...list[idx], role: val };
                                  return { ...prev, projects: list };
                                });
                              }}
                              placeholder="e.g. Lead Developer, Solo Contributor"
                              className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                            />
                          </div>

                          <div className="grid grid-cols-2 gap-1.5">
                            <div>
                              <label className="font-bold text-charcoal block mb-0.5">Start Date</label>
                              <input
                                type="text"
                                value={proj.start_date || ''}
                                onChange={(e) => {
                                  const val = e.target.value;
                                  setEditedData((prev) => {
                                    const list = [...prev.projects];
                                    list[idx] = { ...list[idx], start_date: val };
                                    return { ...prev, projects: list };
                                  });
                                }}
                                placeholder="e.g. Jan 2024"
                                className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                              />
                            </div>
                            <div>
                              <label className="font-bold text-charcoal block mb-0.5">End Date</label>
                              <input
                                type="text"
                                value={proj.end_date || ''}
                                onChange={(e) => {
                                  const val = e.target.value;
                                  setEditedData((prev) => {
                                    const list = [...prev.projects];
                                    list[idx] = { ...list[idx], end_date: val };
                                    return { ...prev, projects: list };
                                  });
                                }}
                                placeholder="e.g. Present"
                                className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                              />
                            </div>
                          </div>

                          <div>
                            <label className="font-bold text-charcoal block mb-0.5">GitHub URL</label>
                            <input
                              type="text"
                              value={proj.github_url || proj.url || ''}
                              onChange={(e) => {
                                const val = e.target.value;
                                setEditedData((prev) => {
                                  const list = [...prev.projects];
                                  list[idx] = { ...list[idx], github_url: val, url: val };
                                  return { ...prev, projects: list };
                                });
                              }}
                              placeholder="https://github.com/..."
                              className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                            />
                          </div>

                          <div>
                            <label className="font-bold text-charcoal block mb-0.5">Live Demo URL</label>
                            <input
                              type="text"
                              value={proj.live_url || ''}
                              onChange={(e) => {
                                const val = e.target.value;
                                setEditedData((prev) => {
                                  const list = [...prev.projects];
                                  list[idx] = { ...list[idx], live_url: val };
                                  return { ...prev, projects: list };
                                });
                              }}
                              placeholder="https://..."
                              className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">
                            Technologies (comma-separated)
                          </label>
                          <input
                            type="text"
                            value={
                              Array.isArray(proj.technologies)
                                ? proj.technologies.join(', ')
                                : proj.technologies || ''
                            }
                            onChange={(e) => {
                              const val = e.target.value;
                              const parsed = val.split(',').map((t) => t.trim()).filter(Boolean);
                              setEditedData((prev) => {
                                const list = [...prev.projects];
                                list[idx] = { ...list[idx], technologies: parsed };
                                return { ...prev, projects: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>

                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">
                            Bullet Points (one bullet per line)
                          </label>
                          <textarea
                            rows={3}
                            value={
                              Array.isArray(proj.bullets)
                                ? proj.bullets.join('\n')
                                : proj.bullets || ''
                            }
                            onChange={(e) => {
                              const val = e.target.value;
                              const parsed = val.split('\n').filter((l) => l.trim().length > 0);
                              setEditedData((prev) => {
                                const list = [...prev.projects];
                                list[idx] = { ...list[idx], bullets: parsed };
                                return { ...prev, projects: list };
                              });
                            }}
                            className="w-full p-2 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="p-6 text-center border border-dashed border-charcoal-muted/50 bg-cream/10 text-charcoal-muted">
                    No projects identified in this document.
                  </div>
                )}
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 4: Experience (Full Editing) */}
          {activeTab === 'experience' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                  Extracted Work Experience ({editedData.experience.length})
                </div>
                {editedData.experience.length > 0 ? (
                  editedData.experience.map((exp, idx) => (
                    <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-2">
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Role / Title</label>
                          <input
                            type="text"
                            value={exp.title || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], title: val };
                                return { ...prev, experience: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Company</label>
                          <input
                            type="text"
                            value={exp.company || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], company: val };
                                return { ...prev, experience: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Location</label>
                          <input
                            type="text"
                            value={exp.location || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], location: val };
                                return { ...prev, experience: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Start Date</label>
                          <input
                            type="text"
                            value={exp.start_date || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], start_date: val };
                                return { ...prev, experience: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">End Date</label>
                          <input
                            type="text"
                            value={exp.end_date || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], end_date: val };
                                return { ...prev, experience: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Technologies Used</label>
                          <input
                            type="text"
                            value={Array.isArray(exp.technologies) ? exp.technologies.join(', ') : exp.technologies || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              const parsed = val.split(',').map((t) => t.trim()).filter(Boolean);
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], technologies: parsed };
                                return { ...prev, experience: list };
                              });
                            }}
                            placeholder="e.g. Python, Docker, PostgreSQL"
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Company / Project URL</label>
                          <input
                            type="text"
                            value={exp.url || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.experience];
                                list[idx] = { ...list[idx], url: val };
                                return { ...prev, experience: list };
                              });
                            }}
                            placeholder="https://..."
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="font-bold text-charcoal block mb-0.5">
                          Bullets / Responsibilities (one per line)
                        </label>
                        <textarea
                          rows={3}
                          value={
                            Array.isArray(exp.bullets)
                              ? exp.bullets.join('\n')
                              : exp.bullets || ''
                          }
                          onChange={(e) => {
                            const val = e.target.value;
                            const parsed = val.split('\n').filter((l) => l.trim().length > 0);
                            setEditedData((prev) => {
                              const list = [...prev.experience];
                              list[idx] = { ...list[idx], bullets: parsed };
                              return { ...prev, experience: list };
                            });
                          }}
                          className="w-full p-2 bg-white border border-charcoal text-xs font-mono text-charcoal"
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center border border-dashed border-charcoal-muted/50 bg-cream/10 text-charcoal-muted">
                    No work experience entries detected in this document.
                  </div>
                )}
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 5: Education (Full Editing) */}
          {activeTab === 'education' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                  Extracted Education ({editedData.education.length})
                </div>
                {editedData.education.length > 0 ? (
                  editedData.education.map((edu, idx) => (
                    <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-2">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Degree / Qualification</label>
                          <input
                            type="text"
                            value={edu.degree || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.education];
                                list[idx] = { ...list[idx], degree: val };
                                return { ...prev, education: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Institution / University</label>
                          <input
                            type="text"
                            value={edu.institution || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.education];
                                list[idx] = { ...list[idx], institution: val };
                                return { ...prev, education: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Field of Study</label>
                          <input
                            type="text"
                            value={edu.field_of_study || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.education];
                                list[idx] = { ...list[idx], field_of_study: val };
                                return { ...prev, education: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Grade / Score</label>
                          <input
                            type="text"
                            value={edu.grade || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.education];
                                list[idx] = { ...list[idx], grade: val };
                                return { ...prev, education: list };
                              });
                            }}
                            placeholder="e.g. 3.8 / 85%"
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Grade Type</label>
                          <input
                            type="text"
                            value={edu.grade_type || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.education];
                                list[idx] = { ...list[idx], grade_type: val };
                                return { ...prev, education: list };
                              });
                            }}
                            placeholder="CGPA / Percentage"
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Dates / Year</label>
                          <input
                            type="text"
                            value={edu.end_date || edu.dates || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.education];
                                list[idx] = { ...list[idx], end_date: val, dates: val };
                                return { ...prev, education: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="font-bold text-charcoal block mb-0.5">Description / Honors</label>
                        <input
                          type="text"
                          value={edu.description || ''}
                          onChange={(e) => {
                            const val = e.target.value;
                            setEditedData((prev) => {
                              const list = [...prev.education];
                              list[idx] = { ...list[idx], description: val };
                              return { ...prev, education: list };
                            });
                          }}
                          placeholder="Dean's List, First Class with Distinction..."
                          className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center border border-dashed border-charcoal-muted/50 bg-cream/10 text-charcoal-muted">
                    No education entries detected.
                  </div>
                )}
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 6: Certifications (Full Editing) */}
          {activeTab === 'certifications' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border">
                  Extracted Certifications ({editedData.certifications.length})
                </div>
                {editedData.certifications.length > 0 ? (
                  editedData.certifications.map((cert, idx) => (
                    <div key={idx} className="p-3 border border-charcoal bg-cream/20 space-y-2">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Certification Name</label>
                          <input
                            type="text"
                            value={cert.name || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.certifications];
                                list[idx] = { ...list[idx], name: val };
                                return { ...prev, certifications: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Issuer</label>
                          <input
                            type="text"
                            value={cert.issuer || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.certifications];
                                list[idx] = { ...list[idx], issuer: val };
                                return { ...prev, certifications: list };
                              });
                            }}
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Issue Date</label>
                          <input
                            type="text"
                            value={cert.issue_date || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.certifications];
                                list[idx] = { ...list[idx], issue_date: val };
                                return { ...prev, certifications: list };
                              });
                            }}
                            placeholder="e.g. 2023"
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Expiry Date</label>
                          <input
                            type="text"
                            value={cert.expiry_date || cert.expiration_date || ''}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.certifications];
                                list[idx] = { ...list[idx], expiry_date: val, expiration_date: val };
                                return { ...prev, certifications: list };
                              });
                            }}
                            placeholder="e.g. 2026 or Never"
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-charcoal block mb-0.5">Item Type / Status</label>
                          <input
                            type="text"
                            value={cert.status_note || cert.item_type || 'certification'}
                            onChange={(e) => {
                              const val = e.target.value;
                              setEditedData((prev) => {
                                const list = [...prev.certifications];
                                list[idx] = { ...list[idx], status_note: val, item_type: val };
                                return { ...prev, certifications: list };
                              });
                            }}
                            placeholder="certification / license / active"
                            className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="font-bold text-charcoal block mb-0.5">Credential URL</label>
                        <input
                          type="text"
                          value={cert.credential_url || ''}
                          onChange={(e) => {
                            const val = e.target.value;
                            setEditedData((prev) => {
                              const list = [...prev.certifications];
                              list[idx] = { ...list[idx], credential_url: val };
                              return { ...prev, certifications: list };
                            });
                          }}
                          placeholder="https://..."
                          className="w-full px-2 py-1 bg-white border border-charcoal text-xs font-mono text-charcoal"
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center border border-dashed border-charcoal-muted/50 bg-cream/10 text-charcoal-muted">
                    No certifications detected.
                  </div>
                )}
              </div>
            </SectionErrorBoundary>
          )}

          {/* TAB 7: Preserved Custom Sections */}
          {activeTab === 'custom_sections' && (
            <SectionErrorBoundary>
              <div className="space-y-4 text-xs">
                <div className="font-bold uppercase tracking-wider text-charcoal-muted pb-1 border-b border-cream-border flex justify-between items-center">
                  <span>Preserved Custom Sections ({customSectionKeys.length})</span>
                  <span className="text-[11px] font-normal text-emerald-700">Captured without loss</span>
                </div>
                <div className="space-y-3">
                  {customSectionKeys.map((key) => (
                    <div key={key} className="p-3 border border-charcoal bg-cream/30 space-y-1.5">
                      <div className="font-bold text-charcoal flex items-center justify-between">
                        <span className="uppercase tracking-wide">{key}</span>
                        <span className="badge-tag bg-blue-50 text-blue-800 border-blue-600 text-[10px]">
                          Preserved Custom Section
                        </span>
                      </div>
                      <pre className="text-charcoal whitespace-pre-wrap font-sans text-xs bg-white p-2.5 border border-charcoal-muted/30 max-h-48 overflow-y-auto">
                        {typeof customSections[key] === 'string'
                          ? customSections[key]
                          : JSON.stringify(customSections[key], null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            </SectionErrorBoundary>
          )}
        </div>

        {/* Modal Stepper & Action Controls */}
        <div className="p-3 sm:p-4 border-t-2 border-charcoal bg-cream flex flex-col sm:flex-row items-center justify-between gap-3 overflow-y-auto">
          <div className="flex items-center justify-between sm:justify-start space-x-2 w-full sm:w-auto">
            <button
              onClick={handlePrevTab}
              disabled={currentTabIndex <= 0}
              className={`btn-secondary text-xs py-1.5 px-2.5 flex items-center space-x-1 ${
                currentTabIndex <= 0 ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>
            <span className="text-[11px] text-charcoal-muted px-1">
              Step {currentTabIndex + 1} of {tabs.length}
            </span>
            <button
              onClick={handleNextTab}
              disabled={currentTabIndex >= tabs.length - 1}
              className={`btn-secondary text-xs py-1.5 px-2.5 flex items-center space-x-1 ${
                currentTabIndex >= tabs.length - 1 ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2.5 sm:gap-3 w-full sm:w-auto justify-end">
            <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
              <label className="flex items-center space-x-1.5 text-xs text-charcoal cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberCorrections}
                  onChange={(e) => setRememberCorrections(e.target.checked)}
                  className="rounded-none border-charcoal accent-coral h-4 w-4 cursor-pointer"
                />
                <span title="Persists any corrections or duplicate resolutions made in this review to automatically guide future resume uploads.">
                  Remember corrections
                </span>
              </label>

              <label className="flex items-center space-x-1.5 text-xs text-charcoal cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={overwriteExisting}
                  onChange={(e) => setOverwriteExisting(e.target.checked)}
                  className="rounded-none border-charcoal accent-coral h-4 w-4 cursor-pointer"
                />
                <span title="When unchecked, only fills empty fields and adds new items without touching your existing profile entries.">
                  Overwrite existing
                </span>
              </label>
            </div>

            <div className="flex items-center space-x-2 w-full sm:w-auto justify-end">
              <button
                onClick={onClose}
                className="btn-secondary text-xs py-2 px-3 cursor-pointer flex-1 sm:flex-initial"
              >
                Cancel
              </button>
              <button
                onClick={handleApply}
                disabled={applying}
                className="btn-primary text-xs py-2 px-4 flex items-center justify-center space-x-1.5 cursor-pointer flex-1 sm:flex-initial"
              >
                {applying ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Applying...</span>
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
    </div>
  );
}
