import customtkinter as ctk
from tkinter import ttk, messagebox
from ffl_suite.logic.settings_manager import get_ffl_info, set_setting

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="FFL Information", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(padx=20, pady=10)

        ctk.CTkLabel(form_frame, text="Licensee Name:").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.name_entry = ctk.CTkEntry(form_frame, width=300)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="License Number:").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.license_entry = ctk.CTkEntry(form_frame, width=300)
        self.license_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Premise Address:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.address_entry = ctk.CTkEntry(form_frame, width=300)
        self.address_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)

        ctk.CTkButton(main_frame, text="Save Settings", command=self.save_settings).pack(pady=20)

        # Data Management
        data_frame = ctk.CTkFrame(main_frame)
        data_frame.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(data_frame, text="Data Management", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        btn_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Backup Database", command=self.backup_db).pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Export Contacts (CSV)", command=self.export_contacts).pack(side='left', padx=10)

        # Profiles
        prof_frame = ctk.CTkFrame(main_frame)
        prof_frame.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(prof_frame, text="FFL Profiles", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.prof_combo = ctk.CTkComboBox(prof_frame, values=["Default"])
        self.prof_combo.pack(pady=5)

        ctk.CTkButton(prof_frame, text="Add Current as New Profile", command=self.add_profile).pack(pady=10)

    def add_profile(self):
        from ffl_suite.logic.profile_manager import add_profile
        name = self.name_entry.get()
        if name:
            add_profile(name, self.license_entry.get(), self.address_entry.get())
            messagebox.showinfo("Success", "Profile Added")

    def backup_db(self):
        from ffl_suite.logic.data.backup_manager import create_backup
        path = create_backup()
        if path:
            messagebox.showinfo("Backup", f"Backup created at:\n{path}")
        else:
            messagebox.showerror("Backup", "Backup failed.")

    def export_contacts(self):
        from ffl_suite.logic.data.backup_manager import export_contacts_csv
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                export_contacts_csv(filename)
                messagebox.showinfo("Success", "Contacts exported.")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def load_settings(self):
        info = get_ffl_info()
        if info['name']: self.name_entry.insert(0, info['name'])
        if info['license_number']: self.license_entry.insert(0, info['license_number'])
        if info['premise_address']: self.address_entry.insert(0, info['premise_address'])

    def save_settings(self):
        set_setting('ffl_name', self.name_entry.get())
        set_setting('ffl_license_number', self.license_entry.get())
        set_setting('ffl_premise_address', self.address_entry.get())
        messagebox.showinfo("Success", "Settings saved successfully.")
