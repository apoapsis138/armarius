# Install

The easiest way to get Armarius is the ready-to-run download: one zip file
for Windows or Linux, with nothing else to install. It takes a few minutes.

If you'd rather run it from its source (on a Mac, or to try changes
before they're released), see [Run from the source](#run-from-the-source)
below.

## Download it (Windows)

1. Go to the [latest release](https://github.com/apoapsis138/armarius/releases/latest)
   on GitHub.
2. Under **Assets**, click the Windows zip, named like
   `Armarius-X.Y.Z-windows.zip`, where X.Y.Z is the version. Your browser
   saves it in your Downloads folder.
3. Open Downloads, **right-click the zip and choose Extract All…**, and
   click **Extract**. It makes a folder named like `Armarius-X.Y.Z`. Move
   that folder wherever you keep programs, such as your Documents.
4. Open the folder and double-click **Armarius** to start the desktop
   version. **armarius-terminal**, beside it, starts the terminal version.

!!! warning "Extract it first"
    Double-clicking a zip only *shows* what's inside; Windows doesn't really
    open the files from there. Armarius started from inside the zip can't
    find its own files. Always use **Extract All…** and run it from the
    extracted folder.

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

1. From the [latest release](https://github.com/apoapsis138/armarius/releases/latest),
   download the Linux zip, named like `Armarius-X.Y.Z-linux.zip`, where
   X.Y.Z is the version.
2. Unzip it, for example `unzip Armarius-X.Y.Z-linux.zip`.
3. Run `./Armarius-X.Y.Z/Armarius` for the desktop version, or
   `./Armarius-X.Y.Z/armarius-terminal` in a terminal for the terminal
   version.

It runs on Ubuntu 22.04 and newer, or another system of that age. If the
desktop version won't start, run it from a terminal to see which system
library is missing.

There is no macOS download yet: on a Mac, [run it from the
source](#run-from-the-source).

## A newer version

Download the newer zip, extract it beside the old folder and start the new
one. Your sagas and settings carry over, because they aren't kept in the
app's folder (see below). Delete the old folder once the new one works.

If your troupe shares a saga, move to the new version together: an older
version still opens a saga a newer one saved, but it says so and can't show
what only the newer one knows. Players who join with Remote seats need the
same version as the host. The app's guide,
[How to download and run the app](help/guide-download/index.md), has the
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
in a release yet. It needs one small tool, **uv**, which fetches the right
version of Python (3.14) and everything else Armarius needs, and keeps them
apart from anything else on your computer.

### 1. Install uv

On Windows:

1. Open the Start menu, type **PowerShell** and open **Windows
   PowerShell**.
2. Copy this line, paste it into the window (right-click pastes) and press
   Enter:

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    It downloads uv from its makers, Astral, and installs it for your user
    only (no administrator password).

3. **Close the PowerShell window and open a new one**, then type
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

- **As a zip:** on the
  [latest release](https://github.com/apoapsis138/armarius/releases/latest),
  under **Assets**, click **Source code (zip)**, then right-click it and
  **Extract All…**, as above. (This is not the `-windows.zip`.)
- **With [git](https://git-scm.com/):** in PowerShell, in the folder where
  you want it, run
  `git clone https://github.com/apoapsis138/armarius.git`. To update later,
  run `git pull` in the `armarius` folder it makes. The `main` branch is
  always the latest release.

### 4. Start it

On Windows, open the folder and **double-click `run-gui.bat`**. The first
time, a console window opens for a few minutes while uv downloads Python
and the libraries Armarius draws its windows with (a few hundred
megabytes); then Armarius's window opens and the console closes behind it.
Later starts take seconds.

On any system, in the folder, in a terminal:

```bash
uv sync
uv run python gui.py       # the desktop version
uv run python main.py      # the terminal version
```

On a Mac the save folder is `~/Library/Application Support/Armarius`.
