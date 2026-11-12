# Install

These steps put Armarius on a Windows PC. You don't need to know anything
about programming: you will install one small tool, download Armarius, and
double-click a file to start it. Allow about fifteen minutes the first
time, most of it waiting for downloads.

Armarius is tested on Windows and Linux and should run on macOS; the
[last section](#on-linux-or-macos) has the short version for those.

!!! tip "A one-file download is on its way"
    A ready-to-run download, with nothing else to install, is being
    prepared. Until it appears on the
    [Releases page](https://github.com/apoapsis138/armarius/releases/latest),
    use the steps below. [What to do once it is there](#the-ready-to-run-download)
    is at the end of this page.

## 1. Install uv

Armarius is written in Python. **uv** is a small, free tool that fetches
the right version of Python and everything else Armarius needs, and keeps
them apart from anything else on your computer.

1. Open the Start menu, type **PowerShell** and open **Windows
   PowerShell** (a blue window where you type commands).
2. Copy this line, paste it into the window (right-click pastes) and press
   Enter:

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    It downloads uv from its makers, Astral, and installs it for your user
    only (no administrator password). When it finishes it says where it put
    uv.

3. **Close the PowerShell window and open a new one**, so it sees the new
   tool, then type `uv --version` and press Enter. It should answer with a
   version number, such as `uv 0.9.0`. If it says `uv` is not recognized,
   see [the FAQ](faq.md#uv-is-not-recognized).

!!! note "Another way"
    If you use **winget** (Windows' own package manager), `winget install
    --id=astral-sh.uv -e` installs the same tool.

## 2. Python 3.14 (uv does this for you)

Armarius needs **Python 3.14** or later. You don't have to install it
yourself: the first time Armarius starts, uv downloads Python 3.14 into its
own folder and uses it only for Armarius. Any other Python on your computer
is left alone.

If you would rather install Python yourself (for example because you use
it for other things), get it from
[python.org/downloads](https://www.python.org/downloads/) and choose a 3.14
release. Python itself isn't needed to *run* the installer steps on this
page, only uv.

<p class="unverified">Not checked on a clean PC: the exact screens of
python.org's Windows installer for 3.14, which has changed between
versions. uv's own download of Python, above, is the tested path.</p>

## 3. Get Armarius

Choose one of these.

### As a zip file (simplest)

1. Go to the [latest release](https://github.com/apoapsis138/armarius/releases/latest)
   on GitHub.
2. Under **Assets**, click **Source code (zip)**. Your browser saves a file
   such as `armarius-4.11.2.zip` in your Downloads folder.
3. Open Downloads, **right-click the zip and choose Extract All…**, pick a
   folder you'll find again (for example `C:\Users\you\Armarius`) and click
   **Extract**.

!!! warning "Extract it first"
    Double-clicking a zip only *shows* what's inside; Windows doesn't really
    open the files from there. Armarius started from inside a zip can't
    find its own files. Always use **Extract All…** and run it from the
    extracted folder.

To update later, download the new release's zip and extract it in the same
way (into a new folder, or over the old one). Your sagas are kept
elsewhere (see [Where your sagas are kept](#where-your-sagas-are-kept)), so
updating never touches them.

### With git (easiest to keep up to date)

If you have [git](https://git-scm.com/) installed, open PowerShell in the
folder where you want Armarius and run:

```powershell
git clone https://github.com/apoapsis138/armarius.git
```

That makes a folder called `armarius`. To update later, open PowerShell in
that folder and run `git pull`.

The `main` branch is always the latest release.

## 4. Start it

1. Open the folder you extracted (or cloned): it holds files such as
   `README.md`, `gui.py` and **`run-gui.bat`**.
2. **Double-click `run-gui.bat`.**

The first time, a black console window opens for a few minutes while uv
downloads Python 3.14 and the libraries Armarius draws its windows with
(a few hundred megabytes). Then Armarius's window opens and the console
closes behind it. Later starts take a few seconds.

Windows may ask whether to run a file downloaded from the internet: choose
**Run** (or, if it says *Windows protected your PC*, **More info › Run
anyway**). If the console window shows an error and waits for a key, the
[FAQ](faq.md) covers the usual causes.

To put it on your desktop or Start menu, right-click `run-gui.bat` and
choose **Show more options › Create shortcut**, then move the shortcut
where you like.

Once it's open, choose **New Saga** and follow
[Getting started](help/guide-getting-started/index.md).

### The terminal version

The terminal version does the same things from the keyboard, in a console
window. Open PowerShell in the Armarius folder and run:

```powershell
uv run python main.py
```

## Where your sagas are kept

Your sagas, their backups, exports and your settings live in your **save
folder**, not in the Armarius folder, so you can update or reinstall
Armarius without losing anything.

- With **OneDrive** on the computer, the save folder is `Armarius` at the
  top of your OneDrive (for example `C:\Users\you\OneDrive\Armarius`),
  where OneDrive backs it up.
- Without OneDrive, it is `Armarius` in your app data folder
  (`C:\Users\you\AppData\Local\Armarius` on Windows).

The **Sagas** page shows the folder in use at its foot. **Change Save
Folder** there moves it somewhere else and can carry your saves across. The
[FAQ](faq.md#onedrive-and-the-save-folder) has more.

## The ready-to-run download

<p class="unverified">This section is for a download that hasn't been
released yet: its file name and the exact screens below are what is
planned, not yet checked against a real release.</p>

When the ready-to-run version is out, you won't need uv or Python at all:

1. Go to the [latest release](https://github.com/apoapsis138/armarius/releases/latest)
   and, under **Assets**, download the Windows zip (named like
   `Armarius-4.12.0-windows.zip`).
2. Right-click it and choose **Extract All…**, as above.
3. Open the extracted folder and double-click **Armarius.exe**.
4. The first time, Windows SmartScreen may say *Windows protected your
   PC*, because the download isn't signed with a paid certificate. Click
   **More info**, check the app is Armarius, then click **Run anyway**.
   Windows remembers your choice for that copy.

Your save folder is the same one, so sagas made with one version open in
the other.

## On Linux or macOS

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), get
the code as above, and in its folder run:

```bash
uv sync
uv run python gui.py       # the desktop version
uv run python main.py      # the terminal version
```

The save folder is `Armarius` in your user data folder
(`~/.local/share/Armarius` on Linux, `~/Library/Application Support/Armarius`
on macOS).
