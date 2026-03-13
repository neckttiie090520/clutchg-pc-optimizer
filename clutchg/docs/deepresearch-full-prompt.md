# Project Context: ClutchG

You are working on the ClutchG project.

ClutchG is a Windows PC Optimizer focused on safe, evidence-based tweaks only. It uses batch scripts for optimization and a CustomTkinter GUI. The project is bilingual (EN/TH) and includes a complete Help & Documentation system with tooltips, inline help boxes, a help view, and a welcome tutorial overlay.

Current status:
- Version: 1.0.0
- Phase 9 complete: Help & Information System
- Next phase: Testing + Brainstorming enhancements

Key modules:
- core: system detection (PassMark), profiles (SAFE/COMPETITIVE/EXTREME), backup/restore, help manager
- gui: minimal UI, navigation, help view, tooltips, inline help, welcome overlay
- data: help_content.json (EN/TH)
- batch: optimization scripts (power, services, bcdedit, network)

Safety constraints:
- Do NOT disable Defender, UAC, DEP/ASLR/CFG, or Windows Update.
- All tweaks must be reversible and logged.
- Always create backups before applying changes.

Mission:
- Be practical, small-team friendly
- Avoid over-engineering
- Keep ideas realistic and safe

---

# Deep Research Prompt: Enhancement Ideas

You are a research analyst. Perform deep research to generate actionable, evidence-backed enhancement ideas for the ClutchG Windows PC Optimizer app. Cover all dimensions: UX/UI, help/documentation, performance benchmarking, safety/rollback, testing & QA, power-user features, integrations, platform expansion, and product strategy.

Research Requirements:
1) Identify 3–5 best-in-class tools or apps in each category (performance tools, Windows optimization suites, help systems, benchmarking tools, recovery/rollback tools, system monitoring tools).
2) Extract specific features and UX patterns that ClutchG can adopt safely.
3) For each idea, include:
   - Problem it solves
   - Implementation approach (high level)
   - Risk/safety concerns
   - Effort estimate (Low/Med/High)
   - Expected impact
4) Include a section on "Do NOT do" ideas (unsafe / misleading / placebo).
5) Provide at least 2 realistic experiments to validate each major idea (A/B test, user testing, benchmark comparisons).
6) Summarize with a prioritized roadmap (Phase 10/11/12) using Impact vs Effort.

Output Format:
- Executive summary (short)
- Category breakdown
- Idea table (problem → solution → risk → effort → impact)
- Validation experiments
- "Do NOT do" list
- Final roadmap

Constraints:
- Focus on ideas feasible for a small team.
- Avoid speculative claims; cite sources when possible.
- Do not propose security-damaging tweaks.
