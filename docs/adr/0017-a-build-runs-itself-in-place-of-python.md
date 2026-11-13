# A build runs itself in place of Python

Hosting starts more copies of the app: the desktop's Host runs the server as
`python -m <module>`, and the terminal's browser hosting runs `python main.py`
for each player who connects. A Build has no Python to run. Instead, each
Build's terminal program takes a word that says what to run (`host`, `play`,
and so on), looked up in one table, and a single `relaunch()` helper makes
the command line for either layout: `python -m ...` from source, the Build's
own program with its word from a Build. Nothing else reads `sys.executable`.

## Considered Options

- Hide Host in a Build: simplest, but people who download the app could
  never run a game for their players.
- Ship a Python beside the app and keep `python -m`: a second interpreter
  in the download, and the bundled packages would still have to be found
  by it.

## Consequences

- The table of words is part of the terminal program's command line;
  removing or renaming a word breaks hosts and players on older Builds.
- A Build holds two programs over one set of files: `Armarius`, the desktop
  with no console window, and `armarius-terminal`, which needs one on
  Windows and is the one relaunched.
- The trial of every new Build includes hosting from the desktop and
  joining from the terminal program.
