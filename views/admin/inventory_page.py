"""
Inventory management page for admin view
"""
import customtkinter as ctk
from tkinter import messagebox
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
        """Show inventory overview"""
        # Stats cards
        stats_frame = ctk.CTkFrame(self.inventory_content, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        # Get inventory data
        all_products = self.database.get_all_products()
        low_stock = self.database.get_low_stock_products(10)
        out_of_stock = self.database.get_out_of_stock_products()
        inventory_value = self.database.get_inventory_value()
        
        stats = [
            ("Total Products", len(all_products), COLORS["info"]),
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
        
        adjustments = self.database.get_stock_adjustments(limit=10)
        
        if adjustments:
            for adj in adjustments:
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
        """Show low stock products"""
        ctk.CTkLabel(
            self.inventory_content,
            text="⚠️ Low Stock Alert",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=20, padx=20, anchor="w")
        
        products_list = ctk.CTkScrollableFrame(
            self.inventory_content,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        products_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        low_stock = self.database.get_low_stock_products(10)
        
        if low_stock:
            for product in low_stock:
                card = ctk.CTkFrame(products_list, fg_color=COLORS["dark"], corner_radius=10)
                card.pack(fill="x", pady=5)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=12)
                
                left = ctk.CTkFrame(content, fg_color="transparent")
                left.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(
                    left,
                    text=product[1],
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    left,
                    text=f"Category: {product[2]} | Price: {CURRENCY_SYMBOL}{product[3]:.2f}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="w")
                
                stock_color = COLORS["danger"] if product[4] == 0 else COLORS["warning"]
                ctk.CTkLabel(
                    content,
                    text=f"Stock: {product[4]}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=stock_color
                ).pack(side="right")
        else:
            ctk.CTkLabel(
                products_list,
                text="✅ All products have sufficient stock!",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["success"]
            ).pack(pady=50)
    
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
        
        # Product search - compact
        ctk.CTkLabel(
            form_frame,
            text="Select Product",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 3), padx=15, anchor="w")
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="🔍 Search product...",
            textvariable=search_var,
            height=30,
            font=ctk.CTkFont(size=11)
        )
        search_entry.pack(fill="x", padx=15, pady=(0, 5))
        
        # Compact product list
        products_frame = ctk.CTkScrollableFrame(
            form_frame,
            fg_color=COLORS["card_bg"],
            corner_radius=5,
            height=120,
            scrollbar_button_color=COLORS["primary"]
        )
        products_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        selected_product = [None]
        
        def update_product_list(*args):
            for widget in products_frame.winfo_children():
                widget.destroy()
            
            search_term = search_var.get().lower()
            all_products = self.database.get_all_products()
            filtered = [p for p in all_products if search_term in p[1].lower() or (p[5] and search_term in p[5].lower())]
            
            if not filtered:
                ctk.CTkLabel(
                    products_frame,
                    text="No products found",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"]
                ).pack(pady=10)
                return
            
            for product in filtered[:8]:
                btn = ctk.CTkButton(
                    products_frame,
                    text=f"{product[1]} - Stock: {product[4]}",
                    command=lambda p=product: select_product(p),
                    height=28,
                    font=ctk.CTkFont(size=10),
                    fg_color="transparent",
                    hover_color=COLORS["primary"],
                    anchor="w"
                )
                btn.pack(fill="x", pady=1, padx=3)
        
        def select_product(product):
            selected_product[0] = product
            selected_label.configure(text=f"✓ {product[1]} (Stock: {product[4]})")
            quantity_entry.focus()
        
        search_var.trace("w", update_product_list)
        update_product_list()
        
        # Selected product - compact
        selected_label = ctk.CTkLabel(
            form_frame,
            text="No product selected",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["info"]
        )
        selected_label.pack(pady=(0, 8), padx=15, anchor="w")
        
        # Compact inputs in grid
        inputs_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=15, pady=(0, 8))
        inputs_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Quantity
        ctk.CTkLabel(
            inputs_frame,
            text="Quantity",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        quantity_entry = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="0",
            height=28,
            font=ctk.CTkFont(size=11)
        )
        quantity_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        # Reason
        ctk.CTkLabel(
            inputs_frame,
            text="Reason",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 2))
        
        reason_var = ctk.StringVar(value="Purchase")
        reason_dropdown = ctk.CTkComboBox(
            inputs_frame,
            values=["Purchase", "Return", "Adjustment", "Other"],
            variable=reason_var,
            height=28,
            font=ctk.CTkFont(size=10),
            dropdown_font=ctk.CTkFont(size=10)
        )
        reason_dropdown.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Notes - compact
        ctk.CTkLabel(
            form_frame,
            text="Notes (Optional)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(5, 2), padx=15, anchor="w")
        
        notes_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Additional notes...",
            height=28,
            font=ctk.CTkFont(size=10)
        )
        notes_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Compact submit button
        def submit_stock_in():
            if not selected_product[0]:
                messagebox.showerror("Error", "Please select a product")
                return
            
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity")
                return
            
            product = selected_product[0]
            self.database.update_product_stock(product[0], quantity)
            
            notes = notes_entry.get() or ""
            details = f"Stock In: {product[1]} +{quantity} ({reason_var.get()}) {notes}"
            self.database.log_activity(self.user_data['id'], self.user_data['username'], "Stock In", details)
            
            messagebox.showinfo("Success", f"Added {quantity} units to {product[1]}\nNew stock: {product[4] + quantity}")
            
            selected_product[0] = None
            selected_label.configure(text="No product selected")
            quantity_entry.delete(0, "end")
            notes_entry.delete(0, "end")
            search_var.set("")
            search_entry.focus()
        
        ctk.CTkButton(
            form_frame,
            text="✓ Add Stock",
            command=submit_stock_in,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60"
        ).pack(fill="x", padx=15, pady=(0, 15))
    
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
        
        # Product search - compact
        ctk.CTkLabel(
            form_frame,
            text="Select Product",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 3), padx=15, anchor="w")
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="🔍 Search product...",
            textvariable=search_var,
            height=30,
            font=ctk.CTkFont(size=11)
        )
        search_entry.pack(fill="x", padx=15, pady=(0, 5))
        
        # Compact product list
        products_frame = ctk.CTkScrollableFrame(
            form_frame,
            fg_color=COLORS["card_bg"],
            corner_radius=5,
            height=120,
            scrollbar_button_color=COLORS["primary"]
        )
        products_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        selected_product = [None]
        
        def update_product_list(*args):
            for widget in products_frame.winfo_children():
                widget.destroy()
            
            search_term = search_var.get().lower()
            all_products = self.database.get_all_products()
            filtered = [p for p in all_products if search_term in p[1].lower() or (p[5] and search_term in p[5].lower())]
            
            if not filtered:
                ctk.CTkLabel(
                    products_frame,
                    text="No products found",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"]
                ).pack(pady=10)
                return
            
            for product in filtered[:8]:
                stock_color = COLORS["danger"] if product[4] < 10 else COLORS["text_primary"]
                btn = ctk.CTkButton(
                    products_frame,
                    text=f"{product[1]} - Stock: {product[4]}",
                    command=lambda p=product: select_product(p),
                    height=28,
                    font=ctk.CTkFont(size=10),
                    fg_color="transparent",
                    text_color=stock_color,
                    hover_color=COLORS["primary"],
                    anchor="w"
                )
                btn.pack(fill="x", pady=1, padx=3)
        
        def select_product(product):
            selected_product[0] = product
            stock_warning = " ⚠️ Low!" if product[4] < 10 else ""
            selected_label.configure(text=f"✓ {product[1]} (Stock: {product[4]}){stock_warning}")
            quantity_entry.focus()
        
        search_var.trace("w", update_product_list)
        update_product_list()
        
        # Selected product - compact
        selected_label = ctk.CTkLabel(
            form_frame,
            text="No product selected",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["info"]
        )
        selected_label.pack(pady=(0, 8), padx=15, anchor="w")
        
        # Compact inputs in grid
        inputs_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=15, pady=(0, 8))
        inputs_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Quantity
        ctk.CTkLabel(
            inputs_frame,
            text="Quantity",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        quantity_entry = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="0",
            height=28,
            font=ctk.CTkFont(size=11)
        )
        quantity_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        # Reason
        ctk.CTkLabel(
            inputs_frame,
            text="Reason",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 2))
        
        reason_var = ctk.StringVar(value="Damage")
        reason_dropdown = ctk.CTkComboBox(
            inputs_frame,
            values=["Damage", "Expired", "Theft", "Return to Supplier", "Adjustment", "Other"],
            variable=reason_var,
            height=28,
            font=ctk.CTkFont(size=10),
            dropdown_font=ctk.CTkFont(size=10)
        )
        reason_dropdown.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Notes - compact
        ctk.CTkLabel(
            form_frame,
            text="Notes (Optional)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(5, 2), padx=15, anchor="w")
        
        notes_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Additional notes...",
            height=28,
            font=ctk.CTkFont(size=10)
        )
        notes_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Compact submit button
        def submit_stock_out():
            if not selected_product[0]:
                messagebox.showerror("Error", "Please select a product")
                return
            
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity")
                return
            
            product = selected_product[0]
            if quantity > product[4]:
                messagebox.showerror("Error", f"Insufficient stock!\nAvailable: {product[4]}, Requested: {quantity}")
                return
            
            self.database.update_product_stock(product[0], -quantity)
            
            notes = notes_entry.get() or ""
            details = f"Stock Out: {product[1]} -{quantity} ({reason_var.get()}) {notes}"
            self.database.log_activity(self.user_data['id'], self.user_data['username'], "Stock Out", details)
            
            new_stock = product[4] - quantity
            warning = "\n⚠️ Warning: Stock is now low!" if new_stock < 10 else ""
            messagebox.showinfo("Success", f"Removed {quantity} units from {product[1]}\nNew stock: {new_stock}{warning}")
            
            selected_product[0] = None
            selected_label.configure(text="No product selected")
            quantity_entry.delete(0, "end")
            notes_entry.delete(0, "end")
            search_var.set("")
            search_entry.focus()
        
        ctk.CTkButton(
            form_frame,
            text="✓ Remove Stock",
            command=submit_stock_out,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b"
        ).pack(fill="x", padx=15, pady=(0, 15))
    
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
