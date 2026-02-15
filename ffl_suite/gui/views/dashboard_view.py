import customtkinter as ctk
from tkinter import messagebox
from ffl_suite.logic.analytics.dashboard_metrics import (
    get_inventory_count, get_total_acquisitions_count, get_total_dispositions_count,
    get_open_dispositions_warning, get_recent_activity
)

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Grid layout for cards
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Row 0: Metrics Cards
        self.create_card(0, 0, "Current Inventory", "inv_count_label")
        self.create_card(0, 1, "Total Acquisitions", "acq_count_label")
        self.create_card(0, 2, "Total Dispositions", "disp_count_label")

        # Row 1: Warnings / Alerts
        self.create_card(1, 0, "Aged Inventory (>1 Yr)", "aged_count_label", warning=True)

        # Row 2: Recent Activity
        activity_frame = ctk.CTkFrame(self)
        activity_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=20, pady=20)

        ctk.CTkLabel(activity_frame, text="Recent Acquisitions", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Use a Text widget or series of labels for activity since CTK has no treeview yet
        self.activity_container = ctk.CTkScrollableFrame(activity_frame)
        self.activity_container.pack(expand=True, fill='both', padx=10, pady=10)

        # Refresh Button
        ctk.CTkButton(self, text="Refresh Dashboard", command=self.load_data).grid(row=3, column=0, columnspan=3, pady=10)

    def create_card(self, row, col, title, attr_name, warning=False):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))

        color = "red" if warning else ("#3B8ED0" if ctk.get_appearance_mode()=="Light" else "#1F6AA5")
        # In CTK we can set text_color dynamically or just rely on standard themes
        # For warning, explicit red is good.
        text_color = "red" if warning else None

        value_label = ctk.CTkLabel(frame, text="0", font=ctk.CTkFont(size=36, weight="bold"), text_color=text_color)
        value_label.pack(pady=10)

        setattr(self, attr_name, value_label)

    def load_data(self):
        try:
            self.inv_count_label.configure(text=str(get_inventory_count()))
            self.acq_count_label.configure(text=str(get_total_acquisitions_count()))
            self.disp_count_label.configure(text=str(get_total_dispositions_count()))
            self.aged_count_label.configure(text=str(get_open_dispositions_warning()))

            # Clear activity
            for widget in self.activity_container.winfo_children():
                widget.destroy()

            activity = get_recent_activity(limit=5)
            if activity:
                # Header
                header = ctk.CTkFrame(self.activity_container, fg_color="transparent")
                header.pack(fill='x', pady=2)
                ctk.CTkLabel(header, text="Type", width=100, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
                ctk.CTkLabel(header, text="Item", width=300, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
                ctk.CTkLabel(header, text="Date", width=100, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)

                for row in activity:
                    # row: type, item, date
                    row_frame = ctk.CTkFrame(self.activity_container, fg_color="transparent")
                    row_frame.pack(fill='x', pady=2)
                    ctk.CTkLabel(row_frame, text=row[0], width=100, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=row[1], width=300, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=row[2], width=100, anchor="w").pack(side="left", padx=5)
            else:
                 ctk.CTkLabel(self.activity_container, text="No recent activity found.").pack(pady=20)

        except Exception as e:
            print(f"Error loading dashboard: {e}")
