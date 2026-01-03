"""
Inventory management page for admin view
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config import COLORS, CURRENCY_SYMBOL


class InventoryPage:
    def __init__(self, parent, database, user_data):
        self.parent = parent
        self.database = database
        self.user_data = user_data
        self.inventory_tab = "overview"
        self.tab_buttons = {}
        self.inventory_content = None
        self.selected_adj_product_id = None
    
    def show(self):
        """Show inventory management page"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="📋 Inventory Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Main container with tabs
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(main_container, fg_color=COLORS["card_bg"], corner_radius=10, height=60)
        tab_frame.pack(fill="x", pady=(0, 10))
        tab_frame.pack_propagate(False)
        
        tabs = [
            ("📊 Overview", "overview"),
            ("⚠️ Low Stock", "low_stock"),
            ("📥 Stock In", "stock_in"),
            ("📤 Stock Out", "stock_out"),
            ("🏢 Suppliers", "suppliers")
        ]
        
        for text, tab_id in tabs:
            btn = ctk.CTkButton(
                tab_frame,
                text=text,
                command=lambda t=tab_id: self.switch_inventory_tab(t),
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"] if tab_id == "overview" else "transparent",
                hover_color=COLORS["primary"],
                corner_radius=8
            )
            btn.pack(side="left", padx=5, pady=10)
            self.tab_buttons[tab_id] = btn
        
        # Content area
        self.inventory_content = ctk.CTkFrame(main_container, fg_color=COLORS["card_bg"], corner_radius=15)
        self.inventory_content.pack(fill="both", expand=True)
        
        # Show default tab
        self.show_inventory_overview()
    
    def switch_inventory_tab(self, tab):
        """Switch inventory tabs"""
        self.inventory_tab = tab
        
        # Update button colors
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == tab:
                btn.configure(fg_color=COLORS["primary"])
            else:
                btn.configure(fg_color="transparent")
        
        # Clear content
        for widget in self.inventory_content.winfo_children():
            widget.destroy()
        
        # Show selected tab
        if tab == "overview":
            self.show_inventory_overview()
        elif tab == "low_stock":
            self.show_low_stock()
        elif tab == "stock_in":
            self.show_stock_in()
        elif tab == "stock_out":
            self.show_stock_out()
        elif tab == "suppliers":
            self.show_suppliers()
    
    def show_inventory_overview(self):
        """Show inventory overview with caching optimization"""
        from datetime import datetime
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.inventory_content, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        # Get inventory data with caching
        if not hasattr(self, '_inventory_cache') or not hasattr(self, '_inventory_cache_time'):
            self._inventory_cache = {
                'products': self.database.get_all_products(),
                'low_stock': self.database.get_low_stock_products(10),
                'out_of_stock': self.database.get_out_of_stock_products(),
                'inventory_value': self.database.get_inventory_value()
            }
            self._inventory_cache_time = datetime.now()
        else:
            # Refresh cache if older than 30 seconds
            if (datetime.now() - self._inventory_cache_time).seconds > 30:
                self._inventory_cache = {
                    'products': self.database.get_all_products(),
                    'low_stock': self.database.get_low_stock_products(10),
                    'out_of_stock': self.database.get_out_of_stock_products(),
                    'inventory_value': self.database.get_inventory_value()
                }
                self._inventory_cache_time = datetime.now()
        
        all_products = self._inventory_cache['products']
        low_stock = self._inventory_cache['low_stock']
        out_of_stock = self._inventory_cache['out_of_stock']
        inventory_value = self._inventory_cache['inventory_value']
        
        # Filter for stock tracked only for the count
        # Indices: use_stock_tracking=12
        stock_tracked_products = [p for p in all_products if (len(p) > 12 and p[12] == 1)]
        
        stats = [
            ("Stock Items", len(stock_tracked_products), COLORS["info"]),
            ("Low Stock Items", len(low_stock), COLORS["warning"]),
            ("Out of Stock", len(out_of_stock), COLORS["danger"]),
            ("Inventory Value", f"{CURRENCY_SYMBOL}{inventory_value:.2f}", COLORS["success"])
        ]
        
        for label, value, color in stats:
            card = ctk.CTkFrame(stats_frame, fg_color=COLORS["dark"], corner_radius=10)
            card.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            ).pack(pady=(0, 15))
        
        # Recent stock adjustments
        adjustments_frame = ctk.CTkFrame(self.inventory_content, fg_color=COLORS["dark"], corner_radius=10)
        adjustments_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            adjustments_frame,
            text="Recent Stock Adjustments",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=15, padx=20, anchor="w")
        
        adjustments_list = ctk.CTkScrollableFrame(
            adjustments_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        adjustments_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Cache adjustments separately
        if not hasattr(self, '_adjustments_cache') or not hasattr(self, '_adjustments_cache_time'):
            self._adjustments_cache = self.database.get_stock_adjustments(limit=20)
            self._adjustments_cache_time = datetime.now()
        else:
            if (datetime.now() - self._adjustments_cache_time).seconds > 30:
                self._adjustments_cache = self.database.get_stock_adjustments(limit=20)
                self._adjustments_cache_time = datetime.now()
        
        adjustments = self._adjustments_cache
        
        if adjustments:
            # Only show first 10 initially
            for adj in adjustments[:10]:
                card = ctk.CTkFrame(adjustments_list, fg_color=COLORS["card_bg"], corner_radius=8)
                card.pack(fill="x", pady=5)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)
                
                ctk.CTkLabel(
                    content,
                    text=f"{adj[7]} - {adj[2].upper()}",  # product_name, adjustment_type
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    content,
                    text=f"Qty: {adj[3]} | {adj[4] or 'No reason'} | {adj[6][:16]}",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                adjustments_list,
                text="No stock adjustments yet",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(pady=20)
    
    def show_low_stock(self):
        """Show low stock products with lazy loading optimization"""
        from datetime import datetime
        
        # Get low stock products with caching
        if not hasattr(self, '_low_stock_cache') or not hasattr(self, '_low_stock_cache_time'):
            self._low_stock_cache = self.database.get_low_stock_products(10)
            self._low_stock_cache_time = datetime.now()
        else:
            if (datetime.now() - self._low_stock_cache_time).seconds > 30:
                self._low_stock_cache = self.database.get_low_stock_products(10)
                self._low_stock_cache_time = datetime.now()
        
        low_stock_raw = self._low_stock_cache
        
        # Filter for only stock-tracked items
        # Indices: use_stock_tracking=12
        low_stock = []
        if low_stock_raw:
            for p in low_stock_raw:
                use_stock = p[12] if len(p) > 12 and p[12] is not None else 1
                if use_stock == 1:
                    low_stock.append(p)

        # Header
        header = ctk.CTkFrame(self.inventory_content, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=f"⚠️ Low Stock Alert ({len(low_stock)})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Table Header
        table_header = ctk.CTkFrame(self.inventory_content, fg_color=COLORS["dark"], height=35)
        table_header.pack(fill="x", padx=20, pady=(0, 5))
        table_header.pack_propagate(False)
        
        h_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        h_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        ctk.CTkLabel(h_frame, text="Product Name", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"], width=200, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(h_frame, text="Category", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"], width=120, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(h_frame, text="Price", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(h_frame, text="Stock Level", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"], width=80, anchor="e").pack(side="right")

        self.low_stock_list_frame = ctk.CTkScrollableFrame(
            self.inventory_content,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        self.low_stock_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        if low_stock:
            # OPTIMIZATION: Lazy loading with batch rendering
            self._all_low_stock = low_stock
            self._low_stock_rendered = 0
            self._low_stock_batch = 20
            
            # Initial batch render
            self._render_low_stock_batch()
            
            # Add "Load More" button if there are more products
            if len(low_stock) > self._low_stock_batch:
                load_more_btn = ctk.CTkButton(
                    self.low_stock_list_frame,
                    text=f"Load More ({len(low_stock) - self._low_stock_batch} remaining)",
                    command=self._render_low_stock_batch,
                    height=40,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["secondary"]
                )
                load_more_btn.pack(pady=15, padx=20, fill="x")
                self._low_stock_load_more_btn = load_more_btn
        else:
            ctk.CTkLabel(
                self.low_stock_list_frame,
                text="✅ All tracked products have sufficient stock!",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["success"]
            ).pack(pady=50)
    
    def _render_low_stock_batch(self):
        """Render the next batch of low stock products"""
        if not hasattr(self, '_all_low_stock'):
            return
        
        products = self._all_low_stock
        start_idx = self._low_stock_rendered
        end_idx = min(start_idx + self._low_stock_batch, len(products))
        
        # Remove load more button if it exists
        if hasattr(self, '_low_stock_load_more_btn') and self._low_stock_load_more_btn.winfo_exists():
            self._low_stock_load_more_btn.destroy()
        
        # Render batch
        for i in range(start_idx, end_idx):
            product = products[i]
            
            row = ctk.CTkFrame(self.low_stock_list_frame, fg_color=COLORS["card_bg"], corner_radius=5, height=35)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)
            
            content = ctk.CTkFrame(row, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15, pady=5)
            
            # Name
            ctk.CTkLabel(
                content,
                text=product[1],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_primary"],
                width=200,
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            # Category
            ctk.CTkLabel(
                content,
                text=product[2],
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"],
                width=120,
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            # Price
            ctk.CTkLabel(
                content,
                text=f"{CURRENCY_SYMBOL}{product[3]:.2f}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"],
                width=80,
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            # Stock (Right aligned)
            stock_val = product[4]
            stock_color = COLORS["danger"] if stock_val == 0 else COLORS["warning"]
            
            ctk.CTkLabel(
                content,
                text=f"{stock_val}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=stock_color,
                width=80,
                anchor="e"
            ).pack(side="right")
        
        self._low_stock_rendered = end_idx
        
        # Re-add load more button if there are still more products
        remaining = len(products) - self._low_stock_rendered
        if remaining > 0:
            load_more_btn = ctk.CTkButton(
                self.low_stock_list_frame,
                text=f"Load More ({remaining} remaining)",
                command=self._render_low_stock_batch,
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"],
                hover_color=COLORS["secondary"]
            )
            load_more_btn.pack(pady=15, padx=20, fill="x")
            self._low_stock_load_more_btn = load_more_btn
    
    def show_stock_in(self):
        """Show stock in interface for adding inventory"""
        # Compact header
        ctk.CTkLabel(
            self.inventory_content,
            text="📥 Stock In - Add Inventory",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        # Compact form container
        form_frame = ctk.CTkFrame(self.inventory_content, fg_color=COLORS["dark"], corner_radius=8)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Product search - with button
        search_header = ctk.CTkFrame(form_frame, fg_color="transparent")
        search_header.pack(fill="x", padx=15, pady=(15, 3))
        
        ctk.CTkLabel(
            search_header,
            text="Select Product to Add Stock",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkButton(
            search_header,
            text="📋 View All Items",
            command=self.show_all_items_modal,
            height=24,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=COLORS["info"]
        ).pack(side="right")
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="🔍 Search product...",
            textvariable=search_var,
            height=30,
            font=ctk.CTkFont(size=11)
        )
        search_entry.pack(fill="x", padx=15, pady=(0, 5))
        
        # Product list
        products_frame = ctk.CTkScrollableFrame(
            form_frame,
            fg_color=COLORS["card_bg"],
            corner_radius=5,
            height=300,
            scrollbar_button_color=COLORS["primary"]
        )
        products_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        def update_product_list(*args):
            for widget in products_frame.winfo_children():
                widget.destroy()
            
            search_term = search_var.get().lower()
            all_products = self.database.get_all_products()
            
            # Filter matches
            filtered = []
            for p in all_products:
                use_stock = p[12] if len(p) > 12 and p[12] is not None else 1
                if use_stock == 0: continue
                
                if search_term in p[1].lower() or (p[5] and search_term in p[5].lower()):
                    filtered.append(p)
            
            if not filtered:
                ctk.CTkLabel(products_frame, text="No products found", text_color=COLORS["text_secondary"]).pack(pady=10)
                return
            
            for product in filtered[:20]: # Show top 20 matches
                stock_color = COLORS["danger"] if product[4] < 10 else COLORS["text_primary"]
                btn = ctk.CTkButton(
                    products_frame,
                    text=f"{product[1]} - Stock: {product[4]}",
                    command=lambda p=product: self.open_stock_modal(p, "add", lambda: update_product_list()),
                    height=40,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    fg_color="transparent",
                    text_color=stock_color,
                    hover_color=COLORS["primary"],
                    anchor="w"
                )
                btn.pack(fill="x", pady=1, padx=3)
        
        search_var.trace("w", update_product_list)
        update_product_list()

    
    def show_stock_out(self):
        """Show stock out interface for removing inventory"""
        # Compact header
        ctk.CTkLabel(
            self.inventory_content,
            text="📤 Stock Out - Remove Inventory",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        # Compact form container
        form_frame = ctk.CTkFrame(self.inventory_content, fg_color=COLORS["dark"], corner_radius=8)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Product search - with button
        search_header = ctk.CTkFrame(form_frame, fg_color="transparent")
        search_header.pack(fill="x", padx=15, pady=(15, 3))
        
        ctk.CTkLabel(
            search_header,
            text="Select Product to Remove Stock",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkButton(
            search_header,
            text="📋 View All Items",
            command=self.show_all_items_modal,
            height=24,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=COLORS["info"]
        ).pack(side="right")
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="🔍 Search product...",
            textvariable=search_var,
            height=30,
            font=ctk.CTkFont(size=11)
        )
        search_entry.pack(fill="x", padx=15, pady=(0, 5))
        
        # Product list
        products_frame = ctk.CTkScrollableFrame(
            form_frame,
            fg_color=COLORS["card_bg"],
            corner_radius=5,
            height=300,
            scrollbar_button_color=COLORS["primary"]
        )
        products_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        def update_product_list(*args):
            for widget in products_frame.winfo_children():
                widget.destroy()
            
            search_term = search_var.get().lower()
            all_products = self.database.get_all_products()
            
            # Filter matches
            filtered = []
            for p in all_products:
                use_stock = p[12] if len(p) > 12 and p[12] is not None else 1
                if use_stock == 0: continue
                
                if search_term in p[1].lower() or (p[5] and search_term in p[5].lower()):
                    filtered.append(p)
            
            if not filtered:
                ctk.CTkLabel(products_frame, text="No products found", text_color=COLORS["text_secondary"]).pack(pady=10)
                return
            
            for product in filtered[:20]:
                stock_color = COLORS["danger"] if product[4] < 10 else COLORS["text_primary"]
                btn = ctk.CTkButton(
                    products_frame,
                    text=f"{product[1]} - Stock: {product[4]}",
                    command=lambda p=product: self.open_stock_modal(p, "remove", lambda: update_product_list()),
                    height=40,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    fg_color="transparent",
                    text_color=stock_color,
                    hover_color=COLORS["primary"],
                    anchor="w"
                )
                btn.pack(fill="x", pady=1, padx=3)
        
        search_var.trace("w", update_product_list)
        update_product_list()

    def open_stock_modal(self, product, mode, on_success=None):
        """Open modal for adding/removing stock"""
        is_add = (mode == "add")
        title_text = f"Stock In - {product[1]}" if is_add else f"Stock Out - {product[1]}"
        color = COLORS["success"] if is_add else COLORS["danger"]
        
        modal = ctk.CTkToplevel(self.parent)
        modal.title(title_text)
        modal.geometry("400x450")
        
        # Center modal
        x = (modal.winfo_screenwidth() - 400) // 2
        y = (modal.winfo_screenheight() - 450) // 2
        modal.geometry(f"+{x}+{y}")
        
        modal.configure(fg_color=COLORS["dark"])
        modal.transient(self.parent)
        modal.grab_set()
        
        # Fetch last restock info
        last_restock_text = "No recent history"
        adjustments = self.database.get_stock_adjustments(product[0], limit=5)
        # Find last 'add' if mode is add, or just last
        found_date = None
        for adj in adjustments:
            # adj[2] is type, adj[6] is date
            if adj[2] == 'add': 
                found_date = datetime.strptime(adj[6], "%Y-%m-%d %H:%M:%S")
                break
        
        if found_date:
            days = (datetime.now() - found_date).days
            if days == 0:
                last_restock_text = "Restocked today"
            elif days == 1:
                last_restock_text = "Restocked yesterday"
            else:
                last_restock_text = f"Last restocked {days} days ago"
        
        # UI
        ctk.CTkLabel(modal, text=product[1], font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(30, 5))
        ctk.CTkLabel(modal, text=f"Current Stock: {product[4]}", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]).pack(pady=(0, 5))
        ctk.CTkLabel(modal, text=last_restock_text, font=ctk.CTkFont(size=12, slant="italic"), text_color=COLORS["info"]).pack(pady=(0, 20))
        
        # Form
        input_label = "ADD QTY:" if is_add else "REMOVE QTY:"
        ctk.CTkLabel(modal, text=input_label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=40)
        
        qty_entry = ctk.CTkEntry(modal, placeholder_text="0", height=35)
        qty_entry.pack(fill="x", padx=40, pady=(5, 15))
        qty_entry.focus()
        
        ctk.CTkLabel(modal, text="REASON:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=40)
        reasons = ["Purchase", "Return", "Adjustment", "Other"] if is_add else ["Damage", "Expired", "Theft", "Use", "Other"]
        reason_var = ctk.StringVar(value=reasons[0])
        reason_menu = ctk.CTkOptionMenu(modal, values=reasons, variable=reason_var, height=35, fg_color=COLORS["card_bg"], button_color=COLORS["primary"])
        reason_menu.pack(fill="x", padx=40, pady=(5, 15))
        
        ctk.CTkLabel(modal, text="NOTES (OPTIONAL):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=40)
        notes_entry = ctk.CTkEntry(modal, placeholder_text="Notes...", height=35)
        notes_entry.pack(fill="x", padx=40, pady=(5, 20))
        
        def save(event=None):
            try:
                qty = int(qty_entry.get())
                if qty <= 0: raise ValueError
            except:
                messagebox.showerror("Error", "Invalid Quantity")
                return
            
            if not is_add and qty > product[4]:
                messagebox.showerror("Error", "Insufficient Stock")
                return
            
            change = qty if is_add else -qty
            self.database.update_product_stock(product[0], change)
            
            # Log
            act_type = "Stock In" if is_add else "Stock Out"
            notes = notes_entry.get()
            details = f"{act_type}: {product[1]} {change:+} ({reason_var.get()}) {notes}"
            self.database.log_activity(self.user_data['id'], self.user_data['username'], act_type, details)
            
            # Stock Adjustment Log
            adj_type = "add" if is_add else "remove"
            self.database.cursor.execute("""
                INSERT INTO stock_adjustments (product_id, adjustment_type, quantity, reason, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (product[0], adj_type, qty, reason_var.get(), self.user_data['id']))
            self.database.conn.commit()
            
            messagebox.showinfo("Success", "Stock Updated")
            modal.destroy()
            if on_success: on_success()
            
        qty_entry.bind("<Return>", save)
        notes_entry.bind("<Return>", save)

        ctk.CTkButton(modal, text="SAVE", height=40, font=ctk.CTkFont(weight="bold"), fg_color=color, hover_color=color, command=save).pack(fill="x", padx=40, pady=10)
    
    def show_suppliers(self):
        """Show suppliers management"""
        # Clear previous content
        for widget in self.inventory_content.winfo_children():
            widget.destroy()

        # Header
        header = ctk.CTkFrame(self.inventory_content, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header, text="🏢 Suppliers", font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkButton(
            header, text="+ Add Supplier", command=self.add_supplier_dialog,
            width=120, height=32, fg_color=COLORS["success"], font=ctk.CTkFont(weight="bold")
        ).pack(side="right")
        
        # Suppliers Grid
        content_frame = ctk.CTkScrollableFrame(self.inventory_content, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        suppliers = self.database.get_all_suppliers()
        
        if not suppliers:
            ctk.CTkLabel(
                content_frame, text="No suppliers found. Add one to get started!",
                font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return

        # Suppliers List
        list_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        list_frame.pack(fill="x")
        
        for idx, supp in enumerate(suppliers):
            # supp: (id, name, contact_person, phone, email, address, created_at)
            row = ctk.CTkFrame(list_frame, fg_color=COLORS["card_bg"], corner_radius=8, height=50)
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)
            
            # Clickable area
            btn = ctk.CTkButton(
                row,
                text=f"  📁  {supp[1]}",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="transparent",
                hover_color=COLORS["primary"],
                anchor="w",
                command=lambda s=supp: self.open_supplier_details(s)
            )
            btn.pack(side="left", fill="both", expand=True, padx=5)
            
            # Optional contact info badge
            contact = supp[2] or supp[3] or "" # contact_person or phone
            if contact:
                ctk.CTkLabel(
                    row,
                    text=contact,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"],
                    padx=10
                ).pack(side="right")

    def add_supplier_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Supplier")
        dialog.geometry("400x300")
        
        # Center
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 300) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent); dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Add New Supplier", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Supplier Name", width=250)
        name_entry.pack(pady=10)
        name_entry.focus()
        
        info_entry = ctk.CTkEntry(dialog, placeholder_text="Contact Info (Optional)", width=250)
        info_entry.pack(pady=10)
        
        def save(event=None):
            name = name_entry.get().strip()
            if not name: messagebox.showerror("Error", "Name required"); return
            try:
                # Map info input to contact_person
                self.database.add_supplier(name, contact_person=info_entry.get().strip())
                messagebox.showinfo("Success", "Supplier Added")
                dialog.destroy()
                self.show_suppliers() # Refresh
            except Exception as e: messagebox.showerror("Error", str(e))
        
        name_entry.bind("<Return>", save)
        info_entry.bind("<Return>", save)
            
        ctk.CTkButton(dialog, text="Save", command=save, fg_color=COLORS["success"]).pack(pady=20)

    def open_supplier_details(self, supplier):
        # Clear content specific to tab
        for widget in self.inventory_content.winfo_children(): widget.destroy()
        
        # Header with Back Button
        header = ctk.CTkFrame(self.inventory_content, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkButton(
            header, text="← Back", width=80, height=28, fg_color="transparent", border_width=1,
            text_color=COLORS["text_primary"], command=self.show_suppliers
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header, text=f"📁 {supplier[1]}", font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Linked Products
        products = self.database.get_products_by_supplier(supplier[0])
        
        ctk.CTkLabel(
            self.inventory_content, text=f"Linked Products ({len(products)})", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        prod_list = ctk.CTkScrollableFrame(self.inventory_content, fg_color="transparent")
        prod_list.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        if not products:
            ctk.CTkLabel(prod_list, text="No products linked to this supplier yet.", text_color=COLORS["text_secondary"]).pack(pady=20)
        else:
            # Table Header
            h_frame = ctk.CTkFrame(prod_list, fg_color=COLORS["dark"], height=30)
            h_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(h_frame, text="Product Name", font=ctk.CTkFont(weight="bold"), width=200, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(h_frame, text="Category", font=ctk.CTkFont(weight="bold"), width=100, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(h_frame, text="Stock", font=ctk.CTkFont(weight="bold"), width=80, anchor="center").pack(side="left", padx=10)
            ctk.CTkLabel(h_frame, text="Price", font=ctk.CTkFont(weight="bold"), width=80, anchor="e").pack(side="right", padx=10)
            
            for p in products:
                row = ctk.CTkFrame(prod_list, fg_color=COLORS["card_bg"])
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=p[1], width=200, anchor="w").pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(row, text=p[2], width=100, anchor="w", text_color=COLORS["text_secondary"]).pack(side="left", padx=10)
                
                stock_color = COLORS["danger"] if p[4] < 10 else COLORS["text_secondary"]
                ctk.CTkLabel(row, text=str(p[4]), width=80, anchor="center", text_color=stock_color, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                
                ctk.CTkLabel(row, text=f"{CURRENCY_SYMBOL}{p[3]:.2f}", width=80, anchor="e", text_color=COLORS["success"]).pack(side="right", padx=10)

    def show_all_items_modal(self):
        """Show modal with all items and stock levels"""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("All Stock Items")
        modal.geometry("700x600")
        
        # Center modal
        x = (modal.winfo_screenwidth() - 700) // 2
        y = (modal.winfo_screenheight() - 600) // 2
        modal.geometry(f"+{x}+{y}")
        
        modal.configure(fg_color=COLORS["dark"])
        modal.transient(self.parent)
        modal.grab_set() # Modal behavior
        
        # Header
        header = ctk.CTkFrame(modal, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header, 
            text="📦 All Stock Items", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        # Filter
        self.filter_var = ctk.StringVar(value="A-Z")
        filter_menu = ctk.CTkOptionMenu(
            header,
            values=["A-Z", "Recent Restocks", "Out of Stock"],
            variable=self.filter_var,
            width=140,
            height=32,
            fg_color=COLORS["card_bg"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["secondary"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        filter_menu.pack(side="right")
        
        # Search in modal
        search_frame = ctk.CTkFrame(modal, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search products...",
            textvariable=search_var,
            font=ctk.CTkFont(size=13),
            height=35
        )
        search_entry.pack(fill="x")
        
        # List Header
        list_header = ctk.CTkFrame(modal, fg_color=COLORS["card_bg"], height=40)
        list_header.pack(fill="x", padx=20, pady=(10, 5))
        list_header.pack_propagate(False)
        
        h_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        h_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(h_frame, text="Product Name", font=ctk.CTkFont(weight="bold"), width=300, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="Stock", font=ctk.CTkFont(weight="bold"), width=100, anchor="e").pack(side="right", padx=15)
        
        # Product List
        list_frame = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        all_products = self.database.get_all_products()
        
        # Helper to get restock dates (cache)
        self._restock_map = None
        
        def get_restock_map():
            if self._restock_map is None:
                try:
                    self.database.cursor.execute("SELECT product_id, MAX(created_at) FROM stock_adjustments GROUP BY product_id")
                    self._restock_map = {r[0]: r[1] for r in self.database.cursor.fetchall()}
                except:
                    self._restock_map = {}
            return self._restock_map

        def render_list(*args):
             for widget in list_frame.winfo_children():
                 widget.destroy()
             
             term = search_var.get().lower()
             filter_mode = self.filter_var.get()
             
             # Filter first
             filtered = []
             for p in all_products:
                 # Check stock tracking indices: use_stock_tracking=12
                 use_stock = p[12] if len(p) > 12 and p[12] is not None else 1
                 if use_stock == 0:
                     continue
                 
                 # Search filter
                 if term and term not in p[1].lower():
                     continue
                
                 # Out of Stock Filter
                 if filter_mode == "Out of Stock" and p[4] > 0:
                     continue
                     
                 filtered.append(p)
             
             # Apply Sort
             if filter_mode == "A-Z":
                 filtered.sort(key=lambda x: x[1].lower())
             elif filter_mode == "Recent Restocks":
                 rmap = get_restock_map()
                 # Sort by restock date desc, fallback to created_at
                 # p[7] is created_at, p[0] is id
                 filtered.sort(key=lambda x: rmap.get(x[0], x[7]), reverse=True)
             
             if not filtered:
                 ctk.CTkLabel(list_frame, text="No products found", text_color=COLORS["text_secondary"]).pack(pady=20)
                 return

             # Render first 50 items for performance
             for p in filtered[:50]:
                 row = ctk.CTkFrame(list_frame, fg_color="transparent", height=35)
                 row.pack(fill="x", ipady=2)
                 
                 # Name
                 ctk.CTkLabel(
                     row, 
                     text=p[1], 
                     font=ctk.CTkFont(size=13),
                     anchor="w"
                 ).pack(side="left", padx=15)
                 
                 # Stock
                 stock_val = p[4]
                 color = COLORS["danger"] if stock_val < 10 else COLORS["success"]
                 
                 ctk.CTkLabel(
                     row, 
                     text=str(stock_val), 
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=color,
                     width=80,
                     anchor="e"
                 ).pack(side="right", padx=15)
                 
                 # Separator
                 ctk.CTkFrame(list_frame, fg_color=COLORS["dark"], height=1).pack(fill="x", padx=10)
            
             if len(filtered) > 50:
                 ctk.CTkLabel(
                     list_frame, 
                     text=f"... and {len(filtered) - 50} more items. Search to find specific products.", 
                     font=ctk.CTkFont(size=11, slant="italic"),
                     text_color=COLORS["text_secondary"]
                 ).pack(pady=10)
 
        search_var.trace("w", render_list)
        self.filter_var.trace("w", render_list)
        render_list()
