import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ffl_suite.reports.pdf_generator import generate_4473_pdf
from ffl_suite.logic.settings_manager import get_ffl_info

class Wizard4473(tk.Toplevel):
    def __init__(self, parent_view, firearm_id, firearm_data, contact_name, contact_id):
        super().__init__(parent_view)
        self.title("Form 4473 Wizard")
        self.geometry("600x700")

        self.firearm_data = firearm_data
        self.contact_name = contact_name
        self.contact_id = contact_id
        self.answers = {}

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="ATF Form 4473 - Transferee Questions", font=("Arial", 14, "bold")).pack(pady=10)

        # Scrollable frame for questions
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Questions 21.a - 21.m (Simplified text)
        questions = [
            ("21.a", "Are you the actual transferee/buyer of the firearm(s)?"),
            ("21.b", "Are you under indictment/information for a felony?"),
            ("21.c", "Have you ever been convicted of a felony?"),
            ("21.d", "Are you a fugitive from justice?"),
            ("21.e", "Are you an unlawful user of marijuana or any depressant/stimulant/narcotic drug?"),
            ("21.f", "Have you ever been adjudicated as a mental defective or committed to a mental institution?"),
            ("21.g", "Have you been discharged from the Armed Forces under dishonorable conditions?"),
            ("21.h", "Are you subject to a court order restraining you from harassing, stalking, or threatening?"),
            ("21.i", "Have you ever been convicted of a misdemeanor crime of domestic violence?"),
            ("21.j", "Have you ever renounced your United States citizenship?"),
            ("21.k", "Are you an alien illegally or unlawfully in the United States?"),
            ("21.l.1", "Are you an alien who has been admitted to the United States under a nonimmigrant visa?"),
            ("21.l.2", "If 'yes' to 21.l.1, do you fall within any of the exceptions stated in the instructions?"),
        ]

        self.vars = {}
        row = 0
        for q_id, q_text in questions:
            q_frame = ttk.Frame(scroll_frame)
            q_frame.pack(fill='x', pady=5)

            lbl = ttk.Label(q_frame, text=f"{q_id}. {q_text}", wraplength=500)
            lbl.pack(anchor='w')

            var = tk.StringVar(value="No") # Default
            self.vars[q_id] = var

            rb_frame = ttk.Frame(q_frame)
            rb_frame.pack(anchor='w', padx=20)
            ttk.Radiobutton(rb_frame, text="Yes", variable=var, value="Yes").pack(side='left', padx=5)
            ttk.Radiobutton(rb_frame, text="No", variable=var, value="No").pack(side='left', padx=5)
            row += 1

        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=20)
        ttk.Button(btn_frame, text="Generate PDF", command=self.generate).pack(side='right')

    def generate(self):
        # Collect answers
        for q_id, var in self.vars.items():
            self.answers[q_id] = var.get()

        # Basic validation logic (simplified)
        # 21.a must be Yes, most others No.
        if self.answers.get('21.a') == "No":
            messagebox.showwarning("Warning", "Question 21.a is 'No'. Transaction typically prohibited.")

        # Generate PDF
        buyer_data = {'name': self.contact_name}
        ffl_data = get_ffl_info()

        filename = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"4473_{self.firearm_data['serial']}.pdf")
        if filename:
            try:
                generate_4473_pdf(filename, self.firearm_data, buyer_data, ffl_data, self.answers)
                messagebox.showinfo("Success", "4473 Generated.")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF: {e}")
