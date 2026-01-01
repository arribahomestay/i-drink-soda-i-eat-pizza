"""
Payment dialog for cashier view
Handles payment processing and transaction completion
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config import COLORS, CURRENCY_SYMBOL, TAX_RATE
from receipt_renderer import ReceiptRenderer


class PaymentDialog:
    def __init__(self, parent, database, user_data, cart_items, total, subtotal, tax):
        self.parent = parent
        self.database = database
        self.user_data = user_data
        self.cart_items = cart_items
        self.total = total
        self.subtotal = subtotal
        self.tax = tax
    
    def show(self, on_success_callback):
        """Show payment dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Payment")
        dialog.geometry("500x650")
        dialog.configure(fg_color=COLORS["dark"])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        self.center_window(dialog, 500, 650)
        
        # Title
        ctk.CTkLabel(
            dialog,
            text="💳 Payment",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=20)
        
        # Summary
        summary_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=15)
        summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            summary_frame,
            text=f"Subtotal: {CURRENCY_SYMBOL}{self.subtotal:.2f}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(15, 5), padx=20, anchor="w")
        
        ctk.CTkLabel(
            summary_frame,
            text=f"TOTAL: {CURRENCY_SYMBOL}{self.total:.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["success"]
        ).pack(pady=(5, 15), padx=20, anchor="w")
        
        # Payment method
        payment_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card_bg"], corner_radius=15)
        payment_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            payment_frame,
            text="Payment Method",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        payment_method = ctk.StringVar(value="Cash")
        
        cash_radio = ctk.CTkRadioButton(
            payment_frame,
            text="💵 Cash",
            variable=payment_method,
            value="Cash",
            font=ctk.CTkFont(size=14),
            radiobutton_width=20,
            radiobutton_height=20
        )
        cash_radio.pack(pady=5, padx=20, anchor="w")
        
        gcash_radio = ctk.CTkRadioButton(
            payment_frame,
            text="📱 GCash",
            variable=payment_method,
            value="GCash",
            font=ctk.CTkFont(size=14),
            radiobutton_width=20,
            radiobutton_height=20
        )
        gcash_radio.pack(pady=5, padx=20, anchor="w")
        
        # Amount tendered (for cash)
        amount_frame = ctk.CTkFrame(payment_frame, fg_color="transparent")
        amount_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        ctk.CTkLabel(
            amount_frame,
            text="Amount Tendered:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 5))
        
        amount_entry = ctk.CTkEntry(
            amount_frame,
            height=40,
            font=ctk.CTkFont(size=16),
            placeholder_text=f"Enter amount (min: {CURRENCY_SYMBOL}{self.total:.2f})"
        )
        amount_entry.pack(fill="x")
        amount_entry.insert(0, f"{self.total:.2f}")
        
        # Change display
        change_label = ctk.CTkLabel(
            payment_frame,
            text=f"Change: {CURRENCY_SYMBOL}0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["info"]
        )
        change_label.pack(pady=(10, 15), padx=20)
        
        def calculate_change(*args):
            """Calculate change"""
            try:
                tendered = float(amount_entry.get())
                change = tendered - self.total
                if change >= 0:
                    change_label.configure(
                        text=f"Change: {CURRENCY_SYMBOL}{change:.2f}",
                        text_color=COLORS["success"]
                    )
                else:
                    change_label.configure(
                        text=f"Insufficient: {CURRENCY_SYMBOL}{abs(change):.2f}",
                        text_color=COLORS["danger"]
                    )
            except:
                change_label.configure(
                    text="Change: Invalid amount",
                    text_color=COLORS["danger"]
                )
        
        amount_entry.bind("<KeyRelease>", calculate_change)
        
        def process_payment():
            """Process the payment"""
            method = payment_method.get()
            
            try:
                if method == "Cash":
                    tendered = float(amount_entry.get())
                    if tendered < self.total:
                        messagebox.showerror("Insufficient Amount", "Amount tendered is less than total")
                        return
                    change = tendered - self.total
                else:  # GCash
                    tendered = self.total
                    change = 0
                
                # Create transaction
                # Prepare items for database
                items_for_db = []
                for item in self.cart_items:
                    items_for_db.append({
                        'id': item['product_id'],
                        'name': item.get('raw_name', item['name'].split('\n')[0]),
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'variant_id': item.get('selected_variant', {}).get('id') if isinstance(item.get('selected_variant'), dict) else None,
                        'variant_name': item.get('selected_variant', {}).get('name') if isinstance(item.get('selected_variant'), dict) else None,
                        'modifiers': None, # Default
                        'selected_modifiers': item.get('selected_modifiers') # Pass full objects for stock logic
                    })
                    
                    # Serialize modifiers to JSON if present
                    if item.get('selected_modifiers'):
                        import json
                        items_for_db[-1]['modifiers'] = json.dumps(item['selected_modifiers'])
                
                # Generate transaction number
                transaction_number = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Save transaction
                transaction_id = self.database.add_transaction_with_payment(
                    transaction_number=transaction_number,
                    cashier_id=self.user_data['id'],
                    items=items_for_db,
                    payment_method=method,
                    payment_amount=tendered,
                    change_amount=change,
                    tax_rate=TAX_RATE * 100
                )
                
                # Generate receipt
                settings = self.database.get_receipt_settings()
                renderer = ReceiptRenderer(settings)
                
                # Construct transaction dummy for receipt
                t_dummy = [
                    transaction_id, transaction_number, self.user_data['id'],
                    self.total, self.tax, 0, method, tendered,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.user_data['full_name']
                ]
                
                receipt_file = renderer.save_receipt(t_dummy, self.cart_items, folder="receipts")
                
                # Log activity
                self.database.log_activity(
                    self.user_data['id'],
                    self.user_data['username'],
                    "SALE_COMPLETED",
                    f"Transaction {transaction_number} - {method} - {CURRENCY_SYMBOL}{self.total:.2f}"
                )
                
                dialog.destroy()
                
                messagebox.showinfo(
                    "Success",
                    f"Transaction completed!\n\n" +
                    f"Transaction #: {transaction_number}\n" +
                    f"Total: {CURRENCY_SYMBOL}{self.total:.2f}\n" +
                    f"Payment: {method}\n" +
                    f"Tendered: {CURRENCY_SYMBOL}{tendered:.2f}\n" +
                    f"Change: {CURRENCY_SYMBOL}{change:.2f}\n\n" +
                    f"Receipt saved: {receipt_file}"
                )
                
                # Call success callback
                on_success_callback()
                
            except Exception as e:
                messagebox.showerror("Error", f"Transaction failed: {str(e)}")
        
        # Bind Enter key to process payment
        amount_entry.bind("<Return>", lambda e: process_payment())
        
        # Focus amount entry automatically
        dialog.after(100, lambda: amount_entry.focus_set())
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="Complete Payment",
            command=process_payment,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#27ae60",
            corner_radius=10
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def center_window(self, window, width, height):
        """Center a window on screen"""
        window.update_idletasks()
        try:
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
        except:
            screen_width = 1920
            screen_height = 1080
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
