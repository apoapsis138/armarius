# Install

You want Armarius running for tonight's session. The ready-to-run
download is one zip for Windows or Linux, with nothing else to install,
and it takes a few minutes.

On a Mac, or to try changes before they're released, see
[Run from the source](#run-from-the-source) below.

## Download it (Windows)

1. **Open the release.** Go to the
   [latest release](https://github.com/apoapsis138/armarius/releases/latest)
   on GitHub.
2. **Download the zip.** Under **Assets**, click the Windows zip, named
   like `Armarius-X.Y.Z-windows.zip`, where X.Y.Z is the version. Your
   browser saves it in your Downloads folder.
3. **Extract it.** Open Downloads, right-click the zip, choose **Extract
   All…** and click **Extract**. It makes a folder named like
   `Armarius-X.Y.Z`.
4. **Put the folder away.** Move it wherever you keep programs, such as
   your Documents.
5. **Start it.** Open the folder and double-click **Armarius** for the
   desktop version. **armarius-terminal**, beside it, starts the terminal
   version.

!!! warning "Extract it first"
    Double-clicking a zip only *shows* what's inside, and Windows doesn't
    really open the files from there. Armarius started from inside the zip
    can't find its own files. Always use **Extract All…** and run it from
    the extracted folder.

### "Windows protected your PC"

The first time you start a new version, Windows SmartScreen may show a
blue box saying *Windows protected your PC*. Armarius isn't signed with a
paid certificate, so Windows doesn't know it yet. Click **More info**,
check the app is Armarius, then click **Run anyway**. Windows asks only
once for each version.

To keep it handy, right-click **Armarius** and choose **Pin to Start**, or
**Send to › Desktop (create shortcut)**.

Once it's open, choose **New Saga** and follow
[Getting started](help/guide-getting-started/index.md).

## Download it (Linux)

1. **Download the zip.** From the
   [latest release](https://github.com/apoapsis138/armarius/releases/latest),
   download the Linux zip, named like `Armarius-X.Y.Z-linux.zip`, where
   X.Y.Z is the version.
2. **Unzip it.** For example, `unzip Armarius-X.Y.Z-linux.zip`.
3. **Start it.** Run `./Armarius-X.Y.Z/Armarius` for the desktop version,
   or `./Armarius-X.Y.Z/armarius-terminal` in a terminal for the terminal
   version.

It runs on Ubuntu 22.04 and newer, or another system of that age. If the
desktop version won't start, run it from a terminal to see which system
library is missing.

There's no macOS download yet. On a Mac,
[run it from the source](#run-from-the-source).

## A newer version

1. **Download and extract the new zip** beside the old folder.
2. **Start the new one.** Your sagas and settings carry over, because
   they aren't kept in the app's folder (see below).
3. **Delete the old folder** once the new one works.

If your troupe shares a saga, move to the new version together. An older
version still opens a saga a newer one saved, but it says so and can't
show what only the newer one knows. Players who join with Remote seats
need the same major version as the host, 4.x with 4.x.
[How to update to a new version](help/guide-update/index.md) has the
details.

## Where your sagas are kept

Your sagas, their backups, exports and your settings live in your **save
folder**, not in the app's folder, so you can update or reinstall Armarius
without losing anything.

- With **OneDrive** on the computer, the save folder is `Armarius` at the
  top of your OneDrive (for example `C:\Users\you\OneDrive\Armarius`),
  where OneDrive backs it up.
- Without OneDrive, it is `Armarius` in your app data folder
  (`C:\Users\you\AppData\Local\Armarius` on Windows,
  `~/.local/share/Armarius` on Linux).

The **Sagas** page shows the folder in use at its foot. **Change Save
Folder** there moves it somewhere else and can carry your saves across. The
[FAQ](faq.md#onedrive-and-the-save-folder) has more.

## Run from the source

This is the way to run Armarius on a Mac, or to try changes that aren't
in a release yet. It needs one small tool, **uv**. It fetches Python 3.14
and everything else Armarius needs, and keeps them apart from anything
else on your computer.

### 1. Install uv

On Windows:

1. **Open PowerShell.** Open the Start menu, type **PowerShell** and open
   **Windows PowerShell**.
2. **Run the installer.** Copy this line, paste it into the window
   (right-click pastes) and press Enter.

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    It downloads uv from its makers, Astral, and installs it for your user
    only (no administrator password).

3. **Check it.** Close the PowerShell window and open a new one, then type
   `uv --version` and press Enter. It should answer with a version number.
   If it says `uv` is not recognized, see
   [the FAQ](faq.md#uv-is-not-recognized).

If you use **winget**, `winget install --id=astral-sh.uv -e` installs the
same tool. On a Mac or Linux, follow
[uv's own instructions](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Python 3.14 (uv does this for you)

Armarius needs **Python 3.14** or later. You don't have to install it
yourself: the first time Armarius starts, uv downloads Python 3.14 into its
own folder and uses it only for Armarius. Any other Python on your computer
is left alone.

If you'd rather install Python yourself, get a 3.14 release from
[python.org/downloads](https://www.python.org/downloads/).

### 3. Get the source

Either:

- **As a zip.** On the
  [latest release](https://github.com/apoapsis138/armarius/releases/latest),
  under **Assets**, click **Source code (zip)**, not the `-windows.zip`.
  Then right-click it and choose **Extract All…**, as above.
- **With [git](https://git-scm.com/).** In PowerShell, in the folder where
  you want it, run
  `git clone https://github.com/apoapsis138/armarius.git`. To update later,
  run `git pull` in the `armarius` folder it makes. The `main` branch is
  always the latest release.

### 4. Start it

On Windows, open the folder and **double-click `run-gui.bat`**. The first
time, a console window opens for a few minutes while uv downloads Python
and the libraries Armarius draws its windows with, a few hundred
megabytes. Then Armarius's window opens and the console closes behind it.
Later starts take seconds.

On any system, in the folder, in a terminal:

```bash
uv sync
uv run python gui.py       # the desktop version
uv run python main.py      # the terminal version
```

On a Mac the save folder is `~/Library/Application Support/Armarius`.
