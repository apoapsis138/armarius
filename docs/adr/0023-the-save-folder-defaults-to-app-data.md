---
status: accepted
---

# The save folder defaults to the app data folder

Since the start, the save folder (sagas, backups, exports, portraits, maps and settings) defaulted to `Armarius` at the top of the user's OneDrive, for its backups and earlier versions, with the app data folder only where there was no OneDrive. The app data folder was already the fallback because Windows' Controlled folder access blocked saving in Documents. But a synced folder is a poor default for a file the app rewrites on every change: a sync can catch a save half-written, a file kept only in the cloud isn't there to read, and two computers saving the same saga at once overwrite each other.

New installs now save in `Armarius` in the user's app data folder (`platformdirs.user_data_dir`): `AppData\Local\Armarius` on Windows, Local rather than Roaming because the backups and exports grow, and a roaming profile copies its whole folder at every sign-in. Existing users are never moved: when no folder is chosen and the new default doesn't exist, the first older default folder found (OneDrive\Armarius, OneDrive\Ars Magica Manager, AppData\Local\Ars Magica Manager) is recorded once as the chosen folder, as it is, without renaming it or asking. The once-only rename of an "Ars Magica Manager" default folder to "Armarius" is removed.

## Considered options

- **Move existing saves to the new default:** carries every user across, but moving a folder OneDrive is syncing can fail half-way, and it would change where people know their files are.
- **Ask on first start:** a question most people can't answer well, asked before they've seen the app.

## Consequences

- OneDrive users stay in OneDrive until they use Change save folder; the saga picker shows it as chosen in the app.
- Emptying the old folder doesn't send its user to the new default: once recorded, the choice stands.
- A user who wants a cloud drive chooses its folder themself, and the FAQ says how to use one safely.
- Renaming the `ars_magica_manager` package to `armarius` is left to a separate change.
