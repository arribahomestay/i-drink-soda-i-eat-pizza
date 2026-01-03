"""
Main application entry point
"""
import customtkinter as ctk
from config import APP_NAME, WINDOW_SIZE, MIN_WINDOW_SIZE, LOGIN_WINDOW_SIZE, THEME_MODE, COLOR_THEME, COLORS
from database import Database
from views.login_view import LoginView
from views.cashier_view import CashierView
from views.admin_view import AdminView
from tkinter import messagebox


class POSApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(APP_NAME)
        
        # Start with small login window
        self.geometry(LOGIN_WINDOW_SIZE)
        self.resizable(False, False)
        
        # Center the login window
        self.center_window(LOGIN_WINDOW_SIZE)
        
        # Set theme
        ctk.set_appearance_mode(THEME_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        
        # Initialize database
        self.database = Database()
        
        # Current user
        self.current_user = None
        
        # Current view
        self.current_view = None
        
        # Show login view
        self.show_login()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self, size_string):
        """Center the window on screen"""
        self.update_idletasks()
        width, height = map(int, size_string.split('x'))
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def show_login(self):
        """Show login view"""
        if self.current_view:
            self.current_view.destroy()
        
        self.current_view = LoginView(self, self.handle_login)
        self.current_view.pack(fill="both", expand=True)
    
    def handle_login(self, username, password):
        """Handle user login"""
        user = self.database.authenticate_user(username, password)
        
        if user:
            self.current_user = user
            
            # Show appropriate view based on role
            if user['role'] == 'admin':
                self.show_admin_view()
            elif user['role'] == 'cashier':
                self.show_cashier_view()
            else:
                messagebox.showerror("Error", "Invalid user role")
        else:
            self.current_view.show_error("Invalid username or password")
    
    def show_cashier_view(self):
        """Show cashier POS view"""
        if self.current_view:
            self.current_view.destroy()
        
        # Expand window to full size
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.resizable(True, True)
        self.center_window(WINDOW_SIZE)
        
        self.current_view = CashierView(
            self,
            self.database,
            self.current_user,
            self.handle_logout
        )
        self.current_view.pack(fill="both", expand=True)
    
    def show_admin_view(self):
        """Show admin dashboard view"""
        if self.current_view:
            self.current_view.destroy()
        
        # Expand window to full size
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.resizable(True, True)
        self.center_window(WINDOW_SIZE)
        
        self.current_view = AdminView(
            self,
            self.database,
            self.current_user,
            self.handle_logout
        )
        self.current_view.pack(fill="both", expand=True)
    
    def handle_logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            
            # Reset minimum size first
            self.minsize(1, 1)
            
            # Shrink window back to login size
            self.geometry(LOGIN_WINDOW_SIZE)
            self.resizable(False, False)
            self.center_window(LOGIN_WINDOW_SIZE)
            
            self.show_login()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.database.close()
            self.destroy()


def main():
    """Main entry point"""
    try:
        app = POSApplication()
        app.mainloop()
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
