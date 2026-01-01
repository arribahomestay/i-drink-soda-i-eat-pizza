"""
Product grid component for cashier view
Handles product display and search
"""
import customtkinter as ctk
from config import COLORS, CURRENCY_SYMBOL


class ProductGrid:
    def __init__(self, parent, database, add_to_cart_callback):
        self.parent = parent
        self.database = database
        self.add_to_cart_callback = add_to_cart_callback
        self.products_frame = None
        self.search_entry = None
    
    def create(self):
        """Create the product grid UI"""
        # Container
        left_panel = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search bar
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Products",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        search_label.pack(anchor="w", pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by name or barcode...",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(fill="x", pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Products grid
        products_container = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        products_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.products_frame = products_container
        self.load_products()
        
        return left_panel
    
    def load_products(self, search_term=""):
        """Load products into the grid"""
        # Clear existing products
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # Get products
        if search_term:
            products = self.database.search_products(search_term)
        else:
            products = self.database.get_all_products()
            
        # Filter out products from hidden categories
        # Get visible categories first
        visible_categories = self.database.get_all_categories(include_hidden=False)
        visible_cat_names = {c[1] for c in visible_categories} # Set of visible category names
        
        # Filter products (product[2] is category name)
        products = [p for p in products if p[2] in visible_cat_names]
        
        # Filter out only stock-tracked products with 0 stock
        # Availability-mode products should always show (even if not available)
        filtered_products = []
        for p in products:
            # Check if product has the new columns (backwards compatibility)
            # Indices: use_stock_tracking=12, is_available=13
            if len(p) > 12:
                use_stock_tracking = p[12] if p[12] is not None else 1
                
                if use_stock_tracking == 1:
                    # Stock tracking mode - only hide if stock is 0
                    if p[4] > 0:
                        filtered_products.append(p)
                else:
                    # Availability mode - always show (will be grayed out if not available)
                    filtered_products.append(p)
            else:
                # Old products without new columns - show if stock > 0
                if p[4] > 0:
                    filtered_products.append(p)
        
        products = filtered_products
        
        # Create product cards (Grid: 3 cols)
        self.products_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="product_grid")
        
        for idx, product in enumerate(products):
            product_card = self.create_product_card(self.products_frame, product)
            row = idx // 3
            col = idx % 3
            product_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
    
    def create_product_card(self, parent, product):
        """Create a product card"""
        # Check if product is available
        is_available = True
        use_stock_tracking = True
        
        # Indices: use_stock_tracking=12, is_available=13
        if len(product) > 12:
            use_stock_tracking = product[12] if product[12] is not None else 1
            if use_stock_tracking == 0:  # Availability mode
                is_available = product[13] if product[13] is not None else 1
        
        card = ctk.CTkFrame(parent, fg_color=COLORS["dark"], corner_radius=10)
        
        # Product info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=12)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=product[1],  # name
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_secondary"] if not is_available else COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        category_label = ctk.CTkLabel(
            info_frame,
            text=product[2],  # category
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        category_label.pack(anchor="w", pady=(2, 5))
        
        bottom_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        bottom_row.pack(fill="x")
        
        price_label = ctk.CTkLabel(
            bottom_row,
            text=f"{CURRENCY_SYMBOL}{product[3]:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_secondary"] if not is_available else COLORS["success"]
        )
        price_label.pack(side="left")
        
        # Check stock tracking mode and display accordingly
        # Indices: use_stock_tracking=12
        if len(product) > 12 and product[12] == 0:
            # Availability mode - show availability status
            if is_available:
                stock_text = "✓ Available"
                stock_color = COLORS["success"]
            else:
                stock_text = "✗ Not Available"
                stock_color = COLORS["danger"]
        else:
            # Stock tracking mode - show stock count
            stock_val = product[4]
            stock_text = f"Stock: {stock_val}"
            stock_color = COLORS["danger"] if stock_val < 10 else COLORS["text_secondary"]
        
        stock_label = ctk.CTkLabel(
            bottom_row,
            text=stock_text,
            font=ctk.CTkFont(size=10),
            text_color=stock_color
        )
        stock_label.pack(side="right")
        
        # Add button - disabled if not available
        if is_available:
            add_btn = ctk.CTkButton(
                card,
                text="Add to Cart",
                command=lambda p=product: self.add_to_cart_callback(p),
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLORS["primary"],
                hover_color=COLORS["secondary"],
                corner_radius=8
            )
        else:
            add_btn = ctk.CTkButton(
                card,
                text="Not Available",
                command=lambda: None,  # No action
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLORS["text_secondary"],
                hover_color=COLORS["text_secondary"],
                corner_radius=8,
                state="disabled"
            )
        add_btn.pack(fill="x", padx=10, pady=(0, 10))
        
        return card
    
    def on_search(self, event):
        """Handle search input"""
        search_term = self.search_entry.get().strip()
        self.load_products(search_term)
