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
        """Show add user dialog - Placeholder"""
        messagebox.showinfo("Info", "Add user dialog - to be implemented")
    
    def edit_user_dialog(self, user):
        """Show edit user dialog - Placeholder"""
        messagebox.showinfo("Info", f"Edit user dialog for {user[1]} - to be implemented")
    
    def delete_user(self, user):
        """Delete a user"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{user[1]}'?\n\nThis action cannot be undone."):
            try:
                self.database.delete_user(user[0])
                messagebox.showinfo("Success", "User deleted successfully!")
                self.switch_page("users")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
