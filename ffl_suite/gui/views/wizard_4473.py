import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import date
from ffl_suite.reports.pdf_generator import generate_4473_pdf
from ffl_suite.logic.settings_manager import get_ffl_info
from ffl_suite.logic.transaction_manager import save_draft_4473
from ffl_suite.logic.inventory_manager import get_bound_book, record_disposition

class Wizard4473(ctk.CTkToplevel):
    def __init__(self, parent_view, firearm_id, firearm_data, contact_name, contact_id):
        super().__init__(parent_view)
        self.title("Form 4473 Wizard")
        self.geometry("900x800")
        self.attributes("-topmost", True)

        self.firearm_id = firearm_id
        self.firearm_data = firearm_data
        self.contact_name = contact_name
        self.contact_id = contact_id

        self.data = {
            'transferee_name': contact_name,
            'firearm_id': firearm_id,
            'transfer_date': date.today().isoformat()
        }

        self.current_step = 0
        self.steps = [
            ("Section B (PII)", self.create_step_pii),
            ("Section B (Questions)", self.create_step_questions),
            ("Section C (ID/NICS)", self.create_step_id_nics),
            ("Certification", self.create_step_certify)
        ]

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill='both', expand=True, padx=20, pady=20)

        self.show_step(0)

    def show_step(self, step_idx):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        title, create_func = self.steps[step_idx]

        # Header
        ctk.CTkLabel(self.container, text=f"Step {step_idx + 1}: {title}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # Content
        content_frame = ctk.CTkScrollableFrame(self.container)
        content_frame.pack(fill='both', expand=True, pady=10)
        create_func(content_frame)

        # Navigation
        nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_frame.pack(fill='x', pady=10)

        if step_idx > 0:
            ctk.CTkButton(nav_frame, text="Back", command=lambda: self.change_step(-1)).pack(side='left')

        if step_idx < len(self.steps) - 1:
            ctk.CTkButton(nav_frame, text="Next", command=lambda: self.change_step(1)).pack(side='right')
        else:
            ctk.CTkButton(nav_frame, text="Complete & Generate PDF", fg_color="green", command=self.finish).pack(side='right')

    def change_step(self, delta):
        # Here we could validate current step data before moving
        if delta > 0:
             if not self.save_current_step_data():
                 return
        self.current_step += delta
        self.show_step(self.current_step)

    def save_current_step_data(self):
        # This function would pull data from widgets based on current step
        # Since widgets are dynamic, we need to store references.
        # For simplicity, I'll update self.data inside the widget creation logic or use a shared dict
        # Ideally, we bind variables.
        return True

    def create_step_pii(self, parent):
        fields = [
            ("Full Name", "transferee_name"),
            ("Address", "transferee_address"),
            ("City", "transferee_city"),
            ("State", "transferee_state"),
            ("Zip", "transferee_zip"),
            ("Date of Birth", "transferee_dob"),
            ("Place of Birth", "transferee_pob"),
            ("Height", "transferee_height"),
            ("Weight", "transferee_weight"),
            ("Sex", "transferee_sex"),
            ("Ethnicity", "transferee_ethnicity"),
            ("Race", "transferee_race"),
        ]

        # Need to re-init vars dict if not exists or if re-creating view
        if not hasattr(self, 'pii_vars'): self.pii_vars = {}

        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(parent, text=label).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            if key not in self.pii_vars:
                self.pii_vars[key] = ctk.StringVar(value=self.data.get(key, ""))
            var = self.pii_vars[key]

            entry = ctk.CTkEntry(parent, textvariable=var, width=300)
            entry.grid(row=i, column=1, sticky='w', padx=10, pady=5)

    def create_step_questions(self, parent):
        questions = [
            ("21.a", "Are you the actual transferee/buyer?", "q_21a"),
            ("21.b", "Under indictment for felony?", "q_21b"),
            ("21.c", "Convicted of felony?", "q_21c"),
            ("21.d", "Fugitive from justice?", "q_21d"),
            ("21.e", "Unlawful user of drugs?", "q_21e"),
            ("21.f", "Adjudicated mental defective?", "q_21f"),
            ("21.g", "Dishonorable discharge?", "q_21g"),
            ("21.h", "Restraining order?", "q_21h"),
            ("21.i", "Convicted of domestic violence?", "q_21i"),
            ("21.j", "Renounced citizenship?", "q_21j"),
            ("21.k", "Illegal alien?", "q_21k"),
            ("21.l.1", "Nonimmigrant visa?", "q_21l1"),
        ]

        if not hasattr(self, 'q_vars'): self.q_vars = {}

        for i, (qid, text, key) in enumerate(questions):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill='x', pady=5)
            ctk.CTkLabel(f, text=f"{qid}. {text}", width=400, anchor='w').pack(side='left')

            if key not in self.q_vars:
                self.q_vars[key] = ctk.StringVar(value=self.data.get(key, "No"))
            var = self.q_vars[key]

            ctk.CTkRadioButton(f, text="Yes", variable=var, value="Yes").pack(side='left', padx=5)
            ctk.CTkRadioButton(f, text="No", variable=var, value="No").pack(side='left', padx=5)

    def create_step_id_nics(self, parent):
        fields = [
            ("ID Type (e.g. TX DL)", "id_type"),
            ("ID Number", "id_number"),
            ("Expiration Date", "id_expiration_date"),
            ("NICS NTN", "nics_ntn"),
            ("NICS Status (Proceed/Delayed/Denied)", "nics_status"),
            ("NICS Response Date", "nics_date")
        ]

        if not hasattr(self, 'id_vars'): self.id_vars = {}

        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(parent, text=label).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            if key not in self.id_vars:
                self.id_vars[key] = ctk.StringVar(value=self.data.get(key, ""))
            var = self.id_vars[key]

            entry = ctk.CTkEntry(parent, textvariable=var, width=300)
            entry.grid(row=i, column=1, sticky='w', padx=10, pady=5)

    def create_step_certify(self, parent):
        ctk.CTkLabel(parent, text="Signature").pack(pady=10)

        # Signature Canvas
        self.canvas = ctk.CTkCanvas(parent, width=400, height=150, bg="white")
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.draw)

        ctk.CTkButton(parent, text="Clear Signature", command=lambda: self.canvas.delete("all")).pack(pady=5)

        self.cert_date = date.today().isoformat()
        ctk.CTkLabel(parent, text=f"Date: {self.cert_date}").pack(pady=10)

        self.points = []

    def draw(self, event):
        x, y = event.x, event.y
        r = 2
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")
        self.points.append((x, y))

    def collect_all_data(self):
        # Update self.data from vars
        if hasattr(self, 'pii_vars'):
            for k, v in self.pii_vars.items(): self.data[k] = v.get()
        if hasattr(self, 'q_vars'):
            for k, v in self.q_vars.items(): self.data[k] = v.get()
        if hasattr(self, 'id_vars'):
            for k, v in self.id_vars.items(): self.data[k] = v.get()

        self.data['certification_date'] = date.today().isoformat()
        # Save points as simplistic string for now (SVG path ideally)
        self.data['buyer_signature_svg'] = str(self.points)

    def finish(self):
        self.collect_all_data()

        # 1. Save to DB
        try:
            tid = save_draft_4473(self.data)

            # 2. Record Disposition (if not already done? usually done after)
            record_disposition(self.firearm_id, self.contact_id, date.today().isoformat())

            # 3. Generate PDF
            buyer_data = {'name': self.data['transferee_name']}
            ffl_data = get_ffl_info()

            filename = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"4473_{self.firearm_data['serial']}_FINAL.pdf")
            if filename:
                generate_4473_pdf(filename, self.firearm_data, buyer_data, ffl_data, self.data)
                messagebox.showinfo("Success", "Transaction Complete & PDF Generated.")
                self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete transaction: {e}")
