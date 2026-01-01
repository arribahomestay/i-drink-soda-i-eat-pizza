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
        
        # Create product cards (Grid: 3 cols)
        self.products_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="product_grid")
        
        for idx, product in enumerate(products):
            product_card = self.create_product_card(self.products_frame, product)
            row = idx // 3
            col = idx % 3
            product_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
    
    def create_product_card(self, parent, product):
        """Create a product card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["dark"], corner_radius=10)
        
        # Product info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=12)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=product[1],  # name
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"],
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
            text_color=COLORS["success"]
        )
        price_label.pack(side="left")
        
        stock_label = ctk.CTkLabel(
            bottom_row,
            text=f"Stock: {product[4]}",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        stock_label.pack(side="right")
        
        # Add button
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
        add_btn.pack(fill="x", padx=10, pady=(0, 10))
        
        return card
    
    def on_search(self, event):
        """Handle search input"""
        search_term = self.search_entry.get().strip()
        self.load_products(search_term)
