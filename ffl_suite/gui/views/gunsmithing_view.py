import customtkinter as ctk
from tkinter import messagebox
from ffl_suite.logic.gunsmith_manager import get_active_jobs, create_job
from ffl_suite.logic.inventory_manager import search_inventory # To select gun

class GunsmithingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_jobs()

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(header, text="Gunsmithing Jobs", font=ctk.CTkFont(size=24, weight="bold")).pack(side='left')

        ctk.CTkButton(header, text="New Intake", height=40, font=ctk.CTkFont(weight="bold"), command=self.new_intake).pack(side='right')

        # Board (Kanban-lite: Just columns for statuses)
        # Use a container for the board to provide a nice background/padding
        self.board_container = ctk.CTkFrame(self, fg_color="transparent")
        self.board_container.pack(fill='both', expand=True, padx=10, pady=10)

        self.board = ctk.CTkScrollableFrame(self.board_container, fg_color="transparent", orientation="horizontal")
        self.board.pack(fill='both', expand=True)

        self.cols = {}
        statuses = ["Intake", "In Progress", "Waiting Parts", "Completed"]

        for status in statuses:
            # Column Frame (The "Swimlane")
            col = ctk.CTkFrame(self.board, width=320, corner_radius=15, fg_color=("gray90", "#2b2b2b"))
            col.pack(side='left', fill='y', padx=10, pady=10)

            # Header
            header = ctk.CTkFrame(col, height=40, corner_radius=10, fg_color=("gray80", "#1e293b"))
            header.pack(fill='x', padx=5, pady=5)
            ctk.CTkLabel(header, text=status, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

            # Container for cards
            card_container = ctk.CTkScrollableFrame(col, fg_color="transparent")
            card_container.pack(fill='both', expand=True, padx=5, pady=5)
            self.cols[status] = card_container

    def load_jobs(self):
        # Clear
        for s, container in self.cols.items():
            for w in container.winfo_children(): w.destroy()

        jobs = get_active_jobs()
        if jobs:
            for job in jobs:
                # job: id, customer, gun, desc, status, date
                status = job[4]
                if status in self.cols:
                    self.create_job_card(self.cols[status], job)

    def create_job_card(self, parent, job):
        # Card style: Slightly lighter than column background
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("white", "#334155"))
        card.pack(fill='x', pady=5, padx=2)

        # Color strip on left based on status? Maybe later.

        ctk.CTkLabel(card, text=f"Job #{job[0]}", font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray50", "gray40")).pack(anchor='w', padx=10, pady=(10, 0))
        ctk.CTkLabel(card, text=job[1], font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10)
        ctk.CTkLabel(card, text=job[2], font=ctk.CTkFont(size=12)).pack(anchor='w', padx=10)

        # Divider
        ctk.CTkFrame(card, height=1, fg_color=("gray90", "gray40")).pack(fill='x', padx=5, pady=5)

        ctk.CTkLabel(card, text=job[3], font=ctk.CTkFont(size=11, slant="italic"), text_color=("gray40", "gray50")).pack(anchor='w', padx=10, pady=(0, 10))

    def new_intake(self):
        # MVP Dialog
        d = ctk.CTkToplevel(self)
        d.title("New Job")
        d.geometry("400x400")

        ctk.CTkLabel(d, text="Customer ID:").pack()
        cust = ctk.CTkEntry(d)
        cust.pack()

        ctk.CTkLabel(d, text="Firearm ID (Inventory):").pack()
        gun = ctk.CTkEntry(d)
        gun.pack()

        ctk.CTkLabel(d, text="Description:").pack()
        desc = ctk.CTkEntry(d)
        desc.pack()

        def save():
            create_job(cust.get(), gun.get(), desc.get())
            self.load_jobs()
            d.destroy()

        ctk.CTkButton(d, text="Create", command=save).pack(pady=20)
