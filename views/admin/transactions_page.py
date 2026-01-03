import customtkinter as ctk
import json
from tkinter import messagebox
from datetime import datetime, timedelta
from config import COLORS, CURRENCY_SYMBOL


class TransactionsPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
        
        # Optimization: Reuse fonts to speed up rendering
        self.f_reg = ctk.CTkFont(size=12)
        self.f_bold = ctk.CTkFont(size=12, weight="bold")
        self.f_head = ctk.CTkFont(size=12, weight="bold")
        
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
        import tkinter as tk
        
        # Initialize filter state
        self.filter_cashier = None
        self.filter_order_type = None
        self.filter_date_range = None
        self.custom_start_date = None
        self.custom_end_date = None
        
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
        
        # Calculate button
        calc_btn = ctk.CTkButton(
            header,
            text="🧮 Calculate",
            width=100,
            height=35,
            command=self.show_calculate_dialog,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=5
        )
        calc_btn.pack(side="right", padx=(10, 0))
        
        # Filter button
        self.filter_btn = ctk.CTkButton(
            header,
            text="🔽",
            width=35,
            height=35,
            command=self.show_filter_menu,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            corner_radius=5
        )
        self.filter_btn.pack(side="right", padx=(10, 0))
        
        # Transactions list container
        transactions_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        transactions_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        
        # Store reference for refreshing
        self.transactions_list_container = transactions_frame
        
        # Load transactions
        self.load_transactions(transactions_frame)

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
        # txn: id(0), txn_num(1), cashier_id(2), total(3), tax(4), discount(5), payment(6), order_type(7), created_at(8), username(9), full_name(10)
        date_str = self.format_date_mnl(txn[8]) # Index 8
        ctk.CTkLabel(h_inner, text=f"#{txn[1]}", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkLabel(h_inner, text=date_str, font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="right")
        
        # Bottom Row: Cashier & Method & Type
        h_row2 = ctk.CTkFrame(header, fg_color="transparent")
        h_row2.pack(fill="x", padx=15, pady=(0, 15))
        
        cashier_name = txn[10] if txn[10] else (txn[9] or "Unknown") # Index 9/10
        ctk.CTkLabel(h_row2, text=f"Cashier: {cashier_name}", font=ctk.CTkFont(size=12)).pack(side="left")
        
        # Right side container for badges
        right_badges = ctk.CTkFrame(h_row2, fg_color="transparent")
        right_badges.pack(side="right")
        
        # Payment Method
        ctk.CTkLabel(right_badges, text=txn[6], font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["success"]).pack(side="right", padx=(10, 0))
        
        # Order Type
        order_type = txn[7] if txn[7] else "Regular"
        type_color = COLORS["info"] if order_type == "Dine In" else (COLORS["warning"] if order_type == "Take Out" else COLORS["text_secondary"])
        ctk.CTkLabel(right_badges, text=f"[{order_type}]", font=ctk.CTkFont(size=12, weight="bold"), text_color=type_color).pack(side="right")

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
        
        # Total Row
        r1 = ctk.CTkFrame(total_frame, fg_color="transparent")
        r1.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(r1, text="TOTAL", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(r1, text=f"{CURRENCY_SYMBOL}{display_total:.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["success"]).pack(side="right")
        
        # Payment Details (if available)
        if len(txn) > 11:
            pay_amt = txn[11] or 0
            change_amt = txn[12] or 0
            
            if pay_amt > 0:
                # Paid
                r2 = ctk.CTkFrame(total_frame, fg_color="transparent")
                r2.pack(fill="x", padx=15, pady=(0, 2))
                ctk.CTkLabel(r2, text=f"Paid ({txn[6]})", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="left")
                ctk.CTkLabel(r2, text=f"{CURRENCY_SYMBOL}{pay_amt:.2f}", font=ctk.CTkFont(size=12)).pack(side="right")
                
                # Change
                r3 = ctk.CTkFrame(total_frame, fg_color="transparent")
                r3.pack(fill="x", padx=15, pady=(0, 10))
                ctk.CTkLabel(r3, text="Change", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="left")
                ctk.CTkLabel(r3, text=f"{CURRENCY_SYMBOL}{change_amt:.2f}", font=ctk.CTkFont(size=12)).pack(side="right")
        
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

    def show_filter_menu(self):
        """Show filter dropdown menu"""
        import tkinter as tk
        
        menu = tk.Menu(self.filter_btn, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text_primary"],
                      activebackground=COLORS["primary"], activeforeground="white",
                      font=("Segoe UI", 10))
        
        # Cashier filter submenu
        cashier_menu = tk.Menu(menu, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text_primary"],
                              activebackground=COLORS["primary"], activeforeground="white",
                              font=("Segoe UI", 10))
        
        # Get all cashiers
        users = self.database.get_all_users()
        cashiers = [u for u in users if u[2] == "cashier"] + [u for u in users if u[2] == "admin"]
        
        cashier_menu.add_command(label="All Cashiers", command=lambda: self.filter_by_cashier(None))
        cashier_menu.add_separator()
        for cashier in cashiers:
            cashier_menu.add_command(
                label=f"{cashier[1]} ({cashier[3] or 'No name'})",
                command=lambda c=cashier: self.filter_by_cashier(c)
            )
        
        menu.add_cascade(label="👤 Select Cashier", menu=cashier_menu)
        menu.add_separator()
        
        # Order Type Filter
        type_menu = tk.Menu(menu, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text_primary"],
                              activebackground=COLORS["primary"], activeforeground="white",
                              font=("Segoe UI", 10))
        
        types = ["Regular", "Dine In", "Take Out"]
        type_menu.add_command(label="All Types", command=lambda: self.filter_by_order_type(None))
        type_menu.add_separator()
        for t in types:
             type_menu.add_command(label=t, command=lambda x=t: self.filter_by_order_type(x))
        
        menu.add_cascade(label="🍽️ Select Order Type", menu=type_menu)
        menu.add_separator()
        
        # Date range filters
        menu.add_command(label="📅 Recent (Last 7 days)", command=lambda: self.filter_by_date_range("recent"))
        menu.add_command(label="📅 Today", command=lambda: self.filter_by_date_range("today"))
        menu.add_command(label="📅 Yesterday", command=lambda: self.filter_by_date_range("yesterday"))
        menu.add_command(label="📅 Custom Date Range", command=self.show_custom_date_dialog)
        menu.add_separator()
        
        # Clear filter
        menu.add_command(label="✖️  Clear All Filters", command=self.clear_filters)
        
        # Get button position
        x = self.filter_btn.winfo_rootx()
        y = self.filter_btn.winfo_rooty() + self.filter_btn.winfo_height()
        menu.post(x, y)
    
    def filter_by_cashier(self, cashier):
        """Filter transactions by cashier"""
        if cashier is None:
            self.filter_cashier = None
            self.filter_btn.configure(text="🔽", fg_color=COLORS["primary"])
        else:
            self.filter_cashier = cashier[0]  # user_id
            self.filter_btn.configure(text="👤", fg_color=COLORS["info"])
        
        self.refresh_transactions()

    def filter_by_order_type(self, order_type):
        """Filter transactions by order type"""
        if order_type is None:
            self.filter_order_type = None
        else:
            self.filter_order_type = order_type
            self.filter_btn.configure(text="🍽️", fg_color=COLORS["info"])
        
        self.refresh_transactions()
    
    def filter_by_date_range(self, range_type):
        """Filter transactions by date range"""
        from datetime import datetime, timedelta
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if range_type == "recent":
            self.custom_start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            self.custom_end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            self.filter_date_range = "recent"
            self.filter_btn.configure(text="📅7", fg_color=COLORS["success"])
        elif range_type == "today":
            self.custom_start_date = today.strftime("%Y-%m-%d")
            self.custom_end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            self.filter_date_range = "today"
            self.filter_btn.configure(text="📅T", fg_color=COLORS["success"])
        elif range_type == "yesterday":
            yesterday = today - timedelta(days=1)
            self.custom_start_date = yesterday.strftime("%Y-%m-%d")
            self.custom_end_date = today.strftime("%Y-%m-%d")
            self.filter_date_range = "yesterday"
            self.filter_btn.configure(text="📅Y", fg_color=COLORS["success"])
        
        self.refresh_transactions()
    
    def show_custom_date_dialog(self):
        """Show custom date range picker dialog"""
        from datetime import datetime
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Custom Date Range")
        dialog.geometry("400x300")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 300) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        ctk.CTkLabel(
            dialog,
            text="📅 Select Date Range",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(20, 10))
        
        # Info
        ctk.CTkLabel(
            dialog,
            text="Enter dates in YYYY-MM-DD format",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 20))
        
        # Form
        form_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Start Date
        ctk.CTkLabel(
            form_frame,
            text="Start Date:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        start_date_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="2026-01-01",
            height=35,
            font=ctk.CTkFont(size=13)
        )
        start_date_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Set default to today
        today = datetime.now().strftime("%Y-%m-%d")
        start_date_entry.insert(0, today)
        
        # End Date
        ctk.CTkLabel(
            form_frame,
            text="End Date:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        end_date_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="2026-01-31",
            height=35,
            font=ctk.CTkFont(size=13)
        )
        end_date_entry.pack(fill="x", padx=20, pady=(0, 20))
        end_date_entry.insert(0, today)
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def apply_custom_range():
            start = start_date_entry.get().strip()
            end = end_date_entry.get().strip()
            
            # Validate date format
            try:
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            self.custom_start_date = start
            self.custom_end_date = end
            self.filter_date_range = "custom"
            self.filter_btn.configure(text="📅C", fg_color=COLORS["warning"])
            dialog.destroy()
            self.refresh_transactions()
        
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
            text="Apply",
            command=apply_custom_range,
            height=35,
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Bind Enter key
        end_date_entry.bind("<Return>", lambda e: apply_custom_range())
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_cashier = None
        self.filter_order_type = None
        self.filter_date_range = None
        self.custom_start_date = None
        self.custom_end_date = None
        self.filter_btn.configure(text="🔽", fg_color=COLORS["primary"])
        self.refresh_transactions()
    
    def refresh_transactions(self):
        """Refresh the transactions list with current filters"""
        # Clear and reload
        for widget in self.transactions_list_container.winfo_children():
            widget.destroy()
        self.load_transactions(self.transactions_list_container)
    
    def load_transactions(self, parent_frame):
        """Load and display transactions with filters applied"""
        # Scrollable area
        transactions_list = ctk.CTkScrollableFrame(
            parent_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"]
        )
        transactions_list.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid Configuration for Table Layout
        transactions_list.grid_columnconfigure(0, weight=2)
        transactions_list.grid_columnconfigure(1, weight=2)
        transactions_list.grid_columnconfigure(2, weight=2)
        transactions_list.grid_columnconfigure(3, weight=1)
        transactions_list.grid_columnconfigure(4, weight=1) # Type
        transactions_list.grid_columnconfigure(5, weight=1) # Total
        transactions_list.grid_columnconfigure(6, weight=1) # Action
        
        # Table Header
        headers = ["Ref #", "Date & Time", "Cashier", "Method", "Type", "Total", "Action"]
        for idx, h_text in enumerate(headers):
            ctk.CTkLabel(
                transactions_list,
                text=h_text,
                font=self.f_head, # Optimization
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=idx, sticky="ew", padx=5, pady=(0, 10))
        
        # Header Separator
        ctk.CTkFrame(transactions_list, height=2, fg_color=COLORS["primary"]).grid(row=1, column=0, columnspan=7, sticky="ew", pady=(0, 5))
        
        # Get transactions with filters
        transactions = self.get_filtered_transactions()
        
        if transactions:
            for i, txn in enumerate(transactions):
                row_idx = 2 + (i * 2)
                
                # Ref (1)
                ctk.CTkLabel(
                    transactions_list, text=txn[1], font=self.f_reg, text_color=COLORS["text_primary"]
                ).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
                
                # Date (9)
                date_str = self.format_date_mnl(txn[9])
                ctk.CTkLabel(
                    transactions_list, text=date_str, font=self.f_reg
                ).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)
                
                # Cashier (10)
                ctk.CTkLabel(
                    transactions_list, text=txn[10], font=self.f_reg
                ).grid(row=row_idx, column=2, sticky="w", padx=5, pady=5)
                
                # Method (6)
                ctk.CTkLabel(
                    transactions_list, text=txn[6], font=self.f_reg
                ).grid(row=row_idx, column=3, sticky="w", padx=5, pady=5)
                
                # Order Type (7)
                order_type = txn[7] if txn[7] else "Regular"
                type_color = COLORS["info"] if order_type == "Dine In" else (COLORS["warning"] if order_type == "Take Out" else COLORS["text_secondary"])
                ctk.CTkLabel(
                    transactions_list, 
                    text=f"• {order_type}", 
                    font=self.f_bold,
                    text_color=type_color
                ).grid(row=row_idx, column=4, sticky="w", padx=5, pady=5)
                
                # Total (3) - tax(4)
                display_total = txn[3] - (txn[4] or 0)
                ctk.CTkLabel(
                    transactions_list,
                    text=f"{CURRENCY_SYMBOL}{display_total:.2f}",
                    font=self.f_bold, # Optimization
                    text_color=COLORS["success"]
                ).grid(row=row_idx, column=5, sticky="e", padx=20, pady=5)
                
                # View Button (0 = id)
                ctk.CTkButton(
                    transactions_list,
                    text="View",
                    width=60,
                    height=24,
                    font=ctk.CTkFont(size=11),
                    fg_color=COLORS["secondary"],
                    command=lambda tid=txn[0]: self.show_transaction_details(tid)
                ).grid(row=row_idx, column=6, sticky="e", padx=5, pady=5)
                
                # Row Separator
                sep_idx = row_idx + 1
                ctk.CTkFrame(transactions_list, height=1, fg_color="#2c3e50").grid(row=sep_idx, column=0, columnspan=7, sticky="ew", pady=(0, 0))
        else:
            ctk.CTkLabel(
                transactions_list,
                text="No transactions found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).grid(row=2, column=0, columnspan=7, pady=50)
    
    def get_filtered_transactions(self):
        """Get transactions with current filters applied"""
        # Build SQL query with filters
        query = """
            SELECT t.id, t.transaction_number, t.cashier_id, t.total_amount, t.tax_amount,
                   t.discount_amount, t.payment_method, t.order_type, t.status, t.created_at, u.username
            FROM transactions t
            LEFT JOIN users u ON t.cashier_id = u.id
            WHERE 1=1
        """
        params = []
        
        # Apply cashier filter
        if self.filter_cashier:
            query += " AND t.cashier_id = ?"
            params.append(self.filter_cashier)
        
        # Apply order type filter
        if self.filter_order_type:
            query += " AND t.order_type = ?"
            params.append(self.filter_order_type)
        
        # Apply date range filter
        if self.filter_date_range and self.custom_start_date and self.custom_end_date:
            query += " AND DATE(t.created_at) >= ? AND DATE(t.created_at) < ?"
            params.append(self.custom_start_date)
            params.append(self.custom_end_date)
        
        # Limit to 30 for faster loading
        query += " ORDER BY t.created_at DESC LIMIT 30"
        
        self.database.cursor.execute(query, params)
        return self.database.cursor.fetchall()

    def show_calculate_dialog(self):
        """Show sales calculation and analysis dialog"""
        from datetime import datetime
        import json
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Sales Analysis & Calculation")
        dialog.geometry("700x750")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        x = (dialog.winfo_screenwidth() - 700) // 2
        y = (dialog.winfo_screenheight() - 750) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text="🧮 Sales Analysis & Calculation",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Date selection
        date_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=10)
        date_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            date_frame,
            text="Select Date to Analyze:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=20, pady=15)
        
        date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            width=150,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        date_entry.pack(side="left", padx=10, pady=15)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Results container
        results_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def calculate_sales():
            selected_date = date_entry.get().strip()
            
            # Validate date
            try:
                datetime.strptime(selected_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Clear previous results
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            # Get transactions for the date
            self.database.cursor.execute("""
                SELECT id, transaction_number, total_amount, tax_amount, created_at
                FROM transactions
                WHERE DATE(created_at) = ?
                ORDER BY created_at
            """, (selected_date,))
            
            transactions = self.database.cursor.fetchall()
            
            if not transactions:
                ctk.CTkLabel(
                    results_frame,
                    text=f"No transactions found for {selected_date}",
                    font=ctk.CTkFont(size=14),
                    text_color=COLORS["text_secondary"]
                ).pack(pady=50)
                return
            
            # Calculate total sales
            total_sales = sum(txn[2] - (txn[3] or 0) for txn in transactions)
            
            # Summary Section - Compact
            summary_frame = ctk.CTkFrame(results_frame, fg_color=COLORS["success"], corner_radius=8)
            summary_frame.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                summary_frame,
                text=f"💰 Total Sales: {CURRENCY_SYMBOL}{total_sales:.2f}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            ).pack(pady=10)
            
            ctk.CTkLabel(
                summary_frame,
                text=f"📊 {len(transactions)} Transactions",
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).pack(pady=(0, 10))
            
            # Analyze ingredients, add-ons, and stock deductions
            ingredients_used = {}  # {ingredient_name: {qty: total_qty, cost: total_cost}}
            addons_used = {}  # {addon_name: {qty: count, revenue: total}}
            stock_deductions = {}  # {product_name: qty}
            
            for txn in transactions:
                txn_id = txn[0]
                
                # Get transaction items
                self.database.cursor.execute("""
                    SELECT product_id, product_name, quantity, modifiers
                    FROM transaction_items
                    WHERE transaction_id = ?
                """, (txn_id,))
                
                items = self.database.cursor.fetchall()
                
                for item in items:
                    prod_id, prod_name, qty, mods_str = item
                    
                    # Track stock deductions
                    if prod_name not in stock_deductions:
                        stock_deductions[prod_name] = 0
                    stock_deductions[prod_name] += qty
                    
                    # Get ingredients for this product
                    try:
                        ingredients = self.database.get_product_ingredients(prod_id)
                        for ing in ingredients:
                            ing_name = ing[2]
                            qty_per_unit = ing[3]
                            unit_price = ing[4]
                            
                            total_qty_used = qty_per_unit * qty
                            total_cost = unit_price * total_qty_used
                            
                            if ing_name not in ingredients_used:
                                ingredients_used[ing_name] = {'qty': 0, 'cost': 0}
                            
                            ingredients_used[ing_name]['qty'] += total_qty_used
                            ingredients_used[ing_name]['cost'] += total_cost
                    except:
                        pass
                    
                    # Parse modifiers/add-ons
                    if mods_str:
                        try:
                            mods_list = json.loads(mods_str)
                            for mod in mods_list:
                                if isinstance(mod, dict):
                                    mod_name = mod.get('name', 'Unknown')
                                    mod_qty = mod.get('quantity', 1)
                                    mod_price = mod.get('price', 0)
                                    
                                    if mod_name not in addons_used:
                                        addons_used[mod_name] = {'qty': 0, 'revenue': 0}
                                    
                                    addons_used[mod_name]['qty'] += mod_qty
                                    addons_used[mod_name]['revenue'] += mod_price * mod_qty
                        except:
                            pass
            
            # Display Ingredients Used - Compact
            if ingredients_used:
                ctk.CTkLabel(
                    results_frame,
                    text="🥫 Ingredients Used",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["info"]
                ).pack(anchor="w", pady=(5, 5))
                
                ing_frame = ctk.CTkFrame(results_frame, fg_color=COLORS["card_bg"], corner_radius=8)
                ing_frame.pack(fill="x", pady=(0, 10))
                
                for ing_name, data in sorted(ingredients_used.items()):
                    row = ctk.CTkFrame(ing_frame, fg_color="transparent", height=25)
                    row.pack(fill="x", padx=8, pady=2)
                    row.pack_propagate(False)
                    
                    ctk.CTkLabel(
                        row,
                        text=f"• {ing_name}",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_primary"]
                    ).pack(side="left", padx=5)
                    
                    ctk.CTkLabel(
                        row,
                        text=f"{data['qty']:g} qty | {CURRENCY_SYMBOL}{data['cost']:.2f}",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_secondary"]
                    ).pack(side="right", padx=5)
            
            # Display Add-ons Used - Compact
            if addons_used:
                ctk.CTkLabel(
                    results_frame,
                    text="➕ Add-ons / Modifiers",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["warning"]
                ).pack(anchor="w", pady=(5, 5))
                
                addon_frame = ctk.CTkFrame(results_frame, fg_color=COLORS["card_bg"], corner_radius=8)
                addon_frame.pack(fill="x", pady=(0, 10))
                
                for addon_name, data in sorted(addons_used.items()):
                    row = ctk.CTkFrame(addon_frame, fg_color="transparent", height=25)
                    row.pack(fill="x", padx=8, pady=2)
                    row.pack_propagate(False)
                    
                    ctk.CTkLabel(
                        row,
                        text=f"• {addon_name}",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_primary"]
                    ).pack(side="left", padx=5)
                    
                    ctk.CTkLabel(
                        row,
                        text=f"{data['qty']}x | {CURRENCY_SYMBOL}{data['revenue']:.2f}",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_secondary"]
                    ).pack(side="right", padx=5)
            
            # Display Stock Deductions - Compact
            if stock_deductions:
                ctk.CTkLabel(
                    results_frame,
                    text="📦 Products Sold",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["danger"]
                ).pack(anchor="w", pady=(5, 5))
                
                stock_frame = ctk.CTkFrame(results_frame, fg_color=COLORS["card_bg"], corner_radius=8)
                stock_frame.pack(fill="x", pady=(0, 10))
                
                for prod_name, qty in sorted(stock_deductions.items()):
                    row = ctk.CTkFrame(stock_frame, fg_color="transparent", height=25)
                    row.pack(fill="x", padx=8, pady=2)
                    row.pack_propagate(False)
                    
                    ctk.CTkLabel(
                        row,
                        text=f"• {prod_name}",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_primary"]
                    ).pack(side="left", padx=5)
                    
                    ctk.CTkLabel(
                        row,
                        text=f"{qty} units",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_secondary"]
                    ).pack(side="right", padx=5)
        
        # Calculate button
        ctk.CTkButton(
            date_frame,
            text="Calculate",
            command=calculate_sales,
            height=35,
            width=120,
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10, pady=15)
        
        # Close button
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            width=150,
            height=35,
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=15)
        
        # Auto-calculate for today
        calculate_sales()

