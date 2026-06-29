import os
import glob
import json
import zipfile
import tempfile
import shutil
import tkinter as tk
import re
from tkinter import messagebox, ttk

# Replace this with the correct path to your Disco Elysium SaveGames folder
SAVE_DIR = "/home/user/Downloads/Games/Disco Elysium/Disco Elysium/SaveGames"
TARGET_JSON_ENDING = "2nd.ntwtf.json"

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
        self.root.geometry("450x500")
        self.root.resizable(False, False)

        self.current_zip_path = None
        self.save_data = None
        self.target_filename_inside_zip = None
        
        self.base_entries = {}
        self.skill_entries = {}

        self.setup_ui()
        self.load_latest_quicksave()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.lbl_status = ttk.Label(main_frame, text="Searching for save...", foreground="blue", font=("Arial", 9, "bold"))
        self.lbl_status.pack(pady=(0, 10))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- TAB 1: GENERAL & ATTRIBUTES ---
        tab_general = ttk.Frame(notebook, padding="15")
        notebook.add(tab_general, text="General & Attributes")

        res_frame = ttk.LabelFrame(tab_general, text="Resources", padding="10")
        res_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(res_frame, text="Skill Points:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_skillpoints = ttk.Entry(res_frame, width=15)
        self.entry_skillpoints.grid(row=0, column=1, sticky=tk.E, pady=2)

        ttk.Label(res_frame, text="Money (Reál):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_money = ttk.Entry(res_frame, width=15)
        self.entry_money.grid(row=1, column=1, sticky=tk.E, pady=2)

        attr_frame = ttk.LabelFrame(tab_general, text="Base Attributes", padding="10")
        attr_frame.pack(fill=tk.X)

        for idx, (label_name, json_key) in enumerate(BASE_ATTR_MAP.items()):
            ttk.Label(attr_frame, text=f"{label_name}:").grid(row=idx, column=0, sticky=tk.W, pady=5)
            ent = ttk.Entry(attr_frame, width=15)
            ent.grid(row=idx, column=1, sticky=tk.E, pady=5, padx=(20, 0))
            self.base_entries[json_key] = ent

        # --- SKILL TABS ---
        for tab_name, skill_list in SKILLS_MAP.items():
            tab = ttk.Frame(notebook, padding="15")
            notebook.add(tab, text=tab_name)
            
            skill_frame = ttk.LabelFrame(tab, text=f"{tab_name} Skills", padding="10")
            skill_frame.pack(fill=tk.BOTH, expand=True)
            
            for idx, (skill_label, json_key) in enumerate(skill_list):
                ttk.Label(skill_frame, text=f"{skill_label}:").grid(row=idx, column=0, sticky=tk.W, pady=6)
                ent = ttk.Entry(skill_frame, width=10)
                ent.grid(row=idx, column=1, sticky=tk.E, pady=6, padx=(40, 0))
                self.skill_entries[json_key] = ent

        # --- ACTION BUTTONS ---
        self.btn_max = ttk.Button(main_frame, text="⚡ GOD MODE ⚡", command=self.max_everything, state=tk.DISABLED)
        self.btn_max.pack(fill=tk.X, pady=(15, 5))

        self.btn_save = ttk.Button(main_frame, text="💾 Save Changes to ZIP", command=self.save_changes, state=tk.DISABLED)
        self.btn_save.pack(fill=tk.X, pady=(0, 5))

    def get_latest_quicksave(self):
        # Get all zips in the directory
        all_zips = glob.glob(os.path.join(SAVE_DIR, "*.zip"))
        
        if not all_zips:
            return None
            
        # Filter using regex to ignore case ("quicksave", "QuickSave", etc)
        quicksaves = [f for f in all_zips if re.search(r'quicksave', os.path.basename(f), re.IGNORECASE)]
        
        # If quicksaves found, get the latest. Otherwise, get any latest zip as fallback
        valid_files = quicksaves if quicksaves else all_zips
            
        return max(valid_files, key=os.path.getmtime)

    def load_latest_quicksave(self):
        latest_zip = self.get_latest_quicksave()
        if not latest_zip:
            self.lbl_status.config(text="Error: No save found.", foreground="red")
            return

        try:
            with zipfile.ZipFile(latest_zip, 'r') as z:
                for file_info in z.infolist():
                    if file_info.filename.endswith(TARGET_JSON_ENDING):
                        self.target_filename_inside_zip = file_info.filename
                        with z.open(file_info) as f:
                            self.save_data = json.load(f)
                        break
            
            if self.save_data is None:
                self.lbl_status.config(text=f"Error: JSON not found in ZIP.", foreground="red")
                return

            self.current_zip_path = latest_zip
            self.lbl_status.config(text=f"Loaded: {os.path.basename(latest_zip)}", foreground="green")
            
            self.populate_ui()
            self.btn_save.config(state=tk.NORMAL)
            self.btn_max.config(state=tk.NORMAL)

        except Exception as e:
            self.lbl_status.config(text="Error reading ZIP file.", foreground="red")
            messagebox.showerror("Read Error", str(e))

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
        # 1. Safety limit for money (999.00 Reál)
        self.entry_money.delete(0, tk.END)
        self.entry_money.insert(0, "999.00")
        
        # 2. Sufficient and safe skill points
        self.entry_skillpoints.delete(0, tk.END)
        self.entry_skillpoints.insert(0, "999")
        
        # 3. Safe limit to avoid breaking game UI: 20
        # Values of 20 for attributes and skills ensure you pass any checks without UI bugs
        for entry in self.base_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "20")
            
        for entry in self.skill_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "20")
            
        messagebox.showinfo("God Mode Enabled", "Fields filled with safe maximum values!\n\nMoney: 999.00\nAttributes and Skills: 20\n\nVerify data in tabs and click 'Save Changes to ZIP' to confirm.")

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
                
                # Update the maximum cap in the Unity rule engine
                current_max = self.save_data["characterSheet"][json_key].get("maximumValue", 0)
                if new_val > current_max:
                    self.save_data["characterSheet"][json_key]["maximumValue"] = new_val

        except ValueError:
            messagebox.showerror("Error", "Invalid values. Please ensure you only use numbers.")
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
            messagebox.showinfo("Success", "Save written successfully!\nLoad the latest save in-game.")
            self.load_latest_quicksave()

        except Exception as e:
            messagebox.showerror("Write Error", str(e))
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscoElysiumEditor(root)
    root.mainloop()