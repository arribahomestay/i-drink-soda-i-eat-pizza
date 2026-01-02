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
        """Create a user row"""
        row = ctk.CTkFrame(parent, fg_color=COLORS["dark"], corner_radius=8)
        row.pack(fill="x", pady=5)
        
        row_content = ctk.CTkFrame(row, fg_color="transparent")
        row_content.pack(fill="x", padx=5, pady=8)
        
        # ID
        ctk.CTkLabel(
            row_content,
            text=str(user[0]),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=50
        ).pack(side="left", padx=5)
        
        # Username
        ctk.CTkLabel(
            row_content,
            text=user[1],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_primary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Full Name
        ctk.CTkLabel(
            row_content,
            text=user[3] or "N/A",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=200,
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Role
        role_color = COLORS["warning"] if user[2] == "admin" else COLORS["info"]
        ctk.CTkLabel(
            row_content,
            text=user[2].upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=role_color,
            width=100
        ).pack(side="left", padx=5)
        
        # Created date
        ctk.CTkLabel(
            row_content,
            text=user[4][:16] if user[4] else "N/A",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"],
            width=180
        ).pack(side="left", padx=5)
        
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
            ctk.CTkLabel(
                actions_frame,
                text="Protected",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"]
            ).pack()
    
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
