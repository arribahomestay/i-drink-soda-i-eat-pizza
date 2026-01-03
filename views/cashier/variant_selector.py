"""
Variant and modifier selector dialog for cashier view
Handles product customization
"""
import customtkinter as ctk
from config import COLORS, CURRENCY_SYMBOL

class VariantSelector:
    def __init__(self, parent, product, variants, modifiers, add_callback, prices=None, initial_state=None):
        self.parent = parent
        self.product = product
        self.variants = variants
        self.modifiers = modifiers
        self.add_callback = add_callback
        self.prices = prices or []
        self.initial_state = initial_state
        
        # State
        self.selected_price_idx = None
        self.modifiers_visible = None
        self.mod_vars = {} 
        self.qty_var = None
        self.total_var = None
        
        # UI
        self.dialog = None
        self.left_frame = None
        self.right_frame = None

    def show(self):
        """Show variant selector dialog - Horizontal Layout"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Add to Cart")
        self.dialog.configure(fg_color=COLORS["dark"])
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Initialize Variables
        self.selected_price_idx = ctk.IntVar(value=-1)
        self.modifiers_visible = ctk.IntVar(value=0)
        self.qty_var = ctk.StringVar(value="1")
        self.total_var = ctk.DoubleVar(value=self.product[3])
        
        # --- HEADER ---
        header = ctk.CTkFrame(self.dialog, fg_color=COLORS["card_bg"], corner_radius=0, height=50)
        header.pack(fill="x", side="top")
        
        ctk.CTkLabel(
            header,
            text=self.product[1],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=20, pady=10)
        
        # Check stock/availability
        # Indices: use_stock_tracking=12, is_available=13
        use_stock = self.product[12] if len(self.product) > 12 and self.product[12] is not None else 1
        is_avail = self.product[13] if len(self.product) > 13 and self.product[13] is not None else 1
        
        if use_stock == 0:
            # Availability mode
            if is_avail:
                status_text = "✓ Available"
                status_color = COLORS["success"]
            else:
                status_text = "✗ Not Available"
                status_color = COLORS["danger"]
        else:
            # Stock tracking mode
            stock_val = self.product[4]
            if stock_val <= 0:
                status_text = "Out of Stock"
                status_color = COLORS["danger"]
            else:
                status_text = f"Stock: {stock_val}"
                status_color = COLORS["success"] if stock_val > 5 else "#ff9800"
        
        ctk.CTkLabel(
            header,
            text=status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color
        ).pack(side="right", padx=20)

        # --- BODY (Horizontal Container) ---
        body = ctk.CTkFrame(self.dialog, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=15)
        
        # LEFT COLUMN (Core Info)
        self.left_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        # 1. Price Type
        if self.prices:
            price_map = {} 
            std_name = "Standard"
            price_map[std_name] = -1
            values = [std_name]
            for idx, p in enumerate(self.prices):
                name = p[2]
                if name in price_map: name = f"{name} {idx}"
                price_map[name] = idx
                values.append(name)
            
            def on_price_change(value):
                self.selected_price_idx.set(price_map[value])
                self.update_total()

            ctk.CTkLabel(self.left_frame, text="Price Type", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 5))
            seg_btn = ctk.CTkSegmentedButton(
                self.left_frame, values=values, command=on_price_change,
                selected_color=COLORS["primary"], font=ctk.CTkFont(size=12)
            )
            seg_btn.pack(fill="x", pady=(0, 15))
            seg_btn.set(std_name)
            self.seg_btn = seg_btn
            self.price_values = values

        # 2. Quantity
        ctk.CTkLabel(self.left_frame, text="Quantity", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 5))
        qty_frame = ctk.CTkFrame(self.left_frame, fg_color=COLORS["card_bg"], corner_radius=8)
        qty_frame.pack(fill="x", pady=(0, 15))
        
        def change_qty(v):
            try: curr = int(self.qty_var.get())
            except: curr = 1
            new_val = max(1, curr + v)
            self.qty_var.set(str(new_val))
            self.update_total()

        ctk.CTkButton(qty_frame, text="-", width=40, height=35, fg_color="transparent", text_color=COLORS["text_primary"], font=ctk.CTkFont(size=18), hover_color=COLORS["dark"], command=lambda: change_qty(-1)).pack(side="left")
        
        qty_entry = ctk.CTkEntry(qty_frame, textvariable=self.qty_var, width=60, height=35, font=ctk.CTkFont(size=16, weight="bold"), justify="center", border_width=0, fg_color="transparent")
        qty_entry.pack(side="left", expand=True)
        
        ctk.CTkButton(qty_frame, text="+", width=40, height=35, fg_color="transparent", text_color=COLORS["text_primary"], font=ctk.CTkFont(size=18), hover_color=COLORS["dark"], command=lambda: change_qty(1)).pack(side="right")

        # 3. Note
        ctk.CTkLabel(self.left_frame, text="Note", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 5))
        self.note_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Special instructions...", height=35)
        self.note_entry.pack(fill="x")
        
        # 4. Add-on Toggle (If modifiers exist)
        if self.modifiers:
            switch_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
            switch_frame.pack(fill="x", pady=(20, 0))
            
            ctk.CTkLabel(switch_frame, text="Extras / Add-ons", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_secondary"]).pack(side="left")
            ctk.CTkSwitch(switch_frame, text="", variable=self.modifiers_visible, command=self.toggle_layout, width=40, height=20, switch_width=36, onvalue=1, offvalue=0).pack(side="right")

        # RIGHT COLUMN (Add-ons List) - Initially Hidden
        self.right_frame = ctk.CTkFrame(body, fg_color=COLORS["card_bg"], corner_radius=10)
        # We don't pack it initially. toggle_layout will pack it side="left".
        
        # Populate Right Frame Content
        if self.modifiers:
            ctk.CTkLabel(self.right_frame, text="Select Add-ons", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10,padx=10, anchor="w")
            
            mod_scroll = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
            mod_scroll.pack(fill="both", expand=True, padx=5, pady=5)
            
            for m in self.modifiers:
                res_id, name, price = m[0], m[1], m[2]
                
                row = ctk.CTkFrame(mod_scroll, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                check_var = ctk.BooleanVar(value=False)
                qty_var = ctk.IntVar(value=1)
                self.mod_vars[res_id] = {'checked': check_var, 'qty': qty_var, 'data': m}
                
                # Checkbox (Name + Price + Link Status)
                linked_status = "🔗" if len(m) > 3 and m[3] else ""
                display_text = f"{name} {linked_status}"
                
                ctk.CTkCheckBox(row, text=display_text, variable=check_var, command=self.update_total, font=ctk.CTkFont(size=12), width=20, height=20, checkbox_width=18, checkbox_height=18).pack(side="left")
                price_lbl = ctk.CTkLabel(row, text=f"+{CURRENCY_SYMBOL}{price:.0f}", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"])
                price_lbl.pack(side="left", padx=5)
                self.mod_vars[res_id]['label'] = price_lbl
                
                # Tiny Qty Controls
                q_frame = ctk.CTkFrame(row, fg_color="transparent")
                q_frame.pack(side="right")
                
                def mq(v, qv=qty_var, cv=check_var):
                    qv.set(max(1, qv.get() + v))
                    self.update_total()
                    
                ctk.CTkButton(q_frame, text="-", width=20, height=20, fg_color=COLORS["dark"], command=lambda qv=qty_var, cv=check_var: mq(-1,qv,cv)).pack(side="left", padx=1)
                ctk.CTkLabel(q_frame, textvariable=qty_var, width=15).pack(side="left")
                ctk.CTkButton(q_frame, text="+", width=20, height=20, fg_color=COLORS["dark"], command=lambda qv=qty_var, cv=check_var: mq(1,qv,cv)).pack(side="left", padx=1)


        # --- FOOTER ---
        footer = ctk.CTkFrame(self.dialog, fg_color=COLORS["card_bg"], corner_radius=0, height=60)
        footer.pack(fill="x", side="bottom")
        
        self.total_lbl = ctk.CTkLabel(
            footer,
            text=f"{CURRENCY_SYMBOL}{self.product[3]:.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["success"]
        )
        self.total_lbl.pack(side="left", padx=30)
        
        ctk.CTkButton(
            footer, text="ADD TO CART", command=self.confirm_add,
            height=36, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"], width=150, corner_radius=18
        ).pack(side="right", padx=30, pady=12)

        # Initial Updates
        qty_entry.bind("<KeyRelease>", lambda e: self.update_total())
        self.dialog.bind('<Return>', self.confirm_add)
        
        # Auto-select text when focused
        def select_all_qty(event):
            try:
                qty_entry.select_range(0, 'end')
                qty_entry.icursor('end')
            except:
                pass
            return 'break'
        
        qty_entry.bind("<FocusIn>", select_all_qty)
        
        # Focus and select the quantity field
        def focus_qty():
            try:
                if qty_entry.winfo_exists():
                    qty_entry.focus()
                    qty_entry.select_range(0, 'end')
            except:
                pass
        
        self.dialog.after(100, focus_qty)
        
        # Apply Initial State (Editing Mode)
        if self.initial_state:
            # Qty
            self.qty_var.set(str(self.initial_state.get('quantity', 1)))
            # Note
            self.note_entry.delete(0, 'end')
            self.note_entry.insert(0, self.initial_state.get('note', ''))
            
            # Price Variant
            saved_base = self.initial_state.get('base_price', self.product[3])
            matched_idx = -1
            if abs(saved_base - self.product[3]) > 0.01 and self.prices:
                for idx, p in enumerate(self.prices):
                    # p[5] is price
                    if abs(p[5] - saved_base) < 0.01:
                        matched_idx = idx
                        break
            
            if matched_idx != -1 and hasattr(self, 'seg_btn') and hasattr(self, 'price_values'):
                 try:
                     val_str = self.price_values[matched_idx + 1]
                     self.seg_btn.set(val_str)
                     self.selected_price_idx.set(matched_idx)
                 except: pass

            # Modifiers
            saved_mods = self.initial_state.get('selected_modifiers', [])
            if saved_mods:
                self.modifiers_visible.set(1)
                for sm in saved_mods:
                     mid = sm['id']
                     if mid in self.mod_vars:
                         self.mod_vars[mid]['checked'].set(True)
                         self.mod_vars[mid]['qty'].set(sm.get('quantity', 1))

        self.update_total()
        self.toggle_layout() # Apply initial state

    def toggle_layout(self):
        """Switches between Compact (Left only) and Expanded (Split) layout"""
        if self.modifiers_visible.get():
            # Show Right Panel
            self.right_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))
            w = 750
        else:
            # Hide Right Panel
            self.right_frame.pack_forget()
            w = 380
            
        # Animate/Resize
        h = 420
        self.center_window(w, h)
        self.update_total()

    def center_window(self, width, height):
        self.dialog.minsize(width, height) # Prevent resizing too small
        # Center Logic
        try:
            sw = self.dialog.winfo_screenwidth()
            sh = self.dialog.winfo_screenheight()
        except: sw,sh = 1920,1080
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def update_total(self, *args):
        if not self.dialog or not self.dialog.winfo_exists(): return
        
        idx = self.selected_price_idx.get()
        base_price = self.product[3] if idx == -1 else self.prices[idx][5]
        
        added_cost = 0
        if self.modifiers and self.modifiers_visible.get():
            for mid, data in self.mod_vars.items():
                qty = data['qty'].get()
                price = data['data'][2]
                
                # Update label to show total line cost
                if 'label' in data:
                    total_line_cost = price * qty
                    data['label'].configure(text=f"+{CURRENCY_SYMBOL}{total_line_cost:.0f}")

                if data['checked'].get():
                    added_cost += (price * qty)
        
        try: qty = int(self.qty_var.get())
        except: qty = 1
        
        # CHANGED: Modifiers are now treated as "Global/Per Line" (added once) 
        # instead of "Per Item" (multiplied by quantity), based on user request.
        # Total = (Base Price * Qty) + Total Modifier Cost
        final_total = (base_price * qty) + added_cost
        
        self.total_var.set(final_total)
        self.total_lbl.configure(text=f"{CURRENCY_SYMBOL}{final_total:.2f}")

    def confirm_add(self, *args):
        final_price_total = self.total_var.get()
        try: quantity = int(self.qty_var.get())
        except: quantity = 1
        if quantity < 1: quantity = 1
        
        idx = self.selected_price_idx.get()
        if idx == -1:
            base_unit_price = self.product[3]
            price_name = None
        else:
            base_unit_price = self.prices[idx][5]
            price_name = self.prices[idx][2]
            
        modifier_list = []
        mods_cost = 0
        if self.modifiers and self.modifiers_visible.get():
            for mid, data in self.mod_vars.items():
                if data['checked'].get():
                    m_data = data['data']
                    q = data['qty'].get()
                    cost = m_data[2] * q
                    mods_cost += cost
                    
                    modifier_list.append({
                        'id': m_data[0],
                        'name': m_data[1],
                        'price': m_data[2],
                        'quantity': q,
                        'linked_product_id': m_data[3],
                        'deduct_qty': m_data[4]
                    })
        
        # Global Modifier Logic: Modifiers added once to total, not per item
        total_cart_price = (base_unit_price * quantity) + mods_cost
        effective_unit_price = total_cart_price / quantity if quantity > 0 else 0
        
        display_name = self.product[1]
        if price_name: display_name += f" ({price_name})"
        for mod in modifier_list:
            qty_str = f"{mod['quantity']}x " if mod['quantity'] > 1 else ""
            display_name += f"\n  + {qty_str}{mod['name']}"
            
        note = self.note_entry.get().strip()
        if note: display_name += f"\n  (Note: {note})"
        # specific for Cart Item
        item = {
            'product_id': self.product[0],
            'name': display_name,
            'raw_name': self.product[1],
            'price': effective_unit_price,
            'base_price': base_unit_price, 
            'quantity': quantity,
            'subtotal': total_cart_price,
            'selected_modifiers': modifier_list,
            'note': note
        }
        self.add_callback(item)
        self.dialog.destroy()
