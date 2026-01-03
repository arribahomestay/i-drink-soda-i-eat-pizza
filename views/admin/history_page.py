"""
Activity History page for admin view
Shows all system activities with timestamps and user information
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS


class HistoryPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
    
    def show(self):
        """Show activity history page"""
        # Clear existing content first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="📜 Activity History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header,
            text="🔄 Refresh",
            command=self.show,
            height=35,
            width=100,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            corner_radius=8
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Main container
        main_container = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Activity list header
        list_header = ctk.CTkFrame(main_container, fg_color=COLORS["dark"], corner_radius=0, height=40)
        list_header.pack(fill="x", padx=0, pady=0)
        list_header.pack_propagate(False)
        
        # Header columns
        header_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        header_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        ctk.CTkLabel(
            header_frame,
            text="Time",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            width=140,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="User",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Action",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Details",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        # Activity list
        activities_list = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        activities_list.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Get activity logs from database
        activities = self.database.get_activity_logs(limit=200)
        
        if activities:
            for activity in activities:
                self.create_activity_row(activities_list, activity)
        else:
            ctk.CTkLabel(
                activities_list,
                text="No activity logs found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
    
    def create_activity_row(self, parent, activity):
        """Create a row for an activity log entry"""
        # activity structure: [id, user_id, username, action, details, timestamp]
        
        # Determine color based on action type
        action_colors = {
            "Login": COLORS["info"],
            "Logout": COLORS["text_secondary"],
            "Stock In": COLORS["success"],
            "Stock Out": COLORS["danger"],
            "Add Product": COLORS["primary"],
            "Edit Product": COLORS["warning"],
            "Delete Product": COLORS["danger"],
            "Add User": COLORS["success"],
            "Edit User": COLORS["warning"],
            "Delete User": COLORS["danger"],
        }
        
        action = activity[3]
        action_color = action_colors.get(action, COLORS["text_primary"])
        
        # Row container
        row = ctk.CTkFrame(parent, fg_color=COLORS["dark"], corner_radius=0, height=35)
        row.pack(fill="x", pady=1, padx=0)
        row.pack_propagate(False)
        
        # Row content
        content = ctk.CTkFrame(row, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=6)
        
        # Timestamp - convert to Manila timezone
        timestamp_raw = activity[6] if len(activity) > 6 else None
        if timestamp_raw:
            try:
                from datetime import datetime, timedelta
                # Parse the UTC timestamp
                dt = datetime.strptime(timestamp_raw, "%Y-%m-%d %H:%M:%S")
                # Add 8 hours for Manila timezone (UTC+8)
                dt_manila = dt + timedelta(hours=8)
                timestamp = dt_manila.strftime("%Y-%m-%d %I:%M:%S %p")
            except:
                timestamp = timestamp_raw
        else:
            timestamp = "N/A"
        
        ctk.CTkLabel(
            content,
            text=timestamp,
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"],
            width=140,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        # Username
        username = activity[2] if len(activity) > 2 else "Unknown"
        ctk.CTkLabel(
            content,
            text=username,
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_primary"],
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        # Action
        ctk.CTkLabel(
            content,
            text=action,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=action_color,
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        # Details - Parse and format with order type highlighting
        details = activity[4] if len(activity) > 4 else ""
        
        # Check if this is a SALE_COMPLETED action and parse order type
        if action == "SALE_COMPLETED" and details:
            # Try to extract order type from details
            # Format: "Transaction TXN... - [OrderType] - [PaymentMethod] - ₱..."
            parts = details.split(" - ")
            if len(parts) >= 3:
                # Create a frame to hold formatted details
                details_frame = ctk.CTkFrame(content, fg_color="transparent")
                details_frame.pack(side="left", fill="x", expand=True)
                
                # Transaction number
                ctk.CTkLabel(
                    details_frame,
                    text=parts[0] + " - ",  # Transaction TXN...
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                ).pack(side="left")
                
                # Order Type with color coding
                order_type = parts[1]
                order_type_color = COLORS["primary"]  # Default
                if "Dine In" in order_type:
                    order_type_color = COLORS["info"]
                elif "Take Out" in order_type:
                    order_type_color = COLORS["warning"]
                elif "Normal" in order_type:
                    order_type_color = COLORS["text_secondary"]
                
                ctk.CTkLabel(
                    details_frame,
                    text=order_type + " - ",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=order_type_color,
                    anchor="w"
                ).pack(side="left")
                
                # Payment method and amount
                remaining = " - ".join(parts[2:])
                ctk.CTkLabel(
                    details_frame,
                    text=remaining,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                ).pack(side="left")
            else:
                # Fallback to regular display
                ctk.CTkLabel(
                    content,
                    text=details,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)
        else:
            # Regular details display for non-sale actions
            ctk.CTkLabel(
                content,
                text=details,
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

