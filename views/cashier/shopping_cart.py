"""
Shopping cart component for cashier view
Handles cart display and management
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS, CURRENCY_SYMBOL, TAX_RATE


class ShoppingCart:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
        self.cart_items = []
        self.cart_frame = None
        self.subtotal_label = None
        self.tax_label = None
        self.total_label = None
    
    def create(self, checkout_callback, clear_callback, edit_callback=None):
        """Create the shopping cart UI"""
        self.edit_callback = edit_callback
        # Right side - Cart
        right_panel = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15, width=450)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Cart header
        cart_header = ctk.CTkLabel(
            right_panel,
            text="🛍️ Current Sale",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        cart_header.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Order Type Selection
        order_type_frame = ctk.CTkFrame(right_panel, fg_color=COLORS["dark"], corner_radius=10)
        order_type_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Order type state
        self.order_type = "Normal"  # Default: Normal, Dine In, Take Out
        
        # Order type label
        ctk.CTkLabel(
            order_type_frame,
            text="Order Type:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(15, 10), pady=10)
        
        # Order type buttons
        btn_container = ctk.CTkFrame(order_type_frame, fg_color="transparent")
        btn_container.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=8)
        
        self.normal_btn = ctk.CTkButton(
            btn_container,
            text="Normal",
            command=lambda: self.set_order_type("Normal"),
            height=30,
            width=90,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            corner_radius=6
        )
        self.normal_btn.pack(side="left", padx=2)
        
        self.dinein_btn = ctk.CTkButton(
            btn_container,
            text="Dine In",
            command=lambda: self.set_order_type("Dine In"),
            height=30,
            width=90,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["card_bg"],
            hover_color=COLORS["secondary"],
            corner_radius=6
        )
        self.dinein_btn.pack(side="left", padx=2)
        
        self.takeout_btn = ctk.CTkButton(
            btn_container,
            text="Take Out",
            command=lambda: self.set_order_type("Take Out"),
            height=30,
            width=90,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["card_bg"],
            hover_color=COLORS["secondary"],
            corner_radius=6
        )
        self.takeout_btn.pack(side="left", padx=2)
        
        # Cart items
        self.cart_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color=COLORS["dark"],
            corner_radius=10,
            scrollbar_button_color=COLORS["primary"]
        )
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Summary section
        summary_frame = ctk.CTkFrame(right_panel, fg_color=COLORS["dark"], corner_radius=10)
        summary_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Subtotal
        subtotal_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
        subtotal_row.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            subtotal_row,
            text="Subtotal:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        self.subtotal_label = ctk.CTkLabel(
            subtotal_row,
            text=f"{CURRENCY_SYMBOL}0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.subtotal_label.pack(side="right")
        
        # Tax row removed
        self.tax_label = ctk.CTkLabel(self.parent, text="")  # Dummy label
        
        # Total
        total_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
        total_row.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(
            total_row,
            text="TOTAL:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        self.total_label = ctk.CTkLabel(
            total_row,
            text=f"{CURRENCY_SYMBOL}0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["success"]
        )
        self.total_label.pack(side="right")
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear Cart",
            command=clear_callback,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=10
        )
        clear_btn.pack(fill="x", pady=(0, 10))
        
        checkout_btn = ctk.CTkButton(
            buttons_frame,
            text="Checkout",
            command=checkout_callback,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=10
        )
        checkout_btn.pack(fill="x")
        
        # Initial display
        self.update_cart_display()
        
        return right_panel
    
    def add_item(self, item):
        """Add item to cart"""
        self.cart_items.append(item)
        self.update_cart_display()
    
    def remove_item(self, item):
        """Remove item from cart"""
        self.cart_items.remove(item)
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items"""
        self.cart_items = []
        self.update_cart_display()
    
    def get_items(self):
        """Get all cart items"""
        return self.cart_items
    
    def update_cart_display(self):
        """Update cart display"""
        # Clear cart frame
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
        
        if not self.cart_items:
            empty_label = ctk.CTkLabel(
                self.cart_frame,
                text="Cart is empty\nAdd products to get started",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(pady=50)
        else:
            for item in self.cart_items:
                self.create_cart_item(item)
        
        # Update summary
        self.update_summary()
    
    def create_cart_item(self, item):
        """Create compact cart item widget"""
        item_frame = ctk.CTkFrame(self.cart_frame, fg_color=COLORS["card_bg"], corner_radius=6)
        item_frame.pack(fill="x", padx=5, pady=3)
        
        # Layout: Horizontal Container
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=8, pady=8)
        
        # LEFT: Info
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)

        name_label = ctk.CTkLabel(
            left_col,
            text=item['name'],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
            justify="left"
        )
        name_label.pack(anchor="w")
        
        price_txt = f"{item['quantity']} x {CURRENCY_SYMBOL}{item['price']:.2f}"
        price_label = ctk.CTkLabel(
            left_col,
            text=price_txt,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        price_label.pack(anchor="w")
        
        # RIGHT: Totals & Actions
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.pack(side="right", anchor="ne")
        
        subtotal_label = ctk.CTkLabel(
            right_col,
            text=f"{CURRENCY_SYMBOL}{item['subtotal']:.2f}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["success"],
            anchor="e"
        )
        subtotal_label.pack(anchor="e", pady=(0, 2))
        
        # Action Buttons (Compact Row)
        btns_row = ctk.CTkFrame(right_col, fg_color="transparent")
        btns_row.pack(anchor="e")
        
        if self.edit_callback:
            ctk.CTkButton(
                btns_row, text="✎", width=24, height=24,
                font=ctk.CTkFont(size=14), fg_color=COLORS["warning"], hover_color="#f39c12",
                command=lambda i=item: self.edit_callback(i)
            ).pack(side="left", padx=2)
            
        ctk.CTkButton(
            btns_row, text="×", width=24, height=24,
            font=ctk.CTkFont(size=16, weight="bold"), fg_color=COLORS["danger"], hover_color="#c0392b",
            command=lambda i=item: self.remove_item(i)
        ).pack(side="left", padx=0)
        

    
    def increase_quantity(self, item):
        """Increase item quantity"""
        product = self.database.get_product_by_id(item['product_id'])
        if item['quantity'] < product[4]:
            item['quantity'] += 1
            item['subtotal'] = item['quantity'] * item['price']
            self.update_cart_display()
        else:
            messagebox.showwarning("Stock Limit", "Not enough stock available")
    
    def decrease_quantity(self, item):
        """Decrease item quantity"""
        if item['quantity'] > 1:
            item['quantity'] -= 1
            item['subtotal'] = item['quantity'] * item['price']
            self.update_cart_display()
    
    def replace_item(self, old_item, new_item):
        """Replace an existing item with a modified one"""
        if old_item in self.cart_items:
            idx = self.cart_items.index(old_item)
            self.cart_items[idx] = new_item
            self.update_cart_display()

    def update_summary(self):
        """Update price summary"""
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        tax = 0
        total = subtotal
        
        self.subtotal_label.configure(text=f"{CURRENCY_SYMBOL}{subtotal:.2f}")
        self.total_label.configure(text=f"{CURRENCY_SYMBOL}{total:.2f}")
    
    def get_total(self):
        """Get cart total"""
        return sum(item['subtotal'] for item in self.cart_items)
    
    def set_order_type(self, order_type):
        """Set the order type and update button states"""
        self.order_type = order_type
        
        # Update button colors to show selection
        if order_type == "Normal":
            self.normal_btn.configure(fg_color=COLORS["primary"])
            self.dinein_btn.configure(fg_color=COLORS["card_bg"])
            self.takeout_btn.configure(fg_color=COLORS["card_bg"])
        elif order_type == "Dine In":
            self.normal_btn.configure(fg_color=COLORS["card_bg"])
            self.dinein_btn.configure(fg_color=COLORS["info"])
            self.takeout_btn.configure(fg_color=COLORS["card_bg"])
        elif order_type == "Take Out":
            self.normal_btn.configure(fg_color=COLORS["card_bg"])
            self.dinein_btn.configure(fg_color=COLORS["card_bg"])
            self.takeout_btn.configure(fg_color=COLORS["warning"])
    
    def get_order_type(self):
        """Get the current order type"""
        return self.order_type

