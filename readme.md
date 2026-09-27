# Disco Elysium: Save Editor

[🇧🇷 Leia em Português](README.pt.md)

> **Windows Users:** Pre-compiled executable available on the [Releases page](https://github.com/Lilja-J/saveEditorDiscoElysium/releases/latest) ([Direct Download](https://github.com/Lilja-J/saveEditorDiscoElysium/releases/latest/download/DiscoElysiumSaveEditor.exe)), no Python installation needed.

A local tool with a simple Graphical User Interface (GUI) to edit Disco Elysium save files. 

Built in Python, this script directly accesses the `.json` files inside the compressed `.zip` archives used by recent versions of the game. It modifies the data and atomically repacks the save file, ensuring your file system stays clean without requiring manual extraction.

## Features
* **Visual Folder & File Picker:** Select your `SaveGames` folder or open any `.zip` save file directly from the GUI (no need to edit the code).
* **Auto-Detection:** Automatically searches for save directories across common paths (Steam/Proton, Bottles, Heroic/GOG).
* **Persistent Settings:** Remembers your save folder across sessions.
* **Resource Editing:** Alter Skill Points and Money (Reál).
* **Base Attributes:** Modify the 4 core attributes (Intellect, Psyche, Fysique, Motorics).
* **Sub-skills Editing:** Full control over all 24 skills (Inland Empire, Shivers, etc.).
* **God Mode (Max All):** A single click to safely max out attributes and skills to 20, set Money to 999.00 Reál, and grant 999 Skill Points.
* **In-memory Manipulation:** Reads and updates `2nd.ntwtf.json` cleanly inside the ZIP.

## Project Structure
```text
saveEditorDiscoElysium/
├── main.py          # Main application code
├── readme.md        # English documentation
└── README.pt.md     # Portuguese documentation
```

## Prerequisites
This project has no external dependencies that require `pip install`. It relies solely on native Python 3 libraries:
* `os`, `glob`, `json`, `zipfile`, `tempfile`, `shutil`, `re`
* `tkinter` (For the GUI)

> **Note for Linux Users:** Depending on your distribution, the `tkinter` library might not be installed by default with Python. If needed, install it via terminal: `sudo apt-get install python3-tk`

## How to Use

**1. Clone and Run:**
```bash
git clone https://github.com/Lilja-J/saveEditorDiscoElysium.git
cd saveEditorDiscoElysium
python3 main.py
```

**2. Load your Save:**
* The app automatically checks common save locations and loads the latest quicksave.
* You can also click **"Select Folder"** to point to your `SaveGames` directory, or **"Open Save (.zip)"** to choose any save directly.

**3. Edit and Save:**
* Modify values or click **"GOD MODE (MAX ALL)"**.
* Click **"Save Changes to ZIP"** and load your save in-game.

---

## Building a Standalone Executable (Optional)

If you wish to compile the script into a single executable file:

### Windows:
```cmd
pip install pyinstaller
pyinstaller --onefile --noconsole --name "DiscoElysiumSaveEditor" main.py
```
*(The generated executable will be placed in `dist\DiscoElysiumSaveEditor.exe`)*

### Linux:
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "DiscoElysiumSaveEditor" main.py
chmod +x dist/DiscoElysiumSaveEditor
```
*(The standalone binary will be placed in `dist/DiscoElysiumSaveEditor`)*