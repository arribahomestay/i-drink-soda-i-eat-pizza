from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from config import CURRENCY_SYMBOL

class ReceiptRenderer:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.paper_width = 400  # pixels (approx 58mm/80mm printer @ 200dpi)
        self.padding = 20
        self.line_spacing = 6
        
        # Load fonts - try to find a monospace font
        try:
            # Explicit Windows font paths are safer
            font_path = "C:/Windows/Fonts/"
            if os.path.exists(font_path + "arial.ttf"):
                self.font_regular = ImageFont.truetype(font_path + "arial.ttf", 16)
                self.font_bold = ImageFont.truetype(font_path + "arialbd.ttf", 16)
                self.font_large = ImageFont.truetype(font_path + "arialbd.ttf", 24)
                
                if os.path.exists(font_path + "consola.ttf"):
                    self.font_mono = ImageFont.truetype(font_path + "consola.ttf", 14)
                else:
                    self.font_mono = self.font_regular
            else:
                # Try generic names
                self.font_regular = ImageFont.truetype("arial.ttf", 16)
                self.font_bold = ImageFont.truetype("arialbd.ttf", 16)
                self.font_large = ImageFont.truetype("arialbd.ttf", 24)
                self.font_mono = ImageFont.truetype("consola.ttf", 14) 
        except Exception as e:
            print(f"Font loading error: {e}")
            # Fallback
            self.font_regular = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_mono = ImageFont.load_default()

    def generate_image(self, transaction, items, preview=False):
        """Generate receipt image"""
        # Unpack settings
        store_name = str(self.settings[1]) if len(self.settings) > 1 and self.settings[1] else "My POS Store"
        store_address = str(self.settings[2]) if len(self.settings) > 2 and self.settings[2] else ""
        store_phone = str(self.settings[3]) if len(self.settings) > 3 and self.settings[3] else ""
        store_email = str(self.settings[4]) if len(self.settings) > 4 and self.settings[4] else ""
        footer_msg = str(self.settings[6]) if len(self.settings) > 6 and self.settings[6] else "Thank you!"
        
        # Virtual Canvas to calculate height first
        dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        
        y = self.padding
        
        # Prepare items list
        if preview:
            # Dummy items for preview
            items = [
                {'name': 'Double Cheese Burger', 'quantity': 1, 'price': 150.00, 'subtotal': 150.00, 'variants': {'name': 'Large'}, 'modifiers': [{'name': 'Extra Cheese', 'price': 20.0}]},
                {'name': 'Coke Zero', 'quantity': 2, 'price': 50.00, 'subtotal': 100.00}
            ]

        # --- HEIGHT CALCULATION PASS ---
        # We estimate height accurately by simulating drawing
        
        # Header
        y += 30 # Store Name
        if store_address: y += 20
        if store_phone: y += 20
        if store_email: y += 20
        y += 20 # Divider
        
        # Transaction Info
        y += 60 # Date, Txn ID, Cashier
        y += 20 # Divider
        
        # Items
        items_to_draw = items or []
        for item in items_to_draw:
            # Wrapped text simulation could go here, for now assume 1 line per item + 1 line for details
            y += 40 
            if item.get('variants') or item.get('modifiers'):
                # Add extra space for details
                if item.get('variants'): y += 20
                for mod in item.get('modifiers', []): y += 20
                
        y += 20 # Divider
        
        # Totals
        y += 80 # Subtotal, Tax, Total
        y += 40 # Payment info
        
        # Footer
        y += 20 # Divider
        y += 40 # Footer msg
        y += 40 # Barcode space
        
        total_height = y + self.padding

        # --- DRAWING PASS ---
        img = Image.new("RGB", (self.paper_width, total_height), "white")
        draw = ImageDraw.Draw(img)
        
        y = self.padding
        width = self.paper_width
        
        def draw_centered(text, font, y_pos):
            try:
                # Pillow 10+ uses textbbox
                left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                w = right - left
            except:
                # Older Pillow
                w, h = draw.textsize(text, font=font)
            draw.text(((width - w) / 2, y_pos), text, font=font, fill="black")
            return y_pos

        def draw_row(left_text, right_text, font, y_pos, color="black"):
            try:
                left_l, left_t, left_r, left_b = draw.textbbox((0, 0), right_text, font=font)
                rw = left_r - left_l
            except:
                rw, rh = draw.textsize(right_text, font=font)
            
            draw.text((self.padding, y_pos), left_text, font=font, fill=color)
            draw.text((width - self.padding - rw, y_pos), right_text, font=font, fill=color)

        # 1. Header
        draw_centered(store_name, self.font_large, y)
        y += 30
        
        if store_address:
            draw_centered(store_address, self.font_regular, y)
            y += 20
            
        if store_phone:
            draw_centered(f"Tel: {store_phone}", self.font_regular, y)
            y += 20
        
        if store_email:
            draw_centered(f"Email: {store_email}", self.font_regular, y)
            y += 20
            
        # Divider
        draw.line([(self.padding, y + 10), (width - self.padding, y + 10)], fill="black", width=2)
        y += 20
        
        # 2. Transaction Details
        if preview:
            txn_id = "PREVIEW-123456"
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cashier = "Admin"
        else:
            txn_id = transaction[1]
            date_str = transaction[8][:16]
            cashier = transaction[9] if len(transaction) > 9 else "Cashier"
            
        draw_row(f"Date: {date_str}", "", self.font_mono, y)
        y += 20
        draw_row(f"Ref: {txn_id}", "", self.font_mono, y)
        y += 20
        draw_row(f"Cashier: {cashier}", "", self.font_mono, y)
        y += 20
        
        # Divider
        draw.line([(self.padding, y + 10), (width - self.padding, y + 10)], fill="black", width=1)
        y += 20
        
        # 3. Items
        # 3. Items
        items_to_draw = items or []

        for item in items_to_draw:
            name = item['name'].split('\n')[0] # Main name
            
            # Determine Modifiers
            modifiers = item.get('selected_modifiers') or item.get('modifiers')

            # Draw Name
            draw.text((self.padding, y), name, font=self.font_bold, fill="black")
            y += 20
            
            # Draw Qty/Price Row
            if modifiers and item.get('base_price'):
                 # Breakdown mode: Show base price + subtotal of base
                 qty_price = f"{item['quantity']} x {item['base_price']:.2f}"
                 base_subtotal = item['quantity'] * float(item['base_price'])
                 draw_row(f"  {qty_price}", f"{base_subtotal:.2f}", self.font_regular, y)
            else:
                 # Standard rolled-up mode
                 qty_price = f"{item['quantity']} x {item['price']:.2f}"
                 draw_row(f"  {qty_price}", f"{item['subtotal']:.2f}", self.font_regular, y)
            
            y += 20

            # Draw Variants/Modifiers details if they exist
            if item.get('variants') or modifiers:
                # Variants
                if item.get('variants'):
                    v = item['variants']
                    v_name = v if isinstance(v, str) else v.get('name', '')
                    draw.text((self.padding + 20, y), f"• {v_name}", font=self.font_mono, fill="#444444")
                    y += 18
                
                # Modifiers
                if modifiers:
                    for mod in modifiers:
                        m_name = mod['name'] if isinstance(mod, dict) else mod
                        # Price calculation
                        m_price = 0
                        if isinstance(mod, dict):
                            m_price = mod.get('price', 0) * mod.get('quantity', 1)
                            # Append quantity if > 1
                            if mod.get('quantity', 1) > 1:
                                m_name = f"{mod.get('quantity')}x {m_name}"

                        mod_str = f"+ {m_name}"
                        # Calculate total modification cost for this line
                        mod_line_total = item['quantity'] * m_price
                        
                        if m_price > 0:
                            mod_str += f" ({m_price:.2f})"
                            # Draw Mod Subtotal on the right
                            draw_row(f"      {mod_str}", f"{mod_line_total:.2f}", self.font_mono, y, color="#444444")
                        else:
                            draw.text((self.padding + 20, y), mod_str, font=self.font_mono, fill="#444444")
                        y += 18
            
            y += 5 # Spacing between items

        # Divider (Double line for total)
        y += 5
        draw.line([(self.padding, y), (width - self.padding, y)], fill="black", width=1)
        draw.line([(self.padding, y+3), (width - self.padding, y+3)], fill="black", width=1)
        y += 15
        
        # 4. Totals
        if preview:
            subtotal = 270.00
            total = 270.00
            payment = "Cash"
            pay_amt = 300.00
            change = 30.00
        else:
            # Recalculate or use transaction data
            subtotal = sum(i['subtotal'] for i in items_to_draw)
            total = transaction[3]
            payment = transaction[6]
            pay_amt = transaction[7] if len(transaction) > 7 else 0
            change = pay_amt - total if pay_amt > 0 else 0
        
        draw_row("Subtotal:", f"{subtotal:.2f}", self.font_regular, y)
        y += 25
        draw_row("TOTAL:", f"{CURRENCY_SYMBOL}{total:.2f}", self.font_large, y)
        y += 35
        
        if not preview and pay_amt > 0:
             draw_row(f"Paid ({payment}):", f"{pay_amt:.2f}", self.font_regular, y)
             y += 20
             draw_row("Change:", f"{change:.2f}", self.font_regular, y)
             y += 20
        
        # Footer
        y += 10
        draw_centered(footer_msg, self.font_regular, y)
        y += 30
        draw_centered("*** THANK YOU ***", self.font_bold, y)
        
        return img

    def save_receipt(self, transaction, items, folder="receipts"):
        """Save receipt as BMP"""
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        img = self.generate_image(transaction, items)
        
        # Use Transaction ID for filename (e.g., RCP_001.png)
        try:
            # transaction[0] is the auto-increment ID
            txn_id_int = int(transaction[0])
            filename = f"RCP_{txn_id_int:03d}.png"
        except:
            # Fallback to transaction number string if ID is not int
            filename = f"receipt_{transaction[1]}.png"
        path = os.path.join(folder, filename)
        img.save(path, "PNG")
        return path
