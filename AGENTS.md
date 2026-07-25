# How to Use Skills

## Loading a Skill

When starting a task, check the `available_skills` list in the system prompt. If a skill matches your task, load it with the `skill` tool:

```
<skill name="skill-name">
```

Then follow the instructions in the skill.

## Rules

1. **Always check for an applicable skill before starting work** — skills encode processes that prevent common mistakes.
2. **Follow the steps in order.** Don't skip the verification step.
3. **Multiple skills can be chained** for a single task — e.g. `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation`.
4. **When in doubt, start with `using-agent-skills`** — this meta-skill helps discover the right skill for your task.

## Available Skills

### Define
- `interview-me` — Surface what the user actually wants before any plan or code
- `idea-refine` — Refine ideas through divergent/convergent thinking
- `spec-driven-development` — Requirements & acceptance criteria before code

### Plan
- `planning-and-task-breakdown` — Break into small, verifiable tasks

### Build
- `incremental-implementation` — Thin vertical slices, test each before expanding
- `context-engineering` — Load the right context for the AI
- `source-driven-development` — Verify against official docs before implementing
- `doubt-driven-development` — Adversarial review of every non-trivial decision
- `frontend-ui-engineering` — Production UI with accessibility
- `api-and-interface-design` — Stable interfaces with clear contracts

### Verify
- `test-driven-development` — Failing test first, then make it pass
- `browser-testing-with-devtools` — Chrome DevTools MCP for runtime verification
- `debugging-and-error-recovery` — Reproduce → localize → fix → guard

### Review
- `code-review-and-quality` — Five-axis review with quality gates
- `code-simplification` — Reduce complexity while preserving behavior
- `security-and-hardening` — OWASP prevention, input validation, least privilege
- `performance-optimization` — Measure first, optimize what matters

### Release
- `git-workflow-and-versioning` — Atomic commits, clean history
- `ci-cd-and-automation` — Automated quality gates
- `documentation-and-adrs` — Document the why, not just the what
- `observability-and-instrumentation` — Logs, metrics, traces, alerts
- `shipping-and-launch` — Pre-launch checklist, monitoring, rollback plan
- `deprecation-and-migration` — Retire old systems and migrate users safely

## Chaining Multiple Skills

Use `using-agent-skills` to determine the right sequence. Example for a new feature:

```
using-agent-skills → interview-me → spec-driven-development
→ planning-and-task-breakdown → incremental-implementation
→ test-driven-development → code-review-and-quality
→ git-workflow-and-versioning
```
