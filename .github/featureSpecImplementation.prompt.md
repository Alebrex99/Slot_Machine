---
name: featureSpecImplementation
description: Implement a multi-step feature spec into an existing app with minimal, targeted changes.
argument-hint: A markdown specification document describing the required changes, constraints, and expected behavior.
---

You are extending an existing application. A structured specification document is provided.

Follow these rules strictly:

## Constraints
- Apply the **minimum number of code changes** required.
- Do not refactor unrelated logic.
- Preserve existing architecture and file structure.
- Maintain current behavior unless explicitly modified by the spec.
- Prioritize correctness and logical clarity over elegance.

## Process
1. **Read the full spec** before making any changes. Identify all required modifications across all files.
2. **Read the current file contents** before editing — do not assume state from prior conversation.
3. **Identify architectural rules** stated in the spec (e.g. "only this class may call this function") and enforce them across all files.
4. **Implement all changes** described in the spec, grouped by file. Apply independent changes in parallel.
5. **Verify correctness** after each edit: check for broken imports, wrong variable names, misplaced logic, or violations of the architectural rules.
6. **Report** what was changed in each file and why, referencing the spec section that required it.

## Common pitfalls to check
- Global variables used before initialization (e.g. called before a setter runs).
- Values divided by 100 when they are already decimal fractions.
- Asynchronous logic (timers, signals) used inside synchronous loops.
- Imports that shadow local variables or parameters.
- A method that should only be called from one place being called from multiple places.
- CSV/log fields that use a stale cached value instead of the updated one.

## Output format
For each modified file, provide:
- The specific lines changed and why.
- Which spec section required the change.
- Any bug found and fixed beyond the spec (label it clearly as a bug fix).
