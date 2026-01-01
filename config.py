"""
Configuration settings for the POS application
"""

# Application Settings
APP_NAME = "EJ POS"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1400x800"
MIN_WINDOW_SIZE = (1200, 700)
LOGIN_WINDOW_SIZE = "500x650"

# Theme Settings
THEME_MODE = "dark"  # "light" or "dark"
COLOR_THEME = "blue"  # "blue", "green", "dark-blue"

# Color scheme - Modern Dark Theme (matching login page)
COLORS = {
    # Base colors - Pure black theme
    "dark": "#000000",           # Pure black background (like login page)
    "card_bg": "#1a1a1a",        # Dark card background (like login card)
    "sidebar_bg": "#0a0a0a",     # Slightly darker for sidebar
    
    # Primary colors - Modern blue
    "primary": "#1e88e5",        # Modern blue (matching login buttons)
    "secondary": "#1565c0",      # Darker blue
    
    # Accent colors
    "success": "#00e676",        # Bright green
    "danger": "#ff1744",         # Bright red
    "warning": "#ffc107",        # Amber
    "info": "#00b0ff",           # Cyan blue
    
    # Text colors
    "text_primary": "#ffffff",   # Pure white
    "text_secondary": "#888888", # Gray (matching login subtitle)
    
    # Border colors
    "border": "#2a2a2a",         # Subtle border (like login card border)
}

# Database Settings
DATABASE_NAME = "pos_database.db"

# Default Admin Credentials (Change after first login)
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123",
    "role": "admin"
}

# Default Cashier Credentials
DEFAULT_CASHIER = {
    "username": "cashier",
    "password": "cashier123",
    "role": "cashier"
}

# Tax Settings
TAX_RATE = 0.0  # 0% tax (Tax removed as per request)

# Currency
CURRENCY_SYMBOL = "₱"
