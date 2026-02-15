import customtkinter as ctk
from tkinter import messagebox
from ffl_suite.logic.nfa_manager import add_nfa_entity, add_responsible_person

class AddEntityDialog(ctk.CTkToplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Add NFA Entity")
        self.geometry("400x500")
        self.attributes("-topmost", True)
        self.create_widgets()

    def create_widgets(self):
        main = ctk.CTkFrame(self)
        main.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(main, text="New Entity (Trust/Corp/Individual)").pack(pady=10)

        self.entries = {}
        fields = [("Name", "name"), ("Street", "address_street"), ("City", "address_city"), ("State", "address_state"), ("Zip", "address_zip"), ("Phone", "phone"), ("Email", "email")]

        ctk.CTkLabel(main, text="Type").pack()
        self.type_combo = ctk.CTkComboBox(main, values=["Trust", "Corporation", "Individual"])
        self.type_combo.pack(pady=5)

        for lbl, key in fields:
            ctk.CTkLabel(main, text=lbl).pack()
            e = ctk.CTkEntry(main)
            e.pack(pady=2)
            self.entries[key] = e

        ctk.CTkButton(main, text="Save", command=self.save).pack(pady=20)

    def save(self):
        data = {k: v.get() for k, v in self.entries.items()}
        data['entity_type'] = self.type_combo.get()
        if not data['name']: return

        try:
            add_nfa_entity(data)
            self.parent_view.load_entities()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class AddRPDialog(ctk.CTkToplevel):
    def __init__(self, parent_view, entity_id):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.entity_id = entity_id
        self.title("Add Responsible Person")
        self.geometry("400x600")
        self.attributes("-topmost", True)
        self.create_widgets()

    def create_widgets(self):
        main = ctk.CTkScrollableFrame(self)
        main.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(main, text="Add Responsible Person", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.entries = {}
        fields = [
            ("First Name", "first_name"), ("Middle", "middle_name"), ("Last Name", "last_name"),
            ("Title (Trustee)", "title"), ("DOB", "dob"), ("City of Birth", "pob_city"),
            ("State of Birth", "pob_state"), ("Country of Birth", "pob_country"),
            ("SSN", "ssn"), ("UPIN", "upin"),
            ("Photo Path", "photo_path"), ("Fingerprint Path", "fingerprint_path")
        ]

        for lbl, key in fields:
            ctk.CTkLabel(main, text=lbl).pack()
            e = ctk.CTkEntry(main)
            e.pack(pady=2)
            self.entries[key] = e

        ctk.CTkButton(main, text="Save", command=self.save).pack(pady=20)

    def save(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if not data['first_name'] or not data['last_name']: return

        try:
            add_responsible_person(self.entity_id, data)
            self.parent_view.load_entities() # Reload parent
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
