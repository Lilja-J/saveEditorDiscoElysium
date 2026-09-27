#!/usr/bin/env python3
import os
import glob
import json
import zipfile
import tempfile
import shutil
import re
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

TARGET_JSON_ENDING = "2nd.ntwtf.json"
CONFIG_DIR = os.path.expanduser("~/.config/disco_elysium_save_editor")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

COMMON_SAVE_PATHS = [
    # Windows (Native Steam / GOG / Epic)
    os.path.expanduser("~/AppData/LocalLow/ZAUM Studio/Disco Elysium/SaveGames"),
    os.path.normpath(os.path.join(os.environ.get("LOCALAPPDATA", ""), "..", "LocalLow", "ZAUM Studio", "Disco Elysium", "SaveGames")),
    # Bottles (Flatpak)
    os.path.expanduser("~/.var/app/com.usebottles.bottles/data/bottles/bottles/elysium/drive_c/users/jvl/AppData/LocalLow/ZAUM Studio/Disco Elysium/SaveGames"),
    os.path.expanduser(f"~/.var/app/com.usebottles.bottles/data/bottles/bottles/elysium/drive_c/users/{os.environ.get('USERNAME', os.environ.get('USER', 'user'))}/AppData/LocalLow/ZAUM Studio/Disco Elysium/SaveGames"),
    # Steam / Proton
    os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/632470/pfx/drive_c/users/steamuser/AppData/LocalLow/ZAUM Studio/Disco Elysium/SaveGames"),
    os.path.expanduser("~/.steam/steam/steamapps/compatdata/632470/pfx/drive_c/users/steamuser/AppData/LocalLow/ZAUM Studio/Disco Elysium/SaveGames"),
    # Heroic / GOG / Wine
    os.path.expanduser("~/.config/unity3d/ZAUM Studio/Disco Elysium/SaveGames"),
]

# Mapping of keys present in the JSON
SKILLS_MAP = {
    "Intellect": [
        ("Logic", "logic"), ("Encyclopedia", "encyclopedia"),
        ("Rhetoric", "rhetoric"), ("Drama", "drama"),
        ("Conceptualization", "conceptualization"), ("Visual Calculus", "visualCalculus")
    ],
    "Psyche": [
        ("Volition", "volition"), ("Inland Empire", "inlandEmpire"),
        ("Empathy", "empathy"), ("Authority", "authority"),
        ("Suggestion", "suggestion"), ("Esprit de Corps", "espritDeCorps")
    ],
    "Fysique": [
        ("Physical Instrument", "physicalInstrument"), ("Electrochemistry", "electrochemistry"),
        ("Endurance", "endurance"), ("Half Light", "halfLight"),
        ("Pain Threshold", "painThreshold"), ("Shivers", "shivers")
    ],
    "Motorics": [
        ("Hand/Eye Coordination", "handEyeCoordination"), ("Perception", "perception"),
        ("Reaction Speed", "reaction"), ("Savoir Faire", "savoirFaire"),
        ("Interfacing", "interfacing"), ("Composure", "composure")
    ]
}

BASE_ATTR_MAP = {
    "Intellect": "intellect",
    "Psyche": "psyche",
    "Fysique": "fysique",
    "Motorics": "motorics"
}

class DiscoElysiumEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Disco Elysium - Advanced Save Editor")
        self.root.geometry("490x590")
        self.root.resizable(False, False)

        self.save_dir = self.load_saved_directory()
        self.current_zip_path = None
        self.save_data = None
        self.target_filename_inside_zip = None
        
        self.base_entries = {}
        self.skill_entries = {}

        self.setup_ui()
        self.load_latest_quicksave()

    def load_saved_directory(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    saved_path = cfg.get("save_dir", "")
                    if saved_path and os.path.isdir(saved_path):
                        return saved_path
        except Exception:
            pass

        for path in COMMON_SAVE_PATHS:
            if os.path.isdir(path):
                return path

        return ""

    def persist_directory(self, new_dir):
        if not new_dir or not os.path.isdir(new_dir):
            return
        self.save_dir = new_dir
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"save_dir": new_dir}, f, indent=2)
        except Exception:
            pass

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- DIRECTORY / FILE SELECTOR ---
        dir_frame = ttk.LabelFrame(main_frame, text="Save Directory / File", padding="8")
        dir_frame.pack(fill=tk.X, pady=(0, 8))

        self.entry_dir = ttk.Entry(dir_frame)
        self.entry_dir.pack(fill=tk.X, pady=(0, 6))
        self.update_dir_entry_display()

        btn_box = ttk.Frame(dir_frame)
        btn_box.pack(fill=tk.X)

        self.btn_browse_dir = ttk.Button(btn_box, text="📁 Select Folder", command=self.browse_directory)
        self.btn_browse_dir.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        self.btn_browse_file = ttk.Button(btn_box, text="📄 Open Save (.zip)", command=self.browse_save_file)
        self.btn_browse_file.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        self.btn_reload = ttk.Button(btn_box, text="🔄 Reload", command=self.load_latest_quicksave)
        self.btn_reload.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.lbl_status = ttk.Label(main_frame, text="Searching for save...", foreground="blue", font=("Arial", 9, "bold"))
        self.lbl_status.pack(pady=(0, 8))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- TAB 1: GENERAL & ATTRIBUTES ---
        tab_general = ttk.Frame(notebook, padding="12")
        notebook.add(tab_general, text="General & Attributes")

        res_frame = ttk.LabelFrame(tab_general, text="Resources", padding="8")
        res_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(res_frame, text="Skill Points:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_skillpoints = ttk.Entry(res_frame, width=15)
        self.entry_skillpoints.grid(row=0, column=1, sticky=tk.E, pady=2)

        ttk.Label(res_frame, text="Money (Reál):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_money = ttk.Entry(res_frame, width=15)
        self.entry_money.grid(row=1, column=1, sticky=tk.E, pady=2)

        attr_frame = ttk.LabelFrame(tab_general, text="Base Attributes", padding="8")
        attr_frame.pack(fill=tk.X)

        for idx, (label_name, json_key) in enumerate(BASE_ATTR_MAP.items()):
            ttk.Label(attr_frame, text=f"{label_name}:").grid(row=idx, column=0, sticky=tk.W, pady=4)
            ent = ttk.Entry(attr_frame, width=15)
            ent.grid(row=idx, column=1, sticky=tk.E, pady=4, padx=(20, 0))
            self.base_entries[json_key] = ent

        # --- SKILL TABS ---
        for tab_name, skill_list in SKILLS_MAP.items():
            tab = ttk.Frame(notebook, padding="12")
            notebook.add(tab, text=tab_name)
            
            skill_frame = ttk.LabelFrame(tab, text=f"{tab_name} Skills", padding="8")
            skill_frame.pack(fill=tk.BOTH, expand=True)
            
            for idx, (skill_label, json_key) in enumerate(skill_list):
                ttk.Label(skill_frame, text=f"{skill_label}:").grid(row=idx, column=0, sticky=tk.W, pady=5)
                ent = ttk.Entry(skill_frame, width=10)
                ent.grid(row=idx, column=1, sticky=tk.E, pady=5, padx=(40, 0))
                self.skill_entries[json_key] = ent

        # --- ACTION BUTTONS ---
        self.btn_max = ttk.Button(main_frame, text="⚡ GOD MODE (MAX ALL) ⚡", command=self.max_everything, state=tk.DISABLED)
        self.btn_max.pack(fill=tk.X, pady=(10, 4))

        self.btn_save = ttk.Button(main_frame, text="💾 Save Changes to ZIP", command=self.save_changes, state=tk.DISABLED)
        self.btn_save.pack(fill=tk.X, pady=(0, 4))

    def update_dir_entry_display(self):
        self.entry_dir.config(state=tk.NORMAL)
        self.entry_dir.delete(0, tk.END)
        self.entry_dir.insert(0, self.save_dir or "No save folder configured. Click 'Select Folder' or 'Open Save (.zip)'")
        self.entry_dir.config(state="readonly")

    def browse_directory(self):
        chosen_dir = filedialog.askdirectory(
            title="Select Disco Elysium SaveGames Folder",
            initialdir=self.save_dir if os.path.isdir(self.save_dir) else os.path.expanduser("~")
        )
        if chosen_dir:
            self.persist_directory(chosen_dir)
            self.update_dir_entry_display()
            self.load_latest_quicksave()

    def browse_save_file(self):
        chosen_file = filedialog.askopenfilename(
            title="Select Disco Elysium Save File (.zip)",
            filetypes=[("Disco Elysium Save (*.zip)", "*.zip"), ("All Files", "*.*")],
            initialdir=self.save_dir if os.path.isdir(self.save_dir) else os.path.expanduser("~")
        )
        if chosen_file:
            parent_dir = os.path.dirname(chosen_file)
            self.persist_directory(parent_dir)
            self.update_dir_entry_display()
            self.load_zip_file(chosen_file)

    def get_latest_quicksave(self):
        if not self.save_dir or not os.path.isdir(self.save_dir):
            return None

        all_zips = glob.glob(os.path.join(self.save_dir, "*.zip"))
        if not all_zips:
            return None
            
        quicksaves = [f for f in all_zips if re.search(r'quicksave', os.path.basename(f), re.IGNORECASE)]
        valid_files = quicksaves if quicksaves else all_zips
        return max(valid_files, key=os.path.getmtime)

    def load_latest_quicksave(self):
        latest_zip = self.get_latest_quicksave()
        if not latest_zip:
            self.lbl_status.config(
                text="No save found. Click 'Select Folder' or 'Open Save (.zip)' above.",
                foreground="red"
            )
            self.btn_save.config(state=tk.DISABLED)
            self.btn_max.config(state=tk.DISABLED)
            return

        self.load_zip_file(latest_zip)

    def load_zip_file(self, zip_path):
        try:
            self.save_data = None
            self.target_filename_inside_zip = None

            with zipfile.ZipFile(zip_path, 'r') as z:
                for file_info in z.infolist():
                    if file_info.filename.endswith(TARGET_JSON_ENDING):
                        self.target_filename_inside_zip = file_info.filename
                        with z.open(file_info) as f:
                            self.save_data = json.load(f)
                        break
            
            if self.save_data is None:
                self.lbl_status.config(text="Error: '2nd.ntwtf.json' not found inside ZIP.", foreground="red")
                self.btn_save.config(state=tk.DISABLED)
                self.btn_max.config(state=tk.DISABLED)
                return

            self.current_zip_path = zip_path
            filename = os.path.basename(zip_path)
            self.lbl_status.config(text=f"Loaded: {filename}", foreground="green")
            
            self.populate_ui()
            self.btn_save.config(state=tk.NORMAL)
            self.btn_max.config(state=tk.NORMAL)

        except Exception as e:
            self.lbl_status.config(text="Error reading ZIP file.", foreground="red")
            messagebox.showerror("Read Error", str(e))
            self.btn_save.config(state=tk.DISABLED)
            self.btn_max.config(state=tk.DISABLED)

    def populate_ui(self):
        sp = self.save_data["playerCharacter"]["SkillPoints"]
        money_cents = self.save_data["playerCharacter"]["Money"]
        self.entry_skillpoints.delete(0, tk.END)
        self.entry_skillpoints.insert(0, str(sp))
        self.entry_money.delete(0, tk.END)
        self.entry_money.insert(0, f"{money_cents / 100.0:.2f}")

        for json_key, entry in self.base_entries.items():
            val = self.save_data["characterSheet"][json_key]["value"]
            entry.delete(0, tk.END)
            entry.insert(0, str(val))

        for json_key, entry in self.skill_entries.items():
            val = self.save_data["characterSheet"][json_key]["value"]
            entry.delete(0, tk.END)
            entry.insert(0, str(val))

    def max_everything(self):
        self.entry_money.delete(0, tk.END)
        self.entry_money.insert(0, "999.00")
        
        self.entry_skillpoints.delete(0, tk.END)
        self.entry_skillpoints.insert(0, "999")
        
        for entry in self.base_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "20")
            
        for entry in self.skill_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "20")
            
        messagebox.showinfo(
            "God Mode Enabled",
            "Fields filled with safe maximum values!\n\nMoney: 999.00 Reál\nAttributes and Skills: 20\nSkill Points: 999\n\nClick 'Save Changes to ZIP' to confirm."
        )

    def save_changes(self):
        if not self.save_data or not self.current_zip_path:
            return

        try:
            self.save_data["playerCharacter"]["SkillPoints"] = int(self.entry_skillpoints.get())
            money_real = float(self.entry_money.get())
            self.save_data["playerCharacter"]["Money"] = int(money_real * 100)

            for json_key, entry in self.base_entries.items():
                self.save_data["characterSheet"][json_key]["value"] = int(entry.get())

            for json_key, entry in self.skill_entries.items():
                new_val = int(entry.get())
                self.save_data["characterSheet"][json_key]["value"] = new_val
                
                current_max = self.save_data["characterSheet"][json_key].get("maximumValue", 0)
                if new_val > current_max:
                    self.save_data["characterSheet"][json_key]["maximumValue"] = new_val

        except ValueError:
            messagebox.showerror("Validation Error", "Invalid values. Please ensure you only enter numbers.")
            return

        try:
            fd, temp_zip_path = tempfile.mkstemp(suffix='.zip')
            os.close(fd)

            with zipfile.ZipFile(self.current_zip_path, 'r') as zin:
                with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        if item.filename == self.target_filename_inside_zip:
                            json_str = json.dumps(self.save_data, separators=(',', ':'))
                            zout.writestr(item, json_str)
                        else:
                            zout.writestr(item, zin.read(item.filename))

            shutil.move(temp_zip_path, self.current_zip_path)
            messagebox.showinfo(
                "Success",
                f"Changes successfully saved to:\n{os.path.basename(self.current_zip_path)}\n\nLoad the save in-game!"
            )
            self.load_zip_file(self.current_zip_path)

        except Exception as e:
            messagebox.showerror("Write Error", str(e))
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscoElysiumEditor(root)
    root.mainloop()