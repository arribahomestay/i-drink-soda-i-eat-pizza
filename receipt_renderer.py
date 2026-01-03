from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from config import CURRENCY_SYMBOL

class ReceiptRenderer:
    def __init__(self, settings=None):
        self.settings = settings or {}
        # 80mm thermal printer - narrower width to prevent cropping
        # 280px ensures totals are fully visible with no cropping
        self.paper_width = 280  # pixels for 80mm thermal printer
        self.padding = 8  # Minimal padding
        self.line_spacing = 5  # Increased for better readability
        
        # Load fonts - LARGER & ALL BOLD for maximum darkness
        try:
            # Explicit Windows font paths are safer
            font_path = "C:/Windows/Fonts/"
            if os.path.exists(font_path + "arialbd.ttf"):
                # LARGER BOLD fonts for maximum visibility (increased by 2-3px)
                self.font_regular = ImageFont.truetype(font_path + "arialbd.ttf", 13)  # Was 11, now 13
                self.font_bold = ImageFont.truetype(font_path + "arialbd.ttf", 14)     # Was 12, now 14
                self.font_large = ImageFont.truetype(font_path + "arialbd.ttf", 18)    # Was 16, now 18
                
                if os.path.exists(font_path + "consolab.ttf"):
                    self.font_mono = ImageFont.truetype(font_path + "consolab.ttf", 12)  # Was 10, now 12
                else:
                    self.font_mono = ImageFont.truetype(font_path + "arialbd.ttf", 12)  # Was 10, now 12
            else:
                # Try generic names - all bold, larger
                self.font_regular = ImageFont.truetype("arialbd.ttf", 13)
                self.font_bold = ImageFont.truetype("arialbd.ttf", 14)
                self.font_large = ImageFont.truetype("arialbd.ttf", 18)
                self.font_mono = ImageFont.truetype("arialbd.ttf", 12) 
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
        val = str(self.settings[1]) if len(self.settings) > 1 and self.settings[1] else ""
        store_name = val if val.strip() else "My POS Store"
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
        # Add logo height if it exists
        if self.settings and len(self.settings) > 7 and self.settings[7]:
             if os.path.exists(str(self.settings[7])):
                  y += 115 # Max height (100) + padding (15)

        y += 30 # Store Name
        if store_address: y += 20
        if store_phone: y += 20
        if store_email: y += 20
        y += 20 # Divider
        
        # Transaction Info
        # Date, Txn ID, Cashier (20x3 = 60)
        y += 60
        # Add space for Order Type if not Regular
        order_type_check = "Regular"
        if not preview and transaction and len(transaction) > 10:
            order_type_check = transaction[10]
        elif preview:
             order_type_check = "Dine In" # Preview defaults to show it
             
        if order_type_check and order_type_check.lower() != "normal":
             y += 20
        y += 20 # Divider
        
        # Items
        items_to_draw = items or []
        for item in items_to_draw:
            # Wrapped text simulation could go here, for now assume 1 line per item + 1 line for details
            y += 40 
            # Use selected_modifiers to match drawing logic
            mods = item.get('selected_modifiers') or item.get('modifiers') or []
            if mods:
                 # Estimate height (safe upper bound)
                 for mod in mods: y += 20
                
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

        # 1. Logo (if exists)
        logo_path = str(self.settings[7]) if len(self.settings) > 7 and self.settings[7] else ""
        if logo_path and os.path.exists(logo_path):
            try:
                # Load logo
                logo_img = Image.open(logo_path)
                
                # Convert to black and white for thermal printer
                logo_img = logo_img.convert('L')  # Convert to grayscale
                
                # Apply threshold to make it pure black and white
                threshold = 128
                logo_img = logo_img.point(lambda x: 0 if x < threshold else 255, '1')
                
                # Resize to fit receipt width (max height 100px)
                max_logo_height = 100
                max_logo_width = width - (self.padding * 2)
                
                # Calculate new size maintaining aspect ratio
                aspect = logo_img.width / logo_img.height
                if logo_img.height > max_logo_height:
                    new_height = max_logo_height
                    new_width = int(new_height * aspect)
                else:
                    new_height = logo_img.height
                    new_width = logo_img.width
                
                # Ensure width doesn't exceed max
                if new_width > max_logo_width:
                    new_width = max_logo_width
                    new_height = int(new_width / aspect)
                
                logo_img = logo_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center the logo
                logo_x = (width - new_width) // 2
                img.paste(logo_img, (logo_x, y))
                
                y += new_height + 15  # Add spacing after logo
            except Exception as e:
                print(f"Logo error: {e}")
                # Continue without logo if there's an error
        
        # 2. Header (Store Name)
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
            date_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            cashier = "Admin"
            order_type = "Dine In"
        else:
            txn_id = transaction[1]
            try:
                dt_obj = datetime.strptime(transaction[8], "%Y-%m-%d %H:%M:%S")
                date_str = dt_obj.strftime("%Y-%m-%d %I:%M %p")
            except:
                date_str = str(transaction[8])
                
            # Use Full Name (Index 10) instead of Username (Index 9)
            cashier = transaction[10] if len(transaction) > 10 and transaction[10] else (transaction[9] if len(transaction) > 9 else "Cashier")
            order_type = transaction[7] if len(transaction) > 7 else "Regular"
            
        draw_row(f"Date: {date_str}", "", self.font_mono, y)
        y += 20
        draw_row(f"Ref: {txn_id}", "", self.font_mono, y)
        y += 20
        draw_row(f"Cashier: {cashier}", "", self.font_mono, y)
        y += 20
        # Draw Order Type more prominently if possible, or just as a row
        if order_type and order_type.lower() != "normal":
             draw_row(f"Type: {order_type.upper()}", "", self.font_bold, y) # Bold for emphasis
             y += 20
        
        # Divider
        draw.line([(self.padding, y + 10), (width - self.padding, y + 10)], fill="black", width=1)
        y += 20
        
        # 3. Items
        # 3. Items
        items_to_draw = items or []

        for item in items_to_draw:

            try:
                qty = int(item['quantity'])
            except: qty = 1
            try:
                price = float(item['price'])
            except: price = 0.0
            
            # Use base_price for display if available (to show original price before mods)
            display_u_price = price
            if item.get('base_price'):
                try: display_u_price = float(item['base_price'])
                except: pass
            
            name = str(item['name']).split('\n')[0]
            
            # Base Subtotal (Qty * Base Price)
            base_subtotal = qty * display_u_price
            
            # Row 1: Name only
            draw_row(name, "", self.font_bold, y)
            y += 20
            # Row 2: Qty x Base Price ..... Base Subtotal
            draw_row(f"{qty} x {display_u_price:.2f}", f"{base_subtotal:.2f}", self.font_mono, y)
            y += 20
            
            item_modifiers_total = 0
            
            # Modifiers
            if item.get('selected_modifiers'):
                # Aggregate modifiers by name and price to avoid duplicates
                agg_mods = {}
                for mod in item['selected_modifiers']:
                    if isinstance(mod, dict):
                        mn = mod.get('name', 'Modifier')
                        try: mq = int(mod.get('quantity', 1)) 
                        except: mq = 1
                        try: mp = float(mod.get('price', 0))
                        except: mp = 0.0
                    else:
                        mn = str(mod)
                        mq = 1
                        mp = 0.0
                    
                    key = (mn, mp)
                    agg_mods[key] = agg_mods.get(key, 0) + mq
                
                for (m_name, m_price), m_qty in agg_mods.items():
                    if m_qty > 1:
                        display_name = f"{m_qty}x {m_name}"
                    else:
                        display_name = m_name
                        
                    if m_price > 0:
                        m_total = m_qty * m_price
                        item_modifiers_total += m_total
                        draw_row(f" + {display_name}", f"{m_total:.2f}", self.font_mono, y)
                    else:
                        draw_row(f" + {display_name}", "", self.font_mono, y)
                    y += 20
            
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
            # Updated indices to match expected DB schema (11=Paid, 12=Change)
            try:
                pay_amt = float(transaction[11]) if len(transaction) > 11 else 0.0
                change = float(transaction[12]) if len(transaction) > 12 else 0.0
            except:
                pay_amt = 0.0
                change = 0.0
        
        draw_row("Subtotal:", f"{subtotal:.2f}", self.font_regular, y)
        y += 25
        draw_row("TOTAL:", f"{CURRENCY_SYMBOL}{total:.2f}", self.font_large, y)
        y += 35
        
        if pay_amt > 0:
             draw_row(f"Paid ({payment}):", f"{pay_amt:.2f}", self.font_regular, y)
             y += 20
             draw_row("Change:", f"{change:.2f}", self.font_regular, y)
             y += 20
        
        # Footer
        y += 10
        draw_centered(footer_msg, self.font_regular, y)
        
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
