"""
Cashier view - POS Interface (Refactored)
This is the main cashier view that coordinates all cashier components
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS

# Import all cashier components
from views.cashier.product_grid import ProductGrid
from views.cashier.shopping_cart import ShoppingCart
from views.cashier.variant_selector import VariantSelector
from views.cashier.payment_dialog import PaymentDialog


class CashierView(ctk.CTkFrame):
    def __init__(self, parent, database, user_data, logout_callback):
        super().__init__(parent, fg_color=COLORS["dark"])
        self.database = database
        self.user_data = user_data
        self.logout_callback = logout_callback
        
        # Initialize components
        self.product_grid = None
        self.shopping_cart = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the cashier POS interface"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"], height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Header content
        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", padx=20, pady=15)
        
        title = ctk.CTkLabel(
            header_left,
            text="🛒 Point of Sale",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Header right
        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=20, pady=15)
        
        cashier_label = ctk.CTkLabel(
            header_right,
            text=f"Cashier: {self.user_data['full_name']}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        cashier_label.pack(side="left", padx=(0, 15))
        
        # Items button
        items_btn = ctk.CTkButton(
            header_right,
            text="📦 Items",
            command=self.show_items,
            width=100,
            height=35,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            corner_radius=8
        )
        items_btn.pack(side="left", padx=(0, 10))
        
        # History button
        history_btn = ctk.CTkButton(
            header_right,
            text="📜 History",
            command=self.show_history,
            width=100,
            height=35,
            fg_color=COLORS["info"],
            hover_color=COLORS["primary"],
            corner_radius=8
        )
        history_btn.pack(side="left", padx=(0, 10))
        
        logout_btn = ctk.CTkButton(
            header_right,
            text="Logout",
            command=self.logout_callback,
            width=100,
            height=35,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=8
        )
        logout_btn.pack(side="left")
        
        # Main content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Initialize components
        self.product_grid = ProductGrid(content, self.database, self.add_to_cart)
        self.shopping_cart = ShoppingCart(content, self.database)
        
        # Create UI
        self.product_grid.create()
        self.shopping_cart.create(self.checkout, self.clear_cart)
    
    def add_to_cart(self, product):
        """Add product to cart with customization and quantity dialog"""
        # Check stock first
        if product[4] <= 0:
            messagebox.showwarning("Out of Stock", "This product is out of stock")
            return

        product_id = product[0]
        
        # Get global modifiers (Add-ons)
        global_modifiers = self.database.get_all_global_modifiers()
        
        # Get alternative prices
        prices = self.database.get_product_prices(product_id)
        
        # Show details/quantity dialog
        # Pass global_modifiers instead of product-specific lists
        selector = VariantSelector(
            self,
            product,
            [], # Variants deprecated
            global_modifiers,
            self.add_customized_item_to_cart,
            prices
        )
        selector.show()
    
    def add_simple_product_to_cart(self, product):
        """Add simple product to cart"""
        product_id = product[0]
        
        # Check if identical item already in cart
        for item in self.shopping_cart.get_items():
            # Only aggregate if no variants/modifiers
            if item['product_id'] == product_id and not item.get('variants') and not item.get('modifiers'):
                if item['quantity'] < product[4]:  # Check stock
                    item['quantity'] += 1
                    item['subtotal'] = item['quantity'] * item['price']
                    self.shopping_cart.update_cart_display()
                    return
                else:
                    messagebox.showwarning("Stock Limit", "Not enough stock available")
                    return
        
        if product[4] > 0:
            item = {
                'product_id': product_id,
                'name': product[1],
                'price': product[3],
                'quantity': 1,
                'subtotal': product[3],
                'variants': [],
                'modifiers': [],
                'note': ""
            }
            self.shopping_cart.add_item(item)
        else:
            messagebox.showwarning("Out of Stock", "This product is out of stock")
    
    def add_customized_item_to_cart(self, item):
        """Add customized item to cart (from variant selector)"""
        self.shopping_cart.add_item(item)
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.shopping_cart.get_items():
            if messagebox.askyesno("Clear Cart", "Are you sure you want to clear the cart?"):
                self.shopping_cart.clear_cart()
    
    def checkout(self):
        """Process checkout with payment dialog"""
        cart_items = self.shopping_cart.get_items()
        
        if not cart_items:
            messagebox.showwarning("Empty Cart", "Please add items to cart before checkout")
            return
        
        # Calculate totals
        subtotal = sum(item['subtotal'] for item in cart_items)
        tax = 0
        total = subtotal
        
        # Show payment dialog
        payment = PaymentDialog(
            self,
            self.database,
            self.user_data,
            cart_items,
            total,
            subtotal,
            tax
        )
        payment.show(self.on_checkout_success)
    
    
    def on_checkout_success(self):
        """Handle successful checkout"""
        # Clear cart
        self.shopping_cart.clear_cart()
        # Reload products (to update stock display)
        self.product_grid.load_products()
    
    
    def show_items(self):
        """Show all items with stock levels and real-time search"""
        from config import CURRENCY_SYMBOL
        
        # Create items dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Product Inventory")
        dialog.geometry("700x600")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 700) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f"700x600+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text="📦 Product Inventory",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Close button
        ctk.CTkButton(
            header,
            text="Close",
            command=dialog.destroy,
            width=80,
            height=30,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=8
        ).pack(side="right")
        
        # Search bar
        search_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search products...",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        search_entry.pack(fill="x", padx=15, pady=10)
        
        # Product list container
        list_container = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # List header
        list_header = ctk.CTkFrame(list_container, fg_color=COLORS["dark"], corner_radius=0, height=35)
        list_header.pack(fill="x", padx=0, pady=0)
        list_header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(list_header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=15, pady=8)
        
        ctk.CTkLabel(header_content, text="Product Name", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=200, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_content, text="Category", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=120, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_content, text="Price", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_content, text="Stock", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=60, anchor="w").pack(side="left")
        
        # Scrollable list
        list_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        list_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        def display_products(search_term=""):
            """Display products filtered by search term"""
            # Clear existing items
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            # Get all products
            all_products = self.database.get_all_products()
            
            # Filter by search term
            if search_term:
                search_lower = search_term.lower()
                filtered_products = [
                    p for p in all_products 
                    if search_lower in p[1].lower() or  # name
                       (p[2] and search_lower in p[2].lower())  # category
                ]
            else:
                filtered_products = all_products
            
            # Display products
            if filtered_products:
                for product in filtered_products:
                    # product: [id, name, category, price, stock, barcode, description, created_at, unit, cost, markup]
                    product_name = product[1] if len(product) > 1 else "Unknown"
                    category = product[2] if len(product) > 2 and product[2] else "Uncategorized"
                    price = product[3] if len(product) > 3 else 0
                    stock = product[4] if len(product) > 4 else 0
                    
                    # Determine stock status color
                    if stock == 0:
                        stock_color = COLORS["danger"]
                        stock_text = "Out of Stock"
                    elif stock <= 10:
                        stock_color = "#ff9800"  # Orange
                        stock_text = str(stock)
                    else:
                        stock_color = COLORS["success"]
                        stock_text = str(stock)
                    
                    row = ctk.CTkFrame(list_frame, fg_color=COLORS["dark"], corner_radius=0, height=32)
                    row.pack(fill="x", pady=1, padx=0)
                    row.pack_propagate(False)
                    
                    row_content = ctk.CTkFrame(row, fg_color="transparent")
                    row_content.pack(fill="both", expand=True, padx=15, pady=6)
                    
                    # Product name
                    ctk.CTkLabel(
                        row_content,
                        text=product_name,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_primary"],
                        width=200,
                        anchor="w"
                    ).pack(side="left", padx=(0, 10))
                    
                    # Category
                    ctk.CTkLabel(
                        row_content,
                        text=category,
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_secondary"],
                        width=120,
                        anchor="w"
                    ).pack(side="left", padx=(0, 10))
                    
                    # Price
                    ctk.CTkLabel(
                        row_content,
                        text=f"{CURRENCY_SYMBOL}{price:.2f}",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_primary"],
                        width=80,
                        anchor="w"
                    ).pack(side="left", padx=(0, 10))
                    
                    # Stock
                    ctk.CTkLabel(
                        row_content,
                        text=stock_text,
                        font=ctk.CTkFont(size=10, weight="bold"),
                        text_color=stock_color,
                        width=60,
                        anchor="w"
                    ).pack(side="left")
            else:
                ctk.CTkLabel(
                    list_frame,
                    text="No products found",
                    font=ctk.CTkFont(size=14),
                    text_color=COLORS["text_secondary"]
                ).pack(pady=50)
        
        # Bind search
        def on_search(*args):
            display_products(search_entry.get())
        
        search_entry.bind("<KeyRelease>", on_search)
        
        # Initial display
        display_products()
    
    
    def show_history(self):
        """Show cashier's transaction history with filters and detailed breakdown"""
        from config import CURRENCY_SYMBOL
        from datetime import datetime, timedelta
        
        # Create history dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("My Sales History")
        dialog.geometry("900x650")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 900) // 2
        y = (dialog.winfo_screenheight() - 650) // 2
        dialog.geometry(f"900x650+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text="📜 My Sales History",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Close button
        ctk.CTkButton(
            header,
            text="Close",
            command=dialog.destroy,
            width=80,
            height=30,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=8
        ).pack(side="right")
        
        # Filter and Summary Frame
        filter_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Date filter buttons
        filter_btn_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_btn_frame.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            filter_btn_frame,
            text="Filter:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 10))
        
        filter_var = ctk.StringVar(value="all")
        
        # Summary display
        summary_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        summary_frame.pack(side="right", padx=15, pady=10)
        
        total_label = ctk.CTkLabel(
            summary_frame,
            text="Total Sales: ₱0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["success"]
        )
        total_label.pack(side="right", padx=(15, 0))
        
        count_label = ctk.CTkLabel(
            summary_frame,
            text="Transactions: 0",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        count_label.pack(side="right")
        
        # Tabbed interface
        tab_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        tab_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        current_tab = {"value": "transactions"}
        
        def switch_tab(tab_name):
            current_tab["value"] = tab_name
            refresh_data()
        
        tab_transactions = ctk.CTkButton(
            tab_frame,
            text="📋 Transactions",
            command=lambda: switch_tab("transactions"),
            height=32,
            fg_color=COLORS["primary"],
            corner_radius=8
        )
        tab_transactions.pack(side="left", padx=(0, 5))
        
        tab_breakdown = ctk.CTkButton(
            tab_frame,
            text="📊 Sales Breakdown",
            command=lambda: switch_tab("breakdown"),
            height=32,
            fg_color=COLORS["secondary"],
            corner_radius=8
        )
        tab_breakdown.pack(side="left")
        
        # Content container
        content_container = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        content_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def get_filtered_transactions():
            """Get transactions based on filter"""
            filter_type = filter_var.get()
            all_txns = self.database.get_transactions_by_cashier(self.user_data['id'], limit=200)
            
            if filter_type == "all":
                return all_txns
            
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            filtered = []
            for txn in all_txns:
                txn_date_str = txn[8] if len(txn) > 8 else ""
                try:
                    txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d %H:%M:%S").date()
                    if filter_type == "today" and txn_date == today:
                        filtered.append(txn)
                    elif filter_type == "yesterday" and txn_date == yesterday:
                        filtered.append(txn)
                except:
                    pass
            
            return filtered
        
        def refresh_data():
            """Refresh the display based on filter and tab"""
            # Clear content
            for widget in content_container.winfo_children():
                widget.destroy()
            
            # Update tab button colors
            if current_tab["value"] == "transactions":
                tab_transactions.configure(fg_color=COLORS["primary"])
                tab_breakdown.configure(fg_color=COLORS["secondary"])
            else:
                tab_transactions.configure(fg_color=COLORS["secondary"])
                tab_breakdown.configure(fg_color=COLORS["primary"])
            
            transactions = get_filtered_transactions()
            
            # Update summary
            total_sales = sum(txn[3] for txn in transactions if len(txn) > 3)
            count_label.configure(text=f"Transactions: {len(transactions)}")
            total_label.configure(text=f"Total Sales: {CURRENCY_SYMBOL}{total_sales:.2f}")
            
            if current_tab["value"] == "transactions":
                show_transactions_tab(transactions)
            else:
                show_breakdown_tab(transactions)
        
        def show_transactions_tab(transactions):
            """Show transactions list"""
            # List header
            list_header = ctk.CTkFrame(content_container, fg_color=COLORS["dark"], corner_radius=0, height=35)
            list_header.pack(fill="x", padx=0, pady=0)
            list_header.pack_propagate(False)
            
            header_frame = ctk.CTkFrame(list_header, fg_color="transparent")
            header_frame.pack(fill="both", expand=True, padx=15, pady=8)
            
            ctk.CTkLabel(header_frame, text="Transaction #", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=130, anchor="w").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(header_frame, text="Date & Time", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=130, anchor="w").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(header_frame, text="Total", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(header_frame, text="Payment", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=70, anchor="w").pack(side="left")
            
            # Scrollable list
            list_frame = ctk.CTkScrollableFrame(content_container, fg_color="transparent", scrollbar_button_color=COLORS["primary"])
            list_frame.pack(fill="both", expand=True, padx=0, pady=0)
            
            if transactions:
                for txn in transactions:
                    row = ctk.CTkFrame(list_frame, fg_color=COLORS["dark"], corner_radius=0, height=32)
                    row.pack(fill="x", pady=1, padx=0)
                    row.pack_propagate(False)
                    
                    content = ctk.CTkFrame(row, fg_color="transparent")
                    content.pack(fill="both", expand=True, padx=15, pady=6)
                    
                    txn_number = txn[1] if len(txn) > 1 else "N/A"
                    ctk.CTkLabel(content, text=txn_number, font=ctk.CTkFont(size=10), text_color=COLORS["text_primary"], width=130, anchor="w").pack(side="left", padx=(0, 10))
                    
                    created_at = txn[8] if len(txn) > 8 else "N/A"
                    ctk.CTkLabel(content, text=created_at, font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"], width=130, anchor="w").pack(side="left", padx=(0, 10))
                    
                    total = txn[3] if len(txn) > 3 else 0
                    ctk.CTkLabel(content, text=f"{CURRENCY_SYMBOL}{total:.2f}", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["success"], width=80, anchor="w").pack(side="left", padx=(0, 10))
                    
                    payment = txn[6] if len(txn) > 6 else "N/A"
                    payment_icon = "💵" if payment == "Cash" else "📱"
                    ctk.CTkLabel(content, text=f"{payment_icon} {payment}", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"], width=70, anchor="w").pack(side="left")
            else:
                ctk.CTkLabel(list_frame, text="No transactions found", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]).pack(pady=50)
        
        def show_breakdown_tab(transactions):
            """Show detailed sales breakdown"""
            # Scrollable breakdown
            breakdown_frame = ctk.CTkScrollableFrame(content_container, fg_color="transparent", scrollbar_button_color=COLORS["primary"])
            breakdown_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            if not transactions:
                ctk.CTkLabel(breakdown_frame, text="No sales data available", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]).pack(pady=50)
                return
            
            # Collect all sales data
            product_sales = {}  # {product_name: {qty, total, product_id, variants: {}, modifiers: {}}}
            
            for txn in transactions:
                txn_id = txn[0]
                items = self.database.get_transaction_items(txn_id)
                
                for item in items:
                    # item: [id, txn_id, product_id, product_name, qty, unit_price, subtotal, variant_id, variant_name, modifiers]
                    product_id = item[2] if len(item) > 2 else None
                    product_name = item[3] if len(item) > 3 else "Unknown"
                    qty = item[4] if len(item) > 4 else 0
                    subtotal = item[6] if len(item) > 6 else 0
                    variant_name = item[8] if len(item) > 8 and item[8] else None
                    modifiers_str = item[9] if len(item) > 9 and item[9] else None
                    
                    if product_name not in product_sales:
                        product_sales[product_name] = {
                            'qty': 0,
                            'total': 0,
                            'product_id': product_id,
                            'variants': {},
                            'modifiers': {}
                        }
                    
                    product_sales[product_name]['qty'] += qty
                    product_sales[product_name]['total'] += subtotal
                    
                    if variant_name:
                        if variant_name not in product_sales[product_name]['variants']:
                            product_sales[product_name]['variants'][variant_name] = 0
                        product_sales[product_name]['variants'][variant_name] += qty
                    
                    if modifiers_str:
                        for mod in modifiers_str.split(", "):
                            if mod not in product_sales[product_name]['modifiers']:
                                product_sales[product_name]['modifiers'][mod] = 0
                            product_sales[product_name]['modifiers'][mod] += qty
            
            def show_ingredient_details(product_name, product_id, qty_sold):
                """Show modal with ingredient deduction details"""
                if not product_id:
                    messagebox.showinfo("No Data", "Product ID not found")
                    return
                
                # Get ingredients
                ingredients = self.database.get_product_ingredients(product_id)
                
                if not ingredients:
                    messagebox.showinfo("No Ingredients", f"{product_name} has no linked ingredients")
                    return
                
                # Create modal
                modal = ctk.CTkToplevel(dialog)
                modal.title(f"Ingredient Breakdown - {product_name}")
                modal.geometry("550x400")
                modal.configure(fg_color=COLORS["dark"])
                modal.transient(dialog)
                modal.grab_set()
                
                # Center modal
                modal.update_idletasks()
                x = (modal.winfo_screenwidth() - 550) // 2
                y = (modal.winfo_screenheight() - 400) // 2
                modal.geometry(f"550x400+{x}+{y}")
                
                # Header
                header = ctk.CTkFrame(modal, fg_color="transparent")
                header.pack(fill="x", padx=20, pady=(20, 10))
                
                ctk.CTkLabel(
                    header,
                    text=f"🔍 Ingredient Breakdown",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(side="left")
                
                ctk.CTkButton(
                    header,
                    text="Close",
                    command=modal.destroy,
                    width=70,
                    height=28,
                    fg_color=COLORS["danger"],
                    hover_color="#c0392b",
                    corner_radius=8
                ).pack(side="right")
                
                # Product info
                info_frame = ctk.CTkFrame(modal, fg_color=COLORS["card_bg"], corner_radius=8)
                info_frame.pack(fill="x", padx=20, pady=(0, 10))
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📦 {product_name}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(pady=(10, 5), padx=15, anchor="w")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"Total Sold: {qty_sold} units",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["success"]
                ).pack(pady=(0, 10), padx=15, anchor="w")
                
                # Ingredients list
                list_container = ctk.CTkFrame(modal, fg_color=COLORS["card_bg"], corner_radius=8)
                list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                
                # List header
                list_header = ctk.CTkFrame(list_container, fg_color=COLORS["dark"], corner_radius=0, height=32)
                list_header.pack(fill="x", padx=0, pady=0)
                list_header.pack_propagate(False)
                
                header_content = ctk.CTkFrame(list_header, fg_color="transparent")
                header_content.pack(fill="both", expand=True, padx=15, pady=6)
                
                ctk.CTkLabel(header_content, text="Ingredient", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=150, anchor="w").pack(side="left", padx=(0, 10))
                ctk.CTkLabel(header_content, text="Per Unit", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left", padx=(0, 10))
                ctk.CTkLabel(header_content, text="Total Deducted", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=100, anchor="w").pack(side="left")
                
                # Scrollable list
                list_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent", scrollbar_button_color=COLORS["primary"])
                list_frame.pack(fill="both", expand=True, padx=0, pady=0)
                
                # Display ingredients
                for ingredient in ingredients:
                    # ingredient: [link_id, ingredient_id, ingredient_name, qty_per_product, price, cost]
                    ing_name = ingredient[2] if len(ingredient) > 2 else "Unknown"
                    qty_per = ingredient[3] if len(ingredient) > 3 else 0
                    total_deducted = qty_sold * qty_per
                    
                    row = ctk.CTkFrame(list_frame, fg_color=COLORS["dark"], corner_radius=0, height=28)
                    row.pack(fill="x", pady=1, padx=0)
                    row.pack_propagate(False)
                    
                    row_content = ctk.CTkFrame(row, fg_color="transparent")
                    row_content.pack(fill="both", expand=True, padx=15, pady=4)
                    
                    ctk.CTkLabel(row_content, text=f"🥘 {ing_name}", font=ctk.CTkFont(size=10), text_color=COLORS["text_primary"], width=150, anchor="w").pack(side="left", padx=(0, 10))
                    ctk.CTkLabel(row_content, text=f"{qty_per}", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left", padx=(0, 10))
                    ctk.CTkLabel(row_content, text=f"{total_deducted}", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["danger"], width=100, anchor="w").pack(side="left")
            
            
            # Display breakdown
            for product_name, data in sorted(product_sales.items(), key=lambda x: x[1]['total'], reverse=True):
                product_card = ctk.CTkFrame(breakdown_frame, fg_color=COLORS["dark"], corner_radius=8)
                product_card.pack(fill="x", pady=5, padx=5)
                
                # Make card clickable
                def make_clickable(card, pn, pid, qty):
                    def on_click(event=None):
                        show_ingredient_details(pn, pid, qty)
                    card.bind("<Button-1>", on_click)
                    # Bind all children too
                    for child in card.winfo_children():
                        child.bind("<Button-1>", on_click)
                        for subchild in child.winfo_children():
                            subchild.bind("<Button-1>", on_click)
                    # Change cursor on hover
                    card.configure(cursor="hand2")
                
                # Product header
                header = ctk.CTkFrame(product_card, fg_color="transparent")
                header.pack(fill="x", padx=12, pady=(10, 5))
                
                ctk.CTkLabel(
                    header,
                    text=f"📦 {product_name}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(side="left")
                
                ctk.CTkLabel(
                    header,
                    text=f"{data['qty']} sold • {CURRENCY_SYMBOL}{data['total']:.2f}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=COLORS["success"]
                ).pack(side="right")
                
                # Details
                details = ctk.CTkFrame(product_card, fg_color="transparent")
                details.pack(fill="x", padx=12, pady=(0, 10))
                
                details_text = []
                
                if data['variants']:
                    variants_str = ", ".join([f"{v} ({c}x)" for v, c in data['variants'].items()])
                    details_text.append(f"🎨 Variants: {variants_str}")
                
                if data['modifiers']:
                    modifiers_str = ", ".join([f"{m} ({c}x)" for m, c in data['modifiers'].items()])
                    details_text.append(f"➕ Modifiers: {modifiers_str}")
                
                # Add click hint
                details_text.append("💡 Click to view ingredient breakdown")
                
                if details_text:
                    for text in details_text:
                        ctk.CTkLabel(
                            details,
                            text=text,
                            font=ctk.CTkFont(size=10),
                            text_color=COLORS["text_secondary"],
                            anchor="w"
                        ).pack(anchor="w", pady=1)
                
                # Apply click binding
                make_clickable(product_card, product_name, data['product_id'], data['qty'])
        
        # Filter buttons with refresh
        for filter_type, label in [("all", "All"), ("today", "Today"), ("yesterday", "Yesterday")]:
            btn = ctk.CTkRadioButton(
                filter_btn_frame,
                text=label,
                variable=filter_var,
                value=filter_type,
                command=refresh_data,
                font=ctk.CTkFont(size=11)
            )
            btn.pack(side="left", padx=5)
        
        # Initial load
        refresh_data()
