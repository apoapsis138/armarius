# FAQ and troubleshooting

Answers to the questions that come up while installing and setting up
Armarius. For how to *use* it, start with
[Getting started](help/guide-getting-started/index.md). If your problem
isn't here, please [open an issue](https://github.com/apoapsis138/armarius/issues)
with what you did and what the window said.

## Installing

### "python" is not recognized, or the Microsoft Store opens { #python-not-found }

You don't need to type `python` yourself: `run-gui.bat` and `uv run` use
the Python that uv downloaded for Armarius. If you followed a guide that
says to type `python ...`, type `uv run python ...` in the Armarius folder
instead.

If typing `python` opens the **Microsoft Store**, that's Windows' *app
execution alias* standing in for Python. To turn it off: **Settings › Apps
› Advanced app settings › App execution aliases**, then switch off the two
entries for **python.exe** and **python3.exe**.

### It says the Python version is wrong { #wrong-python }

Armarius needs Python **3.14** or later, and an error mentioning
`requires-python` or "3.14" means an older one was picked up. Let uv fetch
the right one; in PowerShell, in the Armarius folder:

```powershell
uv python install 3.14
uv sync
```

Then start Armarius again. This doesn't change any other Python on your
computer.

### "uv" is not recognized { #uv-is-not-recognized }

The installer puts uv in `C:\Users\you\.local\bin` and adds that folder to
your PATH (the list of places Windows looks for commands), but windows that
were already open don't see the change.

1. Close every PowerShell or console window and open a new one.
2. If it still isn't found, sign out of Windows and back in (or restart).
3. Still not? Check that `C:\Users\you\.local\bin\uv.exe` exists. If it
   does, run the [install line](install.md#1-install-uv) again; if it
   doesn't, the install didn't finish, so run it again and read what it
   prints.

### run-gui.bat flashes and closes, or says it can't find files { #inside-the-zip }

The most common cause is running it **from inside the zip**. Windows shows
a zip's contents like a folder, but they aren't really there to run.
Right-click the zip, choose **Extract All…**, and run `run-gui.bat` from
the extracted folder.

If the console stays open with an error and "Press any key", read the last
lines: a network error means the first-time download was interrupted (run
it again); "uv is not recognized" is [above](#uv-is-not-recognized).

### The first start takes ages

The first start downloads Python and the libraries the desktop draws with,
a few hundred megabytes, so it takes a few minutes on a slow connection.
Later starts take seconds. Don't close the console window while it works.

### Windows says it protected my PC { #smartscreen }

That's SmartScreen, which warns about programs it hasn't seen often.
Armarius isn't signed with a paid certificate. If you downloaded it from
[the project's Releases page](https://github.com/apoapsis138/armarius/releases),
click **More info**, then **Run anyway**.

### The window is too big for my screen

On a high-resolution screen with display scaling, the window might not fit.
Since version 4.11.1 the window fits the screen it opens on; see
[How to fit the window to your screen](help/guide-window-size/index.md) for
what else you can change.

## Your sagas

### Where are my sagas saved? { #onedrive-and-the-save-folder }

In your **save folder**: `Armarius` at the top of your OneDrive when the
computer has OneDrive, otherwise `C:\Users\you\AppData\Local\Armarius`. The
**Sagas** page shows the folder in use at its foot, and what chose it. Each
saga is one `.json` file there, beside its backups, exports and your
settings.

### Is OneDrive safe for my sagas?

Yes: it's the default because OneDrive backs the folder up and keeps
earlier versions of each file. A few things to know:

- If you use Armarius on two computers through the same OneDrive, close it
  on one before opening the same saga on the other, and give OneDrive a
  moment to sync. Two copies changed at once end up as two files.
- If OneDrive has paused syncing or is signed out, your saves stay on this
  computer until it catches up.
- Armarius also keeps its own backups, in the `backups` folder beside the
  sagas, before each season is applied.

### How do I move the save folder?

On the **Sagas** page, click **Change Save Folder**, pick a folder and
choose whether to move your saves there. A file already in the new folder
is never overwritten. Armarius checks it can save in the folder first.

### Windows blocks saving in Documents or on the Desktop

Windows Security's **Controlled folder access** protects Documents, the
Desktop and some other folders from programs it doesn't know, Python
included. Choose a save folder outside them (the default OneDrive or app
data folder is fine), or allow Python in **Windows Security › Virus &
threat protection › Ransomware protection › Allowed apps**.

### What is ARMARIUS_DATA? { #armarius-data }

An environment variable that sets the save folder, overriding both the
default and the folder chosen in the app; while it's set, the app can't
change the folder. It's useful for keeping sagas on another drive or for
trying things out with a separate set of saves. In PowerShell:

```powershell
setx ARMARIUS_DATA "D:\Sagas\Armarius"
```

Then open a **new** window (or sign out and in) and start Armarius. To go
back to the default, delete the variable: **Settings › System › About ›
Advanced system settings › Environment Variables**, choose ARMARIUS_DATA
under your user's variables and click **Delete**.

### I updated Armarius. Are my sagas still there?

Yes. They live in the save folder, not with the program, and a newer
version opens sagas saved by an older one.

## Other questions

### Does it cost anything, or need an account?

No. Armarius is free software under the GNU GPL v3.0, and it runs on your
own computer with no account. Only sharing a saga with your players over
the internet involves a connection between your computers; see
[How to host a saga for your troupe](help/guide-hosting/index.md).

### Is it official?

No. It's an unofficial fan project, not endorsed by Atlas Games or Paradox
Interactive. The Ars Magica rules text it uses is adapted from material
Atlas Games released under CC BY-SA 4.0; see [About](about.md).
