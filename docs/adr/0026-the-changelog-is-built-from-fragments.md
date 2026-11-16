---
status: accepted
---

# The changelog is built from fragments

Each change used to add its lines by hand under `## Unreleased` at the top of CHANGELOG.md, and a release renamed that heading to the version's. With every pull request now going straight into `main` (ADR 0024), several open at once all edited the same few lines, so each merge left the others with a conflict in CHANGELOG.md to resolve before they could merge in turn.

Now each change adds a fragment instead: a small file in `changelog.d/` named `<slug>.<feature>.md`, holding one entry, one paragraph for the user under a bold headline. Two pull requests never touch the same file. A release runs `towncrier build`, which assembles the fragments into the version's section, `## X.Y.Z — date` with each feature's entries under its `### <Feature>` heading in the Features table's order, writes it above the newest version and deletes them. This is the Builder pattern: the parts are gathered over time and put together into the finished product, the version's notes, in one step at the end, by one template (`changelog.d/template.md.jinja`). CHANGELOG.md itself holds only released versions, so `changelog.py` refuses an `## Unreleased` heading, and What's New shows released versions only.

## Considered options

- **Keep the Unreleased section:** no new tool, but every pull request conflicts with the one merged before it, and resolving those by hand is where entries get lost or land under the wrong heading.
- **Show the waiting fragments in What's New as Unreleased:** keeps work in progress visible in the app, but a Build would then carry `changelog.d/` and a second reader of it; the maintainer chose released versions only.
- **Write the changelog from commit messages or pull request titles:** no extra file, but those are written for developers, while the changelog is written for the user, by feature.

## Consequences

- A fragment's feature key comes from `[tool.towncrier]` in `pyproject.toml`, one type per row of the Features table; `tests/test_changelog.py` holds the two to each other and checks every fragment's name, shape and length (at most 60 words).
- The template must write what `changelog.py` parses. The same test builds a release from the fragments in a copy of the repository and checks that What's New, `tools/release_notes.py` and so the help site read it, so a template change can't break them unnoticed.
- Unreleased work no longer shows in What's New until its release.
- towncrier is a development dependency only; the app and its Builds never import it.
