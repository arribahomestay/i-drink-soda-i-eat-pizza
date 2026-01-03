"""
Database management for the POS application
"""
import sqlite3
import hashlib
from datetime import datetime
from config import DATABASE_NAME, DEFAULT_ADMIN, DEFAULT_CASHIER


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_email_tables()
        self.initialize_default_data()
    
    def create_tables(self):
        """Create all necessary tables"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                barcode TEXT UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_number TEXT UNIQUE NOT NULL,
                cashier_id INTEGER,
                total_amount REAL NOT NULL,
                tax_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                payment_method TEXT,
                order_type TEXT DEFAULT 'Regular',
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cashier_id) REFERENCES users(id)
            )
        ''')
        
        # Transaction items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                product_id INTEGER,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Migration: Add new columns to transaction_items if they don't exist (for Variant Tracking)
        try:
            self.cursor.execute("ALTER TABLE transaction_items ADD COLUMN variant_id INTEGER")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE transaction_items ADD COLUMN variant_name TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE transaction_items ADD COLUMN modifiers TEXT")
        except: pass
        
        # Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_hidden INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration: Add is_hidden to categories if not exists
        try:
            self.cursor.execute("ALTER TABLE categories ADD COLUMN is_hidden INTEGER DEFAULT 0")
        except: pass
        
        # Migration: Add use_stock_tracking to products if not exists
        try:
            self.cursor.execute("ALTER TABLE products ADD COLUMN use_stock_tracking INTEGER DEFAULT 1")
        except: pass
        
        # Migration: Add is_available to products if not exists (for non-stock items)
        try:
            self.cursor.execute("ALTER TABLE products ADD COLUMN is_available INTEGER DEFAULT 1")
        except: pass

        # Migration: Add payment_amount and change_amount to transactions
        try:
            self.cursor.execute("ALTER TABLE transactions ADD COLUMN payment_amount REAL DEFAULT 0")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE transactions ADD COLUMN change_amount REAL DEFAULT 0")
        except: pass
        
        # Product Variants table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                variant_name TEXT NOT NULL,
                variant_value TEXT NOT NULL,
                price_adjustment REAL DEFAULT 0,
                stock INTEGER DEFAULT 0,
                sku TEXT UNIQUE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        # Product Modifiers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_modifiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                modifier_name TEXT NOT NULL,
                modifier_price REAL DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        # Product Ingredients table (Linked Products)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                ingredient_id INTEGER,
                quantity REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                FOREIGN KEY (ingredient_id) REFERENCES products(id)
            )
        ''')
        
        # Activity Logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Purchase Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT UNIQUE NOT NULL,
                supplier_id INTEGER,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')
        
        # Purchase Order Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Stock Adjustments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                adjustment_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                reason TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Receipt Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipt_settings (
                id INTEGER PRIMARY KEY,
                store_name TEXT DEFAULT 'My Store',
                store_address TEXT,
                store_phone TEXT,
                store_email TEXT,
                tax_rate REAL DEFAULT 0,
                receipt_footer TEXT,
                logo_path TEXT,
                paper_width INTEGER DEFAULT 80,
                show_barcode INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default receipt settings if not exists
        self.cursor.execute('''
            INSERT OR IGNORE INTO receipt_settings (id, store_name) 
            VALUES (1, 'My POS Store')
        ''')
        
        # Migration: Add unit to products if not exists
        try:
            self.cursor.execute("ALTER TABLE products ADD COLUMN unit TEXT DEFAULT 'pcs'")
        except: pass
        
        # Migration: Add cost and markup to products
        try:
            self.cursor.execute("ALTER TABLE products ADD COLUMN cost REAL DEFAULT 0")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE products ADD COLUMN markup REAL DEFAULT 0")
        except: pass
        
        # Migration: Add linked_product_id to modifiers for inventory tracking
        try:
            self.cursor.execute("ALTER TABLE product_modifiers ADD COLUMN linked_product_id INTEGER")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE product_modifiers ADD COLUMN deduct_quantity REAL DEFAULT 1")
        except: pass
        
        # Migration: Add supplier_id to products
        try:
            self.cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER")
        except: pass
        
        # Migration: Add order_type to transactions
        try:
            self.cursor.execute("ALTER TABLE transactions ADD COLUMN order_type TEXT DEFAULT 'Regular'")
        except: pass
        
        # Product Prices table (Alternative Prices)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                name TEXT NOT NULL,
                cost REAL DEFAULT 0,
                markup REAL DEFAULT 0,
                price REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')

        # Global Modifiers table (General Add-ons)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_modifiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL DEFAULT 0,
                linked_product_id INTEGER,
                deduct_quantity REAL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (linked_product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        ''')

        self.conn.commit()

    def add_product_price(self, product_id, name, cost, markup, price):
        """Add an alternative price for a product"""
        self.cursor.execute("""
            INSERT INTO product_prices (product_id, name, cost, markup, price)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, name, cost, markup, price))
        self.conn.commit()
    
    def get_product_prices(self, product_id):
        """Get all alternative prices for a product"""
        self.cursor.execute("SELECT * FROM product_prices WHERE product_id = ?", (product_id,))
        return self.cursor.fetchall()
    
    def delete_product_price(self, price_id):
        """Delete an alternative price"""
        self.cursor.execute("DELETE FROM product_prices WHERE id = ?", (price_id,))
        self.conn.commit()

    # --- Global Modifiers ---
    def add_global_modifier(self, name, price, linked_product_id=None, deduct_quantity=1):
        """Add a global modifier"""
        self.cursor.execute("""
            INSERT INTO global_modifiers (name, price, linked_product_id, deduct_quantity)
            VALUES (?, ?, ?, ?)
        """, (name, price, linked_product_id, deduct_quantity))
        self.conn.commit()
    
    def get_all_global_modifiers(self):
        """Get all global modifiers with linked product info"""
        self.cursor.execute("""
            SELECT m.id, m.name, m.price, m.linked_product_id, COALESCE(m.deduct_quantity, 1), m.created_at, p.name as linked_name, p.stock as linked_stock 
            FROM global_modifiers m
            LEFT JOIN products p ON m.linked_product_id = p.id
            ORDER BY m.name
        """)
        return self.cursor.fetchall()
        
    def update_global_modifier(self, mod_id, name, price, linked_product_id, deduct_quantity):
        """Update a global modifier"""
        self.cursor.execute("""
            UPDATE global_modifiers 
            SET name=?, price=?, linked_product_id=?, deduct_quantity=?
            WHERE id=?
        """, (name, price, linked_product_id, deduct_quantity, mod_id))
        self.conn.commit()

    def delete_global_modifier(self, mod_id):
        """Delete a global modifier"""
        self.cursor.execute("DELETE FROM global_modifiers WHERE id=?", (mod_id,))
        self.conn.commit()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_email_tables(self):
        """Create email settings table"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_settings (
                id INTEGER PRIMARY KEY,
                sender_email TEXT,
                sender_password TEXT,
                receiver_email TEXT,
                smtp_server TEXT DEFAULT 'smtp.gmail.com',
                smtp_port INTEGER DEFAULT 587,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Insert default row
        self.cursor.execute("INSERT OR IGNORE INTO email_settings (id) VALUES (1)")
        self.conn.commit()
    
    def get_email_settings(self):
        """Get email configuration"""
        self.cursor.execute("SELECT * FROM email_settings WHERE id = 1")
        return self.cursor.fetchone()
        
    def save_email_settings(self, sender, password, receiver, server="smtp.gmail.com", port=587):
        """Save email configuration"""
        self.cursor.execute("""
            UPDATE email_settings 
            SET sender_email = ?, sender_password = ?, receiver_email = ?, smtp_server = ?, smtp_port = ?
            WHERE id = 1
        """, (sender, password, receiver, server, port))
        self.conn.commit()

    def initialize_default_data(self):
        """Initialize default users and sample products"""
        # ... (keep existing initialization)
        # Add default admin
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                (DEFAULT_ADMIN["username"], 
                 self.hash_password(DEFAULT_ADMIN["password"]), 
                 DEFAULT_ADMIN["role"],
                 "System Administrator")
            )
        except sqlite3.IntegrityError:
            pass  # User already exists
        
        # Add default cashier
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                (DEFAULT_CASHIER["username"], 
                 self.hash_password(DEFAULT_CASHIER["password"]), 
                 DEFAULT_CASHIER["role"],
                 "Default Cashier")
            )
        except sqlite3.IntegrityError:
            pass
        
        self.conn.commit()
    
    def authenticate_user(self, username, password):
        """Authenticate user and return user data"""
        hashed_password = self.hash_password(password)
        
        # Add is_active column if it doesn't exist (migration)
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
            self.conn.commit()
        except:
            pass  # Column already exists
        
        self.cursor.execute(
            "SELECT id, username, role, full_name, is_active FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        result = self.cursor.fetchone()
        if result:
            # Check if user is active (default to active if column doesn't exist)
            is_active = result[4] if len(result) > 4 and result[4] is not None else 1
            
            if not is_active:
                return {"error": "deactivated"}
            
            return {
                "id": result[0],
                "username": result[1],
                "role": result[2],
                "full_name": result[3]
            }
        return None
    


    def get_products_by_supplier(self, supplier_id):
        """Get products linked to a supplier"""
        self.cursor.execute("""
            SELECT id, name, category, price, stock, barcode, description, created_at, 
                   unit, cost, markup, supplier_id, use_stock_tracking, is_available 
            FROM products 
            WHERE supplier_id = ? 
            ORDER BY name
        """, (supplier_id,))
        return self.cursor.fetchall()
    
    def get_all_products(self):
        """Get all products"""
        # Use explicit column names to ensure consistent ordering
        # Order: id, name, category, price, stock, barcode, description, created_at, unit, cost, markup, supplier_id, use_stock_tracking, is_available
        self.cursor.execute("""
            SELECT id, name, category, price, stock, barcode, description, created_at, 
                   unit, cost, markup, supplier_id, use_stock_tracking, is_available 
            FROM products 
            ORDER BY name
        """)
        return self.cursor.fetchall()
    
    def search_products(self, search_term):
        """Search products by name or barcode"""
        self.cursor.execute("""
            SELECT id, name, category, price, stock, barcode, description, created_at, 
                   unit, cost, markup, supplier_id, use_stock_tracking, is_available 
            FROM products 
            WHERE name LIKE ? OR barcode LIKE ? 
            ORDER BY name
        """, (f"%{search_term}%", f"%{search_term}%"))
        return self.cursor.fetchall()
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        self.cursor.execute("""
            SELECT id, name, category, price, stock, barcode, description, created_at, 
                   unit, cost, markup, supplier_id, use_stock_tracking, is_available 
            FROM products 
            WHERE id = ?
        """, (product_id,))
        return self.cursor.fetchone()
    
    def update_product_stock(self, product_id, quantity_change):
        """Update product stock"""
        self.cursor.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (quantity_change, product_id)
        )
        self.conn.commit()
    
    def add_product(self, name, category, price, stock, barcode, description, unit="pcs", cost=0, markup=0, supplier_id=None, use_stock_tracking=1, is_available=1):
        """Add new product"""
        self.cursor.execute(
            """INSERT INTO products (name, category, price, stock, barcode, description, unit, cost, markup, supplier_id, use_stock_tracking, is_available) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, category, price, stock, barcode, description, unit, cost, markup, supplier_id, use_stock_tracking, is_available)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_product(self, product_id, name, category, price, stock, barcode, description, unit="pcs", cost=0, markup=0, supplier_id=None, use_stock_tracking=1, is_available=1):
        """Update product"""
        self.cursor.execute(
            """UPDATE products SET name=?, category=?, price=?, stock=?, barcode=?, description=?, unit=?, cost=?, markup=?, supplier_id=?, use_stock_tracking=?, is_available=? 
               WHERE id=?""",
            (name, category, price, stock, barcode, description, unit, cost, markup, supplier_id, use_stock_tracking, is_available, product_id)
        )
        self.conn.commit()
    
    def delete_product(self, product_id):
        """Delete product"""
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()
    
    def create_transaction(self, cashier_id, items, total_amount, tax_amount, discount_amount, payment_method):
        """Create a new transaction"""
        transaction_number = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.cursor.execute(
            """INSERT INTO transactions 
               (transaction_number, cashier_id, total_amount, tax_amount, discount_amount, payment_method) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (transaction_number, cashier_id, total_amount, tax_amount, discount_amount, payment_method)
        )
        transaction_id = self.cursor.lastrowid
        
        for item in items:
            # Prepare modifiers text and deduct stock for linked modifiers
            modifiers_str = ""
            if item.get('selected_modifiers'):
                # Handle list of dicts (new format) or list of lists (old format, fallback)
                mod_list = item['selected_modifiers']
                str_parts = []
                for m in mod_list:
                    # New format: dict
                    if isinstance(m, dict):
                        m_name = m.get('name', 'Unknown')
                        m_qty = m.get('quantity', 1)
                        if m_qty > 1: m_name += f" ({m_qty}x)"
                        str_parts.append(m_name)
                        
                        # Deduct linked stock
                        if m.get('linked_product_id'):
                            deduct_factor = m.get('deduct_qty', 1)
                            total_deduct = m_qty * item['quantity'] * deduct_factor
                            self.update_product_stock(m['linked_product_id'], -total_deduct)
                    else:
                        # Fallback for old simple list format implies plain name?
                        pass
                modifiers_str = ", ".join(str_parts)

            self.cursor.execute(
                """INSERT INTO transaction_items 
                   (transaction_id, product_id, product_name, quantity, unit_price, subtotal, modifiers, variant_name) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (transaction_id, item['product_id'], item['name'], 
                 item['quantity'], item['price'], item['subtotal'], 
                 modifiers_str, "") # Variant name empty for now
            )
            # Update main product stock
            self.update_product_stock(item['product_id'], -item['quantity'])
        
        self.conn.commit()
        return transaction_number
    
    def get_transactions(self, limit=100):
        """Get recent transactions"""
        self.cursor.execute(
            """SELECT t.id, t.transaction_number, t.cashier_id, t.total_amount, 
                      t.tax_amount, t.discount_amount, t.payment_method, t.order_type,
                      t.status, t.created_at, u.username as cashier_name 
               FROM transactions t 
               LEFT JOIN users u ON t.cashier_id = u.id 
               ORDER BY t.created_at DESC LIMIT ?""",
            (limit,)
        )
        return self.cursor.fetchall()
    
    def get_transactions_by_cashier(self, cashier_id, limit=100):
        """Get transactions for a specific cashier"""
        self.cursor.execute(
            """SELECT t.id, t.transaction_number, t.cashier_id, t.total_amount, 
                      t.tax_amount, t.discount_amount, t.payment_method, t.order_type,
                      t.status, t.created_at, u.username as cashier_name 
               FROM transactions t 
               LEFT JOIN users u ON t.cashier_id = u.id 
               WHERE t.cashier_id = ?
               ORDER BY t.created_at DESC LIMIT ?""",
            (cashier_id, limit)
        )
        return self.cursor.fetchall()
    
    def get_transaction_by_id(self, transaction_id):
        """Get single transaction by ID"""
        self.cursor.execute(
            """SELECT t.id, t.transaction_number, t.cashier_id, t.total_amount, 
                      t.tax_amount, t.discount_amount, t.payment_method, t.order_type,
                      t.created_at, u.username, u.full_name, t.payment_amount, t.change_amount
               FROM transactions t
               LEFT JOIN users u ON t.cashier_id = u.id
               WHERE t.id = ?""",
            (transaction_id,)
        )
        return self.cursor.fetchone()

    def get_transaction_items(self, transaction_id):
        """Get items for a specific transaction"""
        self.cursor.execute(
            "SELECT * FROM transaction_items WHERE transaction_id = ?",
            (transaction_id,)
        )
        return self.cursor.fetchall()
    
    def get_sales_summary(self, start_date=None, end_date=None):
        """Get sales summary for reporting"""
        if start_date and end_date:
            self.cursor.execute(
                """SELECT COUNT(*) as total_transactions, 
                          SUM(total_amount) as total_sales,
                          SUM(tax_amount) as total_tax,
                          AVG(total_amount) as avg_transaction
                   FROM transactions 
                   WHERE DATE(created_at) BETWEEN ? AND ?""",
                (start_date, end_date)
            )
        else:
            self.cursor.execute(
                """SELECT COUNT(*) as total_transactions, 
                          SUM(total_amount) as total_sales,
                          SUM(tax_amount) as total_tax,
                          AVG(total_amount) as avg_transaction
                   FROM transactions"""
            )
        return self.cursor.fetchone()
    
    def get_product_type_sales_count(self, start_date=None, end_date=None):
        """Get sales count grouped by product type (stock tracking vs availability)"""
        if start_date and end_date:
            self.cursor.execute("""
                SELECT p.use_stock_tracking, SUM(ti.quantity) as total_quantity
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                JOIN transactions t ON ti.transaction_id = t.id
                WHERE DATE(t.created_at) BETWEEN ? AND ?
                GROUP BY p.use_stock_tracking
            """, (start_date, end_date))
        else:
            self.cursor.execute("""
                SELECT p.use_stock_tracking, SUM(ti.quantity) as total_quantity
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                GROUP BY p.use_stock_tracking
            """)
        return self.cursor.fetchall()
    
    def get_transactions_by_date(self, start_date, end_date, limit=100):
        """Get transactions within a date range"""
        self.cursor.execute(
            """SELECT t.id, t.transaction_number, t.cashier_id, t.total_amount, 
                      t.tax_amount, t.discount_amount, t.payment_method, t.order_type,
                      t.status, t.created_at, u.username as cashier_name 
               FROM transactions t 
               LEFT JOIN users u ON t.cashier_id = u.id 
               WHERE DATE(t.created_at) BETWEEN ? AND ?
               ORDER BY t.created_at DESC LIMIT ?""",
            (start_date, end_date, limit)
        )
        return self.cursor.fetchall()
    
    def get_all_users(self):
        """Get all users"""
        # Ensure is_active column exists
        try:
            self.cursor.execute("SELECT is_active FROM users LIMIT 1")
        except:
            try:
                self.cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
                self.conn.commit()
            except: pass
            
        self.cursor.execute("SELECT id, username, role, full_name, created_at, is_active FROM users ORDER BY created_at DESC")
        return self.cursor.fetchall()

    def update_user_status(self, user_id, is_active):
        """Update user active status"""
        self.cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if is_active else 0, user_id))
        self.conn.commit()

    def get_user_by_username(self, username):
        """Get user by username to check status"""
        try: self.cursor.execute("SELECT id, username, role, full_name, is_active FROM users WHERE username = ?", (username,))
        except: return None # Table/Column issue
        return self.cursor.fetchone()
    
    def get_cashier_users(self):
        """Get all cashier users"""
        self.cursor.execute("SELECT id, username, role, full_name, created_at FROM users WHERE role = 'cashier' ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def add_user(self, username, password, role, full_name):
        """Add new user"""
        hashed_password = self.hash_password(password)
        self.cursor.execute(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            (username, hashed_password, role, full_name)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_user(self, user_id, username, role, full_name, password=None):
        """Update user (password optional)"""
        if password:
            hashed_password = self.hash_password(password)
            self.cursor.execute(
                "UPDATE users SET username=?, password=?, role=?, full_name=? WHERE id=?",
                (username, hashed_password, role, full_name, user_id)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET username=?, role=?, full_name=? WHERE id=?",
                (username, role, full_name, user_id)
            )
        self.conn.commit()
    
    def delete_user(self, user_id):
        """Delete user"""
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        self.cursor.execute("SELECT id, username, role, full_name, created_at FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def get_all_categories(self, include_hidden=True):
        """Get all categories"""
        if include_hidden:
            self.cursor.execute("SELECT id, name, is_hidden FROM categories ORDER BY name")
        else:
            self.cursor.execute("SELECT id, name, is_hidden FROM categories WHERE is_hidden = 0 ORDER BY name")
        return self.cursor.fetchall()
    
    def add_category(self, name):
        """Add new category"""
        self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def delete_category(self, category_id):
        """Delete category and its products (CASCADE)"""
        # Get category name first to delete products
        self.cursor.execute("SELECT name FROM categories WHERE id=?", (category_id,))
        res = self.cursor.fetchone()
        if res:
            cat_name = res[0]
            # Delete products in this category
            self.cursor.execute("DELETE FROM products WHERE category = ?", (cat_name,))
            # Delete category
            self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            self.conn.commit()
            
    def rename_category(self, old_name, new_name):
        """Rename a category and update all linked products"""
        try:
            # Atomic update
            self.cursor.execute("UPDATE categories SET name = ? WHERE name = ?", (new_name, old_name))
            self.cursor.execute("UPDATE products SET category = ? WHERE category = ?", (new_name, old_name))
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False
            
    def toggle_category_visibility(self, category_id, is_hidden):
        """Toggle category visibility"""
        self.cursor.execute("UPDATE categories SET is_hidden = ? WHERE id = ?", (1 if is_hidden else 0, category_id))
        self.conn.commit()

    def get_category_by_name(self, name):
        """Get category by name"""
        self.cursor.execute("SELECT id, name, is_hidden FROM categories WHERE name = ?", (name,))
        return self.cursor.fetchone()
    
    # Activity Logs
    def log_activity(self, user_id, username, action, details=""):
        """Log user activity"""
        self.cursor.execute("""
            INSERT INTO activity_logs (user_id, username, action, details)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, action, details))
        self.conn.commit()
    
    def get_activity_logs(self, limit=100):
        """Get recent activity logs"""
        self.cursor.execute("""
            SELECT * FROM activity_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()
    
    # Receipt Settings
    def get_receipt_settings(self):
        """Get receipt settings"""
        self.cursor.execute("SELECT * FROM receipt_settings WHERE id = 1")
        return self.cursor.fetchone()
    
    def update_receipt_settings(self, store_name, store_address, store_phone, 
                               store_email, tax_rate, receipt_footer, paper_width):
        """Update receipt settings"""
        self.cursor.execute("""
            UPDATE receipt_settings 
            SET store_name = ?, store_address = ?, store_phone = ?,
                store_email = ?, tax_rate = ?, receipt_footer = ?,
                paper_width = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (store_name, store_address, store_phone, store_email, 
              tax_rate, receipt_footer, paper_width))
        self.conn.commit()
    
    # Enhanced transaction with payment details
    def add_transaction_with_payment(self, transaction_number, cashier_id, items, 
                                    payment_method, payment_amount, change_amount,
                                    tax_rate=0, discount_amount=0, order_type="Regular"):
        """Add transaction with payment details"""
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount - discount_amount
        
        # Insert transaction
        self.cursor.execute("""
            INSERT INTO transactions 
            (transaction_number, cashier_id, total_amount, tax_amount, 
             discount_amount, payment_method, order_type, status, payment_amount, change_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'completed', ?, ?)
        """, (transaction_number, cashier_id, total, tax_amount, discount_amount, payment_method, order_type, payment_amount, change_amount))
        
        transaction_id = self.cursor.lastrowid
        
        # Insert transaction items
        for item in items:
            # Extract optional variant info
            variant_id = item.get('variant_id')
            variant_name = item.get('variant_name')
            modifiers = item.get('modifiers')

            self.cursor.execute("""
                INSERT INTO transaction_items 
                (transaction_id, product_id, product_name, quantity, unit_price, subtotal, variant_id, variant_name, modifiers)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id, item['id'], item['name'], item['quantity'], 
                  item['price'], item['price'] * item['quantity'], 
                  variant_id, variant_name, modifiers))
            
            
            # Update MAIN PRODUCT stock (Prevent negative)
            self.cursor.execute("""
                UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?
            """, (item['quantity'], item['id']))

            # Update VARIANT stock (Critical Fix)
            if variant_id:
                self.cursor.execute("""
                    UPDATE product_variants SET stock = MAX(0, stock - ?) WHERE id = ?
                """, (item['quantity'], variant_id))
            
            # Deduct LINKED INGREDIENTS stock
            # Get all ingredients linked to this product
            ingredients = self.get_product_ingredients(item['id'])
            for ingredient in ingredients:
                # ingredient structure: [link_id, ingredient_id, ingredient_name, quantity_per_product, price, cost]
                ingredient_id = ingredient[1]
                qty_per_product = ingredient[3]
                # Total to deduct = quantity of product sold * quantity of ingredient per product
                total_deduct = item['quantity'] * qty_per_product
                self.cursor.execute("""
                    UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?
                """, (total_deduct, ingredient_id))

            # Deduct MODIFIER linked stock (Add-ons)
            if item.get('selected_modifiers'):
                for m in item['selected_modifiers']:
                    # m should be a dict with linked info
                    if isinstance(m, dict):
                        # Fallback for missing link info
                        if not m.get('linked_product_id') and m.get('id'):
                            try:
                                self.cursor.execute("SELECT linked_product_id, COALESCE(deduct_quantity, 1) FROM global_modifiers WHERE id=?", (m['id'],))
                                row = self.cursor.fetchone()
                                if row:
                                    m['linked_product_id'] = row[0]
                                    m['deduct_qty'] = row[1]
                            except: pass

                        if m.get('linked_product_id'):
                            try:
                                linked_pid = int(m['linked_product_id'])
                                m_qty = float(m.get('quantity') or 1)
                                deduct_factor = float(m.get('deduct_qty') or 1)
                                item_qty = float(item.get('quantity') or 1)
                                
                                total_mod_deduct = item_qty * m_qty * deduct_factor
                                
                                self.cursor.execute("""
                                    UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?
                                """, (total_mod_deduct, linked_pid))
                            except Exception:
                                pass # Prevent crash on bad data
        
        self.conn.commit()
        return transaction_id
    
    def get_transaction_details(self, transaction_id):
        """Get full transaction details including items"""
        # Get transaction
        self.cursor.execute("""
            SELECT t.*, u.full_name as cashier_name
            FROM transactions t
            LEFT JOIN users u ON t.cashier_id = u.id
            WHERE t.id = ?
        """, (transaction_id,))
        transaction = self.cursor.fetchone()
        
        # Get items
        self.cursor.execute("""
            SELECT * FROM transaction_items WHERE transaction_id = ?
        """, (transaction_id,))
        items = self.cursor.fetchall()
        
        return transaction, items
    
    # Product Variants
    def add_variant(self, product_id, variant_name, variant_value, price_adjustment, stock, sku):
        """Add product variant"""
        self.cursor.execute("""
            INSERT INTO product_variants 
            (product_id, variant_name, variant_value, price_adjustment, stock, sku)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, variant_name, variant_value, price_adjustment, stock, sku))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_variants(self, product_id):
        """Get all variants for a product"""
        self.cursor.execute("""
            SELECT * FROM product_variants WHERE product_id = ?
        """, (product_id,))
        return self.cursor.fetchall()
    
    def delete_variant(self, variant_id):
        """Delete a variant"""
        self.cursor.execute("DELETE FROM product_variants WHERE id = ?", (variant_id,))
        self.conn.commit()
    
    # Product Modifiers
    def add_modifier(self, product_id, modifier_name, modifier_price, linked_product_id=None, deduct_quantity=1):
        """Add product modifier"""
        self.cursor.execute("""
            INSERT INTO product_modifiers (product_id, modifier_name, modifier_price, linked_product_id, deduct_quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, modifier_name, modifier_price, linked_product_id, deduct_quantity))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_modifiers(self, product_id):
        """Get all modifiers for a product with linked product info"""
        self.cursor.execute("""
            SELECT pm.*, p.name as linked_product_name, p.stock as linked_product_stock
            FROM product_modifiers pm
            LEFT JOIN products p ON pm.linked_product_id = p.id
            WHERE pm.product_id = ?
        """, (product_id,))
        return self.cursor.fetchall()
    
    def delete_modifier(self, modifier_id):
        """Delete a modifier"""
        self.cursor.execute("DELETE FROM product_modifiers WHERE id = ?", (modifier_id,))
        self.conn.commit()
    
    # Product Ingredients (Linked Inventory)
    def add_product_ingredient(self, product_id, ingredient_id, quantity):
        """Link an ingredient to a product"""
        # Check if already linked
        self.cursor.execute("SELECT id FROM product_ingredients WHERE product_id=? AND ingredient_id=?", (product_id, ingredient_id))
        if self.cursor.fetchone():
            # Update quantity
            self.cursor.execute("UPDATE product_ingredients SET quantity=? WHERE product_id=? AND ingredient_id=?", (quantity, product_id, ingredient_id))
        else:
            self.cursor.execute("""
                INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
                VALUES (?, ?, ?)
            """, (product_id, ingredient_id, quantity))
        self.conn.commit()

    def remove_product_ingredient(self, link_id):
        """Remove a linked ingredient"""
        self.cursor.execute("DELETE FROM product_ingredients WHERE id = ?", (link_id,))
        self.conn.commit()

    def get_product_ingredients(self, product_id):
        """Get all ingredients linked to a product"""
        self.cursor.execute("""
            SELECT pi.id, pi.ingredient_id, p.name, pi.quantity, p.price, (p.price * pi.quantity) as cost
            FROM product_ingredients pi
            JOIN products p ON pi.ingredient_id = p.id
            WHERE pi.product_id = ?
        """, (product_id,))
        return self.cursor.fetchall()
        
    def get_product_overall_cost(self, product_id):
        """Calculate total cost of ingredients for one unit of product"""
        self.cursor.execute("""
            SELECT SUM(p.price * pi.quantity)
            FROM product_ingredients pi
            JOIN products p ON pi.ingredient_id = p.id
            WHERE pi.product_id = ?
        """, (product_id,))
        result = self.cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    
    # Suppliers
    def add_supplier(self, name, contact_person="", phone="", email="", address=""):
        """Add supplier"""
        try:
            self.cursor.execute("""
                INSERT INTO suppliers (name, contact_person, phone, email, address)
                VALUES (?, ?, ?, ?, ?)
            """, (name, contact_person, phone, email, address))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Return existing if duplicate name
            self.cursor.execute("SELECT id FROM suppliers WHERE name = ?", (name,))
            res = self.cursor.fetchone()
            return res[0] if res else None
    
    def get_all_suppliers(self):
        """Get all suppliers"""
        self.cursor.execute("SELECT * FROM suppliers ORDER BY name")
        return self.cursor.fetchall()
    
    def update_supplier(self, supplier_id, name, contact_person, phone, email, address):
        """Update supplier"""
        self.cursor.execute("""
            UPDATE suppliers 
            SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
        """, (name, contact_person, phone, email, address, supplier_id))
        self.conn.commit()
    
    def delete_supplier(self, supplier_id):
        """Delete supplier"""
        self.cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        self.conn.commit()
    
    # Stock Adjustments
    def add_stock_adjustment(self, product_id, adjustment_type, quantity, reason, user_id):
        """Add stock adjustment"""
        self.cursor.execute("""
            INSERT INTO stock_adjustments 
            (product_id, adjustment_type, quantity, reason, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, adjustment_type, quantity, reason, user_id))
        
        # Update product stock
        if adjustment_type == "add":
            self.cursor.execute("""
                UPDATE products SET stock = stock + ? WHERE id = ?
            """, (quantity, product_id))
        elif adjustment_type == "remove":
            self.cursor.execute("""
                UPDATE products SET stock = stock - ? WHERE id = ?
            """, (quantity, product_id))
        elif adjustment_type == "set":
            self.cursor.execute("""
                UPDATE products SET stock = ? WHERE id = ?
            """, (quantity, product_id))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_stock_adjustments(self, product_id=None, limit=100):
        """Get stock adjustments"""
        if product_id:
            self.cursor.execute("""
                SELECT sa.*, p.name as product_name, u.full_name as user_name
                FROM stock_adjustments sa
                LEFT JOIN products p ON sa.product_id = p.id
                LEFT JOIN users u ON sa.user_id = u.id
                WHERE sa.product_id = ?
                ORDER BY sa.created_at DESC
                LIMIT ?
            """, (product_id, limit))
        else:
            self.cursor.execute("""
                SELECT sa.*, p.name as product_name, u.full_name as user_name
                FROM stock_adjustments sa
                LEFT JOIN products p ON sa.product_id = p.id
                LEFT JOIN users u ON sa.user_id = u.id
                ORDER BY sa.created_at DESC
                LIMIT ?
            """, (limit,))
        return self.cursor.fetchall()
    
    # Inventory Analytics
    def get_low_stock_products(self, threshold=10):
        """Get products with low stock (only tracked items)"""
        self.cursor.execute("""
            SELECT id, name, category, price, stock, barcode, description, created_at, 
                   unit, cost, markup, supplier_id, use_stock_tracking, is_available
            FROM products 
            WHERE stock <= ? AND use_stock_tracking = 1
            ORDER BY stock ASC
        """, (threshold,))
        return self.cursor.fetchall()
    
    def get_out_of_stock_products(self):
        """Get out of stock products (only tracked items)"""
        self.cursor.execute("""
            SELECT id, name, category, price, stock, barcode, description, created_at, 
                   unit, cost, markup, supplier_id, use_stock_tracking, is_available
            FROM products 
            WHERE stock <= 0 AND use_stock_tracking = 1
            ORDER BY name
        """)
        return self.cursor.fetchall()
    
    def get_inventory_value(self):
        """Get total inventory value (only tracked items)"""
        self.cursor.execute("""
            SELECT SUM(price * stock) as total_value 
            FROM products
            WHERE use_stock_tracking = 1
        """)
        result = self.cursor.fetchone()
        return result[0] if result[0] else 0
    
    def get_products_by_category_with_stock(self):
        """Get products grouped by category with stock info"""
        self.cursor.execute("""
            SELECT category, COUNT(*) as product_count, 
                   SUM(stock) as total_stock,
                   SUM(price * stock) as category_value
            FROM products
            GROUP BY category
            ORDER BY category
        """)
        return self.cursor.fetchall()
    
    
    # Receipt Settings
    def get_receipt_settings(self):
        """Get receipt settings"""
        self.cursor.execute("SELECT * FROM receipt_settings WHERE id = 1")
        settings = self.cursor.fetchone()
        if not settings:
            # Create default if missing
            self.cursor.execute("INSERT INTO receipt_settings (id, store_name) VALUES (1, 'My POS Store')")
            self.conn.commit()
            self.cursor.execute("SELECT * FROM receipt_settings WHERE id = 1")
            settings = self.cursor.fetchone()
        return settings
    
    def update_receipt_settings(self, name, address, phone, email, tax_rate, footer, logo_path, paper_width):
        """Update receipt settings"""
        self.cursor.execute("""
            UPDATE receipt_settings 
            SET store_name = ?, 
                store_address = ?, 
                store_phone = ?, 
                store_email = ?, 
                tax_rate = ?, 
                receipt_footer = ?, 
                logo_path = ?, 
                paper_width = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (name, address, phone, email, tax_rate, footer, logo_path, paper_width))
        self.conn.commit()
    
    # Analytics Methods for Dashboard
    def get_top_selling_products(self, start_date=None, end_date=None, limit=10):
        """Get top selling products by quantity and revenue"""
        if start_date and end_date:
            self.cursor.execute("""
                SELECT p.name, SUM(ti.quantity) as total_qty, SUM(ti.subtotal) as total_revenue
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                JOIN transactions t ON ti.transaction_id = t.id
                WHERE DATE(t.created_at) BETWEEN ? AND ?
                GROUP BY ti.product_id, p.name
                ORDER BY total_qty DESC
                LIMIT ?
            """, (start_date, end_date, limit))
        else:
            self.cursor.execute("""
                SELECT p.name, SUM(ti.quantity) as total_qty, SUM(ti.subtotal) as total_revenue
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                GROUP BY ti.product_id, p.name
                ORDER BY total_qty DESC
                LIMIT ?
            """, (limit,))
        return self.cursor.fetchall()
    
    def get_payment_method_breakdown(self, start_date=None, end_date=None):
        """Get breakdown of sales by payment method"""
        if start_date and end_date:
            self.cursor.execute("""
                SELECT payment_method, SUM(total_amount) as total, COUNT(*) as count
                FROM transactions
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY payment_method
                ORDER BY total DESC
            """, (start_date, end_date))
        else:
            self.cursor.execute("""
                SELECT payment_method, SUM(total_amount) as total, COUNT(*) as count
                FROM transactions
                GROUP BY payment_method
                ORDER BY total DESC
            """)
        return self.cursor.fetchall()
    
    def get_order_type_breakdown(self, start_date=None, end_date=None):
        """Get breakdown of sales by order type"""
        if start_date and end_date:
            self.cursor.execute("""
                SELECT order_type, COUNT(*) as count, SUM(total_amount) as total
                FROM transactions
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY order_type
                ORDER BY count DESC
            """, (start_date, end_date))
        else:
            self.cursor.execute("""
                SELECT order_type, COUNT(*) as count, SUM(total_amount) as total
                FROM transactions
                GROUP BY order_type
                ORDER BY count DESC
            """)
        return self.cursor.fetchall()

    def get_hourly_sales(self, start_date=None, end_date=None):
        """Get sales aggregated by hour of the day"""
        if start_date and end_date:
            self.cursor.execute("""
                SELECT 
                    CAST(strftime('%H', created_at) AS INTEGER) as hour,
                    SUM(total_amount) as total_sales,
                    COUNT(*) as transaction_count
                FROM transactions
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY hour
                ORDER BY total_sales DESC
            """, (start_date, end_date))
        else:
            self.cursor.execute("""
                SELECT 
                    CAST(strftime('%H', created_at) AS INTEGER) as hour,
                    SUM(total_amount) as total_sales,
                    COUNT(*) as transaction_count
                FROM transactions
                GROUP BY hour
                ORDER BY total_sales DESC
            """)
        return self.cursor.fetchall()

    def get_category_performance(self, start_date=None, end_date=None):
        """Get sales performance by product category"""
        if start_date and end_date:
            self.cursor.execute("""
                SELECT 
                    p.category,
                    SUM(ti.subtotal) as total_sales,
                    SUM(ti.quantity) as total_qty
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                JOIN transactions t ON ti.transaction_id = t.id
                WHERE DATE(t.created_at) BETWEEN ? AND ?
                GROUP BY p.category
                ORDER BY total_sales DESC
            """, (start_date, end_date))
        else:
            self.cursor.execute("""
                SELECT 
                    p.category,
                    SUM(ti.subtotal) as total_sales,
                    SUM(ti.quantity) as total_qty
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                GROUP BY p.category
                ORDER BY total_sales DESC
            """)
        return self.cursor.fetchall()

    def close(self):
        """Close database connection"""
        self.conn.close()
