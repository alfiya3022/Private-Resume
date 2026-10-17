# PrivateResume - Design Specification

## Status
LOCKED visual and structural direction.

## Primary visual inspiration
Use the supplied reference image as the primary inspiration for design language, layout aesthetic, colors, typography, borders, spacing, cards, buttons, and overall visual personality. Do not copy the reference literally and do not reuse its content.

## Product areas
There are four top-level areas only:
1. Auth
2. Profile
3. Workspace
4. Applications

These are product/navigation areas, not the total number of screens.

## Workspace interaction model
Workspace is one cohesive progressive workflow. Stages replace the current Workspace view rather than appearing as one giant scrolling page:

Add Inputs -> Analyze -> Match -> Tailor -> Generate/Validate

Individual stages may scroll internally when information density requires it.

## Required primary views
- Login / Sign Up
- Profile Workspace
- Workspace - Initial State
- Workspace - Job Analysis State
- Workspace - Tailored Resume Editing State
- Workspace - Final Resume + Validation State
- Application Tracker

These are not seven separate top-level navigation items.

## Profile
One unified workspace with tabs or clearly separated sections:
Personal, Education, Experience, Projects, Skills, Certifications, Activities, Achievements, Resume Template.

Resume Template supports a ZIP package containing main.tex, section files, assets, and other supporting files. Provide Upload, Current Template, Replace Template, and status.

## Workspace initial state
Show current master resume and a large JD input area. Optional job metadata: company, title, location, URL, salary/CTC. Primary CTA: Generate Analysis.

## Job analysis state
Show job requirements including required/preferred skills, languages, frameworks, databases, cloud/tools, responsibilities, qualifications, experience, and soft skills.

## Match state
Separate:
- Matched skills
- Weakly represented skills
- Missing skills
- Unsupported claims

Missing does not mean the user should add the skill. Unsupported claims must visually communicate that they should not be invented.

Provide evidence drawers/expanders that connect a requirement to candidate evidence.

## Tailored resume state
Show structured editable sections such as Summary, Skills, Experience, Projects, Education, Certifications, Activities, Achievements. Each section supports Edit and Ask AI. Candidate can accept, reject, or manually modify suggestions.

## Evidence UX
Show concise explanations such as "Selected because this skill appears in your project experience and matches a required job skill." Do not expose internal chain-of-thought.

## Versioning
Support Draft v1, v2, v3, Final style version history. Prefer a dropdown, compact history panel, or timeline over a large history screen. Historical versions are immutable.

## Final generation
Approved structured resume content -> user's LaTeX template -> compiler -> PDF -> validation.

## Validation
Validation panel should clearly separate success, warning, and error states. Example checks: PDF generated, text extractable, required sections present, contact details detected, no obvious placeholder text, standard headings, content validated, no unsupported claims.

## Match metric language
Use "Estimated Job Match" or equivalent. Never call it an ATS score. ATS Compatibility is a separate concrete check area.

## Applications
Dedicated tracker using table/cards with company, role, location, date applied, status, estimated match, and resume version. Application detail can open in a drawer/panel.

## Navigation
PrivateResume logo + Profile + Workspace + Applications. Settings are accessed from the user/avatar menu.

## Visual language
- Warm cream/off-white base
- Charcoal/black typography
- Thin dark borders
- Subtle outlined cards
- Strong typography hierarchy
- Coral/red primary action color
- Small pastel accents for statuses
- Generous whitespace
- Editorial / modern neo-brutalist influence
- Polished SaaS quality

## Avoid
- Generic corporate dashboard appearance
- Neon cyberpunk styling
- Excessive gradients
- Glowing AI effects
- Gaming aesthetics
- Generic job-board appearance

## UX principles
1. One obvious next action at each stage.
2. Do not overwhelm the user with AI output.
3. Keep related information grouped.
4. Preserve candidate control.
5. Make recommendations understandable.
6. Make evidence easy to inspect.
7. Keep version history understandable.
8. Avoid unnecessary screens.
9. Prefer progressive disclosure.
10. Do not make the product look like an AI gimmick.

## Accessibility
Readable contrast, visible focus states, keyboard-friendly controls, understandable status indicators, non-color-only status communication, clear labels, and clear validation messaging.

## Responsive behavior
Desktop-first because resume editing is information dense, with deliberate tablet/mobile layouts rather than simply shrinking the desktop UI.
