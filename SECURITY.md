# Security

## Reporting a problem

Please report a security problem privately, through GitHub: on this
repository's **Security** tab, choose **Report a vulnerability**. Don't
open a public issue for it.

Say what you found, which version it affects (on the desktop app,
the title page and Help's About page; on the terminal app, its title bar
and About; on a headless host, ARMARIUS_VERSION in `.env`), and how to reproduce it. You'll get an answer when the report has been
read; Armarius is a one-person project, so a fix may take a while, and
you'll be told what is planned.

## Supported versions

Only the latest release gets security fixes.

## What is worth reporting

Most of Armarius runs on your own computer and reads your own files. The
parts that face other people are the ones that matter most:

- **Remote seats**: players and storyguides joining a saga from their own
  copy of Armarius over the internet. Its threat model is
  [docs/threat-model-remote-seats.md](docs/threat-model-remote-seats.md).
- **Hosting for browsers and SSH**: a saga served to players' browsers or
  terminals. It is meant only for a private, encrypting network (Tailscale,
  ZeroTier or a trusted home network), never a public address; its threat
  model, with the risks accepted and the guards not yet built, is
  [docs/threat-model-browser-and-ssh-hosting.md](docs/threat-model-browser-and-ssh-hosting.md).
- **Files coming in**: saga files, exports, content packs, supplements
  and Mystery Cult files from someone else, which are shape-checked as
  they load, and a saga is checked again before it is saved. Every id in
  them must be a plain name (lowercase letters, digits, `_` and `-`), so
  none can name a file outside its folder.
- **The App update check**: the desktop and terminal apps ask GitHub's API,
  read-only, for the latest Release (at most once a day, or on Check now),
  sending only the app's version; the release notes it reads are shown as
  plain text. It downloads and installs nothing. `ARMARIUS_UPDATES=off`
  turns it off. A threat model will come with downloading and installing
  updates.

A problem that needs an attacker who already controls your computer or
your account is out of scope.
