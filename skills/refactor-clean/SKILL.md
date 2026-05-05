---
name: refactor-clean
description: Safely identify and remove dead code with test verification at every step. Use when Codex needs to clean unused exports, files, dependencies, helpers, wrappers, re-exports, or duplicate code without risking regressions. Trigger for dead-code cleanup, unused dependency audits, stale utility removal, cleanup refactors, or requests to reduce code safely before or alongside maintenance work.
---

# Refactor Clean

Use a conservative cleanup loop. Prefer keeping uncertain code over deleting something with hidden runtime or external consumers.

## Workflow

1. Establish a baseline.
2. Detect dead code with language-appropriate tools.
3. Categorize findings into `SAFE`, `CAUTION`, or `DANGER`.
4. Remove one `SAFE` item at a time.
5. Re-run verification after every deletion.
6. Investigate `CAUTION` items before touching them.
7. Skip `DANGER` items unless the user explicitly wants deeper investigation.
8. Consolidate obvious duplicates only after dead-code cleanup is stable.

## Establish A Baseline

- Run the smallest meaningful baseline first, then the broader project checks required by the repo.
- Record whether the suite already fails before cleanup starts.
- Do not treat newly discovered pre-existing failures as caused by the cleanup.
- If the baseline is red in the target area, pause and tell the user before deleting code.

## Detect Dead Code

Choose tools by ecosystem. Prefer the project's package manager and existing scripts where possible.

| Tool | What it finds | Command |
| --- | --- | --- |
| `knip` | Unused exports, files, dependencies | `npx knip` |
| `depcheck` | Unused npm dependencies | `npx depcheck` |
| `ts-prune` | Unused TypeScript exports | `npx ts-prune` |
| `vulture` | Unused Python code | `vulture src/` |
| `deadcode` | Unused Go code | `deadcode ./...` |
| `cargo-udeps` | Unused Rust dependencies | `cargo +nightly udeps` |

If specialized tooling is unavailable, fall back to targeted search:

- Find exported symbols and files.
- Search for imports, requires, dynamic imports, route references, config references, and string-based lookups.
- Treat "zero obvious references" as a lead, not proof.

## Categorize Findings

Assign every finding to a safety tier before editing.

| Tier | Typical examples | Default action |
| --- | --- | --- |
| `SAFE` | Unused internal utilities, private helpers, unused tests/helpers, wrapper functions with no callers | Delete with verification |
| `CAUTION` | Components, hooks, API routes, middleware, server actions, jobs, CLI commands | Investigate runtime and indirect usage first |
| `DANGER` | Config files, entry points, exported types, schema files, generated boundaries, public APIs | Skip unless the user asks for deeper work |

Escalate to a higher-risk tier when any of these are present:

- Dynamic import paths
- Reflection or registry lookups
- String-based routing or command dispatch
- Framework auto-discovery
- Package public exports
- External consumers or cross-repo usage

## Safe Deletion Loop

For each `SAFE` item:

1. Run the baseline verification.
2. Delete exactly one item with a surgical edit.
3. Re-run the relevant tests immediately.
4. If tests fail, restore the deletion and skip the item.
5. If tests pass, continue to the next item.

Keep deletions atomic. Do not batch multiple unrelated removals into a single verification cycle.

If a revert is needed:

- Restore only the item under test.
- Prefer non-destructive restore methods that do not disturb unrelated user changes.
- Note the failure in the summary and move on.

## Handle Caution Items

Before deleting a `CAUTION` item, explicitly check for:

- `import()` or `require()` usage
- String references in configs, routes, registries, feature flags, and tests
- Re-exports from package or app entry points
- External consumers if the module is part of a published or shared surface
- Framework conventions that auto-load files by name or location

Delete a `CAUTION` item only when indirect usage has been ruled out and verification still passes.

## Consolidate Duplicates

After dead-code removals are green, look for low-risk consolidation:

- Near-duplicate functions with the same behavior
- Redundant type definitions
- Pass-through wrappers that add no policy or ergonomics
- Re-exports that add no discoverability or compatibility value

Keep this phase separate from dead-code deletion. If consolidation changes behavior, stop treating it as cleanup and call it out explicitly.

## Reporting

End with a short cleanup report that includes:

- Deleted functions, files, and dependencies
- Skipped items and why
- Approximate lines removed
- Verification commands run
- Final pass/fail state

Use this format when it helps:

```text
Dead Code Cleanup
----------------------------
Deleted:   12 unused functions
           3 unused files
           5 unused dependencies
Skipped:   2 items (verification failed)
Saved:     ~450 lines removed
----------------------------
All tests passing
```

## Rules

- Never delete code before running a baseline verification step.
- Remove one item at a time.
- Skip uncertain findings instead of guessing.
- Do not mix broad refactors into the deletion loop.
- Preserve unrelated user changes while restoring failed deletions.
- Be explicit about residual risk when `CAUTION` or `DANGER` items remain.
