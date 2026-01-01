# Admin View Modular Structure

## Overview
The admin view has been refactored into a modular structure for better maintainability. Each admin page is now a separate module.

## Directory Structure

```
views/
├── admin/
│   ├── __init__.py                 # Module initializer
│   ├── dashboard_page.py           # Dashboard with stats and recent transactions
│   ├── products_page.py            # Products management with categories
│   ├── inventory_page.py           # Inventory management (4 tabs)
│   ├── users_page.py               # User management
│   ├── reports_page.py             # Reports and export functionality
│   ├── transactions_page.py        # Transaction history
│   └── settings_page.py            # Settings (Receipt config & Activity logs)
├── admin_view.py                   # Main coordinator (imports all pages)
├── cashier_view.py                 # Cashier POS interface
└── login_view.py                   # Login screen
```

## Page Modules

### 1. **dashboard_page.py** (DashboardPage)
- Sales summary cards (Total Sales, Transactions, Products, Low Stock)
- Recent transactions list
- Transaction row creation

### 2. **products_page.py** (ProductsPage)
- Category-based product organization
- Left panel: Category folders
- Right panel: Products in selected category
- Product cards with edit/delete actions
- Add category dialog
- **Note:** Add/Edit product dialogs marked as placeholders

### 3. **inventory_page.py** (InventoryPage)
- **4 Tabs:**
  - Overview: Stats + recent adjustments
  - Low Stock: Alert list
  - Adjust Stock: Stock adjustment form (placeholder)
  - Suppliers: Supplier management (placeholder)

### 4. **users_page.py** (UsersPage)
- User list table
- Add/Edit/Delete users
- Protected admin accounts
- **Note:** Add/Edit user dialogs marked as placeholders

### 5. **reports_page.py** (ReportsPage)
- Date range selection (Today, 7 days, 30 days, All time)
- 5 Report types:
  - Sales Summary
  - Transaction List
  - Product Report
  - Cashier Performance
  - Category Analysis
- Export to CSV/Word
- **Note:** Export functionality marked as placeholder

### 6. **transactions_page.py** (TransactionsPage)
- Transaction history list (last 50)
- Transaction details view button
- **Note:** Transaction details dialog marked as placeholder

### 7. **settings_page.py** (SettingsPage)
- **2 Tabs:**
  - Receipt Config: Live preview with form
  - Activity Logs: System activity tracking

## Main Coordinator (admin_view.py)

The main `AdminView` class:
- Creates sidebar navigation
- Manages page switching
- Lazy-loads page instances (created on first access)
- Passes required dependencies to each page

## Benefits of This Structure

1. **Maintainability**: Each page is isolated in its own file
2. **Readability**: Easier to find and modify specific features
3. **Scalability**: Easy to add new pages or features
4. **Testing**: Individual pages can be tested separately
5. **Collaboration**: Multiple developers can work on different pages
6. **File Size**: Reduced from 3,151 lines to ~200 lines per file

## How to Add a New Page

1. Create new file in `views/admin/` (e.g., `new_page.py`)
2. Create class with `__init__(self, parent, database, ...)` and `show(self)` method
3. Import in `admin_view.py`
4. Add navigation button in `setup_ui()`
5. Add switch case in `switch_page()`
6. Add show method (e.g., `show_new_page()`)

## Example: Adding a New Page

```python
# 1. Create views/admin/analytics_page.py
class AnalyticsPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
    
    def show(self):
        # Your page UI here
        pass

# 2. In admin_view.py, add import:
from views.admin.analytics_page import AnalyticsPage

# 3. Add to nav_buttons:
("📊 Analytics", "analytics"),

# 4. Add to switch_page():
elif page == "analytics":
    self.show_analytics()

# 5. Add show method:
def show_analytics(self):
    if "analytics" not in self.pages:
        self.pages["analytics"] = AnalyticsPage(self.content_frame, self.database)
    self.pages["analytics"].show()
```

## Notes

- Some complex dialogs (add/edit product, add/edit user, etc.) are marked as placeholders
- These can be extracted into separate dialog classes if needed
- The original functionality is preserved in the old admin_view.py (backed up)
- All pages use the same color scheme from `config.py`

## Migration Status

✅ Dashboard - Complete
✅ Products - Complete (dialogs as placeholders)
✅ Inventory - Complete (some tabs as placeholders)
✅ Users - Complete (dialogs as placeholders)
✅ Reports - Complete (export as placeholder)
✅ Transactions - Complete (details dialog as placeholder)
✅ Settings - Complete

## Next Steps

To fully implement all features:
1. Implement product add/edit dialogs in products_page.py
2. Implement user add/edit dialogs in users_page.py
3. Implement stock adjustment form in inventory_page.py
4. Implement suppliers management in inventory_page.py
5. Implement export functionality in reports_page.py
6. Implement transaction details dialog in transactions_page.py
