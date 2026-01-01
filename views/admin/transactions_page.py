import customtkinter as ctk
import json
from tkinter import messagebox
from datetime import datetime, timedelta
from config import COLORS, CURRENCY_SYMBOL


class TransactionsPage:
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
        """Show transactions page"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="🧾 Transaction History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Transactions list container
        transactions_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        transactions_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Scrollable area
        transactions_list = ctk.CTkScrollableFrame(
            transactions_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        transactions_list.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid Configuration for Table Layout
        # Columns: Ref, Date, Cashier, Method, Total, Action
        transactions_list.grid_columnconfigure(0, weight=2) # Ref
        transactions_list.grid_columnconfigure(1, weight=2) # Date
        transactions_list.grid_columnconfigure(2, weight=2) # Cashier
        transactions_list.grid_columnconfigure(3, weight=1) # Method
        transactions_list.grid_columnconfigure(4, weight=1) # Total
        transactions_list.grid_columnconfigure(5, weight=1) # Action
        
        # Table Header
        headers = ["Ref #", "Date & Time", "Cashier", "Method", "Total", "Action"]
        for idx, h_text in enumerate(headers):
            ctk.CTkLabel(
                transactions_list,
                text=h_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=idx, sticky="ew", padx=5, pady=(0, 10))
            
        # Header Separator
        ctk.CTkFrame(transactions_list, height=2, fg_color=COLORS["primary"]).grid(row=1, column=0, columnspan=6, sticky="ew", pady=(0, 5))
            
        transactions = self.database.get_transactions(50)
        
        if transactions:
            for i, txn in enumerate(transactions):
                # Calculate Row Index (Start at 2)
                row_idx = 2 + (i * 2)
                
                # txn: 0:id, 1:txn_num, 2:cid, 3:total, 4:tax, 5:disc, 6:method, 7:status, 8:created_at, 9:c_name
                
                # Ref
                ctk.CTkLabel(
                    transactions_list, text=txn[1], font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"]
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
                
                # Method
                ctk.CTkLabel(
                    transactions_list, text=txn[6], font=ctk.CTkFont(size=12)
                ).grid(row=row_idx, column=3, sticky="w", padx=5, pady=5)
                
                # Total (Remove Tax for Display to match request)
                # stored total includes tax. display = total - tax.
                display_total = txn[3] - (txn[4] or 0)
                
                ctk.CTkLabel(
                    transactions_list,
                    text=f"{CURRENCY_SYMBOL}{display_total:.2f}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["success"]
                ).grid(row=row_idx, column=4, sticky="e", padx=20, pady=5)
                
                # View Button
                ctk.CTkButton(
                    transactions_list,
                    text="View",
                    width=60,
                    height=24,
                    font=ctk.CTkFont(size=11),
                    fg_color=COLORS["secondary"],
                    command=lambda tid=txn[0]: self.show_transaction_details(tid)
                ).grid(row=row_idx, column=5, sticky="e", padx=5, pady=5)
                
                # Row Separator (Subtle)
                sep_idx = row_idx + 1
                ctk.CTkFrame(transactions_list, height=1, fg_color="#2c3e50").grid(row=sep_idx, column=0, columnspan=6, sticky="ew", pady=(0, 0))
                
        else:
            ctk.CTkLabel(
                transactions_list,
                text="No transactions found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).grid(row=1, column=0, columnspan=6, pady=50)

    def show_transaction_details(self, transaction_id):
        """Show details of a transaction in a compact, clean dialog"""
        # Fetch Data
        txn = self.database.get_transaction_by_id(transaction_id)
        if not txn:
            messagebox.showerror("Error", "Transaction not found")
            return
            
        items = self.database.get_transaction_items(transaction_id)
        
        # Pre-fetch Global Modifiers
        mod_map = {}
        try:
            self.database.cursor.execute("""
                SELECT m.name, p.name, COALESCE(m.deduct_quantity, 1)
                FROM global_modifiers m
                LEFT JOIN products p ON m.linked_product_id = p.id
            """)
            for row in self.database.cursor.fetchall():
                 if row[1]: mod_map[row[0]] = (row[1], row[2])
        except: pass

        # Create Dialog
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Transaction Details")
        dialog.geometry("500x650")
        
        # Center the dialog
        dialog.update_idletasks()
        width = 500
        height = 650
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.grab_set()
        
        # Main Container
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header Info (Compact)
        header = ctk.CTkFrame(main_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        header.pack(fill="x", pady=(0, 15))
        
        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="x", padx=15, pady=15)
        
        # Top Row: Ref & Date
        date_str = self.format_date_mnl(txn[7])
        ctk.CTkLabel(h_inner, text=f"#{txn[1]}", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkLabel(h_inner, text=date_str, font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="right")
        
        # Bottom Row: Cashier & Method
        h_row2 = ctk.CTkFrame(header, fg_color="transparent")
        h_row2.pack(fill="x", padx=15, pady=(0, 15))
        
        cashier_name = txn[9] if txn[9] else (txn[8] or "Unknown")
        ctk.CTkLabel(h_row2, text=f"Cashier: {cashier_name}", font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkLabel(h_row2, text=txn[6], font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["success"]).pack(side="right")

        # Items List Header
        list_header = ctk.CTkFrame(main_frame, fg_color="transparent", height=30)
        list_header.pack(fill="x", pady=(0, 5))
        
        # Custom Grid for Header
        # Item(Expand), Qty(40), Price(60), Total(60)
        ctk.CTkLabel(list_header, text="Item / Details", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(list_header, text="Qty", font=ctk.CTkFont(size=12, weight="bold"), width=40, anchor="center").pack(side="left")
        ctk.CTkLabel(list_header, text="Price", font=ctk.CTkFont(size=12, weight="bold"), width=60, anchor="e").pack(side="left")
        ctk.CTkLabel(list_header, text="Total", font=ctk.CTkFont(size=12, weight="bold"), width=70, anchor="e").pack(side="left") # width 70 for total

        # Separator
        ctk.CTkFrame(main_frame, height=2, fg_color=COLORS["primary"]).pack(fill="x", pady=(0, 5))

        # Scrollable List
        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", label_text="")
        scroll.pack(fill="both", expand=True)
        
        for item in items:
            # item schema: 0:id, 1:txn_id, 2:prod_id, 3:name, 4:qty, 5:price, 6:subtotal, 7:var_id, 8:var_name, 9:mods
            prod_id = item[2]
            name = item[3]
            qty = item[4]
            price = item[5]
            subtotal = item[6]
            mods_str = item[9]
            
            # Item Row Frame
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Main Product Line
            ctk.CTkLabel(row, text=str(subtotal), font=ctk.CTkFont(size=12), width=70, anchor="e").pack(side="right") # Total
            ctk.CTkLabel(row, text=f"{price:.2f}", font=ctk.CTkFont(size=12), width=60, anchor="e").pack(side="right") # Price
            ctk.CTkLabel(row, text=str(qty), font=ctk.CTkFont(size=12), width=40, anchor="center").pack(side="right") # Qty
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", fill="x", expand=True) # Name
            
            # Linked Ingredients
            try:
                ingredients = self.database.get_product_ingredients(prod_id)
                if ingredients:
                    for ing in ingredients:
                        total_used = ing[3] * qty
                        ing_row = ctk.CTkFrame(scroll, fg_color="transparent")
                        ing_row.pack(fill="x")
                        ctk.CTkLabel(ing_row, text=f" • Used: {total_used:g} x {ing[2]}", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"], anchor="w").pack(side="left", padx=(15,0))
            except: pass
            
            # Modifiers
            if mods_str:
                try:
                    # Try JSON parsing (New format)
                    mods_list = json.loads(mods_str)
                    
                    for mod in mods_list:
                        # Extract details
                        if isinstance(mod, dict):
                            m_name = mod.get('name', 'Unknown')
                            m_qty = mod.get('quantity', 1)
                            m_price = mod.get('price', 0)
                        else:
                            # Fallback if list of strings
                            m_name = str(mod)
                            m_qty = 1
                            m_price = 0
                            
                        # Display
                        disp_str = f" + {m_qty}x {m_name}"
                        if m_price > 0:
                            disp_str += f" (+{CURRENCY_SYMBOL}{m_price:.2f})"
                            
                        mod_row = ctk.CTkFrame(scroll, fg_color="transparent")
                        mod_row.pack(fill="x")
                        ctk.CTkLabel(mod_row, text=disp_str, font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"], anchor="w").pack(side="left", padx=(10,0))
                        
                        # Linked Ingredient Logic (visual only)
                        # We use mod_map fallback since real linkage is complex to reconstruct without ID
                        if m_name in mod_map:
                            link_name, d_qty = mod_map[m_name]
                            total_mod_used = d_qty * m_qty
                            l_row = ctk.CTkFrame(scroll, fg_color="transparent")
                            l_row.pack(fill="x")
                            ctk.CTkLabel(l_row, text=f"     -> Used: {total_mod_used:g} x {link_name}", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"], anchor="w").pack(side="left", padx=(30,0))
                            
                except (json.JSONDecodeError, TypeError):
                    # Fallback: Comma-separated string (Old format)
                    mod_names = [m.strip() for m in mods_str.split(", ") if m.strip()]
                    for m_name in mod_names:
                        # Mod Row
                        mod_row = ctk.CTkFrame(scroll, fg_color="transparent")
                        mod_row.pack(fill="x")
                        ctk.CTkLabel(mod_row, text=f" + {m_name}", font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"], anchor="w").pack(side="left", padx=(10,0))
                        
                        # Mod Linked Inv
                        if m_name in mod_map:
                            link_name, d_qty = mod_map[m_name]
                            total_mod_used = d_qty * qty
                            l_row = ctk.CTkFrame(scroll, fg_color="transparent")
                            l_row.pack(fill="x")
                            ctk.CTkLabel(l_row, text=f"     -> Used: {total_mod_used:g} x {link_name}", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"], anchor="w").pack(side="left", padx=(15,0))

            # Subtle Divider
            ctk.CTkFrame(scroll, height=1, fg_color="#333").pack(fill="x", pady=5)
            
        # Footer
        footer = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer.pack(fill="x", pady=(15, 0))
        
        display_total = txn[3] - (txn[4] or 0)
        
        total_frame = ctk.CTkFrame(footer, fg_color=COLORS["card_bg"], corner_radius=10)
        total_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(total_frame, text="TOTAL", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(total_frame, text=f"{CURRENCY_SYMBOL}{display_total:.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["success"]).pack(side="right", padx=15, pady=10)
        
        # Close Button
        ctk.CTkButton(
            footer,
            text="Close",
            width=100,
            height=35,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            command=dialog.destroy
        ).pack(side="top")
