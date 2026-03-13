# ClutchG Phase 10 Handoff (Testing + Idea Jam)

Date: 2026-02-02
Owner: Codex
Scope: Testing strategy, pre-research idea brainstorming, and next-step priorities.

## 1) Executive Summary
ClutchG’s Help system is functional and now includes lightweight UX enhancements (search, quick links, live language refresh, Thai font fallback). The next phase should emphasize practical testing across real Windows environments, confirm safety claims, and prioritize a small set of high-impact UX ideas before deeper research.

## 2) What Changed Since Last Handoff
- Help view now refreshes immediately after language change.
- Help search added (sidebar search + results, highlighted query, natural snippet trimming).
- Quick Links section added to Help view.
- Thai font fallback for Help view (Tahoma when language = th).
- Ctrl+F focuses Help search.

Note: These are UX improvements only; no batch scripts or profile logic were changed.

## 3) Test Strategy (Pre-Research)
Goal: Validate safety, language consistency, and UX flow before deeper optimization research.

### A) Core Startup & Navigation
- Launch app (Admin / non-Admin) -> check error handling.
- Verify sidebar icons and view switching.
- First-time Welcome overlay appears only once.

### B) Help System (High Priority)
- Language switch (EN/TH) while Help view is open -> content updates immediately.
- Search behavior:
  - Search with common terms ("backup", "safe", "bcdedit", Thai terms).
  - Ctrl+F focuses input, highlights all text.
  - Clear button returns to previous topic.
- Quick Links:
  - All 6 buttons render and navigate correctly.

### C) Localization & Font Safety
- Thai content rendering: verify no garbled characters.
- Check whether other views render Thai correctly (Settings, Inline Help).

### D) Content Accuracy Checks
- Compare help text against actual script behavior.
- Confirm risk level labels and warnings match profiles.
- Ensure help text does not contradict safety rules (Defender/UAC/Updates).

### E) Robustness / Edge Cases
- Missing or corrupted help_content.json -> app should not crash.
- Unknown topic id -> safe no-op.
- Empty search -> return to current topic.

### F) Windows Compatibility
- Win10 22H2 / Win11 23H2+ smoke tests:
  - Backup creation and restore
  - Profile application
  - Script execution and logs

## 4) Pre-Research Idea Brainstorm (UX + Value)
These ideas are intentionally “pre-research” and can be validated by quick prototyping or user feedback.

### UX / Product Clarity
- “Before & After” mini report (score + toggles applied).
- Recent activity panel (last profile, last script run, last backup).
- Contextual help bubble on risky actions (EXTREME profile, BCDEdit).
- “Safe Mode” banner on first run (emphasize SAFE profile).

### Help & Guidance
- Context-sensitive help: open relevant topic from each view.
- “FAQ” topic based on top 5 recurring issues.
- In-app glossary for technical terms (BCDEdit, registry, telemetry).

### Performance & Transparency
- “What changed?” diff report after running profile.
- Optional log viewer in Help view (read-only).
- System health check (free disk, restore points, admin status).

### Power User / Advanced
- Custom profile builder (select from script list).
- Profile comparison side-by-side (risk, performance, reversibility).

## 5) Suggested Phase 10 Scope (Small, High-Impact)
1) Focused testing (Help/Language/Backup). 
2) Minimal “Recent Activity” UI card (read from log). 
3) Help/FAQ + Glossary drafts.

## 6) Risk Notes
- Thai fonts: Tahoma improves Help view; other views may still need fallback.
- Search: text-only; highlight uses brackets to avoid complex rendering.
- Ensure no changes to security guidance (Defender/UAC/Updates).

## 7) Hand-off Checklist
- [ ] Complete Win10 + Win11 smoke tests
- [ ] Verify language persists across restarts
- [ ] Validate Help content vs actual script behavior
- [ ] Confirm Welcome overlay appears only once
- [ ] Confirm backups restore correctly

## 8) Next Owner Quick Start
1) Run app as Admin: `python clutchg\src\app_minimal.py`
2) Test Help view and language switching first.
3) Run SAFE profile + backup/restore for sanity.

---
If you want this expanded into a full QA plan, convert section 3 into a checklist doc per view.
