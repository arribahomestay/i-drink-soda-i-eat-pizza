# EJ POS - Point of Sale System
## Complete Project Overview & Documentation

---

## 📋 Table of Contents
1. [Project Summary](#project-summary)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Database Schema](#database-schema)
6. [User Roles & Authentication](#user-roles--authentication)
7. [Key Features](#key-features)
8. [File Breakdown](#file-breakdown)
9. [Recent Changes & Fixes](#recent-changes--fixes)
10. [Configuration](#configuration)

---

## Project Summary

**EJ POS** is a comprehensive Point of Sale (POS) system built with Python and CustomTkinter. It features a modern dark-themed UI with separate interfaces for cashiers and administrators. The system handles product management, inventory tracking, sales transactions, reporting, and receipt generation.

### Key Capabilities:
- **Dual-role system**: Cashier (POS) and Admin (Management)
- **Product management**: Categories, variants, modifiers, pricing
- **Inventory tracking**: Stock adjustments, suppliers, low-stock alerts
- **Transaction processing**: Multiple payment methods, receipt generation
- **Reporting**: Sales summaries, transaction history, PDF/email reports
- **User management**: Multiple users with role-based access
- **Receipt customization**: Configurable store info and receipt settings

---

## Technology Stack

### Core Technologies:
- **Python 3.x**
- **CustomTkinter** - Modern UI framework (dark theme)
- **SQLite3** - Database management
- **ReportLab** - PDF generation for receipts/reports
- **SMTP** - Email functionality for reports

### Key Libraries:
```python
customtkinter  # Modern UI components
sqlite3        # Database
hashlib        # Password hashing (SHA-256)
datetime       # Date/time handling
smtplib        # Email sending
reportlab      # PDF generation
tkinter        # Base GUI framework
```

---

## Project Structure

```
POINTOFSALE/
├── main.py                          # Application entry point
├── config.py                        # Configuration settings
├── database.py                      # Database management (1131 lines)
├── receipt_generator.py             # Text receipt generation
├── receipt_renderer.py              # PDF receipt rendering
├── email_sender.py                  # Email functionality
├── pos_database.db                  # SQLite database file
│
├── views/                           # UI Components
│   ├── login_view.py               # Login screen
│   ├── cashier_view.py             # Cashier main coordinator (913 lines)
│   ├── admin_view.py               # Admin main coordinator (200 lines)
│   │
│   ├── cashier/                    # Cashier Components (Modular)
│   │   ├── product_grid.py         # Product display & search
│   │   ├── shopping_cart.py        # Cart management
│   │   ├── variant_selector.py     # Product customization dialog
│   │   ├── payment_dialog.py       # Payment processing
│   │   └── README.md               # Cashier module documentation
│   │
│   └── admin/                      # Admin Pages (Modular)
│       ├── dashboard_page.py       # Dashboard with stats
│       ├── products_page.py        # Product management (1893 lines)
│       ├── modifiers_page.py       # Global modifiers
│       ├── inventory_page.py       # Inventory management (4 tabs)
│       ├── users_page.py           # User management
│       ├── reports_page.py         # Reports & analytics
│       ├── transactions_page.py    # Transaction history
│       ├── history_page.py         # Activity logs
│       ├── settings_page.py        # Settings & configuration
│       ├── report_generator.py     # PDF report generation
│       └── README.md               # Admin module documentation
│
├── receipts/                       # Generated receipts folder
├── build/                          # PyInstaller build files
├── dist/                           # Executable distribution
└── .git/                           # Git repository

```

---

## Core Components

### 1. **Main Application (main.py)**
- Entry point for the application
- Manages window sizing and centering
- Handles user authentication flow
- Switches between Login, Cashier, and Admin views
- Manages logout and application closing

**Key Classes:**
- `POSApplication(ctk.CTk)` - Main application window

**Key Methods:**
- `show_login()` - Display login screen
- `handle_login(username, password)` - Authenticate user
- `show_cashier_view()` - Launch cashier interface
- `show_admin_view()` - Launch admin interface
- `handle_logout()` - Return to login screen

---

### 2. **Database Management (database.py)**

**73 Methods** managing all data operations:

#### Core Tables:
1. **users** - User accounts (admin/cashier)
2. **products** - Product catalog with pricing
3. **categories** - Product categories
4. **variants** - Product variants (size, color, etc.)
5. **modifiers** - Product add-ons/modifiers
6. **global_modifiers** - System-wide modifiers
7. **product_prices** - Alternative pricing
8. **transactions** - Sales transactions
9. **transaction_items** - Line items in transactions
10. **suppliers** - Supplier information
11. **stock_adjustments** - Inventory changes
12. **product_ingredients** - Recipe/ingredient links
13. **activity_logs** - System activity tracking
14. **receipt_settings** - Receipt configuration
15. **email_settings** - Email configuration

#### Key Database Methods:
```python
# Authentication
authenticate_user(username, password)

# Products
get_all_products()
add_product(name, category, price, stock, ...)
update_product(product_id, ...)
delete_product(product_id)
search_products(search_term)

# Transactions
create_transaction(cashier_id, items, total, ...)
get_transactions(limit=100)
get_transaction_by_id(transaction_id)

# Inventory
update_product_stock(product_id, quantity_change)
add_stock_adjustment(product_id, type, quantity, ...)
get_low_stock_products(threshold=10)

# Categories
get_all_categories(include_hidden=True)
add_category(name)
rename_category(old_name, new_name)

# Users
get_all_users()
add_user(username, password, role, full_name)
update_user(user_id, ...)

# Reports
get_sales_summary(start_date, end_date)
get_inventory_value()
```

---

### 3. **Login View (login_view.py)**

Modern, centered login interface with:
- Username and password fields
- Modern dark theme with gradient-like effects
- Icon-based input fields (👤 🔒)
- Default credentials display
- Error message handling
- Enter key support

**Default Credentials:**
- Admin: `admin` / `admin123`
- Cashier: `cashier` / `cashier123`

---

### 4. **Cashier View (cashier_view.py)**

**Main Coordinator** for the POS interface with 913 lines.

#### Components:
1. **ProductGrid** - Product display with search
2. **ShoppingCart** - Cart management
3. **VariantSelector** - Product customization
4. **PaymentDialog** - Payment processing

#### Features:
- Real-time product search (by name or barcode)
- Category-based filtering
- Product variants and modifiers
- Shopping cart with quantity controls
- Multiple payment methods (Cash, GCash)
- Receipt generation (text & PDF)
- Transaction history with breakdown
- Ingredient deduction tracking

#### Key Methods:
```python
add_to_cart(product)              # Add product to cart
add_customized_item_to_cart(item) # Add with variants/modifiers
checkout()                         # Process payment
show_items()                       # Display products
show_history()                     # View transaction history
```

---

### 5. **Admin View (admin_view.py)**

**Main Coordinator** for admin dashboard with modular page system.

#### Pages:
1. **Dashboard** - Sales stats, recent transactions
2. **Products** - Product & category management
3. **Modifiers** - Global modifiers management
4. **Inventory** - Stock tracking, adjustments, suppliers
5. **Users** - User account management
6. **Reports** - Sales reports, analytics, exports
7. **Transactions** - Transaction history & details
8. **History** - Activity logs
9. **Settings** - Receipt config, email settings

#### Navigation:
- Sidebar with page buttons
- Lazy-loading of pages (created on first access)
- User info display
- Logout button

---

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock INTEGER DEFAULT 0,
    barcode TEXT,
    description TEXT,
    unit TEXT DEFAULT 'pcs',
    cost REAL DEFAULT 0,
    markup REAL DEFAULT 0,
    supplier_id INTEGER,
    use_stock_tracking INTEGER DEFAULT 1,  -- 1=track stock, 0=availability mode
    is_available INTEGER DEFAULT 1,         -- For availability mode
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    transaction_number TEXT UNIQUE,
    cashier_id INTEGER,
    total_amount REAL,
    tax_amount REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    payment_method TEXT,
    payment_amount REAL,
    change_amount REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'admin' or 'cashier'
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    is_hidden INTEGER DEFAULT 0,  -- 0=visible (Item), 1=hidden (Ingredient)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## User Roles & Authentication

### Roles:
1. **Admin** - Full system access
   - Product management
   - User management
   - Reports and analytics
   - Settings configuration
   - All cashier functions

2. **Cashier** - POS operations only
   - Process sales
   - View transaction history
   - Cannot access admin functions

### Authentication:
- SHA-256 password hashing
- Session-based user tracking
- Role-based view routing
- Logout confirmation

---

## Key Features

### 1. Product Management
- **Categories**: Organize products into folders
  - Mark as "Item" (visible in POS)
  - Mark as "Ingredient" (hidden from POS, used in recipes)
- **Variants**: Size, color, etc. with price adjustments
- **Modifiers**: Add-ons (e.g., extra cheese, toppings)
- **Alternative Pricing**: Multiple price points per product
- **Stock Tracking Modes**:
  - Numeric tracking (decrements on sale)
  - Availability mode (Available/Not Available toggle)
- **Ingredient Linking**: Link products to ingredients for auto-deduction
- **Supplier Management**: Track product suppliers

### 2. Inventory Management
- **Stock Adjustments**: Add/Remove stock with reasons
- **Low Stock Alerts**: Configurable threshold
- **Out of Stock Tracking**: Automatic detection
- **Inventory Value**: Total value calculation
- **Adjustment History**: Full audit trail

### 3. Transaction Processing
- **Multiple Payment Methods**: Cash, GCash
- **Real-time Calculations**: Subtotal, tax, total, change
- **Receipt Generation**: Text and PDF formats
- **Transaction History**: Full transaction log
- **Item Breakdown**: Detailed sales analysis

### 4. Reporting & Analytics
- **Sales Summary**: Total sales, transactions, averages
- **Date Range Filters**: Today, 7 days, 30 days, All time
- **Product Reports**: Sales by product
- **Cashier Performance**: Sales by cashier
- **Category Analysis**: Sales by category
- **PDF Export**: Professional PDF reports
- **Email Reports**: Send reports via email

### 5. Receipt Customization
- **Store Information**: Name, address, phone, email
- **Paper Width**: 58mm or 80mm thermal printers
- **Custom Footer**: Personalized thank you message
- **Logo Support**: Store logo on receipts
- **Tax Configuration**: Adjustable tax rate (currently 0%)

### 6. Activity Logging
- **User Actions**: Login, logout, product changes
- **Stock Changes**: Adjustments, sales
- **Transaction Records**: Full audit trail
- **Timestamp Tracking**: All activities timestamped

---

## File Breakdown

### Root Files

#### **main.py** (155 lines)
- Application entry point
- Window management
- View switching
- Error logging

#### **config.py** (63 lines)
```python
APP_NAME = "EJ POS"
WINDOW_SIZE = "1400x800"
LOGIN_WINDOW_SIZE = "500x650"
THEME_MODE = "dark"
CURRENCY_SYMBOL = "₱"
TAX_RATE = 0.0  # 0% tax

COLORS = {
    "dark": "#000000",
    "card_bg": "#1a1a1a",
    "primary": "#1e88e5",
    "success": "#00e676",
    "danger": "#ff1744",
    ...
}
```

#### **database.py** (1131 lines)
- 73 methods for data operations
- 15 database tables
- Transaction management
- Stock tracking
- User authentication

#### **receipt_generator.py** (124 lines)
- Text-based receipt generation
- Thermal printer formatting
- Store info integration
- Transaction details formatting

#### **receipt_renderer.py** (11,840 bytes)
- PDF receipt generation using ReportLab
- Professional formatting
- Store logo support
- Email-ready PDFs

#### **email_sender.py** (54 lines)
- SMTP email functionality
- Attachment support
- Gmail App Password support
- Error handling

---

### Cashier Components

#### **cashier_view.py** (913 lines)
Main coordinator with:
- Component initialization
- Cart management
- Checkout flow
- History display

#### **product_grid.py** (~165 lines)
- 3-column grid layout
- Real-time search
- Product cards
- Stock level display

#### **shopping_cart.py** (~250 lines)
- Cart item list
- Quantity controls
- Price calculations
- Clear/Checkout buttons

#### **variant_selector.py** (~210 lines)
- Modal dialog
- Variant selection (radio buttons)
- Modifier selection (checkboxes)
- Live price updates

#### **payment_dialog.py** (~280 lines)
- Payment method selection
- Amount input
- Change calculation
- Transaction creation
- Receipt generation

---

### Admin Pages

#### **admin_view.py** (200 lines)
- Sidebar navigation
- Page switching
- Lazy-loading
- User info display

#### **dashboard_page.py** (~400 lines)
- Sales summary cards
- Recent transactions
- Quick stats
- Low stock alerts

#### **products_page.py** (1893 lines)
**Most complex page** with:
- Category management (folders)
- Product CRUD operations
- Variant management
- Modifier management
- Alternative pricing
- Ingredient linking
- Supplier assignment
- Search functionality
- Context menus

**Key Dialogs:**
- Add Product Dialog (compact, multi-field)
- Edit Product Dialog (tabbed: Details, Variants, Modifiers, Prices, Ingredients)
- Add Category Dialog
- Rename Category Dialog

#### **modifiers_page.py** (~300 lines)
- Global modifiers list
- Add/Edit/Delete modifiers
- Product linking
- Quantity deduction

#### **inventory_page.py** (~900 lines)
**4 Tabs:**
1. Overview - Stats + recent adjustments
2. Low Stock - Alert list
3. Adjust Stock - Stock adjustment form
4. Suppliers - Supplier management

#### **users_page.py** (~200 lines)
- User list table
- Add/Edit/Delete users
- Role assignment
- Password management

#### **reports_page.py** (~400 lines)
- Date range selection
- 5 report types
- PDF generation
- Email sending

#### **transactions_page.py** (~400 lines)
- Transaction list
- Transaction details modal
- Modifier details display
- Date filtering

#### **history_page.py** (~200 lines)
- Activity log display
- User filter
- Action filter
- Date range

#### **settings_page.py** (~500 lines)
**2 Tabs:**
1. Receipt Config - Live preview with form
2. Email Settings - SMTP configuration

#### **report_generator.py** (~600 lines)
- PDF report generation
- Multiple report types
- Professional formatting
- Charts and tables

---

## Recent Changes & Fixes

### Recent Conversation History:

1. **Facebook Login Clone** (2026-01-01)
   - Created Facebook login page replica
   - EmailJS integration for credential saving

2. **Refine Email Reports PDF** (2026-01-01)
   - Fixed AttributeError in ReportsPage
   - Fixed transaction modifier display (was showing raw JSON)
   - Upgraded email reports from HTML to PDF
   - Ensured data consistency

3. **Cashier View Product Display Fix** (2026-01-01)
   - Fixed product visibility based on stock tracking mode
   - Products with numeric stock: hidden if stock = 0
   - Products with availability mode: always visible, grayed out if not available
   - Real-time updates from Admin to Cashier view

4. **Product Costing Logic Fix** (2025-12-31)
   - Added `cost` and `markup` columns to products table
   - Updated add/edit product dialogs
   - Fixed price calculations
   - Ensured proper database persistence

5. **Inventory Search Refinements** (2025-12-29)
   - Fixed cropped search results
   - Improved search relevance
   - Added visual indicator for selected product

---

## Configuration

### Application Settings
```python
# Window
WINDOW_SIZE = "1400x800"
MIN_WINDOW_SIZE = (1200, 700)
LOGIN_WINDOW_SIZE = "500x650"

# Theme
THEME_MODE = "dark"
COLOR_THEME = "blue"

# Currency
CURRENCY_SYMBOL = "₱"

# Tax
TAX_RATE = 0.0  # 0% (tax removed)
```

### Database
- **File**: `pos_database.db`
- **Type**: SQLite3
- **Location**: Project root
- **Size**: ~114 KB (with sample data)

### Default Users
```python
# Admin
Username: admin
Password: admin123

# Cashier
Username: cashier
Password: cashier123
```

### Email Settings
- **Server**: smtp.gmail.com
- **Port**: 587
- **TLS**: Enabled
- **Auth**: Gmail App Password required

### Receipt Settings
- **Paper Width**: 58mm or 80mm
- **Format**: Text (.txt) or PDF (.pdf)
- **Storage**: `receipts/` folder

---

## Development Notes

### Code Organization
- **Modular structure**: Separate files for each page/component
- **Lazy loading**: Pages created on first access
- **Callback pattern**: Components communicate via callbacks
- **Single responsibility**: Each file has one clear purpose

### Best Practices
- **Error handling**: Try-catch blocks for database operations
- **User feedback**: Messagebox confirmations for destructive actions
- **Activity logging**: All major actions logged
- **Data validation**: Input validation before database operations

### Performance Optimizations
- **Lazy loading**: Pages only created when needed
- **Efficient queries**: Indexed database columns
- **Minimal redraws**: Only update changed UI elements
- **Search debouncing**: Real-time search with minimal lag

---

## Future Enhancement Ideas

1. **Barcode Scanner Integration**
2. **Customer Display Screen**
3. **Discount/Coupon System**
4. **Multi-store Support**
5. **Cloud Backup**
6. **Mobile App Integration**
7. **Advanced Analytics Dashboard**
8. **Loyalty Program**
9. **Inventory Forecasting**
10. **Multi-currency Support**

---

## Build & Distribution

### PyInstaller Configuration
- **Spec File**: `main.spec`
- **Build Folder**: `build/`
- **Distribution**: `dist/`
- **Executable**: `EJ POS.exe`

### Build Command
```bash
pyinstaller main.spec
```

---

## Summary Statistics

- **Total Lines of Code**: ~10,000+
- **Python Files**: 20+
- **Database Tables**: 15
- **Database Methods**: 73
- **Admin Pages**: 9
- **Cashier Components**: 4
- **User Roles**: 2
- **Payment Methods**: 2
- **Report Types**: 5

---

**Last Updated**: 2026-01-02
**Version**: 1.0.0
**Status**: Production Ready ✅
