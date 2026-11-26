---
status: accepted
---

# A spec's coupled stories land as one pull request

Development is trunk-based (0024): every change is a short-lived branch from `main` and one pull request. Some specs break into stories that can't each merge alone and keep `main` green: a new record, the form that edits it and the page that shows it. Built one pull request at a time, those stories waited on each other's merges, or were stacked on each other's branches, where a fix made on the wrong branch had to be carried up and down the stack.

Now such a spec gets one short-lived integration branch from `main`, named `spec-<topic>`, and one pull request into `main`. Its stories are built side by side, each on its own branch from the integration branch (`spec-<topic>-story-<n>`, in its own worktree), and merge back into it with a merge commit. Before the pull request opens, `main` is merged into the integration branch and the full suite runs there once. The names sit side by side in git: a ref can't be both `spec/x` and `spec/x/story-1`, so neither uses a slash. CONTRIBUTING.md, "Branches" and "Checks", has the steps.

## Considered options

- **A pull request per story, in order:** keeps every merge small, but stories that only work together wait on each other, and `main` holds half a feature between them.
- **Stacked branches:** each story branches from the one before it. Every story is reviewable alone, but a fix belongs on the lowest branch and has to be merged up through the stack, and a rebase anywhere rewrites the rest.

## Consequences

- An integration branch is one change: its pull request is reviewed and merged as one, and its description lists the spec and every story.
- Stories still close one by one on the board: each moves to In Review when the integration branch's pull request opens, and to Done when it merges.
- Several builders work at once, so test runs share the computer's cores: only single-test runs overlap, slice checks take turns (`tools/runner_turns.py`), and the full suite runs once, on the integration branch.
- A story outside such a spec is unchanged: one branch from `main`, one pull request.
