---
status: accepted
---

# Unfinished features ship behind an off-by-default setting

Development is trunk-based and `main` is released every week (ADR 0024), so a story merges as soon as it is done. Some features only make sense whole: the Virtual Tabletop (the Chronicle, rolling at the host, events to Remote seats, Begin and End Session) is many stories, and a player meeting half of it would find a Chronicle that can't yet whisper, or a Session that is never folded into its record. That feature must reach players whole, in 5.0.

So a feature built across several releases ships behind an app setting that is off by default, for the Virtual Tabletop "Virtual Tabletop (Preview)" in the Settings window. Each story merges into `main` when it is done, with its tests, help and changelog fragment; while the setting is off, the app shows nothing of it. The setting arrives with the feature's first story and is removed when the feature is finished. Each help page written for the feature opens by saying it is a preview and how to turn it on, and each changelog fragment starts "Preview (off by default):".

## Considered options

- **Ship each story visibly in 4.x:** no setting to carry, but every player meets the feature half-built, and its first impression is one it has to live down.
- **Hold the stories back until the feature is whole, unmerged or on a long-lived branch:** the shipped app stays clean, but the branch drifts from `main`, every merge into it is a conflict waiting, and the checks on `main` never see the feature until it lands all at once, against the reasons for ADR 0024.

## Consequences

- `main` stays releasable: with the setting off, a release behaves as it did before the feature began.
- What the setting gates is tested with it both on and off, and removing the setting, with those checks, is part of finishing the feature.
- Where a feature reaches other computers (a host and its seats), the setting lives on the computer that starts it, the host's desktop; seats follow what their host is doing. A headless host has no desktop, so it serves Remote seats as before but offers no previewed feature until the feature is finished.
- Testers can try the feature from any release by turning the setting on, and its help tells them so.
