"""
Login view for the POS application
"""
import customtkinter as ctk
from config import COLORS, APP_NAME


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=COLORS["dark"])  # Match app background
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the modern login interface"""
        # Main container - centered
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Modern login card with gradient-like effect
        login_card = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["card_bg"],
            corner_radius=20,
            width=440,
            height=580,
            border_width=0
        )
        login_card.pack()
        login_card.pack_propagate(False)
        
        # Removed top accent bar for cleaner look
        
        # Logo/Icon area
        logo_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        logo_frame.pack(pady=(35, 15))
        
        # Modern icon/logo
        icon_label = ctk.CTkLabel(
            logo_frame,
            text="🛒",
            font=ctk.CTkFont(size=50),
        )
        icon_label.pack()
        
        # App title
        title_label = ctk.CTkLabel(
            login_card,
            text=APP_NAME,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle with gradient-like text
        subtitle_label = ctk.CTkLabel(
            login_card,
            text="Point of Sale System",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        subtitle_label.pack(pady=(0, 35))
        
        # Input container
        input_container = ctk.CTkFrame(login_card, fg_color="transparent")
        input_container.pack(fill="x", padx=35)
        
        # Username field with icon
        username_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        username_frame.pack(fill="x", pady=(0, 18))
        
        username_icon = ctk.CTkLabel(
            username_frame,
            text="👤",
            font=ctk.CTkFont(size=16),
            width=30
        )
        username_icon.pack(side="left", padx=(0, 8))
        
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="Username",
            height=48,
            font=ctk.CTkFont(size=14),
            corner_radius=12,
            border_width=0,
            fg_color="#2a2a2a",
            text_color="#ffffff",
            placeholder_text_color="#666666"
        )
        self.username_entry.pack(side="left", fill="x", expand=True)
        
        # Password field with icon
        password_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, 25))
        
        password_icon = ctk.CTkLabel(
            password_frame,
            text="🔒",
            font=ctk.CTkFont(size=16),
            width=30
        )
        password_icon.pack(side="left", padx=(0, 8))
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Password",
            show="●",
            height=48,
            font=ctk.CTkFont(size=14),
            corner_radius=12,
            border_width=0,
            fg_color="#2a2a2a",
            text_color="#ffffff",
            placeholder_text_color="#666666"
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        # Login button - modern gradient-like
        self.login_button = ctk.CTkButton(
            input_container,
            text="Sign In",
            command=self.handle_login,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            border_width=0
        )
        self.login_button.pack(fill="x", pady=(0, 15))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            input_container,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#ff4444",
            height=20
        )
        self.error_label.pack()
        
        # Removed default login info for cleaner look
        
        # Version/footer
        footer_label = ctk.CTkLabel(
            login_card,
            text="v1.0.0",
            font=ctk.CTkFont(size=9),
            text_color="#444444"
        )
        footer_label.pack(side="bottom", pady=(0, 15))
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Focus on username
        self.username_entry.focus()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.show_error("⚠️ Please enter username and password")
            return
        
        # Call the login callback
        self.on_login_success(username, password)
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.configure(text=message)
        self.after(3000, lambda: self.error_label.configure(text=""))
    
    def clear_fields(self):
        """Clear input fields"""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
