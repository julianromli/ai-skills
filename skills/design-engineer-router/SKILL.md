---
name: design-engineer-router
description: >-
  Use at the start of EVERY design, UI/UX, frontend, motion, copy-on-screen,
  component, review, or product-idea task, even when the user names no skill.
  Picks the relevant emil-* skills (Emil Kowalski design engineering pack) and
  runs their checks without being asked. Jakub Krehel skills are a second opinion.
---
# Design engineer router

The user never has to name a skill. You pick the skills yourself, every time, and say in one line which ones you used.

## Requirements
This skill only routes. It does not include the emil-* skills. Install them in your agent's skills folder first (for example `~/.cursor/skills/`, `~/.claude/skills/`, or `.claude/skills/` in a project). If a named skill is not installed, skip it and say so in one line.

## How to pick
1. Name the **phase** and the **material** of the ask. When two skills look equal, read `emil-ask-emil` for the full routing table.
2. Load the **1 to 3** most relevant emil skills for this ask. Not five: more skills dilute the craft bar. Read each skill's SKILL.md and its companion files, and follow its exact values.
3. Run the **proactive passes** below on your own, without asking.
4. In the reply, add one short line: which skills you used and why.

## Map of the emil skills
- **Undecided / options:** `emil-prototype` (3-5 versions behind a picker). Stuck on a vibe: `emil-get-creative`.
- **Foundation of any screen:** `emil-design-foundations` (hierarchy, spacing, states, microcopy), `emil-typography`, `emil-color` (OKLCH, contrast).
- **Building pieces:** components `emil-component-design`; forms, inputs, buttons `emil-forms-and-inputs`; cards, shadows, borders, gradients, dark mode `emil-surfaces`; landing, blog, docs, changelog `emil-marketing-pages`; motion `emil-animations` + `emil-design-eng`; animation inspector questions `emil-ask-lapse`.
- **Refining:** feels unfinished `emil-ui-polish`; phone feel `emil-mobile-native`; touch, keyboard, screen reader `emil-touch-and-accessibility`; slow or janky `emil-performance`.
- **Checking:** code review `emil-ui-review`; before launch `emil-prep-for-prod`.
- **De-slop:** visuals `emil-unslop-design`; code `emil-unslop-code`; any text a person reads `emil-unslop-writing`.
- **Words:** design term lookup `emil-design-vocabulary`; frontend term lookup `emil-engineering-vocabulary`.
- **Product:** should this exist, what to build first `emil-product-thinking`; suggest the right tool for a goal `emil-build-a-tool`.
- **Docs and skills:** design system docs for AI (DESIGN.md, AGENTS.md) `emil-design-system-docs`; writing a skill file `emil-writing-skills`; turning someone's public work into a skill `emil-borrow-a-brain`.

## Proactive passes (always, unasked)
- After you build or change any UI: run `emil-ui-review` on your own output, then `emil-unslop-design`. Fix what they find before you deliver.
- If the UI has forms or inputs: also check against `emil-forms-and-inputs`.
- If it runs on mobile or touch: also check `emil-touch-and-accessibility` (44px targets, 16px inputs, focus).
- If you add motion: check `emil-animations` (duration, easing, reduced motion).
- If you write UI copy, README, or docs: run `emil-unslop-writing`.
- If you write code: run `emil-unslop-code` before you hand it over.
- If the user says ship, launch, deploy, or go live: run `emil-prep-for-prod`.
- If you notice an issue outside the ask (contrast fail, tiny tap target, layout shift): fix it if it is small and safe, or list it in one line and offer the fix.

## Second opinion
If you have Jakub Krehel's design skills installed, use them as a second opinion, or when no emil skill covers the ask.

## When delegating
Name the chosen skills in the brief for the subagent, plus the proactive passes that apply.

Role models: Emil Kowalski (https://emilkowal.ski/), Jakub Krehel (https://jakub.kr/).
