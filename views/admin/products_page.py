"""
Products management page for admin view
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS, CURRENCY_SYMBOL


class ProductsPage:
    def __init__(self, parent, database, switch_page_callback):
        self.parent = parent
        self.database = database
        self.switch_page = switch_page_callback
        self.selected_category = None
        self.category_search_var = None
        self.product_search_var = None
    
    def show(self):
        """Show products management page with category folders"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="📦 Products Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Main container with two panels
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # LEFT PANEL - Categories (Folders)
        left_panel = ctk.CTkFrame(main_container, fg_color=COLORS["card_bg"], corner_radius=15, width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Categories header
        cat_header = ctk.CTkFrame(left_panel, fg_color=COLORS["dark"], corner_radius=10)
        cat_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            cat_header,
            text="📁 Categories",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=15, pady=12)
        
        add_cat_btn = ctk.CTkButton(
            cat_header,
            text="+",
            command=self.add_category_dialog,
            width=30,
            height=30,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=8
        )
        add_cat_btn.pack(side="right", padx=10)
    
        # Category search bar
        category_search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        category_search_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.category_search_var = ctk.StringVar()
        self.category_search_var.trace("w", self.search_categories)
        
        category_search_entry = ctk.CTkEntry(
            category_search_frame,
            placeholder_text="🔍 Search categories...",
            textvariable=self.category_search_var,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["dark"],
            border_color=COLORS["primary"],
            border_width=1
        )
        category_search_entry.pack(fill="x")
        
        # Categories list
        self.categories_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        self.categories_list_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        # RIGHT PANEL - Products in selected category
        right_panel = ctk.CTkFrame(main_container, fg_color=COLORS["card_bg"], corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Products header
        self.products_header_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.products_header_frame.pack(fill="x", padx=20, pady=20)
        
        self.selected_category_label = ctk.CTkLabel(
            self.products_header_frame,
            text="📦 All Products",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.selected_category_label.pack(side="left")
    
        # Product search bar (right side of header)
        product_search_frame = ctk.CTkFrame(self.products_header_frame, fg_color="transparent")
        product_search_frame.pack(side="right", padx=(10, 0))
        
        self.product_search_var = ctk.StringVar()
        self.product_search_var.trace("w", self.search_products)
        
        self.product_search_entry = ctk.CTkEntry(
            product_search_frame,
            placeholder_text="🔍 Search products...",
            textvariable=self.product_search_var,
            width=250,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["dark"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.product_search_entry.pack(side="right")
        
        self.add_product_btn = ctk.CTkButton(
            self.products_header_frame,
            text="+ Add Product",
            command=lambda: self.add_product_dialog(self.selected_category),
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=10
        )
        
        # Delete Category Button
        self.delete_category_btn = ctk.CTkButton(
            self.products_header_frame,
            text="🗑️ Delete",
            command=self.delete_current_category,
            height=35,
            width=90,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=10
        )
        
        # Hide/Unhide Category Button
        self.hide_category_btn = ctk.CTkButton(
            self.products_header_frame,
            text="👁️ Hide",
            command=self.toggle_category_visibility,
            height=35,
            width=90,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["warning"],
            hover_color="#f39c12",
            corner_radius=10
        )
        
        # Don't pack buttons initially - shown when category selected
        
        # Products grid
        self.products_display_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color=COLORS["dark"],
            corner_radius=10,
            scrollbar_button_color=COLORS["primary"]
        )
        self.products_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initialize with all products (button will be hidden)
        self.selected_category = None
        self.load_categories()
        self.load_products_for_category(None)
    
    def load_categories(self):
        """Load all categories as folder buttons"""
        # Clear existing
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()
        
        # Get categories from database [id, name, is_hidden, ...]
        db_categories = self.database.get_all_categories()
        
        # Also get categories from products (for backwards compatibility)
        products = self.database.get_all_products()
        product_categories = set(p[2] for p in products if p[2])
        
        # Create map of name -> is_hidden
        category_map = {}
        for cat in db_categories:
            category_map[cat[1]] = cat[2] if len(cat) > 2 else 0
            
        # Add legacy check
        for cat_name in product_categories:
            if cat_name not in category_map:
                category_map[cat_name] = 0
        
        # "All Products" button
        all_btn = ctk.CTkButton(
            self.categories_list_frame,
            text="📦 All Products",
            command=lambda: self.select_category(None),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"] if self.selected_category is None else "transparent",
            hover_color=COLORS["primary"],
            corner_radius=10,
            anchor="w"
        )
        all_btn.pack(fill="x", pady=5)
        
        sorted_categories = sorted(category_map.keys())
        
        for category in sorted_categories:
            # Get product count
            count = len([p for p in products if p[2] == category])
            is_hidden = category_map[category]
            
            # Visual cue
            prefix = "👁️‍🗨️" if is_hidden else "📁"
            text_color = COLORS["text_secondary"] if is_hidden else COLORS["text_primary"]
            
            cat_btn = ctk.CTkButton(
                self.categories_list_frame,
                text=f"{prefix} {category} ({count})",
                command=lambda c=category: self.select_category(c),
                height=40,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                fg_color=COLORS["primary"] if self.selected_category == category else "transparent",
                hover_color=COLORS["primary"],
                corner_radius=10,
                anchor="w"
            )
            cat_btn.pack(fill="x", pady=5)
    
    def toggle_category_visibility(self):
        """Toggle the visibility of the current category"""
        if not self.selected_category: return
        
        cat_data = self.database.get_category_by_name(self.selected_category)
        if cat_data:
            cat_id = cat_data[0]
            current_hidden = cat_data[2] if len(cat_data) > 2 else 0
            new_hidden = not current_hidden
            
            self.database.toggle_category_visibility(cat_id, new_hidden)
            
            # Update UI
            status = "Hidden" if new_hidden else "Visible"
            messagebox.showinfo("Success", f"Category is now {status} to cashiers.")
            self.select_category(self.selected_category) # Refresh state

    def delete_current_category(self):
        """Delete the current category and its contents"""
        if not self.selected_category: return
        
        msg = f"WARNING: This will delete the category '{self.selected_category}' AND ALL PRODUCTS inside it.\n\nThis action cannot be undone.\n\nAre you sure?"
        if messagebox.askyesno("Delete Category", msg, icon='warning'):
            cat_data = self.database.get_category_by_name(self.selected_category)
            if cat_data:
                self.database.delete_category(cat_data[0])
                messagebox.showinfo("Success", "Category and products deleted.")
                self.select_category(None) # Go back to All Products
            else:
                 messagebox.showerror("Error", "Category not found in registry.")

    def select_category(self, category):
        """Select a category and show its products"""
        self.selected_category = category
        
        # Clear product search when switching categories
        if self.product_search_var:
            self.product_search_var.set("")
        
        self.load_categories() # Refresh list to highlight selection
        
        # Update header and button visibility
        if category:
            # Check hidden status
            cat_data = self.database.get_category_by_name(category)
            is_hidden = 0
            if cat_data and len(cat_data) > 2:
                is_hidden = cat_data[2]
            
            status_text = " (Hidden)" if is_hidden else ""
            self.selected_category_label.configure(text=f"📁 {category}{status_text}")
            
            # Configure Hide button appearance
            if is_hidden:
                self.hide_category_btn.configure(text="👁️ Unhide", fg_color=COLORS["success"], hover_color="#27ae60")
            else:
                self.hide_category_btn.configure(text="👁️ Hide", fg_color=COLORS["warning"], hover_color="#f39c12")
            
            # Show buttons (Right to Left packing order)
            self.add_product_btn.pack(side="right", padx=5)
            self.hide_category_btn.pack(side="right", padx=5)
            self.delete_category_btn.pack(side="right", padx=5)
            
        else:
            self.selected_category_label.configure(text="📦 All Products")
            # Hide all category-specific buttons
            self.add_product_btn.pack_forget()
            self.hide_category_btn.pack_forget()
            self.delete_category_btn.pack_forget()
        
        # Load products for this category
        self.load_products_for_category(category)
    
    def load_products_for_category(self, category):
        """Load products for selected category"""
        # Clear existing products
        for widget in self.products_display_frame.winfo_children():
            widget.destroy()
        
        # Get products
        all_products = self.database.get_all_products()
        if category:
            products = [p for p in all_products if p[2] == category]
        else:
            products = all_products
        
        if not products:
            ctk.CTkLabel(
                self.products_display_frame,
                text="No products in this category\nClick '+ Add Product' to add one",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return
        
        # Create product cards in grid
        for idx, product in enumerate(products):
            self.create_product_card(self.products_display_frame, product)
    
    def create_product_card(self, parent, product):
        """Create a simple list item (minimal styling for fast loading)"""
        # Simple row container with minimal styling
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=0, height=35, border_width=1, border_color=COLORS["dark"])
        card.pack(fill="x", pady=1, padx=0)
        card.pack_propagate(False)
        
        # Left: Name and Info (simple horizontal layout)
        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=8, pady=4)
        
        # Product Name (simple text)
        name_label = ctk.CTkLabel(
            left_frame, 
            text=product[1], 
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"], 
            anchor="w"
        )
        name_label.pack(side="left", padx=(0, 15))
        
        # Category (simple text, no badge)
        if product[2]:
            cat_label = ctk.CTkLabel(
                left_frame, 
                text=f"[{product[2]}]", 
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"], 
                anchor="w"
            )
            cat_label.pack(side="left", padx=(0, 10))
        
        # Barcode (simple text)
        if product[5]:
            barcode_label = ctk.CTkLabel(
                left_frame, 
                text=f"Barcode: {product[5]}", 
                font=ctk.CTkFont(size=9),
                text_color=COLORS["text_secondary"]
            )
            barcode_label.pack(side="left", padx=(0, 10))

        # Right: Details & Actions
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=8, pady=4)
        
        # Stock with Unit
        stock_val = product[4]
        unit_val = product[8] if len(product) > 8 and product[8] else "pcs"
        stock_text = f"Stock: {stock_val} {unit_val}"
        stock_color = COLORS["danger"] if stock_val < 10 else COLORS["text_secondary"]
        
        stock_label = ctk.CTkLabel(
             right_frame, 
             text=stock_text, 
             font=ctk.CTkFont(size=10),
             text_color=stock_color,
             anchor="e"
        )
        stock_label.pack(side="left", padx=(0, 15))

        # Price (simple text)
        price_label = ctk.CTkLabel(
            right_frame, 
            text=f"{CURRENCY_SYMBOL}{product[3]:.2f}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["success"]
        )
        price_label.pack(side="left", padx=(0, 10))
        
        # Actions (simple buttons)
        edit_btn = ctk.CTkButton(
            right_frame, 
            text="Edit", 
            width=50, 
            height=24,
            command=lambda p=product: self.edit_product_dialog(p),
            font=ctk.CTkFont(size=10), 
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"], 
            corner_radius=3
        )
        edit_btn.pack(side="left", padx=2)
        
        del_btn = ctk.CTkButton(
            right_frame, 
            text="Del", 
            width=50, 
            height=24,
            command=lambda p=product: self.delete_product(p),
            font=ctk.CTkFont(size=10), 
            fg_color=COLORS["danger"],
            hover_color="#c0392b", 
            corner_radius=3
        )
        del_btn.pack(side="left", padx=2)
    
    def search_categories(self, *args):
        """Filter categories based on search input"""
        search_term = self.category_search_var.get().lower().strip()
        
        # Clear existing
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()
        
        # Get categories from database
        db_categories = self.database.get_all_categories()
        products = self.database.get_all_products()
        product_categories = set(p[2] for p in products if p[2])
        
        # Create map of name -> is_hidden
        category_map = {}
        for cat in db_categories:
            category_map[cat[1]] = cat[2] if len(cat) > 2 else 0
            
        # Add legacy check
        for cat_name in product_categories:
            if cat_name not in category_map:
                category_map[cat_name] = 0
        
        # "All Products" button (always show)
        all_btn = ctk.CTkButton(
            self.categories_list_frame,
            text="📦 All Products",
            command=lambda: self.select_category(None),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"] if self.selected_category is None else "transparent",
            hover_color=COLORS["primary"],
            corner_radius=10,
            anchor="w"
        )
        all_btn.pack(fill="x", pady=5)
        
        sorted_categories = sorted(category_map.keys())
        
        # Filter categories based on search
        for category in sorted_categories:
            if search_term and search_term not in category.lower():
                continue
                
            # Get product count
            count = len([p for p in products if p[2] == category])
            is_hidden = category_map[category]
            
            # Visual cue
            prefix = "👁️‍🗨️" if is_hidden else "📁"
            text_color = COLORS["text_secondary"] if is_hidden else COLORS["text_primary"]
            
            cat_btn = ctk.CTkButton(
                self.categories_list_frame,
                text=f"{prefix} {category} ({count})",
                command=lambda c=category: self.select_category(c),
                height=40,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                fg_color=COLORS["primary"] if self.selected_category == category else "transparent",
                hover_color=COLORS["primary"],
                corner_radius=10,
                anchor="w"
            )
            cat_btn.pack(fill="x", pady=5)
    
    def search_products(self, *args):
        """Filter products based on search input"""
        search_term = self.product_search_var.get().lower().strip()
        
        # Clear existing products
        for widget in self.products_display_frame.winfo_children():
            widget.destroy()
        
        # Get products
        all_products = self.database.get_all_products()
        if self.selected_category:
            products = [p for p in all_products if p[2] == self.selected_category]
        else:
            products = all_products
        
        # Filter products based on search term
        if search_term:
            filtered_products = []
            for product in products:
                # Search in: name, category, barcode
                name = product[1].lower() if product[1] else ""
                category = product[2].lower() if product[2] else ""
                barcode = product[5].lower() if product[5] else ""
                
                if (search_term in name or 
                    search_term in category or 
                    search_term in barcode):
                    filtered_products.append(product)
            products = filtered_products
        
        if not products:
            ctk.CTkLabel(
                self.products_display_frame,
                text="No products found\nTry a different search term" if search_term else "No products in this category\nClick '+ Add Product' to add one",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return
        
        # Create product cards
        for product in products:
            self.create_product_card(self.products_display_frame, product)
    
    def add_category_dialog(self):
        """Show add category dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Category")
        
        # Center window
        width, height = 400, 250
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.configure(fg_color=COLORS["dark"])
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Title
        ctk.CTkLabel(
            dialog,
            text="📁 Add New Category",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=20)
        
        # Form
        form_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            form_frame,
            text="Category Name",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        category_entry = ctk.CTkEntry(form_frame, height=40, font=ctk.CTkFont(size=14))
        category_entry.pack(fill="x", padx=20, pady=(0, 20))
        category_entry.focus()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_category():
            category_name = category_entry.get().strip()
            if not category_name:
                messagebox.showerror("Error", "Please enter a category name")
                return
            
            # Check if category already exists in database
            existing = self.database.get_category_by_name(category_name)
            if existing:
                messagebox.showerror("Error", "This category already exists")
                return
            
            try:
                # Save to database
                self.database.add_category(category_name)
                messagebox.showinfo("Success", f"Category '{category_name}' created!\n\nYou can now add products to this category.")
                dialog.destroy()
                self.load_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create category: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            height=40,
            fg_color=COLORS["danger"],
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="Create Category",
            command=save_category,
            height=40,
            fg_color=COLORS["success"],
            corner_radius=10
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Bind Enter key
        category_entry.bind("<Return>", lambda e: save_category())
    
    def add_product_dialog(self, default_category=None):
        """Show add product dialog - Compact version with unit support"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Product")
        
        # Center window - Responsive height
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        width = 600
        height = min(700, int(screen_height * 0.9))
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Fetch Suppliers
        suppliers = self.database.get_all_suppliers()
        supplier_names = [s[1] for s in suppliers]
        supplier_map = {s[1]: s[0] for s in suppliers}
        
        # Title - smaller
        title_text = f"Add to {default_category}" if default_category else "Add New Product"
        ctk.CTkLabel(
            dialog,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        # Form - Scrollable layout to prevent button cropping
        form_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Row 1: Name
        ctk.CTkLabel(form_frame, text="Product Name *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 2))
        row += 1
        name_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12))
        name_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        name_entry.focus()
        row += 1
        
        # Row 2: Category
        ctk.CTkLabel(form_frame, text="Category *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        category_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12))
        if default_category:
            category_entry.insert(0, default_category)
            category_entry.configure(state="disabled")
        category_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 3: Cost, Markup%, Price
        price_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        price_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        price_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(price_frame, text="Cost *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, sticky="w", padx=0, pady=(0, 2))
        ctk.CTkLabel(price_frame, text="Markup %", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=(0, 2))
        ctk.CTkLabel(price_frame, text="Price *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=2, sticky="w", padx=0, pady=(0, 2))
        
        cost_entry = ctk.CTkEntry(price_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="0.00")
        cost_entry.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=0)
        
        markup_entry = ctk.CTkEntry(price_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="0")
        markup_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=0)
        
        price_entry = ctk.CTkEntry(price_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="0.00")
        price_entry.grid(row=1, column=2, sticky="ew", padx=(4, 0), pady=0)
        row += 1
        
        # Auto-calculation logic
        calculating = [False]
        def calculate_price_from_markup(*args):
            if calculating[0]: return
            try:
                cost = float(cost_entry.get() or 0)
                markup = float(markup_entry.get() or 0)
                if cost > 0:
                    calculating[0] = True
                    price = cost * (1 + markup / 100)
                    price_entry.delete(0, "end"); price_entry.insert(0, f"{price:.2f}")
                    calculating[0] = False
            except: calculating[0] = False
        
        def calculate_markup_from_price(*args):
            if calculating[0]: return
            try:
                cost = float(cost_entry.get() or 0)
                price = float(price_entry.get() or 0)
                if cost > 0 and price >= 0:
                    calculating[0] = True
                    markup = ((price - cost) / cost) * 100
                    markup_entry.delete(0, "end"); markup_entry.insert(0, f"{markup:.1f}")
                    calculating[0] = False
            except: calculating[0] = False
        
        cost_entry.bind("<KeyRelease>", calculate_price_from_markup)
        markup_entry.bind("<KeyRelease>", calculate_price_from_markup)
        price_entry.bind("<KeyRelease>", calculate_markup_from_price)
        
        # Row 4: Stock and Unit
        ctk.CTkLabel(form_frame, text="Stock *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, sticky="w", padx=12, pady=(4, 2))
        ctk.CTkLabel(form_frame, text="Unit", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=1, sticky="w", padx=12, pady=(4, 2))
        row += 1
        
        stock_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="0")
        stock_entry.grid(row=row, column=0, sticky="ew", padx=(12, 6), pady=(0, 8))
        
        unit_row = row
        unit_var = ctk.StringVar(value="pcs")
        unit_dropdown = ctk.CTkComboBox(
            form_frame, values=["pcs", "pack", "box", "sack", "Custom..."], variable=unit_var,
            height=28, font=ctk.CTkFont(size=12),dropdown_font=ctk.CTkFont(size=11), button_color=COLORS["primary"]
        )
        unit_dropdown.grid(row=unit_row, column=1, sticky="ew", padx=(6, 12), pady=(0, 8))
        
        custom_unit_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="Unit")
        
        def on_unit_change(choice):
            if choice == "Custom...":
                custom_unit_entry.grid(row=unit_row, column=1, sticky="ew", padx=(6, 12), pady=(0, 8))
                custom_unit_entry.focus()
                unit_dropdown.grid_forget()
        
        unit_dropdown.configure(command=on_unit_change)
        def show_unit_dropdown():
            custom_unit_entry.grid_forget()
            unit_dropdown.grid(row=unit_row, column=1, sticky="ew", padx=(6, 12), pady=(0, 8))
        custom_unit_entry.bind("<Escape>", lambda e: show_unit_dropdown())
        row += 1
        
        # Row 5: Supplier (New Field)
        ctk.CTkLabel(form_frame, text="Supplier", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        
        supplier_combo = ctk.CTkComboBox(
            form_frame, 
            values=supplier_names if supplier_names else [""],
            height=28, 
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11),
            button_color=COLORS["primary"]
        )
        if not supplier_names: supplier_combo.set("") # Clear if empty
        else: supplier_combo.set("") # Default empty (Optional)
            
        supplier_combo.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 6: Barcode
        ctk.CTkLabel(form_frame, text="Barcode", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        barcode_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="Optional")
        barcode_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 7: Description
        ctk.CTkLabel(form_frame, text="Description", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        desc_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="Optional")
        desc_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        row += 1
        
        # Note
        ctk.CTkLabel(form_frame, text="ℹ️ Save to configure Ingredients, Variants & Modifiers", font=ctk.CTkFont(size=10, slant="italic"), text_color=COLORS["text_secondary"]).grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        def clear_fields():
            name_entry.delete(0, "end"); cost_entry.delete(0, "end"); markup_entry.delete(0, "end"); price_entry.delete(0, "end")
            stock_entry.delete(0, "end"); barcode_entry.delete(0, "end"); desc_entry.delete(0, "end"); supplier_combo.set("")
            unit_var.set("pcs"); show_unit_dropdown(); name_entry.focus()
        
        def get_unit_value():
            if custom_unit_entry.winfo_ismapped(): return custom_unit_entry.get().strip() or "pcs"
            return unit_var.get()
        
        def save_product(close_after=True):
            category = default_category if default_category else category_entry.get()
            if not name_entry.get().strip(): messagebox.showerror("Error", "Name required"); name_entry.focus(); return None
            if not category.strip(): messagebox.showerror("Error", "Category required"); return None
            
            try:
                # Handle Supplier
                supp_name = supplier_combo.get().strip()
                supp_id = None
                if supp_name:
                    if supp_name in supplier_map:
                        supp_id = supplier_map[supp_name]
                    else:
                        # Add new supplier
                        supp_id = self.database.add_supplier(supp_name)
                        # Update map
                        supplier_map[supp_name] = supp_id
                        supplier_names.append(supp_name)
                        supplier_combo.configure(values=supplier_names)
                
                unit = get_unit_value()
                cost_val = float(cost_entry.get() or 0)
                markup_val = float(markup_entry.get() or 0)
                
                product_id = self.database.add_product(
                    name_entry.get().strip(), category.strip(), float(price_entry.get() or 0),
                    int(stock_entry.get() or 0), barcode_entry.get().strip() or None, desc_entry.get().strip() or None,
                    unit, cost_val, markup_val, supplier_id=supp_id
                )
                
                full_desc = desc_entry.get().strip() or ""
                if unit != "pcs": full_desc = f"{full_desc} | Unit: {unit}" if full_desc else f"Unit: {unit}"
                
                if full_desc != desc_entry.get().strip():
                    self.database.update_product(
                        product_id, name_entry.get().strip(), category.strip(),
                        float(price_entry.get() or 0), int(stock_entry.get() or 0),
                        barcode_entry.get().strip() or None, full_desc,
                        unit, cost_val, markup_val, supplier_id=supp_id
                    )
                
                if close_after:
                    messagebox.showinfo("Success", "Product added!")
                    dialog.destroy()
                    self.switch_page("products")
                else:
                    clear_fields(); dialog.title("✓ Added - Add Another"); dialog.after(1500, lambda: dialog.title("Add Product"))
                return product_id
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}"); return None
        
        def handle_enter(event): save_product(close_after=False); return "break"
            
        for entry in [name_entry, category_entry, cost_entry, markup_entry, price_entry, stock_entry, barcode_entry, desc_entry, custom_unit_entry]:
            entry.bind("<Return>", handle_enter) # supplier_combo doesn't need bind usually
            
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, border_width=1, fg_color="transparent", text_color=COLORS["text_primary"], width=60).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save & Add", command=lambda: save_product(False), fg_color=COLORS["secondary"], width=100).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Save", command=lambda: save_product(True), fg_color=COLORS["success"], width=80).pack(side="right")
    
    def edit_product_dialog(self, product, open_tab=None):
        """Show edit product dialog - Compact version"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Product")
        
        # Center window - Responsive height
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        width = 620
        height = min(800, int(screen_height * 0.9))
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Fetch Suppliers
        suppliers = self.database.get_all_suppliers()
        supplier_names = [s[1] for s in suppliers]
        supplier_map = {s[1]: s[0] for s in suppliers}
        supplier_id_map = {s[0]: s[1] for s in suppliers}
        
        # Title
        ctk.CTkLabel(
            dialog, text="Edit Product",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        # Form - Scrollable layout
        form_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        form_frame.grid_columnconfigure((0, 1), weight=1)
        row = 0
        
        # Row 1: Name
        ctk.CTkLabel(form_frame, text="Product Name *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 2))
        row += 1
        name_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12))
        name_entry.insert(0, product[1])
        name_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 2: Category
        ctk.CTkLabel(form_frame, text="Category *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        
        all_products = self.database.get_all_products()
        db_categories = self.database.get_all_categories()
        categories_set = set()
        for cat in db_categories: categories_set.add(cat[1])
        for prod in all_products: categories_set.add(prod[2])
        categories_list = sorted(list(categories_set))
        
        category_dropdown = ctk.CTkComboBox(
            form_frame, values=categories_list if categories_list else ["No categories"],
            height=28, font=ctk.CTkFont(size=12), dropdown_font=ctk.CTkFont(size=11),
            button_color=COLORS["primary"]
        )
        if product[2]: category_dropdown.set(product[2])
        elif categories_list and categories_list[0] != "No categories": category_dropdown.set(categories_list[0])
        
        category_dropdown.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 3: Cost, Markup%, Price
        price_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        price_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        price_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(price_frame, text="Cost *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, sticky="w", padx=0, pady=(0, 2))
        ctk.CTkLabel(price_frame, text="Markup %", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=(0, 2))
        ctk.CTkLabel(price_frame, text="Price *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=2, sticky="w", padx=0, pady=(0, 2))
        
        current_price = product[3]
        if len(product) > 10:
            current_cost = product[9] if product[9] > 0 else current_price
            current_markup = product[10]
        else:
            current_cost = current_price
            current_markup = 0.0
        
        cost_entry = ctk.CTkEntry(price_frame, height=28, font=ctk.CTkFont(size=12))
        cost_entry.insert(0, f"{current_cost:.2f}")
        cost_entry.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=0)
        
        markup_entry = ctk.CTkEntry(price_frame, height=28, font=ctk.CTkFont(size=12))
        markup_entry.insert(0, f"{current_markup:.1f}")
        markup_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=0)
        
        price_entry = ctk.CTkEntry(price_frame, height=28, font=ctk.CTkFont(size=12))
        price_entry.insert(0, str(current_price))
        price_entry.grid(row=1, column=2, sticky="ew", padx=(4, 0), pady=0)
        row += 1
        
        calculating = [False]
        def calculate_price_from_markup(*args):
            if calculating[0]: return
            try:
                cost = float(cost_entry.get() or 0)
                markup = float(markup_entry.get() or 0)
                if cost > 0:
                    calculating[0] = True
                    price = cost * (1 + markup / 100)
                    price_entry.delete(0, "end"); price_entry.insert(0, f"{price:.2f}")
                    calculating[0] = False
            except: calculating[0] = False
        
        def calculate_markup_from_price(*args):
            if calculating[0]: return
            try:
                cost = float(cost_entry.get() or 0)
                price = float(price_entry.get() or 0)
                if cost > 0 and price >= 0:
                    calculating[0] = True
                    markup = ((price - cost) / cost) * 100
                    markup_entry.delete(0, "end"); markup_entry.insert(0, f"{markup:.1f}")
                    calculating[0] = False
            except: calculating[0] = False
        
        cost_entry.bind("<KeyRelease>", calculate_price_from_markup)
        markup_entry.bind("<KeyRelease>", calculate_price_from_markup)
        price_entry.bind("<KeyRelease>", calculate_markup_from_price)
        
        # Row 4: Stock and Unit
        form_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(form_frame, text="Stock *", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, sticky="w", padx=12, pady=(4, 2))
        ctk.CTkLabel(form_frame, text="Unit", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=1, sticky="w", padx=12, pady=(4, 2))
        row += 1
        
        stock_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12))
        stock_entry.insert(0, str(product[4]))
        stock_entry.grid(row=row, column=0, sticky="ew", padx=(12, 6), pady=(0, 8))
        
        current_unit = product[8] if len(product) > 8 and product[8] else "pcs"
        unit_var = ctk.StringVar(value=current_unit)
        unit_dropdown = ctk.CTkComboBox(
            form_frame, values=["pcs", "pack", "box", "sack", "Custom..."], variable=unit_var,
            height=28, font=ctk.CTkFont(size=12), dropdown_font=ctk.CTkFont(size=11),
            button_color=COLORS["primary"]
        )
        unit_dropdown.grid(row=row, column=1, sticky="ew", padx=(6, 12), pady=(0, 8))
        
        def on_unit_change(choice):
            if choice == "Custom...":
                d = ctk.CTkInputDialog(text="Enter custom unit:", title="Custom Unit")
                new_unit = d.get_input()
                if new_unit: unit_dropdown.set(new_unit)
                else: unit_dropdown.set("pcs")
        unit_dropdown.configure(command=on_unit_change)
        
        row += 1
        
        # Row 5: Supplier
        ctk.CTkLabel(form_frame, text="Supplier", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        
        supplier_combo = ctk.CTkComboBox(
            form_frame, 
            values=supplier_names if supplier_names else [""],
            height=28, 
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11),
            button_color=COLORS["primary"]
        )
        # Pre-select supplier if exists
        current_supp_name = ""
        if len(product) > 11 and product[11]: # supplier_id
            current_supp_name = supplier_id_map.get(product[11], "")
        
        if current_supp_name: supplier_combo.set(current_supp_name)
        elif not supplier_names: supplier_combo.set("")
        else: supplier_combo.set("")
            
        supplier_combo.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 6: Barcode
        ctk.CTkLabel(form_frame, text="Barcode", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        barcode_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="Optional")
        barcode_entry.insert(0, product[5] or "")
        barcode_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 7: Description
        ctk.CTkLabel(form_frame, text="Description", font=ctk.CTkFont(size=10, weight="bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 2))
        row += 1
        desc_entry = ctk.CTkEntry(form_frame, height=28, font=ctk.CTkFont(size=12), placeholder_text="Optional")
        desc_entry.insert(0, product[6] or "")
        desc_entry.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        row += 1
        
        # Row 7: Product Options (Variants, Modifiers, Ingredients)
        options_label = ctk.CTkLabel(form_frame, text="⚙️ Product Options", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_primary"])
        options_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 4))
        row += 1
        
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        options_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        def manage_variants():
            var_dialog = ctk.CTkToplevel(dialog)
            var_dialog.title("Manage Variants")
            var_dialog.geometry("550x450")
            var_dialog.configure(fg_color=COLORS["dark"])
            var_dialog.transient(dialog); var_dialog.grab_set()
            
            ctk.CTkLabel(var_dialog, text=f"Variants: {product[1]}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=10)
            
            variants = self.database.get_variants(product[0])
            variants_frame = ctk.CTkScrollableFrame(var_dialog, fg_color=COLORS["card_bg"], corner_radius=8)
            variants_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
            
            def refresh_variants():
                for widget in variants_frame.winfo_children(): widget.destroy()
                current_variants = self.database.get_variants(product[0])
                if current_variants:
                    for variant in current_variants:
                        v_row = ctk.CTkFrame(variants_frame, fg_color=COLORS["dark"], corner_radius=6)
                        v_row.pack(fill="x", pady=2, padx=4)
                        info = ctk.CTkFrame(v_row, fg_color="transparent")
                        info.pack(side="left", fill="x", expand=True, padx=8, pady=6)
                        ctk.CTkLabel(info, text=f"{variant[2]}: {variant[3]}", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
                        ctk.CTkLabel(info, text=f"+{CURRENCY_SYMBOL}{variant[4]:.2f} | Stock: {variant[5]}", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"]).pack(anchor="w")
                        ctk.CTkButton(v_row, text="Del", width=40, height=24, fg_color=COLORS["danger"], font=ctk.CTkFont(size=10), command=lambda vid=variant[0]: delete_variant(vid)).pack(side="right", padx=8)
                else:
                    ctk.CTkLabel(variants_frame, text="No variants yet.", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=11)).pack(pady=15)
            
            def delete_variant(vid):
                if messagebox.askyesno("Confirm", "Delete variant?"): self.database.delete_variant(vid); refresh_variants()
            
            refresh_variants()
            
            add_frame = ctk.CTkFrame(var_dialog, fg_color=COLORS["card_bg"], corner_radius=8)
            add_frame.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkLabel(add_frame, text="Add Variant", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(8, 4), padx=10)
            
            fields_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            fields_frame.pack(fill="x", padx=10, pady=(0, 8))
            fields_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            type_entry = ctk.CTkEntry(fields_frame, placeholder_text="Type", height=26, font=ctk.CTkFont(size=11))
            type_entry.grid(row=0, column=0, sticky="ew", padx=2)
            name_entry = ctk.CTkEntry(fields_frame, placeholder_text="Name", height=26, font=ctk.CTkFont(size=11))
            name_entry.grid(row=0, column=1, sticky="ew", padx=2)
            price_entry = ctk.CTkEntry(fields_frame, placeholder_text="Price+", height=26, font=ctk.CTkFont(size=11))
            price_entry.grid(row=0, column=2, sticky="ew", padx=2)
            stock_entry = ctk.CTkEntry(fields_frame, placeholder_text="Stock", height=26, font=ctk.CTkFont(size=11))
            stock_entry.grid(row=0, column=3, sticky="ew", padx=2)
            
            def add_variant():
                try:
                    self.database.add_variant(product[0], type_entry.get(), name_entry.get(), float(price_entry.get() or 0), int(stock_entry.get() or 0))
                    for e in [type_entry, name_entry, price_entry, stock_entry]: e.delete(0, "end")
                    refresh_variants()
                except Exception as e: messagebox.showerror("Error", str(e))
                
            ctk.CTkButton(add_frame, text="Add", command=add_variant, height=28, fg_color=COLORS["success"], font=ctk.CTkFont(size=11)).pack(fill="x", padx=10, pady=(0, 8))
            ctk.CTkButton(var_dialog, text="Done", command=var_dialog.destroy, height=32, fg_color=COLORS["primary"], font=ctk.CTkFont(size=11)).pack(fill="x", padx=15, pady=(0, 15))

        def manage_modifiers():
            mod_dialog = ctk.CTkToplevel(dialog)
            mod_dialog.title("Manage Modifiers")
            mod_dialog.geometry("650x500")
            mod_dialog.configure(fg_color=COLORS["dark"])
            mod_dialog.transient(dialog); mod_dialog.grab_set()
            
            ctk.CTkLabel(mod_dialog, text=f"Modifiers: {product[1]}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=10)
            
            modifiers_frame = ctk.CTkScrollableFrame(mod_dialog, fg_color=COLORS["card_bg"], corner_radius=8)
            modifiers_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
            
            def refresh_modifiers():
                for widget in modifiers_frame.winfo_children(): widget.destroy()
                current_modifiers = self.database.get_modifiers(product[0])
                if current_modifiers:
                    for modifier in current_modifiers:
                        m_row = ctk.CTkFrame(modifiers_frame, fg_color=COLORS["dark"], corner_radius=6)
                        m_row.pack(fill="x", pady=2, padx=4)
                        
                        # Info section on the left
                        info = ctk.CTkFrame(m_row, fg_color="transparent")
                        info.pack(side="left", fill="x", expand=True, padx=8, pady=6)
                        
                        # Modifier name
                        mod_name = modifier[2] if len(modifier) > 2 else "Unknown"
                        ctk.CTkLabel(info, text=mod_name, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
                        
                        # Price text
                        mod_price = modifier[3] if len(modifier) > 3 else 0
                        price_text = f"+{CURRENCY_SYMBOL}{mod_price:.2f}"
                        
                        # Show linked product info if exists
                        try:
                            if len(modifier) > 4 and modifier[4]:  # linked_product_id exists
                                linked_name = modifier[6] if len(modifier) > 6 and modifier[6] else "Unknown"
                                linked_stock = modifier[7] if len(modifier) > 7 else 0
                                deduct_qty = modifier[5] if len(modifier) > 5 else 1
                                price_text += f" | 🔗 {linked_name} (-{deduct_qty}) [Stock: {linked_stock}]"
                        except:
                            pass  # If there's any issue with linked product data, just show basic info
                        
                        ctk.CTkLabel(info, text=price_text, font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"]).pack(anchor="w")
                        
                        # Delete button on the right - always visible
                        mod_id = modifier[0] if len(modifier) > 0 else None
                        if mod_id:
                            ctk.CTkButton(
                                m_row, 
                                text="Del", 
                                width=50, 
                                height=28, 
                                fg_color=COLORS["danger"], 
                                hover_color="#c0392b",
                                font=ctk.CTkFont(size=10, weight="bold"), 
                                command=lambda mid=mod_id: delete_modifier(mid)
                            ).pack(side="right", padx=8, pady=6)
                else:
                    ctk.CTkLabel(modifiers_frame, text="No modifiers yet.", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=11)).pack(pady=15)
            
            def delete_modifier(mid):
                if messagebox.askyesno("Confirm", "Delete modifier?"): self.database.delete_modifier(mid); refresh_modifiers()
            
            refresh_modifiers()
            
            add_frame = ctk.CTkFrame(mod_dialog, fg_color=COLORS["card_bg"], corner_radius=8)
            add_frame.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkLabel(add_frame, text="Add Modifier", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(8, 4), padx=10)
            
            fields_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            fields_frame.pack(fill="x", padx=10, pady=(0, 8))
            fields_frame.grid_columnconfigure((0, 1), weight=1)
            
            name_entry = ctk.CTkEntry(fields_frame, placeholder_text="Name", height=26, font=ctk.CTkFont(size=11))
            name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            price_entry = ctk.CTkEntry(fields_frame, placeholder_text="Price+", height=26, font=ctk.CTkFont(size=11))
            price_entry.grid(row=0, column=1, sticky="ew", padx=(4, 0))
            
            # Product linking section
            link_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            link_frame.pack(fill="x", padx=10, pady=(4, 0))
            link_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(link_frame, text="Link to Product (Optional):", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
            
            # Get all products for dropdown
            all_products = self.database.get_all_products()
            product_options = ["None"] + [f"{p[1]} (Stock: {p[4]})" for p in all_products]
            product_map = {f"{p[1]} (Stock: {p[4]})": p[0] for p in all_products}
            
            product_var = ctk.StringVar(value="None")
            product_dropdown = ctk.CTkComboBox(link_frame, values=product_options, variable=product_var, height=26, font=ctk.CTkFont(size=10), dropdown_font=ctk.CTkFont(size=10))
            product_dropdown.grid(row=1, column=0, sticky="ew", padx=(0, 4))
            
            def on_product_link_change(choice):
                if choice == "None": return
                pid = product_map.get(choice)
                if pid:
                    # Find product in list [id, name, cat, price, stock, ...]
                    selected_p = next((p for p in all_products if p[0] == pid), None)
                    if selected_p:
                        name_entry.delete(0, "end"); name_entry.insert(0, selected_p[1])
                        price_entry.delete(0, "end"); price_entry.insert(0, f"{selected_p[3]:.2f}")
            
            product_dropdown.configure(command=on_product_link_change)
            
            qty_entry = ctk.CTkEntry(link_frame, placeholder_text="Qty", width=60, height=26, font=ctk.CTkFont(size=10))
            qty_entry.insert(0, "1")
            qty_entry.grid(row=1, column=1, sticky="ew")
            
            def add_modifier():
                try:
                    linked_product_id = None
                    deduct_qty = 1
                    
                    if product_var.get() != "None":
                        linked_product_id = product_map.get(product_var.get())
                        try:
                            deduct_qty = float(qty_entry.get() or 1)
                        except:
                            deduct_qty = 1
                    
                    self.database.add_modifier(
                        product[0], 
                        name_entry.get(), 
                        float(price_entry.get() or 0),
                        linked_product_id,
                        deduct_qty
                    )
                    name_entry.delete(0, "end")
                    price_entry.delete(0, "end")
                    product_var.set("None")
                    qty_entry.delete(0, "end")
                    qty_entry.insert(0, "1")
                    refresh_modifiers()
                except Exception as e: 
                    messagebox.showerror("Error", str(e))
                
            ctk.CTkButton(add_frame, text="Add", command=add_modifier, height=28, fg_color=COLORS["success"], font=ctk.CTkFont(size=11)).pack(fill="x", padx=10, pady=(4, 8))
            ctk.CTkButton(mod_dialog, text="Done", command=mod_dialog.destroy, height=32, fg_color=COLORS["primary"], font=ctk.CTkFont(size=11)).pack(fill="x", padx=15, pady=(0, 15))

        def manage_prices():
            price_dialog = ctk.CTkToplevel(dialog)
            price_dialog.title("Manage Prices")
            price_dialog.geometry("600x500")
            price_dialog.configure(fg_color=COLORS["dark"])
            price_dialog.transient(dialog); price_dialog.grab_set()
            
            # Center
            sw = price_dialog.winfo_screenwidth()
            sh = price_dialog.winfo_screenheight()
            price_dialog.geometry(f"600x500+{(sw-600)//2}+{(sh-500)//2}")
            
            ctk.CTkLabel(price_dialog, text=f"Alternative Prices: {product[1]}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=10)
            
            prices_frame = ctk.CTkScrollableFrame(price_dialog, fg_color=COLORS["card_bg"], corner_radius=8)
            prices_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
            
            def refresh_prices():
                for widget in prices_frame.winfo_children(): widget.destroy()
                current_prices = self.database.get_product_prices(product[0])
                
                # Header
                h_row = ctk.CTkFrame(prices_frame, fg_color="transparent")
                h_row.pack(fill="x", pady=2, padx=4)
                ctk.CTkLabel(h_row, text="Name", font=ctk.CTkFont(size=10, weight="bold"), width=100, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(h_row, text="Cost", font=ctk.CTkFont(size=10, weight="bold"), width=60, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(h_row, text="Markup", font=ctk.CTkFont(size=10, weight="bold"), width=50, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(h_row, text="Price", font=ctk.CTkFont(size=10, weight="bold"), width=60, anchor="w").pack(side="left", padx=5)
                
                if current_prices:
                    for pr in current_prices:
                        # pr: [id, product_id, name, cost, markup, price, created_at]
                        p_row = ctk.CTkFrame(prices_frame, fg_color=COLORS["dark"], corner_radius=6)
                        p_row.pack(fill="x", pady=2, padx=4)
                        
                        ctk.CTkLabel(p_row, text=pr[2], font=ctk.CTkFont(size=11), width=100, anchor="w").pack(side="left", padx=5)
                        ctk.CTkLabel(p_row, text=f"{pr[3]:.2f}", font=ctk.CTkFont(size=11), width=60, anchor="w").pack(side="left", padx=5)
                        ctk.CTkLabel(p_row, text=f"{pr[4]:.1f}%", font=ctk.CTkFont(size=11), width=50, anchor="w", text_color=COLORS["warning"]).pack(side="left", padx=5)
                        ctk.CTkLabel(p_row, text=f"{pr[5]:.2f}", font=ctk.CTkFont(size=11, weight="bold"), width=60, anchor="w", text_color=COLORS["success"]).pack(side="left", padx=5)
                        
                        ctk.CTkButton(
                            p_row, text="Del", width=40, height=24, 
                            fg_color=COLORS["danger"], font=ctk.CTkFont(size=10),
                            command=lambda pid=pr[0]: delete_price(pid)
                        ).pack(side="right", padx=5, pady=5)
                else:
                    ctk.CTkLabel(prices_frame, text="No alternative prices yet.", text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=11)).pack(pady=15)
            
            def delete_price(pid):
                if messagebox.askyesno("Confirm", "Delete price?"): self.database.delete_product_price(pid); refresh_prices()
            
            refresh_prices()
            
            # Add Section
            add_frame = ctk.CTkFrame(price_dialog, fg_color=COLORS["card_bg"], corner_radius=8)
            add_frame.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkLabel(add_frame, text="Add Price", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(8, 4), padx=10)
            
            fields_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            fields_frame.pack(fill="x", padx=10, pady=(0, 8))
            
            name_entry = ctk.CTkEntry(fields_frame, placeholder_text="Name (e.g. Senior)", height=28, font=ctk.CTkFont(size=11))
            name_entry.pack(side="left", fill="x", expand=True, padx=2)
            
            cost_entry = ctk.CTkEntry(fields_frame, placeholder_text="Cost", width=70, height=28, font=ctk.CTkFont(size=11))
            cost_entry.pack(side="left", padx=2)
            cost_entry.insert(0, f"{product[9]:.2f}" if len(product) > 9 else "0.00") # Default to product cost
            
            markup_entry = ctk.CTkEntry(fields_frame, placeholder_text="Markup%", width=60, height=28, font=ctk.CTkFont(size=11))
            markup_entry.pack(side="left", padx=2)
            
            price_entry = ctk.CTkEntry(fields_frame, placeholder_text="Price", width=70, height=28, font=ctk.CTkFont(size=11))
            price_entry.pack(side="left", padx=2)
            
            # Calculation logic
            calc_lock = [False]
            def calc_price(*args):
                if calc_lock[0]: return
                try:
                    c = float(cost_entry.get() or 0)
                    m = float(markup_entry.get() or 0)
                    if c > 0:
                        calc_lock[0] = True
                        price_entry.delete(0, "end"); price_entry.insert(0, f"{c * (1 + m/100):.2f}")
                        calc_lock[0] = False
                except: pass
            
            def calc_markup(*args):
                if calc_lock[0]: return
                try:
                    c = float(cost_entry.get() or 0)
                    p = float(price_entry.get() or 0)
                    if c > 0 and p >= 0:
                        calc_lock[0] = True
                        markup_entry.delete(0, "end"); markup_entry.insert(0, f"{((p-c)/c)*100:.1f}")
                        calc_lock[0] = False
                except: pass
            
            cost_entry.bind("<KeyRelease>", calc_price)
            markup_entry.bind("<KeyRelease>", calc_price)
            price_entry.bind("<KeyRelease>", calc_markup)
            
            def add_price():
                try:
                    self.database.add_product_price(
                        product[0], name_entry.get(),
                        float(cost_entry.get() or 0),
                        float(markup_entry.get() or 0),
                        float(price_entry.get() or 0)
                    )
                    name_entry.delete(0, "end")
                    markup_entry.delete(0, "end")
                    price_entry.delete(0, "end")
                    refresh_prices()
                except Exception as e: messagebox.showerror("Error", str(e))
                
            ctk.CTkButton(add_frame, text="Add", command=add_price, height=28, fg_color=COLORS["success"], font=ctk.CTkFont(size=11)).pack(fill="x", padx=10, pady=(0, 8))
            ctk.CTkButton(price_dialog, text="Done", command=price_dialog.destroy, height=32, fg_color=COLORS["primary"], font=ctk.CTkFont(size=11)).pack(fill="x", padx=15, pady=(0, 15))


        btn_style = {"height": 28, "corner_radius": 6, "font": ctk.CTkFont(size=11)}
        options_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(options_frame, text="🔗 Ingredients", command=lambda: show_ingredient_link_dialog(), fg_color=COLORS["info"], hover_color=COLORS["primary"], **btn_style).grid(row=0, column=0, sticky="ew", padx=2)
        ctk.CTkButton(options_frame, text="💲 Prices", command=manage_prices, fg_color=COLORS["warning"], hover_color=COLORS["primary"], **btn_style).grid(row=0, column=1, sticky="ew", padx=2)
        row += 1
        
        linked_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["dark"], corner_radius=8, height=50)
        linked_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        linked_frame.grid_propagate(False)
        row += 1
        
        def get_linked_data():
            # Fetch from DB: (id, ingredient_id, name, quantity, price, cost)
            raw = self.database.get_product_ingredients(product[0])
            return [{'link_id': r[0], 'id': r[1], 'name': r[2], 'quantity': r[3], 'cost': r[5]} for r in raw]

        def refresh_linked_display():
            for widget in linked_frame.winfo_children(): widget.destroy()
            ingredients = get_linked_data()
            
            if not ingredients:
                ctk.CTkLabel(linked_frame, text="No ingredients linked.", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"]).pack(pady=15)
            else:
                # Total Cost Display
                total_cost = self.database.get_product_overall_cost(product[0])
                info_frame = ctk.CTkFrame(linked_frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(info_frame, text=f"Total Cost: {CURRENCY_SYMBOL}{total_cost:.2f}", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["danger"]).pack(side="right")
                
                # Badges
                badge_container = ctk.CTkFrame(linked_frame, fg_color="transparent")
                badge_container.pack(fill="both", expand=True, padx=8, pady=(0, 5))
                
                # Show first few only to fit
                for ing in ingredients[:3]:
                    ctk.CTkLabel(badge_container, text=f"• {ing['name']} ({ing['quantity']})", font=ctk.CTkFont(size=10), text_color=COLORS["success"], fg_color=COLORS["card_bg"], corner_radius=4, padx=6, pady=2).pack(side="left", padx=2)
                if len(ingredients) > 3:
                     ctk.CTkLabel(badge_container, text=f"+{len(ingredients)-3} more", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"]).pack(side="left", padx=2)
        
        refresh_linked_display()
        
        def show_ingredient_link_dialog():
            ing_dialog = ctk.CTkToplevel(dialog)
            ing_dialog.title("Manage Ingredients")
            ing_dialog.geometry("600x650")
            ing_dialog.configure(fg_color=COLORS["dark"])
            ing_dialog.transient(dialog); ing_dialog.grab_set()
            
            # Center
            sw = ing_dialog.winfo_screenwidth()
            sh = ing_dialog.winfo_screenheight()
            ing_dialog.geometry(f"600x650+{(sw-600)//2}+{(sh-650)//2}")
            
            ctk.CTkLabel(ing_dialog, text=f"Ingredients for: {product[1]}", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(20, 10))
            
            # Cost Summary
            summary_lbl = ctk.CTkLabel(ing_dialog, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["danger"])
            summary_lbl.pack(pady=(0, 10))
            
            links_frame = ctk.CTkScrollableFrame(ing_dialog, fg_color=COLORS["card_bg"], corner_radius=10)
            links_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            
            def refresh_links_list():
                for widget in links_frame.winfo_children(): widget.destroy()
                ingredients = get_linked_data()
                total_cost = sum(i['cost'] for i in ingredients)
                summary_lbl.configure(text=f"Total Production Cost: {CURRENCY_SYMBOL}{total_cost:.2f}")
                
                if not ingredients:
                    ctk.CTkLabel(links_frame, text="No linked ingredients.", text_color=COLORS["text_secondary"]).pack(pady=20)
                else:
                    for ing in ingredients:
                        row = ctk.CTkFrame(links_frame, fg_color=COLORS["dark"])
                        row.pack(fill="x", pady=4, padx=5)
                        
                        info = ctk.CTkFrame(row, fg_color="transparent")
                        info.pack(side="left", fill="x", expand=True, padx=10, pady=8)
                        
                        ctk.CTkLabel(info, text=ing['name'], font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
                        cost_txt = f"{ing['quantity']} x Unit Price = {CURRENCY_SYMBOL}{ing['cost']:.2f}"
                        ctk.CTkLabel(info, text=cost_txt, font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(anchor="w")
                        
                        ctk.CTkButton(row, text="Remove", width=70, height=28, fg_color=COLORS["danger"], font=ctk.CTkFont(size=11), command=lambda lid=ing['link_id']: remove_link(lid)).pack(side="right", padx=10)
            
            def remove_link(link_id):
                self.database.remove_product_ingredient(link_id)
                refresh_links_list()
                refresh_linked_display()
            
            def add_link(ing_prod, qty):
                # ing_prod is (id, name, cat, price, stock, ...)
                # DB add expects: product_id, ingredient_id, quantity
                try:
                    self.database.add_product_ingredient(product[0], ing_prod[0], qty)
                    refresh_links_list()
                    refresh_linked_display()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            refresh_links_list()
            
            # Add Section
            add_frame = ctk.CTkFrame(ing_dialog, fg_color=COLORS["card_bg"], corner_radius=10)
            add_frame.pack(fill="x", padx=20, pady=(0, 20))
            ctk.CTkLabel(add_frame, text="Add Link", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
            
            search_var = ctk.StringVar()
            search_entry = ctk.CTkEntry(add_frame, placeholder_text="Search ingredient to link...", textvariable=search_var)
            search_entry.pack(fill="x", padx=15, pady=(0, 5))
            
            results_frame = ctk.CTkScrollableFrame(add_frame, height=150, fg_color=COLORS["dark"])
            results_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            def search_ingredients(*args):
                for w in results_frame.winfo_children(): w.destroy()
                query = search_var.get().lower()
                all_prods = self.database.get_all_products()
                # Exclude self
                results = [p for p in all_prods if query in p[1].lower() and p[0] != product[0]] 
                
                for res in results[:10]:
                    r_row = ctk.CTkFrame(results_frame, fg_color="transparent")
                    r_row.pack(fill="x", pady=2)
                    
                    price_txt = f"{CURRENCY_SYMBOL}{res[3]:.2f}/{res[8] if len(res)>8 else 'unit'}"
                    ctk.CTkLabel(r_row, text=f"{res[1]} ({price_txt})", width=180, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left")
                    
                    qty_entry = ctk.CTkEntry(r_row, width=60, placeholder_text="Qty", font=ctk.CTkFont(size=11))
                    qty_entry.pack(side="left", padx=5)
                    
                    ctk.CTkButton(r_row, text="Link", width=50, height=24, fg_color=COLORS["success"], font=ctk.CTkFont(size=11), command=lambda p=res, q=qty_entry: add_link(p, float(q.get() or 0))).pack(side="right")
                    
            search_var.trace_add("write", search_ingredients)
            search_ingredients()
            
            ctk.CTkButton(ing_dialog, text="Done", command=ing_dialog.destroy, height=40, fg_color=COLORS["primary"], font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=20, pady=(0, 20))


        
        # Buttons - Compact layout
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        def update_product():
            if not name_entry.get().strip(): messagebox.showerror("Error", "Name required"); return
            try:
                # Handle Supplier
                supp_name = supplier_combo.get().strip()
                supp_id = None
                if supp_name:
                    if supp_name in supplier_map:
                        supp_id = supplier_map[supp_name]
                    else:
                        supp_id = self.database.add_supplier(supp_name)
                        supplier_map[supp_name] = supp_id
                
                self.database.update_product(
                    product[0], name_entry.get().strip(), category_dropdown.get(),
                    float(price_entry.get() or 0), int(stock_entry.get() or 0),
                    barcode_entry.get().strip() or None, desc_entry.get().strip() or None,
                    unit_var.get(), float(cost_entry.get() or 0), float(markup_entry.get() or 0),
                    supplier_id=supp_id
                )
                messagebox.showinfo("Success", "Updated!"); dialog.destroy(); self.switch_page("products")
            except Exception as e: messagebox.showerror("Error", str(e))
            
        ctk.CTkButton(btn_frame, text="✕ Cancel", command=dialog.destroy, height=32, width=90, fg_color=COLORS["danger"], font=ctk.CTkFont(size=11)).pack(side="left")
        ctk.CTkButton(btn_frame, text="✓ Update Product", command=update_product, height=32, fg_color=COLORS["success"], font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", fill="x", expand=True, padx=(5, 0))

        if open_tab == "ingredients":
            dialog.after(200, show_ingredient_link_dialog)
    
    def delete_product(self, product):
        """Delete a product"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product[1]}'?"):
            try:
                self.database.delete_product(product[0])
                messagebox.showinfo("Success", "Product deleted successfully!")
                self.switch_page("products")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
