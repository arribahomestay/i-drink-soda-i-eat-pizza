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
        total_products = len(products)
        low_stock = len([p for p in products if p[4] < 10])
        
        # Calculate Net Sales (Total - Tax)
        total_sales = (sales_summary[1] or 0)
        total_tax = (sales_summary[2] or 0)
        net_sales = total_sales - total_tax
        
        stats = [
            ("💰 Total Sales", f"{CURRENCY_SYMBOL}{net_sales:.2f}", COLORS["success"]),
            ("🧾 Transactions", str(sales_summary[0] or 0), COLORS["info"]),
            ("📦 Products", str(total_products), COLORS["primary"]),
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
            
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=28, weight="bold"),
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
                
                # Ref
                ctk.CTkLabel(
                    transactions_list, text=f"#{txn[1]}", font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"]
                ).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
                
                # Date (Manila Time)
                date_str = self.format_date_mnl(txn[8])
                ctk.CTkLabel(
                    transactions_list, text=date_str, font=ctk.CTkFont(size=12)
                ).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
                
                # Cashier
                ctk.CTkLabel(
                    transactions_list, text=txn[9], font=ctk.CTkFont(size=12)
                ).grid(row=row_idx, column=2, sticky="w", padx=5, pady=5)
                
                # Total (Remove Tax for Display)
                display_total = txn[3] - (txn[4] or 0)
                
                ctk.CTkLabel(
                    transactions_list,
                    text=f"{CURRENCY_SYMBOL}{display_total:.2f}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["success"]
                ).grid(row=row_idx, column=3, sticky="e", padx=20, pady=5)
                
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
