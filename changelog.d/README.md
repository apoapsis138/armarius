# Changelog fragments

Each change adds its CHANGELOG.md entries here, one file per entry. A
release gathers them into the version's section with towncrier and
deletes them (CONTRIBUTING.md, "A release"; docs/adr/0026). Don't edit
CHANGELOG.md's versions by hand.

## Adding a fragment

Name the file `<slug>.<feature>.md`:

- `<slug>`: a few lowercase words joined by hyphens, saying what the
  change is (`report-a-bug-guide`). Different changes need different
  slugs.
- `<feature>`: the key of the feature it belongs to, one per row of
  CHANGELOG.md's Features table (the `directory` of each
  `[[tool.towncrier.type]]` in `pyproject.toml`):

  | Key | Feature |
  | --- | --- |
  | `pagina` | Pagina |
  | `computus` | Computus |
  | `hours` | Book of Hours |
  | `florilegium` | Florilegium |
  | `gauntlet` | Gauntlet |
  | `scriptorum` | Scriptorum |
  | `glossa` | Glossa |
  | `fundamenta` | Fundamenta |
  | `sodales` | Sodales |
  | `illuminatio` | Illuminatio |
  | `orbis` | Orbis |
  | `concilium` | Concilium |
  | `insignia` | Insignia |
  | `peregrinatio` | Peregrinatio |
  | `hedge` | Hedge Magic |
  | `mappa` | Mappa Mundi |
  | `liveries` | Liveries of the Houses |
  | `castellum` | Castellum |
  | `renovatio` | Renovatio |
  | `folia` | Folia |

Write one paragraph in plain English for the user: a bold headline, then
what changed, at most 60 words, with no bullet or heading. For example,
`report-a-bug-guide.glossa.md`:

```markdown
**How to report a bug.** A new guide, under Getting help on the website: where the version and `crash.log` are.
```

A security fix starts with `**Security:**`, which marks its Release as a
security App update.

`tests/test_changelog.py` checks every fragment, and builds a release from
them to check that What's New, the release notes and the help site can
read it. To see the next version's section without writing it:

```
uv run towncrier build --draft --version X.Y.Z
```

## A new feature

Add its row to CHANGELOG.md's Features table and a
`[[tool.towncrier.type]]` with its key and name to `pyproject.toml`, in
the same place in the order, and a row to the table above.

`template.md.jinja` is the template a release renders the fragments with,
in the shape `ars_magica_manager/changelog.py` reads.
