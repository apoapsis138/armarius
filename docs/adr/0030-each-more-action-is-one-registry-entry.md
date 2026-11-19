---
status: accepted
---

# Each More action is one registry entry

Every More and New action is one `MoreAction` record in `forms/more/`: its key, the letter and label its menu shows, its first step, what it changes (a `Refresh`), the one section it is offered in, whether a page offers it or draws it as a row's own button, where a page sets it out, and its rule for when it is offered (by the record on show, else by the section focus is in). The entries live in one module per area of the app (records, the saga, characters, covenants, the Region, conflicts and so on) beside the rules and steps they name, and `forms/more/registry.py` gathers them in `ORDER`, the order the menus and pages list them.

The menus (`MORE_MENU`, `NEW_MENU`), `MORE_SECTIONS`, `NOT_ON_PAGES`, `PLACES`, the steps and `REFRESH` are read from the registry, and `available` asks the generic gates (who may act, Player view, the books in play, a character's interests, a record In Creation) and then the entry's own rule. Before, one action was spread over up to eight tables in four modules; adding one meant touching most of them.

The layers run page (`forms/page.py`) below the steps (`forms/menu_steps.py`), below the rules and the entries (`forms/more/`), below the page placement (`forms/menu.py`). Two steps need what only the registry or the placement knows, and are finished there: Edit Interests lists every action by label (the registry passes `LABELS` in), and Give Silver gives from the purse of the section that offers it (the placement finds it).

## Considered options

- **Entries hold the data, and rules and steps register themselves** (a decorator per function): a much smaller change, but reading an entry wouldn't show when it is offered or what it does first.
- **The entries in one long module:** one place to look, but about 230 entries in one file, far from the rules they name.

## Consequences

- A new action is one entry in its area's module and its key in `ORDER`.
- About 90 actions still have no step of their own: each front-end draws and runs them (a fight's verbs, a charter's clauses, a ship's rolls). Their entries say where they show and when, and give them a step as each moves into the core.
- Actions that aren't More or New (the section verbs, Delete, Edit Saga) keep their small rule and step tables beside the registry.
- Supersedes the More menu paragraph of ADR 0006: the steps and what each changes now live in the entries.
