import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from ffl_suite.logic.settings_manager import get_ffl_info

from ffl_suite.gui.views.dashboard_view import DashboardView
from ffl_suite.gui.views.acquisition_view import AcquisitionView
from ffl_suite.gui.views.disposition_view import DispositionView
from ffl_suite.gui.views.bound_book_view import BoundBookView
from ffl_suite.gui.views.contacts_view import ContactsView
from ffl_suite.gui.views.settings_view import SettingsView
from ffl_suite.gui.views.forms_4473_view import Forms4473View
from ffl_suite.gui.views.nfa_vault_view import NFAVaultView

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("FFL Suite - Open Source FFL Management")
        self.geometry(f"{1200}x{800}")

        # Configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.create_sidebar()
        self.create_main_area()

        self.views = {}
        self.current_view = None

        # Initial View
        self.show_view("Dashboard")
        self.check_initial_setup()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="FFL Suite", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.nav_buttons = {}
        buttons = ["Dashboard", "Acquisition", "Disposition", "Bound Book", "4473 Forms", "NFA Vault", "Contacts", "Settings"]

        for i, name in enumerate(buttons):
            btn = ctk.CTkButton(self.sidebar_frame, corner_radius=0, height=40, border_spacing=10, text=name,
                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                anchor="w", command=lambda n=name: self.show_view(n))
            btn.grid(row=i+1, column=0, sticky="ew")
            self.nav_buttons[name] = btn

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("System")

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def show_view(self, name):
        # Update button states
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        # Hide current view
        if self.current_view:
            self.current_view.pack_forget()

        # Create or show view
        if name not in self.views:
            if name == "Dashboard":
                self.views[name] = DashboardView(self.main_frame)
            elif name == "Acquisition":
                self.views[name] = AcquisitionView(self.main_frame)
            elif name == "Disposition":
                self.views[name] = DispositionView(self.main_frame)
            elif name == "Bound Book":
                self.views[name] = BoundBookView(self.main_frame)
            elif name == "4473 Forms":
                self.views[name] = Forms4473View(self.main_frame)
            elif name == "NFA Vault":
                self.views[name] = NFAVaultView(self.main_frame)
            elif name == "Contacts":
                self.views[name] = ContactsView(self.main_frame)
            elif name == "Settings":
                self.views[name] = SettingsView(self.main_frame)

        self.current_view = self.views[name]
        self.current_view.pack(expand=True, fill="both")

        # Trigger refresh if applicable
        if hasattr(self.current_view, 'load_data'):
            self.current_view.load_data()
        elif hasattr(self.current_view, 'load_contacts'):
            self.current_view.load_contacts()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def check_initial_setup(self):
        info = get_ffl_info()
        if not info['name'] or not info['license_number']:
            messagebox.showinfo("Welcome", "Welcome to FFL Suite! Please configure your FFL information to get started.")
            self.show_view("Settings")

if __name__ == "__main__":
    app = App()
    app.mainloop()
