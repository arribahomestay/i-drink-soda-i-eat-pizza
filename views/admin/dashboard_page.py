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
        self.current_filter = "today"  # today, yesterday, custom
        self.custom_start_date = None
        self.custom_end_date = None
        
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
        
        # Date filter buttons
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.pack(side="right")
        
        # Today button
        today_btn = ctk.CTkButton(
            filter_frame,
            text="Today",
            command=lambda: self.apply_filter("today"),
            width=100,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"] if self.current_filter == "today" else COLORS["card_bg"],
            hover_color=COLORS["primary"],
            corner_radius=8
        )
        today_btn.pack(side="left", padx=5)
        
        # Yesterday button
        yesterday_btn = ctk.CTkButton(
            filter_frame,
            text="Yesterday",
            command=lambda: self.apply_filter("yesterday"),
            width=100,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"] if self.current_filter == "yesterday" else COLORS["card_bg"],
            hover_color=COLORS["primary"],
            corner_radius=8
        )
        yesterday_btn.pack(side="left", padx=5)
        
        # Custom date button
        custom_btn = ctk.CTkButton(
            filter_frame,
            text="Custom Date",
            command=lambda: self.show_custom_date_dialog(),
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"] if self.current_filter == "custom" else COLORS["card_bg"],
            hover_color=COLORS["primary"],
            corner_radius=8
        )
        custom_btn.pack(side="left", padx=5)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Get date range based on filter
        start_date, end_date = self.get_date_range()
        
        # Get statistics with date filter
        sales_summary = self.database.get_sales_summary(start_date, end_date)
        products = self.database.get_all_products()
        
        # Split Product Counts
        # Indices: use_stock_tracking=12
        stock_products = [p for p in products if (len(p) > 12 and p[12] == 1)]
        avail_products = [p for p in products if (len(p) > 12 and p[12] == 0)]
        low_stock = len([p for p in stock_products if p[4] < 10])
        
        # Split Sales Counts
        sales_breakdown = self.database.get_product_type_sales_count(start_date, end_date)
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
        
        
        # Analytics Section - Clean 3-Column Grid Layout
        analytics_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        analytics_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Configure grid weights for equal columns
        analytics_container.grid_columnconfigure(0, weight=1)
        analytics_container.grid_columnconfigure(1, weight=1)
        analytics_container.grid_columnconfigure(2, weight=1)
        analytics_container.grid_rowconfigure(0, weight=1)
        analytics_container.grid_rowconfigure(1, weight=1)
        
        # === ROW 1 ===
        
        # 1. Top Selling Products (Row 1, Col 1)
        top_products_frame = ctk.CTkFrame(analytics_container, fg_color=COLORS["card_bg"], corner_radius=15)
        top_products_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        ctk.CTkLabel(
            top_products_frame,
            text="📊 Top Selling Products",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(12, 8), padx=15, anchor="w")
        
        top_products_list = ctk.CTkScrollableFrame(
            top_products_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"],
            height=150
        )
        top_products_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        top_products = self.database.get_top_selling_products(start_date, end_date, limit=5)
        
        if top_products:
            for idx, product in enumerate(top_products, 1):
                product_name = product[0]
                qty_sold = product[1]
                revenue = product[2]
                
                row = ctk.CTkFrame(top_products_list, fg_color=COLORS["dark"], corner_radius=4, height=32)
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                
                content = ctk.CTkFrame(row, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=10, pady=4)
                
                rank_color = COLORS["warning"] if idx <= 3 else COLORS["text_secondary"]
                ctk.CTkLabel(content, text=f"#{idx}", font=ctk.CTkFont(size=9, weight="bold"), text_color=rank_color, width=25).pack(side="left")
                ctk.CTkLabel(content, text=product_name[:20], font=ctk.CTkFont(size=10), text_color=COLORS["text_primary"], anchor="w").pack(side="left", fill="x", expand=True, padx=(3, 5))
                ctk.CTkLabel(content, text=f"{qty_sold}", font=ctk.CTkFont(size=9), text_color=COLORS["info"], width=35, anchor="e").pack(side="right")
        else:
            ctk.CTkLabel(top_products_list, text="No data", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(pady=20)
        
        # 2. Payment Methods (Row 1, Col 2)
        payment_frame = ctk.CTkFrame(analytics_container, fg_color=COLORS["card_bg"], corner_radius=15)
        payment_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 10))
        
        ctk.CTkLabel(
            payment_frame,
            text="💳 Payment Methods",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(12, 8), padx=15, anchor="w")
        
        payment_list = ctk.CTkFrame(payment_frame, fg_color="transparent")
        payment_list.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        payment_methods = self.database.get_payment_method_breakdown(start_date, end_date)
        
        if payment_methods:
            total_amount = sum(pm[1] for pm in payment_methods)
            
            for pm in payment_methods:
                method = pm[0]
                amount = pm[1]
                count = pm[2]
                percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                
                method_row = ctk.CTkFrame(payment_list, fg_color=COLORS["dark"], corner_radius=4, height=38)
                method_row.pack(fill="x", pady=2)
                method_row.pack_propagate(False)
                
                row_content = ctk.CTkFrame(method_row, fg_color="transparent")
                row_content.pack(fill="both", expand=True, padx=10, pady=4)
                
                method_icon = "💵" if method == "Cash" else "💳"
                ctk.CTkLabel(row_content, text=f"{method_icon} {method}", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_primary"], anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row_content, text=f"{percentage:.0f}%", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["info"], width=40).pack(side="right", padx=(3, 0))
                ctk.CTkLabel(row_content, text=f"{CURRENCY_SYMBOL}{amount:.0f}", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["success"], width=75, anchor="e").pack(side="right")
        else:
            ctk.CTkLabel(payment_list, text="No data", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(pady=20)
        
        # 3. Order Types (Row 1, Col 3)
        order_type_frame = ctk.CTkFrame(analytics_container, fg_color=COLORS["card_bg"], corner_radius=15)
        order_type_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 10))
        
        ctk.CTkLabel(
            order_type_frame,
            text="🍽️ Order Types",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(12, 8), padx=15, anchor="w")
        
        order_type_list = ctk.CTkFrame(order_type_frame, fg_color="transparent")
        order_type_list.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        order_types = self.database.get_order_type_breakdown(start_date, end_date)
        
        if order_types:
            total_orders = sum(ot[1] for ot in order_types)
            
            for ot in order_types:
                order_type = ot[0]
                count = ot[1]
                amount = ot[2]
                percentage = (count / total_orders * 100) if total_orders > 0 else 0
                
                if order_type == "Dine In":
                    type_color = COLORS["info"]
                    icon = "🍽️"
                elif order_type == "Take Out":
                    type_color = COLORS["warning"]
                    icon = "🥡"
                else:
                    type_color = COLORS["primary"]
                    icon = "🛒"
                
                type_row = ctk.CTkFrame(order_type_list, fg_color=COLORS["dark"], corner_radius=4, height=38)
                type_row.pack(fill="x", pady=2)
                type_row.pack_propagate(False)
                
                row_content = ctk.CTkFrame(type_row, fg_color="transparent")
                row_content.pack(fill="both", expand=True, padx=10, pady=4)
                
                ctk.CTkLabel(row_content, text=f"{icon} {order_type}", font=ctk.CTkFont(size=11, weight="bold"), text_color=type_color, anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row_content, text=f"{percentage:.0f}%", font=ctk.CTkFont(size=10, weight="bold"), text_color=type_color, width=40).pack(side="right", padx=(3, 0))
                ctk.CTkLabel(row_content, text=f"{CURRENCY_SYMBOL}{amount:.0f}", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["success"], width=75, anchor="e").pack(side="right")
        else:
            ctk.CTkLabel(order_type_list, text="No data", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(pady=20)
        
        # === ROW 2 ===
        
        # 4. Peak Hours (Row 2, Col 1-2)
        peak_hours_frame = ctk.CTkFrame(analytics_container, fg_color=COLORS["card_bg"], corner_radius=15)
        peak_hours_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 5), pady=(0, 0))
        
        ctk.CTkLabel(
            peak_hours_frame,
            text="⏰ Peak Sales Hours",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(12, 8), padx=15, anchor="w")
        
        peak_hours_content = ctk.CTkFrame(peak_hours_frame, fg_color="transparent")
        peak_hours_content.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        hourly_sales = self.database.get_hourly_sales(start_date, end_date)
        
        if hourly_sales:
            # Create horizontal bar chart
            max_sales = max(hs[1] for hs in hourly_sales) if hourly_sales else 1
            
            for hour_data in hourly_sales[:8]:  # Show top 8 hours
                hour = hour_data[0]
                sales = hour_data[1]
                count = hour_data[2]
                bar_width = (sales / max_sales * 100) if max_sales > 0 else 0
                
                hour_row = ctk.CTkFrame(peak_hours_content, fg_color="transparent", height=28)
                hour_row.pack(fill="x", pady=2)
                hour_row.pack_propagate(False)
                
                # Time label
                time_label = ctk.CTkLabel(hour_row, text=f"{hour:02d}:00", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_secondary"], width=50, anchor="w")
                time_label.pack(side="left", padx=(0, 8))
                
                # Bar container
                bar_container = ctk.CTkFrame(hour_row, fg_color=COLORS["dark"], corner_radius=3, height=20)
                bar_container.pack(side="left", fill="x", expand=True, padx=(0, 8))
                
                # Filled bar
                if bar_width > 0:
                    bar = ctk.CTkFrame(bar_container, fg_color=COLORS["primary"], corner_radius=3, width=int(bar_width * 3), height=20)
                    bar.place(x=0, y=0)
                
                # Sales amount
                ctk.CTkLabel(hour_row, text=f"{CURRENCY_SYMBOL}{sales:.0f}", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["success"], width=70, anchor="e").pack(side="right")
        else:
            ctk.CTkLabel(peak_hours_content, text="No hourly data", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(pady=20)
        
        # 5. Category Performance (Row 2, Col 3)
        category_frame = ctk.CTkFrame(analytics_container, fg_color=COLORS["card_bg"], corner_radius=15)
        category_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0), pady=(0, 0))
        
        ctk.CTkLabel(
            category_frame,
            text="📂 Top Categories",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(12, 8), padx=15, anchor="w")
        
        category_list = ctk.CTkFrame(category_frame, fg_color="transparent")
        category_list.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        categories = self.database.get_category_performance(start_date, end_date)
        
        if categories:
            total_cat_sales = sum(cat[1] for cat in categories)
            
            for idx, cat in enumerate(categories[:5], 1):  # Top 5 categories
                category_name = cat[0] or "Uncategorized"
                sales = cat[1]
                percentage = (sales / total_cat_sales * 100) if total_cat_sales > 0 else 0
                
                cat_row = ctk.CTkFrame(category_list, fg_color=COLORS["dark"], corner_radius=4, height=35)
                cat_row.pack(fill="x", pady=2)
                cat_row.pack_propagate(False)
                
                row_content = ctk.CTkFrame(cat_row, fg_color="transparent")
                row_content.pack(fill="both", expand=True, padx=10, pady=4)
                
                ctk.CTkLabel(row_content, text=category_name[:15], font=ctk.CTkFont(size=10), text_color=COLORS["text_primary"], anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row_content, text=f"{percentage:.0f}%", font=ctk.CTkFont(size=9, weight="bold"), text_color=COLORS["info"], width=35).pack(side="right", padx=(3, 0))
                ctk.CTkLabel(row_content, text=f"{CURRENCY_SYMBOL}{sales:.0f}", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["success"], width=65, anchor="e").pack(side="right")
        else:
            ctk.CTkLabel(category_list, text="No data", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(pady=20)



    def show_item_breakdown(self, product_name, product_id, quantity, unit_price, subtotal, modifiers_str, order_type="Regular"):
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
    
    def get_date_range(self):
        """Get date range based on current filter"""
        from datetime import date, timedelta
        
        if self.current_filter == "today":
            today = date.today()
            return today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif self.current_filter == "yesterday":
            yesterday = date.today() - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")
        elif self.current_filter == "custom" and self.custom_start_date and self.custom_end_date:
            return self.custom_start_date, self.custom_end_date
        else:
            # Default to today
            today = date.today()
            return today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    
    def apply_filter(self, filter_type):
        """Apply date filter and refresh dashboard"""
        self.current_filter = filter_type
        # Clear and reload the dashboard
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.show()
    
    def show_custom_date_dialog(self):
        """Show dialog to select custom date range"""
        from tkcalendar import DateEntry
        from datetime import date
        
        # Modal
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Select Date Range")
        dialog.geometry("450x380")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 450) // 2
        y = (dialog.winfo_screenheight() - 380) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="Select Date Range",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.pack(pady=(20, 30))
        
        # Date inputs frame
        dates_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        dates_frame.pack(pady=10, padx=30, fill="x")
        
        # Start date
        start_label = ctk.CTkLabel(
            dates_frame,
            text="Start Date:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        start_label.grid(row=0, column=0, sticky="w", pady=10, padx=(0, 15))
        
        # Calendar widget for start date
        start_cal = DateEntry(
            dates_frame,
            width=20,
            background=COLORS["primary"],
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 11)
        )
        start_cal.grid(row=0, column=1, pady=10, sticky="ew")
        
        # End date
        end_label = ctk.CTkLabel(
            dates_frame,
            text="End Date:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        end_label.grid(row=1, column=0, sticky="w", pady=10, padx=(0, 15))
        
        # Calendar widget for end date
        end_cal = DateEntry(
            dates_frame,
            width=20,
            background=COLORS["primary"],
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 11)
        )
        end_cal.grid(row=1, column=1, pady=10, sticky="ew")
        
        # Configure grid column to expand
        dates_frame.columnconfigure(1, weight=1)
        
        # Pre-fill with current custom dates if available
        if self.custom_start_date:
            try:
                start_cal.set_date(self.custom_start_date)
            except:
                pass
        if self.custom_end_date:
            try:
                end_cal.set_date(self.custom_end_date)
            except:
                pass
        
        # Info label
        info_label = ctk.CTkLabel(
            dialog,
            text="💡 Click on the date fields to open the calendar",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        info_label.pack(pady=(10, 20))
        
        # Buttons
        def apply_custom_filter():
            start = start_cal.get_date().strftime("%Y-%m-%d")
            end = end_cal.get_date().strftime("%Y-%m-%d")
            
            self.custom_start_date = start
            self.custom_end_date = end
            self.current_filter = "custom"
            dialog.destroy()
            
            # Refresh dashboard
            for widget in self.parent.winfo_children():
                widget.destroy()
            self.show()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(15, 25))
        
        apply_btn = ctk.CTkButton(
            btn_frame,
            text="Apply Filter",
            command=apply_custom_filter,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60"
        )
        apply_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b"
        )
        cancel_btn.pack(side="left", padx=5)


