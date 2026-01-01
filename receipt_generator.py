"""
Receipt Generator for POS System
Generates receipts in text format for thermal printers
"""
from datetime import datetime
from config import CURRENCY_SYMBOL


class ReceiptGenerator:
    def __init__(self, database):
        self.database = database
        self.settings = self.database.get_receipt_settings()
    
    def generate_receipt_text(self, transaction_id, payment_method, payment_amount, change_amount):
        """Generate receipt as text"""
        # Get transaction details
        transaction, items = self.database.get_transaction_details(transaction_id)
        
        if not transaction:
            return "Transaction not found"
        
        # Get settings
        settings = self.settings or {}
        store_name = str(settings[1]) if len(settings) > 1 and settings[1] else "My POS Store"
        store_address = str(settings[2]) if len(settings) > 2 and settings[2] else ""
        store_phone = str(settings[3]) if len(settings) > 3 and settings[3] else ""
        store_email = str(settings[4]) if len(settings) > 4 and settings[4] else ""
        tax_rate = settings[5] if len(settings) > 5 and settings[5] is not None else 0
        receipt_footer = str(settings[6]) if len(settings) > 6 and settings[6] else "Thank you for your purchase!"
        paper_width = settings[8] if len(settings) > 8 and settings[8] else 80
        
        # Build receipt
        receipt = []
        width = paper_width // 2  # Character width
        
        # Header
        receipt.append("=" * width)
        receipt.append(store_name.center(width))
        if store_address:
            receipt.append(store_address.center(width))
        if store_phone:
            receipt.append(f"Tel: {store_phone}".center(width))
        if store_email:
            receipt.append(store_email.center(width))
        receipt.append("=" * width)
        receipt.append("")
        
        # Transaction info
        receipt.append(f"Receipt #: {transaction[1]}")
        receipt.append(f"Date: {transaction[8][:19]}")
        receipt.append(f"Cashier: {transaction[10] if len(transaction) > 10 else 'N/A'}")
        receipt.append(f"Payment: {payment_method}")
        receipt.append("-" * width)
        receipt.append("")
        
        # Items
        receipt.append("ITEMS")
        receipt.append("-" * width)
        
        for item in items:
            # item: id, transaction_id, product_id, product_name, quantity, unit_price, subtotal
            name = item[3][:width-15]  # Truncate if too long
            qty = item[4]
            price = item[5]
            subtotal = item[6]
            
            receipt.append(f"{name}")
            receipt.append(f"  {qty} x {CURRENCY_SYMBOL}{price:.2f}".ljust(width-10) + f"{CURRENCY_SYMBOL}{subtotal:.2f}".rjust(10))
        
        receipt.append("-" * width)
        receipt.append("")
        
        # Totals
        subtotal = sum(item[6] for item in items)
        tax_amount = transaction[4]
        discount = transaction[5]
        total = transaction[3]
        
        receipt.append(f"Subtotal:".ljust(width-10) + f"{CURRENCY_SYMBOL}{subtotal:.2f}".rjust(10))
        
        if tax_amount > 0:
            receipt.append(f"Tax ({tax_rate}%):".ljust(width-10) + f"{CURRENCY_SYMBOL}{tax_amount:.2f}".rjust(10))
        
        if discount > 0:
            receipt.append(f"Discount:".ljust(width-10) + f"-{CURRENCY_SYMBOL}{discount:.2f}".rjust(10))
        
        receipt.append("=" * width)
        receipt.append(f"TOTAL:".ljust(width-10) + f"{CURRENCY_SYMBOL}{total:.2f}".rjust(10))
        receipt.append("=" * width)
        receipt.append("")
        
        # Payment details
        receipt.append(f"Payment ({payment_method}):".ljust(width-10) + f"{CURRENCY_SYMBOL}{payment_amount:.2f}".rjust(10))
        receipt.append(f"Change:".ljust(width-10) + f"{CURRENCY_SYMBOL}{change_amount:.2f}".rjust(10))
        receipt.append("")
        
        # Footer
        receipt.append("=" * width)
        receipt.append(receipt_footer.center(width))
        receipt.append("=" * width)
        receipt.append("")
        receipt.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(width))
        receipt.append("")
        
        return "\n".join(receipt)
    
    def save_receipt_to_file(self, transaction_id, payment_method, payment_amount, change_amount, filename=None):
        """Save receipt to text file"""
        receipt_text = self.generate_receipt_text(transaction_id, payment_method, payment_amount, change_amount)
        
        if not filename:
            transaction, _ = self.database.get_transaction_details(transaction_id)
            filename = f"receipt_{transaction[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(receipt_text)
        
        return filename
    
    def print_receipt(self, transaction_id, payment_method, payment_amount, change_amount):
        """Print receipt (saves to file for now, can be extended for actual printing)"""
        filename = self.save_receipt_to_file(transaction_id, payment_method, payment_amount, change_amount)
        return filename
