"""
Dashboard page for admin view
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config import COLORS, CURRENCY_SYMBOL


class DashboardPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
        
    def format_date_mnl(self, date_str):
        """Convert UTC string to Manila Time (+8) string"""
        try:
            # Assuming DB stores UTC "YYYY-MM-DD HH:MM:SS"
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            dt += timedelta(hours=8)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return date_str # Fallback
    
    def show(self):
        """Show dashboard page"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%B %d, %Y"),
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        date_label.pack(side="right")
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Get statistics
        sales_summary = self.database.get_sales_summary()
        products = self.database.get_all_products()
        
        # Split Product Counts
        # Indices: use_stock_tracking=12
        stock_products = [p for p in products if (len(p) > 12 and p[12] == 1)]
        avail_products = [p for p in products if (len(p) > 12 and p[12] == 0)]
        low_stock = len([p for p in stock_products if p[4] < 10])
        
        # Split Sales Counts
        sales_breakdown = self.database.get_product_type_sales_count()
        sold_stock = 0
        sold_avail = 0
        if sales_breakdown:
            for row in sales_breakdown:
                # row[0] is use_stock_tracking (1 or 0/None), row[1] is qty
                st_type = row[0] if row[0] is not None else 1
                qty = row[1] if row[1] else 0
                if st_type == 1:
                    sold_stock += qty
                else:
                    sold_avail += qty

        # Calculate Net Sales (Total - Tax)
        total_sales = (sales_summary[1] or 0)
        total_tax = (sales_summary[2] or 0)
        net_sales = total_sales - total_tax
        
        stats = [
            ("💰 Total Sales", f"{CURRENCY_SYMBOL}{net_sales:.2f}", COLORS["success"]),
            ("🧾 Sold Items", f"{sold_stock} Stock | {sold_avail} Order", COLORS["info"]),
            ("📦 Products", f"{len(stock_products)} Stock | {len(avail_products)} Order", COLORS["primary"]),
            ("⚠️ Low Stock", str(low_stock), COLORS["warning"]),
        ]
        
        for idx, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=COLORS["card_bg"], corner_radius=15)
            card.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_secondary"]
            ).pack(pady=(20, 5), padx=20)
            
            # Use smaller font if text is long (contains divider)
            font_size = 20 if "|" in value else 28
            
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=font_size, weight="bold"),
                text_color=color
            ).pack(pady=(0, 20), padx=20)
        
        # Recent transactions - Sold Items Format
        recent_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        recent_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        recent_header = ctk.CTkLabel(
            recent_frame,
            text="Recent Sales",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        recent_header.pack(pady=20, padx=20, anchor="w")
        
        # Sales items list container
        sales_list = ctk.CTkScrollableFrame(
            recent_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        sales_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Get recent transaction items (last 20 items sold)
        transactions = self.database.get_transactions(20)
        
        if transactions:
            item_count = 0
            for txn in transactions:
                items = self.database.get_transaction_items(txn[0])
                
                for item in items:
                    if item_count >= 20:  # Limit to 20 items
                        break
                    
                    # transaction_items: id, txn_id, prod_id, product_name, quantity, unit_price, subtotal, variant_id, variant_name, modifiers
                    product_name = item[3]
                    qty = item[4]
                    unit_price = item[5]
                    subtotal = item[6]
                    product_id = item[2]
                    modifiers_str = item[9] if len(item) > 9 else None
                    
                    # Create clickable item card
                    item_card = ctk.CTkFrame(sales_list, fg_color=COLORS["dark"], corner_radius=10, cursor="hand2")
                    item_card.pack(fill="x", pady=5)
                    
                     # Make entire card clickable
                    def make_clickable(card, pname, pid, q, price, sub, mods, o_type):
                        def on_click(event=None):
                            self.show_item_breakdown(pname, pid, q, price, sub, mods, o_type)
                        card.bind("<Button-1>", on_click)
                        card.bind("<Enter>", lambda e: card.configure(fg_color=COLORS["primary"]))
                        card.bind("<Leave>", lambda e: card.configure(fg_color=COLORS["dark"]))
                        return on_click
                    
                    # Order Type
                    order_type = txn[7] if len(txn) > 7 else "Normal"
                    if order_type is None: order_type = "Normal"

                    click_handler = make_clickable(item_card, product_name, product_id, qty, unit_price, subtotal, modifiers_str, order_type)
                    
                    # Content frame
                    content_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                    content_frame.pack(fill="x", padx=15, pady=12)
                    content_frame.bind("<Button-1>", click_handler)
                    
                    # Left side: Sold text
                    left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    left_frame.pack(side="left", fill="x", expand=True)
                    left_frame.bind("<Button-1>", click_handler)
                    
                    sold_label = ctk.CTkLabel(
                        left_frame,
                        text=f"Sold {qty}x {product_name}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=COLORS["text_primary"],
                        anchor="w"
                    )
                    sold_label.pack(side="left")
                    sold_label.bind("<Button-1>", click_handler)
                    
                    # Right side: Price
                    price_label = ctk.CTkLabel(
                        content_frame,
                        text=f"{CURRENCY_SYMBOL}{subtotal:.2f}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=COLORS["success"]
                    )
                    price_label.pack(side="right")
                    price_label.bind("<Button-1>", click_handler)
                    
                    
                    type_color = COLORS["info"] if order_type == "Dine In" else (COLORS["warning"] if order_type == "Take Out" else COLORS["text_secondary"])
                    
                    type_label = ctk.CTkLabel(
                        content_frame,
                        text=order_type,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=type_color
                    )
                    type_label.pack(side="right", padx=15)
                    type_label.bind("<Button-1>", click_handler)
                    
                    item_count += 1
                
                if item_count >= 20:
                    break
        else:
            ctk.CTkLabel(
                sales_list,
                text="No sales yet",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_secondary"]
            ).pack(pady=30)


    def show_item_breakdown(self, product_name, product_id, quantity, unit_price, subtotal, modifiers_str, order_type="Normal"):
        """Show detailed breakdown modal for a sold item with ingredients, add-ons, and prices"""
        import json
        
        # Modal
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Item Breakdown")
        dialog.geometry("600x700")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 600) // 2
        y = (dialog.winfo_screenheight() - 700) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header, 
            text=f"Sold {quantity}x {product_name}", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 5))
        
        # Order Type Badge
        o_color = COLORS["info"] if order_type == "Dine In" else (COLORS["warning"] if order_type == "Take Out" else "#95a5a6")
        ctk.CTkLabel(
            header,
            text=order_type.upper(),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=o_color
        ).pack(pady=(0, 20))
        
        # Content
        content = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product Price Section
        price_card = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=10)
        price_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            price_card,
            text="💰 Product Price",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(15, 5), padx=15, anchor="w")
        
        price_frame = ctk.CTkFrame(price_card, fg_color="transparent")
        price_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            price_frame,
            text=f"Unit Price:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            price_frame,
            text=f"{CURRENCY_SYMBOL}{unit_price:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="right")
        
        # Ingredients Section
        ingredients = self.database.get_product_ingredients(product_id)
        
        if ingredients:
            ing_card = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=10)
            ing_card.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                ing_card,
                text="🥗 Linked Ingredients Used",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["info"]
            ).pack(pady=(15, 10), padx=15, anchor="w")
            
            for ing in ingredients:
                # get_product_ingredients returns: id, ingredient_id, name, quantity, price, cost
                ing_id = ing[0]
                ingredient_id = ing[1]
                ing_name = ing[2]           # Ingredient name (was incorrectly ing[3])
                qty_per_unit = ing[3]       # Quantity per unit (was incorrectly ing[4])
                ing_unit_price = ing[4]     # Unit price of ingredient
                
                total_qty_used = qty_per_unit * quantity
                total_cost = ing_unit_price * total_qty_used if ing_unit_price else 0
                
                ing_row = ctk.CTkFrame(ing_card, fg_color=COLORS["dark"], corner_radius=5)
                ing_row.pack(fill="x", padx=15, pady=5)
                
                # Left: Name and quantity
                left = ctk.CTkFrame(ing_row, fg_color="transparent")
                left.pack(side="left", fill="x", expand=True, padx=10, pady=8)
                
                ctk.CTkLabel(
                    left,
                    text=f"• {ing_name}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    left,
                    text=f"  {qty_per_unit} per unit × {quantity} = {total_qty_used} total",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="w")
                
                # Right: Cost (always show with peso sign)
                ctk.CTkLabel(
                    ing_row,
                    text=f"{CURRENCY_SYMBOL}{total_cost:.2f}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["warning"]
                ).pack(side="right", padx=10, pady=8)
        
        # Add-ons/Modifiers Section
        if modifiers_str:
            try:
                mods = json.loads(modifiers_str)
                if mods:
                    mod_card = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=10)
                    mod_card.pack(fill="x", pady=(0, 15))
                    
                    ctk.CTkLabel(
                        mod_card,
                        text="➕ Add-ons / Modifiers",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=COLORS["success"]
                    ).pack(pady=(15, 10), padx=15, anchor="w")
                    
                    for mod in mods:
                        m_name = mod.get('name', 'Unknown')
                        m_qty = mod.get('quantity', 1)
                        m_price = mod.get('price', 0)
                        
                        mod_row = ctk.CTkFrame(mod_card, fg_color=COLORS["dark"], corner_radius=5)
                        mod_row.pack(fill="x", padx=15, pady=5)
                        
                        # Left: Name and quantity
                        left = ctk.CTkFrame(mod_row, fg_color="transparent")
                        left.pack(side="left", fill="x", expand=True, padx=10, pady=8)
                        
                        ctk.CTkLabel(
                            left,
                            text=f"• {m_qty}x {m_name}",
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=COLORS["text_primary"]
                        ).pack(anchor="w")
                        
                        # Right: Price
                        if m_price > 0:
                            ctk.CTkLabel(
                                mod_row,
                                text=f"+{CURRENCY_SYMBOL}{m_price:.2f}",
                                font=ctk.CTkFont(size=12, weight="bold"),
                                text_color=COLORS["success"]
                            ).pack(side="right", padx=10, pady=8)
            except:
                pass
        
        # Total Section
        total_card = ctk.CTkFrame(content, fg_color=COLORS["primary"], corner_radius=10)
        total_card.pack(fill="x", pady=(10, 0))
        
        total_frame = ctk.CTkFrame(total_card, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            total_frame,
            text="Total Amount:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        ctk.CTkLabel(
            total_frame,
            text=f"{CURRENCY_SYMBOL}{subtotal:.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="right")
        
        # Close button
        ctk.CTkButton(
            dialog, 
            text="Close", 
            command=dialog.destroy, 
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)

    def show_transaction_details(self, transaction_id):

        """Show transaction details modal with item breakdown (modifiers/ingredients)"""
        import json
        
        # Fetch Data
        txn = self.database.get_transaction_by_id(transaction_id)
        items = self.database.get_transaction_items(transaction_id)
        
        if not txn: return
        
        # Modal
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Transaction #{txn[1]}")
        dialog.geometry("500x600")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=0)
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header, text=f"Transaction Details", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Items List
        content = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for item in items:
            # item: id, txn_id, prod_id, name, qty, price, subtotal, var_id, var_name, modifiers
            name = item[3]
            qty = item[4]
            price = item[5]
            subtotal = item[6]
            modifiers_json = item[9] if len(item) > 9 else None
            
            card = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=8)
            card.pack(fill="x", pady=5)
            
            # Header line: Qty x Name ... Price
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(top, text=f"{qty}x", font=ctk.CTkFont(weight="bold"), text_color=COLORS["primary"]).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(top, text=name, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", fill="x", expand=True, anchor="w")
            ctk.CTkLabel(top, text=f"{CURRENCY_SYMBOL}{subtotal:.2f}", font=ctk.CTkFont(weight="bold")).pack(side="right")
            
            # Modifiers / Linked Ingredients
            if modifiers_json:
                try:
                    mods = json.loads(modifiers_json)
                    if mods:
                        mod_frame = ctk.CTkFrame(card, fg_color="transparent")
                        mod_frame.pack(fill="x", padx=30, pady=(0, 10))
                        
                        ctk.CTkLabel(mod_frame, text="Add-ons / Ingredients:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="w")
                        
                        for mod in mods:
                            # mod dict usually has 'name', 'quantity', 'price'
                            m_name = mod.get('name', 'Unknown')
                            m_qty = mod.get('quantity', 1)
                            m_price = mod.get('price', 0)
                            
                            m_str = f"• {m_qty}x {m_name}"
                            if m_price > 0:
                                m_str += f" (+{CURRENCY_SYMBOL}{m_price:.2f})"
                                
                            ctk.CTkLabel(mod_frame, text=m_str, font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=5)
                            
                except:
                    pass
        
        # Footer (Total)
        footer = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], height=60, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        
        display_total = txn[3] - (txn[4] or 0)
        ctk.CTkLabel(
            footer, text=f"Total: {CURRENCY_SYMBOL}{display_total:.2f}", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["success"]
        ).pack(pady=15)
        
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy, fg_color=COLORS["danger"], width=100).pack(pady=10, side="bottom")
