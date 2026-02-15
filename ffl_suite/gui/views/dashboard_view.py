import tkinter as tk
from tkinter import ttk, messagebox
from ffl_suite.logic.analytics.dashboard_metrics import (
    get_inventory_count, get_total_acquisitions_count, get_total_dispositions_count,
    get_open_dispositions_warning, get_recent_activity
)

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Create a style for the dashboard cards
        style = ttk.Style()
        style.configure("Card.TFrame", background="#f0f0f0", relief="raised", borderwidth=1)
        style.configure("CardTitle.TLabel", font=("Arial", 12, "bold"), background="#f0f0f0")
        style.configure("CardValue.TLabel", font=("Arial", 24, "bold"), background="#f0f0f0", foreground="#007bff")

        # Grid layout for cards
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Row 0: Metrics Cards
        self.card1 = self.create_card(0, 0, "Current Inventory")
        self.card2 = self.create_card(0, 1, "Total Acquisitions")
        self.card3 = self.create_card(0, 2, "Total Dispositions")

        # Row 1: Warnings / Alerts
        self.card4 = self.create_card(1, 0, "Aged Inventory (>1 Yr)")
        self.card4_value.configure(foreground="#dc3545") # Red for warning

        # Row 2: Recent Activity
        activity_frame = ttk.LabelFrame(self, text="Recent Acquisitions")
        activity_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=20, pady=20)

        self.activity_tree = ttk.Treeview(activity_frame, columns=('type', 'item', 'date'), show='headings', height=5)
        self.activity_tree.heading('type', text='Type')
        self.activity_tree.heading('item', text='Firearm')
        self.activity_tree.heading('date', text='Date')
        self.activity_tree.column('type', width=100)
        self.activity_tree.column('item', width=300)
        self.activity_tree.column('date', width=100)
        self.activity_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Refresh Button
        ttk.Button(self, text="Refresh Dashboard", command=self.load_data).grid(row=3, column=0, columnspan=3, pady=10)

    def create_card(self, row, col, title):
        frame = ttk.Frame(self, style="Card.TFrame", padding=20)
        frame.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)

        # Store widgets in a dict or attributes
        label_title = ttk.Label(frame, text=title, font=("Arial", 12, "bold"))
        label_title.pack()

        value_label = ttk.Label(frame, text="0", font=("Arial", 24, "bold"), foreground="#007bff")
        value_label.pack(pady=10)

        # Assign to specific attribute based on logical ID, not just row/col
        if title == "Current Inventory": self.inv_count_label = value_label
        elif title == "Total Acquisitions": self.acq_count_label = value_label
        elif title == "Total Dispositions": self.disp_count_label = value_label
        elif title == "Aged Inventory (>1 Yr)":
            self.aged_count_label = value_label
            value_label.config(foreground="#dc3545")

        return frame

    def load_data(self):
        try:
            self.inv_count_label.config(text=str(get_inventory_count()))
            self.acq_count_label.config(text=str(get_total_acquisitions_count()))
            self.disp_count_label.config(text=str(get_total_dispositions_count()))
            self.aged_count_label.config(text=str(get_open_dispositions_warning()))

            # Clear tree
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)

            activity = get_recent_activity(limit=5)
            if activity:
                for row in activity:
                    self.activity_tree.insert('', 'end', values=row)
        except Exception as e:
            # In a real app, maybe log this instead of popup on every refresh
            print(f"Error loading dashboard: {e}")
