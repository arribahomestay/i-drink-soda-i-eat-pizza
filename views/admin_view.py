"""
Admin view - Dashboard and Management (Refactored)
This is the main admin view that coordinates all admin pages
"""
import customtkinter as ctk
from config import COLORS

# Import all page modules
from views.admin.dashboard_page import DashboardPage
from views.admin.products_page import ProductsPage
from views.admin.modifiers_page import ModifiersPage
from views.admin.inventory_page import InventoryPage
from views.admin.users_page import UsersPage
from views.admin.reports_page import ReportsPage
from views.admin.transactions_page import TransactionsPage
from views.admin.history_page import HistoryPage
from views.admin.settings_page import SettingsPage


class AdminView(ctk.CTkFrame):
    def __init__(self, parent, database, user_data, on_logout):
        super().__init__(parent, fg_color=COLORS["dark"])
        self.database = database
        self.user_data = user_data
        self.on_logout = on_logout
        self.current_page = "dashboard"
        
        # Initialize page instances
        self.pages = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the admin interface"""
        # Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"], width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=30, padx=20)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🛒 POS Admin",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        logo_label.pack()
        
        # User info
        user_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["card_bg"], corner_radius=10)
        user_frame.pack(padx=20, pady=(0, 30), fill="x")
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.user_data['full_name']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        user_label.pack(pady=(15, 5), padx=15)
        
        role_label = ctk.CTkLabel(
            user_frame,
            text="Administrator",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        role_label.pack(pady=(0, 15), padx=15)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", "dashboard"),
            ("📦 Products", "products"),
            ("➕ Modifiers", "modifiers"),
            ("📋 Inventory", "inventory"),
            ("👥 Users", "users"),
            ("📈 Reports", "reports"),
            ("🧾 Transactions", "transactions"),
            ("📜 History", "history"),
            ("⚙️ Settings", "settings"),
        ]
        
        for text, page in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda p=page: self.switch_page(p),
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color=COLORS["primary"],
                corner_radius=10,
                anchor="w"
            )
            btn.pack(padx=20, pady=5, fill="x")
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            command=self.on_logout,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=10
        )
        logout_btn.pack(side="bottom", padx=20, pady=20, fill="x")
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def switch_page(self, page):
        """Switch between different pages"""
        self.current_page = page
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if page == "dashboard":
            self.show_dashboard()
        elif page == "products":
            self.show_products()
        elif page == "modifiers":
            self.show_modifiers()
        elif page == "inventory":
            self.show_inventory()
        elif page == "users":
            self.show_users()
        elif page == "reports":
            self.show_reports()
        elif page == "transactions":
            self.show_transactions()
        elif page == "history":
            self.show_history()
        elif page == "settings":
            self.show_settings()
    
    def show_dashboard(self):
        """Show dashboard page"""
        if "dashboard" not in self.pages:
            self.pages["dashboard"] = DashboardPage(self.content_frame, self.database)
        self.pages["dashboard"].show()
    
    def show_products(self):
        """Show products management page"""
        if "products" not in self.pages:
            self.pages["products"] = ProductsPage(self.content_frame, self.database, self.switch_page)
        self.pages["products"].show()

    def show_modifiers(self):
        """Show modifiers management page"""
        if "modifiers" not in self.pages:
            self.pages["modifiers"] = ModifiersPage(self.content_frame, self.database)
        self.pages["modifiers"].show()
    
    def show_inventory(self):
        """Show inventory management page"""
        if "inventory" not in self.pages:
            self.pages["inventory"] = InventoryPage(self.content_frame, self.database, self.user_data)
        self.pages["inventory"].show()
    
    def show_users(self):
        """Show user management page"""
        if "users" not in self.pages:
            self.pages["users"] = UsersPage(self.content_frame, self.database, self.switch_page)
        self.pages["users"].show()
    
    def show_reports(self):
        """Show reports page"""
        if "reports" not in self.pages:
            self.pages["reports"] = ReportsPage(self.content_frame, self.database)
        self.pages["reports"].show()
    
    
    def show_transactions(self):
        """Show transactions page"""
        if "transactions" not in self.pages:
            self.pages["transactions"] = TransactionsPage(self.content_frame, self.database)
        self.pages["transactions"].show()
    
    def show_history(self):
        """Show activity history page"""
        if "history" not in self.pages:
            self.pages["history"] = HistoryPage(self.content_frame, self.database)
        self.pages["history"].show()
    
    def show_settings(self):
        """Show settings page"""
        if "settings" not in self.pages:
            self.pages["settings"] = SettingsPage(self.content_frame, self.database)
        self.pages["settings"].show()
