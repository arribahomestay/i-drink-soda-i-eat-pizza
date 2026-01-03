"""
Users management page for admin view
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS


class UsersPage:
    def __init__(self, parent, database, switch_page_callback):
        self.parent = parent
        self.database = database
        self.switch_page = switch_page_callback
    
    def show(self):
        """Show user management page"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="👥 User Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        add_btn = ctk.CTkButton(
            header,
            text="+ Add Cashier",
            command=self.add_user_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=10
        )
        add_btn.pack(side="right")
        
        # Users table
        table_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Table header
        header_frame = ctk.CTkFrame(table_frame, fg_color=COLORS["dark"], corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        headers = ["ID", "Username", "Full Name", "Role", "Created", "Actions"]
        widths = [50, 150, 200, 100, 180, 150]
        
        for header_text, width in zip(headers, widths):
            ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_primary"],
                width=width
            ).pack(side="left", padx=5, pady=10)
        
        # Users list
        users_list = ctk.CTkScrollableFrame(
            table_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        users_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        users = self.database.get_all_users()
        for user in users:
            self.create_user_row(users_list, user)
    
    def create_user_row(self, parent, user):
        """Create a user row with right-click context menu"""
        import tkinter as tk
        
        # Get user status (check if field exists, default to active)
        is_active = user[5] if len(user) > 5 and user[5] is not None else 1
        
        row = ctk.CTkFrame(parent, fg_color=COLORS["dark"], corner_radius=8)
        row.pack(fill="x", pady=5)
        
        # Add right-click context menu for non-admin users
        if user[2] != "admin":
            def show_context_menu(event):
                menu = tk.Menu(row, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text_primary"],
                              activebackground=COLORS["primary"], activeforeground="white",
                              font=("Segoe UI", 10))
                
                menu.add_command(label="👁️  View Details", command=lambda: self.view_user_details(user))
                menu.add_command(label="✏️  Edit User", command=lambda: self.edit_user_dialog(user))
                menu.add_separator()
                
                # Deactivate or Activate based on current status
                if is_active:
                    menu.add_command(label="🚫 Deactivate Account", command=lambda: self.toggle_user_status(user, False))
                else:
                    menu.add_command(label="✅ Activate Account", command=lambda: self.toggle_user_status(user, True))
                
                menu.add_separator()
                menu.add_command(label="🗑️  Delete User", command=lambda: self.delete_user(user))
                
                menu.post(event.x_root, event.y_root)
            
            row.bind("<Button-3>", show_context_menu)
        
        row_content = ctk.CTkFrame(row, fg_color="transparent")
        row_content.pack(fill="x", padx=5, pady=8)
        
        # Bind right-click to row_content as well
        if user[2] != "admin":
            row_content.bind("<Button-3>", lambda e: show_context_menu(e))
        
        # ID
        id_label = ctk.CTkLabel(
            row_content,
            text=str(user[0]),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=50
        )
        id_label.pack(side="left", padx=5)
        if user[2] != "admin":
            id_label.bind("<Button-3>", lambda e: show_context_menu(e))
        
        # Username with status indicator
        username_text = user[1]
        if not is_active:
            username_text += " (Deactivated)"
        
        username_label = ctk.CTkLabel(
            row_content,
            text=username_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"] if not is_active else COLORS["text_primary"],
            width=150,
            anchor="w"
        )
        username_label.pack(side="left", padx=5)
        if user[2] != "admin":
            username_label.bind("<Button-3>", lambda e: show_context_menu(e))
        
        # Full Name
        fullname_label = ctk.CTkLabel(
            row_content,
            text=user[3] or "N/A",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=200,
            anchor="w"
        )
        fullname_label.pack(side="left", padx=5)
        if user[2] != "admin":
            fullname_label.bind("<Button-3>", lambda e: show_context_menu(e))
        
        # Role
        role_color = COLORS["warning"] if user[2] == "admin" else COLORS["info"]
        role_label = ctk.CTkLabel(
            row_content,
            text=user[2].upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=role_color,
            width=100
        )
        role_label.pack(side="left", padx=5)
        if user[2] != "admin":
            role_label.bind("<Button-3>", lambda e: show_context_menu(e))
        
        # Created date
        created_label = ctk.CTkLabel(
            row_content,
            text=user[4][:16] if user[4] else "N/A",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"],
            width=180
        )
        created_label.pack(side="left", padx=5)
        if user[2] != "admin":
            created_label.bind("<Button-3>", lambda e: show_context_menu(e))
        
        # Actions
        actions_frame = ctk.CTkFrame(row_content, fg_color="transparent", width=150)
        actions_frame.pack(side="left", padx=5)
        
        # Don't allow editing/deleting admin users
        if user[2] != "admin":
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="Edit",
                command=lambda u=user: self.edit_user_dialog(u),
                width=60,
                height=25,
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["primary"],
                corner_radius=5
            )
            edit_btn.pack(side="left", padx=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="Delete",
                command=lambda u=user: self.delete_user(u),
                width=60,
                height=25,
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["danger"],
                corner_radius=5
            )
            delete_btn.pack(side="left", padx=2)
        else:
            protected_label = ctk.CTkLabel(
                actions_frame,
                text="Protected",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"]
            )
            protected_label.pack()
            if user[2] != "admin":
                protected_label.bind("<Button-3>", lambda e: show_context_menu(e))

    
    def add_user_dialog(self):
        """Show add user dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add New Cashier")
        dialog.geometry("450x400")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 450) // 2
        y = (dialog.winfo_screenheight() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        ctk.CTkLabel(
            dialog,
            text="➕ Add New Cashier",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(20, 10))
        
        # Form
        form_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Username
        ctk.CTkLabel(
            form_frame,
            text="Username *",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        username_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        username_entry.pack(fill="x", padx=20, pady=(0, 10))
        username_entry.focus()
        
        # Password
        ctk.CTkLabel(
            form_frame,
            text="Password *",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        password_entry = ctk.CTkEntry(form_frame, height=35, show="*", font=ctk.CTkFont(size=13))
        password_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Full Name
        ctk.CTkLabel(
            form_frame,
            text="Full Name (Optional)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        fullname_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        fullname_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            fullname = fullname_entry.get().strip()
            
            # Validation
            if not username:
                messagebox.showerror("Error", "Username is required")
                return
            
            if not password:
                messagebox.showerror("Error", "Password is required")
                return
            
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            
            # Check if username already exists
            existing_users = self.database.get_all_users()
            if any(u[1].lower() == username.lower() for u in existing_users):
                messagebox.showerror("Error", "Username already exists")
                return
            
            try:
                # Add user with role 'cashier'
                self.database.add_user(username, password, "cashier", fullname or None)
                messagebox.showinfo("Success", f"Cashier '{username}' added successfully!")
                dialog.destroy()
                self.switch_page("users")  # Refresh the page
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add user: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            height=35,
            width=120,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Add Cashier",
            command=save,
            height=35,
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Bind Enter key
        password_entry.bind("<Return>", lambda e: save())
        fullname_entry.bind("<Return>", lambda e: save())
    
    def edit_user_dialog(self, user):
        """Show edit user dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Cashier")
        dialog.geometry("450x450")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 450) // 2
        y = (dialog.winfo_screenheight() - 450) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        ctk.CTkLabel(
            dialog,
            text=f"✏️ Edit Cashier: {user[1]}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(20, 10))
        
        # Form
        form_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Username (read-only)
        ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        username_label = ctk.CTkLabel(
            form_frame,
            text=user[1],
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            height=35,
            anchor="w"
        )
        username_label.pack(fill="x", padx=20, pady=(0, 10))
        
        # New Password (optional)
        ctk.CTkLabel(
            form_frame,
            text="New Password (leave empty to keep current)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        password_entry = ctk.CTkEntry(form_frame, height=35, show="*", font=ctk.CTkFont(size=13))
        password_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Full Name
        ctk.CTkLabel(
            form_frame,
            text="Full Name",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        fullname_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        fullname_entry.pack(fill="x", padx=20, pady=(0, 20))
        fullname_entry.insert(0, user[3] or "")
        fullname_entry.focus()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save():
            new_password = password_entry.get().strip()
            fullname = fullname_entry.get().strip()
            
            # Validation
            if new_password and len(new_password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            
            try:
                # Update user
                if new_password:
                    # Update with new password
                    self.database.update_user_password(user[0], new_password)
                
                # Update full name
                self.database.update_user_fullname(user[0], fullname or None)
                
                messagebox.showinfo("Success", f"Cashier '{user[1]}' updated successfully!")
                dialog.destroy()
                self.switch_page("users")  # Refresh the page
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            height=35,
            width=120,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Update",
            command=save,
            height=35,
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Bind Enter key
        password_entry.bind("<Return>", lambda e: save())
        fullname_entry.bind("<Return>", lambda e: save())
    
    def delete_user(self, user):
        """Delete a user"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{user[1]}'?\n\nThis action cannot be undone."):
            try:
                self.database.delete_user(user[0])
                messagebox.showinfo("Success", "User deleted successfully!")
                self.switch_page("users")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def view_user_details(self, user):
        """Show user details and activity logs"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"User Details - {user[1]}")
        dialog.geometry("700x600")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 700) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=f"👤 {user[1]}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 5))
        
        # User status
        is_active = user[5] if len(user) > 5 and user[5] is not None else 1
        status_text = "Active" if is_active else "Deactivated"
        status_color = COLORS["success"] if is_active else COLORS["danger"]
        
        ctk.CTkLabel(
            header,
            text=status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color
        ).pack(pady=(0, 15))
        
        # Content
        content = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # User Info Section
        info_card = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=10)
        info_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            info_card,
            text="📋 User Information",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        # Info rows
        info_data = [
            ("User ID:", str(user[0])),
            ("Username:", user[1]),
            ("Full Name:", user[3] or "N/A"),
            ("Role:", user[2].upper()),
            ("Created:", user[4][:19] if user[4] else "N/A"),
        ]
        
        for label, value in info_data:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
        
        # Add spacing
        ctk.CTkFrame(info_card, fg_color="transparent", height=10).pack()
        
        # Activity Logs Section
        logs_card = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=10)
        logs_card.pack(fill="both", expand=True, pady=(0, 0))
        
        ctk.CTkLabel(
            logs_card,
            text="📜 Recent Activity (Last 20)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["info"]
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        # Get user's activity logs
        all_logs = self.database.get_activity_logs(limit=200)
        user_logs = [log for log in all_logs if log[1] == user[0]][:20]
        
        if user_logs:
            logs_list = ctk.CTkScrollableFrame(
                logs_card,
                fg_color=COLORS["dark"],
                height=250,
                scrollbar_button_color=COLORS["primary"]
            )
            logs_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            for log in user_logs:
                # log: id, user_id, username, action, details, ip, created_at
                log_row = ctk.CTkFrame(logs_list, fg_color="transparent")
                log_row.pack(fill="x", pady=3)
                
                # Time
                time_str = log[6][:19] if len(log) > 6 and log[6] else "N/A"
                ctk.CTkLabel(
                    log_row,
                    text=time_str,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    width=140,
                    anchor="w"
                ).pack(side="left", padx=5)
                
                # Action
                action_color = COLORS["success"] if "SALE" in log[3] else COLORS["info"]
                ctk.CTkLabel(
                    log_row,
                    text=log[3],
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=action_color,
                    width=120,
                    anchor="w"
                ).pack(side="left", padx=5)
                
                # Details
                details = log[4] if len(log) > 4 else ""
                ctk.CTkLabel(
                    log_row,
                    text=details[:50] + "..." if len(details) > 50 else details,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True, padx=5)
        else:
            ctk.CTkLabel(
                logs_card,
                text="No activity logs found for this user",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(pady=20, padx=15)
        
        # Close button
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)
    
    def toggle_user_status(self, user, activate):
        """Activate or deactivate a user account"""
        action = "activate" if activate else "deactivate"
        status_text = "activated" if activate else "deactivated"
        
        if messagebox.askyesno(
            f"{action.capitalize()} User",
            f"Are you sure you want to {action} user '{user[1]}'?"
        ):
            try:
                # Add is_active column if it doesn't exist
                try:
                    self.database.cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
                    self.database.conn.commit()
                except:
                    pass  # Column already exists
                
                # Update user status
                self.database.cursor.execute(
                    "UPDATE users SET is_active = ? WHERE id = ?",
                    (1 if activate else 0, user[0])
                )
                self.database.conn.commit()
                
                messagebox.showinfo("Success", f"User '{user[1]}' has been {status_text}!")
                self.switch_page("users")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to {action} user: {str(e)}")

