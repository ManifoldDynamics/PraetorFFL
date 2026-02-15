import tkinter as tk
from tkinter import ttk, messagebox
from ffl_suite.logic.settings_manager import get_ffl_info

from ffl_suite.gui.views.acquisition_view import AcquisitionView
from ffl_suite.gui.views.disposition_view import DispositionView
from ffl_suite.gui.views.bound_book_view import BoundBookView
from ffl_suite.gui.views.contacts_view import ContactsView
from ffl_suite.gui.views.settings_view import SettingsView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FFL Suite - Open Source FFL Management")
        self.geometry("1200x800")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.tabs = {}

        self.create_tabs()
        self.check_initial_setup()

    def create_tabs(self):
        # Dashboard (Simple Welcome)
        dashboard = ttk.Frame(self.notebook)
        ttk.Label(dashboard, text="Welcome to FFL Suite", font=("Arial", 24)).pack(pady=50)
        ttk.Label(dashboard, text="Select a tab to begin.", font=("Arial", 14)).pack()
        self.tabs['dashboard'] = dashboard
        self.notebook.add(dashboard, text="Dashboard")

        # Acquisition
        self.tabs['acquisition'] = AcquisitionView(self.notebook)
        self.notebook.add(self.tabs['acquisition'], text="Acquisition")

        # Disposition
        self.tabs['disposition'] = DispositionView(self.notebook)
        self.notebook.add(self.tabs['disposition'], text="Disposition")

        # Bound Book
        self.tabs['bound_book'] = BoundBookView(self.notebook)
        self.notebook.add(self.tabs['bound_book'], text="Bound Book")

        # Contacts
        self.tabs['contacts'] = ContactsView(self.notebook)
        self.notebook.add(self.tabs['contacts'], text="Contacts")

        # Settings
        self.tabs['settings'] = SettingsView(self.notebook)
        self.notebook.add(self.tabs['settings'], text="Settings")

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        # Find which tab is selected
        selected_widget = self.notebook.select()
        widget_name = self.notebook.tab(selected_widget, "text")

        # If the widget has a refresh/load_data method, call it
        # This is a bit hacky because 'selected_widget' is a widget name string in Tkinter usually,
        # but in Python wrapper it might be the widget object or its name.
        # self.notebook.nametowidget(selected_widget) gets the object.

        try:
            widget = self.nametowidget(selected_widget)
            if hasattr(widget, 'load_data'):
                widget.load_data()
            elif hasattr(widget, 'load_contacts'):
                widget.load_contacts()
            # Disposition view doesn't auto-refresh search, which is fine
        except Exception as e:
            # print(f"Error refreshing tab: {e}")
            pass

    def check_initial_setup(self):
        info = get_ffl_info()
        if not info['name'] or not info['license_number']:
            messagebox.showinfo("Welcome", "Welcome to FFL Suite! Please configure your FFL information to get started.")
            self.notebook.select(self.tabs['settings'])

if __name__ == "__main__":
    app = App()
    app.mainloop()
