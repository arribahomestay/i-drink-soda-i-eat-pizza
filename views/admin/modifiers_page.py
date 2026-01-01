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
        
        # Name
        ctk.CTkLabel(row, text=mod[1], font=ctk.CTkFont(size=12)).pack(side="left", padx=15, expand=True, anchor="w")
        
        # Price
        ctk.CTkLabel(row, text=f"{CURRENCY_SYMBOL}{mod[2]:.2f}", width=80, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["success"]).pack(side="left", padx=10)
        
        # Linked Product (Simplified)
        linked_text = ""
        if mod[3]: # linked_product_id
            linked_name = mod[6] or "Unknown"
            deduct = mod[4]
            linked_text = f"📎 {linked_name} (x{deduct:g})"
            
        ctk.CTkLabel(row, text=linked_text, font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(side="left", padx=10, expand=True, anchor="w")
        
        # Actions (Minimalist)
        actions = ctk.CTkFrame(row, fg_color="transparent", width=80)
        actions.pack(side="right", padx=10)
        
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

