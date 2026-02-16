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
from ffl_suite.gui.views.gunsmithing_view import GunsmithingView
from ffl_suite.gui.views.po_view import POView
from ffl_suite.gui.views.inventory_view import InventoryView
import os

# Load custom theme
theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'themes', 'modern_saas.json')
ctk.set_default_color_theme(theme_path)
ctk.set_appearance_mode("Dark")

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
        # Modern Floating Sidebar look
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(12, weight=1)

        # Logo Area
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=30)
        ctk.CTkLabel(logo_frame, text="⚡", font=ctk.CTkFont(size=32)).pack(side="left")
        ctk.CTkLabel(logo_frame, text="FFL Suite", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=10)

        self.nav_buttons = {}
        buttons = [
            ("Dashboard", "🏠"),
            ("Inventory", "📦"),
            ("Acquisition", "➕"),
            ("Disposition", "➖"),
            ("Bound Book", "📖"),
            ("Gunsmithing", "🔨"),
            ("Ordering", "🛒"),
            ("NFA Vault", "🔐"),
            ("4473 Forms", "📝"),
            ("Contacts", "👥"),
            ("Settings", "⚙️")
        ]

        for i, (name, icon) in enumerate(buttons):
            # Using styled buttons from theme
            btn = ctk.CTkButton(self.sidebar_frame, corner_radius=10, height=45, border_spacing=15,
                                text=f"{icon}   {name}", font=ctk.CTkFont(size=14, weight="bold"),
                                fg_color="transparent", text_color=("gray50", "gray30"), hover_color=("gray90", "gray20"),
                                anchor="w", command=lambda n=name: self.show_view(n))
            btn.grid(row=i+1, column=0, sticky="ew", padx=15, pady=2)
            self.nav_buttons[name] = btn

        # User/Footer area
        footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color=("gray95", "gray10"), corner_radius=10)
        footer_frame.grid(row=13, column=0, sticky="ew", padx=15, pady=20)
        ctk.CTkLabel(footer_frame, text="Active Profile:", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10, pady=(5,0))
        self.profile_label = ctk.CTkLabel(footer_frame, text=get_ffl_info().get('name', 'Default'), font=ctk.CTkFont(size=12, weight="bold"))
        self.profile_label.pack(anchor="w", padx=10, pady=(0,5))

    def create_main_area(self):
        # Use a background color for the main area to distinct from sidebar
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "#141414"))
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1) # Row 1 is content, Row 0 is header

        # Persistent Header
        self.header_frame = ctk.CTkFrame(self.main_frame, height=60, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 10))
        self.page_title = ctk.CTkLabel(self.header_frame, text="Dashboard", font=ctk.CTkFont(size=28, weight="bold"))
        self.page_title.pack(side="left")

        self.content_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    def show_view(self, name):
        # Update button states (Active Indicator)
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=("white", "#1e293b"), text_color=("#3b82f6", "#3b82f6"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray50", "gray40"))

        # Update Page Title
        self.page_title.configure(text=name)

        # Hide current view
        if self.current_view:
            self.current_view.pack_forget()

        # Create or show view
        if name not in self.views:
            if name == "Dashboard":
                self.views[name] = DashboardView(self.content_area)
            elif name == "Inventory":
                self.views[name] = InventoryView(self.content_area)
            elif name == "Acquisition":
                self.views[name] = AcquisitionView(self.content_area)
            elif name == "Disposition":
                self.views[name] = DispositionView(self.content_area)
            elif name == "Bound Book":
                self.views[name] = BoundBookView(self.content_area)
            elif name == "4473 Forms":
                self.views[name] = Forms4473View(self.content_area)
            elif name == "NFA Vault":
                self.views[name] = NFAVaultView(self.content_area)
            elif name == "Gunsmithing":
                self.views[name] = GunsmithingView(self.content_area)
            elif name == "Ordering":
                self.views[name] = POView(self.content_area)
            elif name == "Contacts":
                self.views[name] = ContactsView(self.content_area)
            elif name == "Settings":
                self.views[name] = SettingsView(self.content_area)

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
