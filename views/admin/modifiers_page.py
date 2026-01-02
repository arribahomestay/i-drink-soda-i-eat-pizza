"""
Modifiers management page for admin view
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS, CURRENCY_SYMBOL

class ModifiersPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
    
    def show(self):
        """Show modifiers management page"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="➕ Global Modifiers",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Add Button
        add_btn = ctk.CTkButton(
            header,
            text="+ Add Modifier",
            command=self.add_modifier_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=10
        )
        add_btn.pack(side="right")
        
        # Search/Filter (Optional, but good practice)
        # For now just list header
        
        # Content Container (Table)
        self.content_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=COLORS["card_bg"],
            corner_radius=15
        )
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.load_modifiers()

    def load_modifiers(self):
        """Load and display all global modifiers"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        modifiers = self.database.get_all_global_modifiers()
        
        if not modifiers:
            ctk.CTkLabel(
                self.content_frame,
                text="No global modifiers found.\nClick '+ Add Modifier' to create one.",
                font=ctk.CTkFont(size=16),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return
            
        # Table Header
        h_row = ctk.CTkFrame(self.content_frame, fg_color=COLORS["dark"], height=40)
        h_row.pack(fill="x", pady=(0, 10))
        h_row.pack_propagate(False)
        
        # Header Layout
        ctk.CTkLabel(h_row, text="Name", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20, expand=True, anchor="w")
        ctk.CTkLabel(h_row, text="Price", font=ctk.CTkFont(weight="bold"), width=80).pack(side="left", padx=20)
        ctk.CTkLabel(h_row, text="Linked Product", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20, expand=True, anchor="w")
        ctk.CTkLabel(h_row, text="Actions", font=ctk.CTkFont(weight="bold"), width=100).pack(side="right", padx=20)
        
        # Rows
        for mod in modifiers:
            # mod: [id, name, price, linked_prod_id, deduct_qty, created_at, linked_name, linked_stock]
            self.create_modifier_row(mod)
            
    def create_modifier_row(self, mod):
        import tkinter as tk
        
        # Row container with outline
        row = ctk.CTkFrame(
            self.content_frame, 
            fg_color="transparent",
            border_width=1,
            border_color="#2c3e50", # Subtle outline color
            corner_radius=4,
            height=38
        )
        row.pack(fill="x", pady=2)
        row.pack_propagate(False) # Fixed height
        
        # Add right-click context menu
        def show_modifier_menu(event):
            menu = tk.Menu(row, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text_primary"],
                          activebackground=COLORS["primary"], activeforeground="white",
                          font=("Segoe UI", 10))
            menu.add_command(label="👁️  View", command=lambda: self.view_modifier_dialog(mod))
            menu.add_command(label="✏️  Edit", command=lambda: self.add_modifier_dialog(mod))
            menu.add_command(label="📝 Rename", command=lambda: self.rename_modifier_dialog(mod))
            menu.add_separator()
            menu.add_command(label="🗑️  Delete", command=lambda: self.delete_modifier(mod[0]))
            menu.post(event.x_root, event.y_root)
        
        row.bind("<Button-3>", show_modifier_menu)
        
        # Name
        name_label = ctk.CTkLabel(row, text=mod[1], font=ctk.CTkFont(size=12))
        name_label.pack(side="left", padx=15, expand=True, anchor="w")
        name_label.bind("<Button-3>", show_modifier_menu)
        
        # Price
        price_label = ctk.CTkLabel(row, text=f"{CURRENCY_SYMBOL}{mod[2]:.2f}", width=80, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["success"])
        price_label.pack(side="left", padx=10)
        price_label.bind("<Button-3>", show_modifier_menu)
        
        # Linked Product (Simplified)
        linked_text = ""
        if mod[3]: # linked_product_id
            linked_name = mod[6] or "Unknown"
            deduct = mod[4]
            linked_text = f"📎 {linked_name} (x{deduct:g})"
        
        linked_label = ctk.CTkLabel(row, text=linked_text, font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"])
        linked_label.pack(side="left", padx=10, expand=True, anchor="w")
        linked_label.bind("<Button-3>", show_modifier_menu)
        
        # Actions (Minimalist)
        actions = ctk.CTkFrame(row, fg_color="transparent", width=80)
        actions.pack(side="right", padx=10)
        actions.bind("<Button-3>", show_modifier_menu)
        
        # Edit
        ctk.CTkButton(
            actions, text="✎", width=24, height=24,
            command=lambda: self.add_modifier_dialog(mod),
            fg_color="transparent", 
            hover_color=COLORS["dark"],
            text_color=COLORS["primary"],
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=1)
        
        # Delete
        ctk.CTkButton(
            actions, text="✖", width=24, height=24,
            command=lambda: self.delete_modifier(mod[0]),
            fg_color="transparent",
            hover_color=COLORS["dark"],
            text_color=COLORS["danger"],
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=1)

    def delete_modifier(self, mod_id):
        if messagebox.askyesno("Confirm", "Delete this modifier?"):
            self.database.delete_global_modifier(mod_id)
            self.load_modifiers()

    def add_modifier_dialog(self, mod_data=None):
        """Show add/edit modifier dialog - Enforced Product Linking"""
        is_edit = mod_data is not None
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Modifier" if is_edit else "Add Inventory Modifier")
        dialog.geometry("500x550")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        sw = dialog.winfo_screenwidth()
        sh = dialog.winfo_screenheight()
        dialog.geometry(f"500x550+{(sw-500)//2}+{(sh-550)//2}")
        
        form_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 1. Select Product (Required) - Moved to TOP
        ctk.CTkLabel(form_frame, text="Select Inventory Product (Required)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        
        all_products = self.database.get_all_products()
        
        # Filter: Only stock-tracked products can be ingredients
        # Indices: use_stock_tracking=12
        stock_tracked = [p for p in all_products if (len(p) > 12 and p[12] == 1)]
        
        # Map Display -> ID
        prod_map = {f"{p[1]} (Stock: {p[4]})": p[0] for p in stock_tracked}
        prod_options = ["Select a product..."] + sorted(list(prod_map.keys()))
        
        prod_var = ctk.StringVar(value="Select a product...")
        
        # If editing, try to find the linked product
        if is_edit and mod_data[3]:
            current_id = mod_data[3]
            found = False
            for name, pid in prod_map.items():
                if pid == current_id:
                    prod_var.set(name)
                    found = True
                    break
            if not found: prod_var.set("Linked Product Not Found") # Should handle gracefully
        elif is_edit:
             prod_var.set("Legacy Custom Modifier") # If editing a legacy item with no link

        prod_dropdown = ctk.CTkComboBox(form_frame, values=prod_options, variable=prod_var, height=32, width=300)
        prod_dropdown.pack(fill="x", padx=20)
        
        # 2. Name & Price (Auto-filled)
        ctk.CTkLabel(form_frame, text="Modifier Name", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        name_entry = ctk.CTkEntry(form_frame, height=32)
        name_entry.pack(fill="x", padx=20)
        if is_edit: name_entry.insert(0, mod_data[1])
        
        ctk.CTkLabel(form_frame, text="Price (Extra Cost)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        price_entry = ctk.CTkEntry(form_frame, height=32)
        price_entry.pack(fill="x", padx=20)
        if is_edit: price_entry.insert(0, str(mod_data[2]))
        
        # 3. Auto-fill Logic
        def on_prod_change(choice):
            if choice == "Select a product..." or choice == "Legacy Custom Modifier": return
            
            pid = prod_map.get(choice)
            if pid:
                p = next((p for p in all_products if p[0] == pid), None)
                if p:
                    # Auto-fill name and price
                    current_name = name_entry.get().strip()
                    # Always overwrite name if it's empty or matches previous selection? 
                    # For simplicity, let's just update it.
                    name_entry.delete(0, "end")
                    name_entry.insert(0, p[1])
                    
                    # Update price (default to product price, user can edit)
                    price_entry.delete(0, "end")
                    price_entry.insert(0, f"{p[3]:.2f}")
        
        prod_dropdown.configure(command=on_prod_change)
        
        # 4. Deduct Qty
        ctk.CTkLabel(form_frame, text="Deduct Quantity from Inventory", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        deduct_entry = ctk.CTkEntry(form_frame, height=32)
        deduct_entry.pack(fill="x", padx=20)
        deduct_entry.insert(0, str(mod_data[4]) if is_edit else "1")
        
        # Save Handler
        def save():
            selected_choice = prod_var.get()
            
            # Validation: Must have link (unless editing legacy, but user asked for "no custom modifier")
            # If editing legacy, we might force them to link?
            # Let's enforce linking for NEW and force linking if they change it.
            
            link_id = None
            if selected_choice in prod_map:
                link_id = prod_map.get(selected_choice)
            
            if not link_id and not (is_edit and selected_choice == "Legacy Custom Modifier"):
                messagebox.showerror("Error", "You must select an Inventory Product to link.")
                return

            name = name_entry.get().strip()
            if not name: messagebox.showerror("Error", "Name required"); return
            
            try:
                price = float(price_entry.get() or 0)
                deduct = float(deduct_entry.get() or 1)
                
                if is_edit:
                    self.database.update_global_modifier(mod_data[0], name, price, link_id, deduct)
                else:
                    self.database.add_global_modifier(name, price, link_id, deduct)
                
                dialog.destroy()
                self.load_modifiers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(form_frame, text="Save Modifier", command=save, fg_color=COLORS["success"], height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=20, pady=30)

    def view_modifier_dialog(self, mod):
        """Show compact modifier details view modal"""
        import tkinter as tk
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Modifier Details")
        dialog.geometry("500x650")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 650) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=mod[1],  # Modifier name
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Content
        content = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Modifier details
        details = [
            ("Name", mod[1]),
            ("Price", f"{CURRENCY_SYMBOL}{mod[2]:.2f}"),
            ("Linked Product", mod[6] if mod[6] else "None"),
            ("Deduct Quantity", f"{mod[4]:g}" if mod[4] else "1"),
            ("Linked Stock", f"{mod[7]}" if len(mod) > 7 and mod[7] is not None else "N/A"),
        ]
        
        for label, value in details:
            row = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=8)
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"]
            ).pack(side="left", padx=15, pady=10)
            
            ctk.CTkLabel(
                row,
                text=str(value),
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_primary"]
            ).pack(side="right", padx=15, pady=10)
        
        # Show products that use this ingredient (if linked)
        if mod[3]:  # If there's a linked_product_id
            ingredient_id = mod[3]
            
            # Query database for products that use this ingredient
            self.database.cursor.execute("""
                SELECT p.id, p.name, pi.quantity
                FROM product_ingredients pi
                JOIN products p ON pi.product_id = p.id
                WHERE pi.ingredient_id = ?
                ORDER BY p.name
            """, (ingredient_id,))
            
            products_using = self.database.cursor.fetchall()
            
            if products_using:
                # Section header
                ctk.CTkLabel(
                    content,
                    text=f"🔗 Used In Products ({len(products_using)})",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["info"]
                ).pack(anchor="w", pady=(15, 10))
                
                # List of products
                products_frame = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=8)
                products_frame.pack(fill="x", pady=5)
                
                for prod in products_using:
                    prod_id, prod_name, qty_used = prod
                    
                    prod_row = ctk.CTkFrame(products_frame, fg_color=COLORS["dark"], corner_radius=5)
                    prod_row.pack(fill="x", padx=10, pady=5)
                    
                    # Product name
                    ctk.CTkLabel(
                        prod_row,
                        text=f"• {prod_name}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS["text_primary"]
                    ).pack(side="left", padx=10, pady=8)
                    
                    # Quantity used
                    ctk.CTkLabel(
                        prod_row,
                        text=f"Uses {qty_used:g}x",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_secondary"]
                    ).pack(side="right", padx=10, pady=8)
            else:
                # No products use this ingredient
                ctk.CTkLabel(
                    content,
                    text="ℹ️ Not used in any products yet",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="w", pady=(15, 5))
        
        # Close button
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=150,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=15)
    
    def rename_modifier_dialog(self, mod):
        """Show dialog to rename modifier"""
        import tkinter as tk
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Rename Modifier")
        dialog.geometry("400x200")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 200) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        ctk.CTkLabel(
            dialog,
            text=f"Rename Modifier",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(20, 10))
        
        # Current name
        ctk.CTkLabel(
            dialog,
            text=f"Current: {mod[1]}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 10))
        
        # Entry
        entry_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        entry_frame.pack(fill="x", padx=30, pady=10)
        
        name_entry = ctk.CTkEntry(
            entry_frame,
            height=35,
            font=ctk.CTkFont(size=13),
            placeholder_text="New modifier name"
        )
        name_entry.pack(fill="x")
        name_entry.insert(0, mod[1])
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)
        
        def save():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Modifier name cannot be empty")
                return
            
            if new_name == mod[1]:
                dialog.destroy()
                return
            
            try:
                # Update modifier with new name, keeping other values
                self.database.update_global_modifier(
                    mod[0],  # id
                    new_name,  # new name
                    mod[2],  # price
                    mod[3],  # linked_product_id
                    mod[4]   # deduct_quantity
                )
                messagebox.showinfo("Success", f"Modifier renamed to '{new_name}'")
                dialog.destroy()
                self.load_modifiers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            height=35,
            width=120,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Rename",
            command=save,
            height=35,
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        name_entry.bind("<Return>", lambda e: save())

