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
        """Show activity history page with lazy loading optimization"""
        from datetime import datetime
        
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
            command=self._force_refresh,
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
        self.activities_list_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        self.activities_list_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Get activity logs from database with caching
        if not hasattr(self, '_activities_cache') or not hasattr(self, '_cache_time'):
            self._activities_cache = self.database.get_activity_logs(limit=500)
            self._cache_time = datetime.now()
        else:
            # Refresh cache if older than 30 seconds
            if (datetime.now() - self._cache_time).seconds > 30:
                self._activities_cache = self.database.get_activity_logs(limit=500)
                self._cache_time = datetime.now()
        
        activities = self._activities_cache
        
        if activities:
            # OPTIMIZATION: Lazy loading with batch rendering
            self._all_activities = activities
            self._rendered_count = 0
            self._batch_size = 20  # Render 20 activities at a time
            
            # Initial batch render
            self._render_next_batch()
            
            # Add "Load More" button if there are more activities
            if len(activities) > self._batch_size:
                load_more_btn = ctk.CTkButton(
                    self.activities_list_frame,
                    text=f"Load More ({len(activities) - self._batch_size} remaining)",
                    command=self._render_next_batch,
                    height=40,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["secondary"]
                )
                load_more_btn.pack(pady=15, padx=20, fill="x")
                self._load_more_btn = load_more_btn
        else:
            ctk.CTkLabel(
                self.activities_list_frame,
                text="No activity logs found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
    
    def _render_next_batch(self):
        """Render the next batch of activities"""
        if not hasattr(self, '_all_activities'):
            return
        
        activities = self._all_activities
        start_idx = self._rendered_count
        end_idx = min(start_idx + self._batch_size, len(activities))
        
        # Remove load more button if it exists
        if hasattr(self, '_load_more_btn') and self._load_more_btn.winfo_exists():
            self._load_more_btn.destroy()
        
        # Render batch
        for i in range(start_idx, end_idx):
            self.create_activity_row(self.activities_list_frame, activities[i])
        
        self._rendered_count = end_idx
        
        # Re-add load more button if there are still more activities
        remaining = len(activities) - self._rendered_count
        if remaining > 0:
            load_more_btn = ctk.CTkButton(
                self.activities_list_frame,
                text=f"Load More ({remaining} remaining)",
                command=self._render_next_batch,
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"],
                hover_color=COLORS["secondary"]
            )
            load_more_btn.pack(pady=15, padx=20, fill="x")
            self._load_more_btn = load_more_btn
    
    def _force_refresh(self):
        """Force refresh by invalidating cache"""
        if hasattr(self, '_activities_cache'):
            delattr(self, '_activities_cache')
        if hasattr(self, '_cache_time'):
            delattr(self, '_cache_time')
        self.show()
    
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
                elif "Regular" in order_type:
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

