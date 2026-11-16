---
status: accepted
---

# Development is trunk-based, and a release is a tag

Until now the project used two long-lived branches: work went into `dev`, and `main` held the latest release, changed only by a release pull request from `dev`. With one maintainer and many short stories merged a day, that cost more than it gave: every release needed its own pull request and a second full run of the checks, the two branches had to be kept in step, and every open pull request had to be brought up to date with `dev` after each merge before it could merge in turn.

Now `main` is the one long-lived branch, and it is always releasable. Work happens on a short-lived branch from an up-to-date `main`, one change each, and goes back in through a pull request that passes the Checks workflow. A release is a version tag (`vX.Y.Z`) on a commit of `main`: the release commit (Unreleased renamed to the version, the version set in `pyproject.toml`, `uv lock`) goes in through a pull request like any other change, and pushing the tag on its merge commit builds the GitHub Release, the container image and the help site. CONTRIBUTING.md, "Branches" and "A release", has the steps.

## Considered options

- **Keep `dev` and `main`:** `main` alone always shows the latest release, but at the cost above, and the release's tag already marks that commit.
- **Release branches cut from `main`:** let a release be stabilised while work goes on, which a project with one maintainer and no parallel release lines doesn't need.

## Consequences

- `main` may hold work not yet released. People running from the source check out a release's tag rather than pulling `main`; the help and the install page say so.
- The help site is built from a release's tag (or by hand), not on every merge, so it matches the latest release; a docs fix reaches it at the next release or a manual run. The `github-pages` environment allows deployments from tags matching `v*.*.*`.
- The Checks workflow runs on pushes and pull requests to `main` only. A pull request that changes only docs runs the fast tier in place of the sharded full suite; pushes to `main` always run the full suite, so a fault a docs-only pull request let through is still caught before a release.
- An urgent fix is a small PATCH release made the same way: merge the fix into `main`, then tag.
