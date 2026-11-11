# Security

## Reporting a problem

Please report a security problem privately, through GitHub: on this
repository's **Security** tab, choose **Report a vulnerability**. Don't
open a public issue for it.

Say what you found, which version it affects (the title bar shows it),
and how to reproduce it. You'll get an answer when the report has been
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
- **Files coming in**: saga files, exports and content packs from someone
  else, which are shape-checked as they load.

A problem that needs an attacker who already controls your computer or
your account is out of scope.
