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
        
        # Recent transactions
        recent_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        recent_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        recent_header = ctk.CTkLabel(
            recent_frame,
            text="Recent Transactions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        recent_header.pack(pady=20, padx=20, anchor="w")
        
        # Transactions list container
        transactions_list = ctk.CTkScrollableFrame(
            recent_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        transactions_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Table Grid Config
        transactions_list.grid_columnconfigure(0, weight=2) # Ref
        transactions_list.grid_columnconfigure(1, weight=2) # Date
        transactions_list.grid_columnconfigure(2, weight=2) # Cashier
        transactions_list.grid_columnconfigure(3, weight=1) # Total
        
        # Headers
        headers = ["Ref #", "Date & Time", "Cashier", "Total"]
        for idx, h_text in enumerate(headers):
             ctk.CTkLabel(
                transactions_list,
                text=h_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"]
             ).grid(row=0, column=idx, sticky="ew", padx=5, pady=(0, 10))
        
        # Header Separator
        ctk.CTkFrame(transactions_list, height=2, fg_color=COLORS["primary"]).grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        
        transactions = self.database.get_transactions(10)
        
        if transactions:
            for i, txn in enumerate(transactions):
                row_idx = 2 + (i * 2)
                
                # Row Frame
                row_frame = ctk.CTkFrame(transactions_list, fg_color="transparent")
                row_frame.grid(row=row_idx, column=0, columnspan=4, sticky="ew")
                row_frame.grid_columnconfigure(0, weight=2)
                row_frame.grid_columnconfigure(1, weight=2)
                row_frame.grid_columnconfigure(2, weight=2)
                row_frame.grid_columnconfigure(3, weight=1)
                
                # Bind click to row
                def on_click(e, tid=txn[0]): self.show_transaction_details(tid)
                row_frame.bind("<Button-1>", on_click)
                
                # Ref
                l1 = ctk.CTkLabel(row_frame, text=f"#{txn[1]}", font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"])
                l1.grid(row=0, column=0, sticky="w", padx=5, pady=5)
                l1.bind("<Button-1>", on_click)
                
                # Date (Manila Time)
                date_str = self.format_date_mnl(txn[8])
                l2 = ctk.CTkLabel(row_frame, text=date_str, font=ctk.CTkFont(size=12))
                l2.grid(row=0, column=1, sticky="w", padx=5, pady=5)
                l2.bind("<Button-1>", on_click)
                
                # Cashier
                l3 = ctk.CTkLabel(row_frame, text=txn[9], font=ctk.CTkFont(size=12))
                l3.grid(row=0, column=2, sticky="w", padx=5, pady=5)
                l3.bind("<Button-1>", on_click)
                
                # Total
                display_total = txn[3] - (txn[4] or 0)
                l4 = ctk.CTkLabel(
                    row_frame,
                    text=f"{CURRENCY_SYMBOL}{display_total:.2f}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["success"]
                )
                l4.grid(row=0, column=3, sticky="e", padx=20, pady=5)
                l4.bind("<Button-1>", on_click)
                
                # Row Separator
                sep_idx = row_idx + 1
                ctk.CTkFrame(transactions_list, height=1, fg_color="#2c3e50").grid(row=sep_idx, column=0, columnspan=4, sticky="ew", pady=(0, 0))
                
        else:
            ctk.CTkLabel(
                transactions_list,
                text="No transactions yet",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_secondary"]
            ).grid(row=2, column=0, columnspan=4, pady=30)

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
