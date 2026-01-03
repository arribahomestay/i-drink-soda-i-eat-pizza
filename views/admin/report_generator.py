
import csv
import json
from datetime import datetime, timedelta
import os

class DetailedReportGenerator:
    def __init__(self, database):
        self.db = database

    def generate_summary_report(self, report_type, output_format="html"):
        """
        Generates a 3-section summary: Products, Add-ons, Ingredients.
        """
        start_date, end_date = self._get_date_range(report_type)
        
        # Fetch Transactions
        if report_type == 'all':
             query = "SELECT id, created_at, order_type, total_amount FROM transactions"
             params = ()
        else:
             query = "SELECT id, created_at, order_type, total_amount FROM transactions WHERE DATE(created_at) BETWEEN ? AND ?"
             params = (start_date, end_date)
             
        self.db.cursor.execute(query, params)
        transactions = self.db.cursor.fetchall()
        
        # Data Containers
        products_sold = {} # Name -> Qty
        addons_sold = {}   # Name -> Qty
        ingredients_used = {} # Name -> Qty
        order_types = {} # Type -> Count
        total_revenue = 0.0
        
        # Pre-fetch maps
        # Product -> Ingredients
        ing_map = {}
        self.db.cursor.execute("""
            SELECT pi.product_id, p.name, pi.quantity 
            FROM product_ingredients pi
            JOIN products p ON pi.ingredient_id = p.id
        """)
        for row in self.db.cursor.fetchall():
            pid, name, qty = row
            if pid not in ing_map: ing_map[pid] = []
            ing_map[pid].append((name, qty))
            
        # Global Modifiers Map (Name -> LinkedIngredientName, Quantity)
        mod_map = {}
        self.db.cursor.execute("""
            SELECT m.name, p.name, COALESCE(m.deduct_quantity, 1)
            FROM global_modifiers m
            LEFT JOIN products p ON m.linked_product_id = p.id
        """)
        for row in self.db.cursor.fetchall():
            name, link, qty = row
            if link: mod_map[name] = (link, qty)
            
        # Process
        for txn in transactions:
            # Aggregate Order Type
            o_type = txn[2] if len(txn) > 2 else "Regular"
            if not o_type: o_type = "Regular"
            if not o_type: o_type = "Regular"
            order_types[o_type] = order_types.get(o_type, 0) + 1
            
            # Aggregate Revenue
            t_amt = txn[3] if len(txn) > 3 and txn[3] is not None else 0.0
            total_revenue += float(t_amt)
            
            items = self.db.get_transaction_items(txn[0])
            for item in items:
                # transaction_items columns: id, transaction_id, product_id, product_name, quantity, unit_price, subtotal, variant_id, variant_name, modifiers
                # Correct indices:
                item_id = item[0]
                txn_id = item[1]
                pid = item[2]           # product_id
                p_name = item[3]        # product_name (was incorrectly item[4])
                qty = item[4]           # quantity (was incorrectly item[6])
                unit_price = item[5]
                subtotal = item[6]
                variant_id = item[7] if len(item) > 7 else None
                variant_name = item[8] if len(item) > 8 else None
                mods_str = item[9] if len(item) > 9 else None  # modifiers (was incorrectly item[8])
                
                # 1. Product Count
                products_sold[p_name] = products_sold.get(p_name, 0) + qty
                
                # 2. Product Ingredients
                if pid in ing_map:
                    for ing_name, ing_qty in ing_map[pid]:
                        usage = ing_qty * qty
                        ingredients_used[ing_name] = ingredients_used.get(ing_name, 0) + usage
                
                # 3. Add-ons & Linked Ingredients
                if mods_str:
                    try:
                        # JSON Format
                        mods_list = json.loads(mods_str)
                        for mod in mods_list:
                            m_name = mod.get('name', 'Unknown')
                            m_qty = mod.get('quantity', 1)
                            
                            # Add-on Count
                            addons_sold[m_name] = addons_sold.get(m_name, 0) + m_qty
                            
                            # Linked Ingredient from JSON (Historical accuracy)
                            # If JSON has linked_product_id/name, use it? 
                            # The JSON dump from payment_dialog might not include resolved name of linked product easily unless we stuck it there.
                            # Checking PaymentDialog: it dumps 'selected_modifiers'.
                            # Modifier object usually has 'linked_product_id'.
                            # But we need Name. We can rely on mod_map fallback or lookup.
                            # For simplicity, use mod_map based on m_name
                            if m_name in mod_map:
                                link_name, link_qty = mod_map[m_name]
                                total_link = link_qty * m_qty
                                ingredients_used[link_name] = ingredients_used.get(link_name, 0) + total_link
                                
                    except (json.JSONDecodeError, TypeError):
                        # Legacy String Format (comma-separated)
                        for m_str in mods_str.split(", "):
                             m_clean = m_str.strip()
                             if m_clean:
                                 addons_sold[m_clean] = addons_sold.get(m_clean, 0) + 1
                                 if m_clean in mod_map:
                                     link_name, link_qty = mod_map[m_clean]
                                     ingredients_used[link_name] = ingredients_used.get(link_name, 0) + link_qty

        # Fetch Inventory with Tracking Mode & Availability
        try:
             self.db.cursor.execute("""
                SELECT name, category, stock, price, unit, use_stock_tracking, is_available 
                FROM products 
                ORDER BY category, name
             """)
        except:
             # Fallback for schema safety
             self.db.cursor.execute("SELECT name, category, stock, price, unit, 1, 1 FROM products ORDER BY category, name")
             
        inventory = self.db.cursor.fetchall()
        
        # Split Inventory
        inv_stock = []
        inv_avail = []
        for item in inventory:
             # item: name(0), cat(1), stock(2), price(3), unit(4), mode(5), avail(6)
             mode = item[5] if len(item) > 5 and item[5] is not None else 1
             if mode == 1:
                 inv_stock.append(item)
             else:
                 inv_avail.append(item)

        # Generate Output
        filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            'products': products_sold, 
            'addons': addons_sold, 
            'ingredients': ingredients_used, 
            'types': order_types, 
            'total_revenue': total_revenue,
            'inv_stock': inv_stock,
            'inv_avail': inv_avail
        }
        
        if output_format == 'pdf':
            return self._export_pdf(filename, data, start_date, end_date)
        
        path = f"{filename}.html"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #2c3e50; margin-top: 30px; background-color: #ecf0f1; padding: 10px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                th {{ background-color: #34495e; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .section {{ margin-bottom: 40px; }}
                .status-avail {{ color: green; font-weight: bold; }}
                .status-unavail {{ color: red; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>📊 Comprehensive Sales Summary</h1>
            <p><strong>Date Range:</strong> {start_date} to {end_date}</p>
            <p><strong>Generated On:</strong> {datetime.now().strftime('%B %d, %Y %I:%M %p')}</p>
            
            <div class="section">
                <h2>📋 Order Types</h2>
                <table>
                    <tr><th>Type</th><th>Count</th></tr>
                    {''.join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in sorted(order_types.items())])}
                </table>
            </div>
            
            <div class="section">
                <h2>🍔 Sold Items (Products)</h2>
                <table>
                    <tr><th>Product Name</th><th>Total Quantity Sold</th></tr>
                    {''.join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in sorted(products_sold.items())])}
                </table>
            </div>
            
            <div class="section">
                <h2>➕ Sold Add-ons (Modifiers)</h2>
                <table>
                    <tr><th>Add-on Name</th><th>Total Quantity Sold</th></tr>
                    {''.join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in sorted(addons_sold.items())])}
                </table>
            </div>
            
            <div class="section">
                <h2>🥗 Sold Ingredients (Inventory Usage)</h2>
                <table>
                    <tr><th>Ingredient Name</th><th>Total Quantity Used</th></tr>
                    {''.join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in sorted(ingredients_used.items())])}
                </table>
            </div>

            <div class="section">
                <h2>📦 Current Inventory (Stock Based)</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Product Name</th>
                        <th>Current Stock</th>
                        <th>Price</th>
                    </tr>
                    {''.join([f"<tr><td>{item[1]}</td><td>{item[0]}</td><td>{int(item[2])} {item[4]}</td><td>{item[3]:.2f}</td></tr>" for item in inv_stock])}
                </table>
            </div>
            
            <div class="section">
                <h2>🍽️ Product Availability (Made-to-Order)</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Product Name</th>
                        <th>Status</th>
                        <th>Price</th>
                    </tr>
                    {''.join([f"<tr><td>{item[1]}</td><td>{item[0]}</td><td class='{'status-avail' if (str(item[6])=='1' or str(item[6])=='True') else 'status-unavail'}'>{'Available' if (str(item[6])=='1' or str(item[6])=='True') else 'Not Available'}</td><td>{item[3]:.2f}</td></tr>" for item in inv_avail])}
                </table>
            </div>
            
        </body>
        
        # Helper for Inventory PDF
        def draw_inventory_stock_section(items):
            if not items: return
            # ... (Implementation in next block if needed, but I returned via PDF flow usually)


        </html>
        """
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return path

    def _export_pdf(self, filename, data, start, end):
        """Generate PDF report using FPDF with clean, organized tables"""
        try:
            from fpdf import FPDF
        except ImportError:
            return None
            
        class PDF(FPDF):
            def header(self):
                # Title
                self.set_font('Helvetica', 'B', 20)
                self.set_text_color(44, 62, 80)  # Dark blue-gray
                self.cell(0, 12, 'Sales Summary Report', align='C', new_x="LMARGIN", new_y="NEXT")
                
                # Subtitle
                self.set_font('Helvetica', '', 11)
                self.set_text_color(100, 100, 100)
                self.cell(0, 8, f'Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', align='C', new_x="LMARGIN", new_y="NEXT")
                
                # Line separator
                self.set_draw_color(52, 152, 219)  # Blue
                self.set_line_width(0.5)
                self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
                self.ln(8)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 9)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

        pdf = PDF()
        pdf.add_page()
        pdf.alias_nb_pages()
        
        # Period Info Box
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_fill_color(236, 240, 241)  # Light gray
        pdf.set_text_color(44, 62, 80)
        
        # Period + Total Revenue
        # Period + Total Revenue
        total_rev = data.get('total_revenue', 0.0)
        from config import CURRENCY_SYMBOL
        
        # Handle FPDF currency symbol limitation (Standard fonts don't support unicode symbols like Peso)
        symbol = CURRENCY_SYMBOL
        if symbol == "₱": 
            symbol = "P"
            
        info_text = f"  Report Period: {start} to {end}    |    Total Revenue: {symbol}{total_rev:,.2f}"
        
        pdf.cell(0, 10, info_text, fill=True, new_x="LMARGIN", new_y="NEXT", border=0)
        pdf.ln(8)

        # Helper to draw professional table
        def draw_section(title, items, emoji=""):
            if not items: 
                return

            # Section Title
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(52, 73, 94)  # Dark blue
            # Emojis not supported in standard fonts, remove them
            pdf.cell(0, 10, f"{title}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Table Header
            pdf.set_font("Helvetica", 'B', 11)
            pdf.set_fill_color(52, 152, 219)  # Blue header
            pdf.set_text_color(255, 255, 255)  # White text
            pdf.set_draw_color(52, 152, 219)  # Blue border
            
            pdf.cell(140, 10, "Item Name", border=1, fill=True, align='L')
            pdf.cell(40, 10, "Quantity", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
            
            # Table Rows
            pdf.set_font("Helvetica", '', 10)
            pdf.set_text_color(44, 62, 80)  # Dark text
            pdf.set_draw_color(189, 195, 199)  # Light gray borders
            
            # Alternate row colors for better readability
            row_num = 0
            for name, qty in sorted(items.items()):
                # Alternate background colors
                if row_num % 2 == 0:
                    pdf.set_fill_color(255, 255, 255)  # White
                else:
                    pdf.set_fill_color(249, 249, 249)  # Very light gray
                
                # Clean the name to handle special characters
                clean_name = str(name).encode('latin-1', 'replace').decode('latin-1')
                
                # Truncate long names if needed
                if len(clean_name) > 60:
                    clean_name = clean_name[:57] + "..."
                
                pdf.cell(140, 8, f"  {clean_name}", border=1, fill=True, align='L')
                pdf.cell(40, 8, f"{qty:g}", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
                row_num += 1
            
            # Summary row
            total_qty = sum(items.values())
            pdf.set_font("Helvetica", 'B', 10)
            pdf.set_fill_color(236, 240, 241)  # Light gray
            pdf.cell(140, 8, "  TOTAL", border=1, fill=True, align='L')
            pdf.cell(40, 8, f"{total_qty:g}", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(10)  # Space between sections

        # Helper for Stock Inventory
        def draw_inv_stock(items):
            if not items: return
            
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(52, 73, 94)
            pdf.cell(0, 10, "Current Inventory (Stock Based)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Header
            pdf.set_font("Helvetica", 'B', 10)
            pdf.set_fill_color(39, 174, 96) # Green
            pdf.set_text_color(255, 255, 255)
            pdf.set_draw_color(39, 174, 96)
            
            pdf.cell(70, 8, "Product Name", 1, 0, 'L', True)
            pdf.cell(40, 8, "Category", 1, 0, 'L', True)
            pdf.cell(40, 8, "Stock", 1, 0, 'C', True)
            pdf.cell(40, 8, "Price", 1, 1, 'R', True) 
            
            # Rows
            pdf.set_font("Helvetica", '', 9)
            pdf.set_text_color(44, 62, 80)
            pdf.set_draw_color(189, 195, 199)
            
            for i, item in enumerate(items):
                # item: name, cat, stock, price, unit
                name, cat, stock, price, unit = item[0], item[1], item[2], item[3], item[4]
                
                if i % 2 == 1: pdf.set_fill_color(245, 245, 245)
                else: pdf.set_fill_color(255, 255, 255)
                
                name_clean = str(name).encode('latin-1', 'replace').decode('latin-1')[:35]
                cat_clean = str(cat).encode('latin-1', 'replace').decode('latin-1')[:18]
                
                pdf.cell(70, 7, f" {name_clean}", 1, 0, 'L', True)
                pdf.cell(40, 7, f" {cat_clean}", 1, 0, 'L', True)
                
                # Integer Stock Force
                try:
                    s_int = int(stock)
                except:
                    s_int = 0
                pdf.cell(40, 7, f" {s_int} {unit}", 1, 0, 'C', True)
                
                pdf.cell(40, 7, f"{price:,.2f}", 1, 1, 'R', True)
            pdf.ln(8)

        # Helper for Made to Order
        def draw_inv_avail(items):
            if not items: return
            
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(52, 73, 94)
            pdf.cell(0, 10, "Product Availability (Made-to-Order)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Header
            pdf.set_font("Helvetica", 'B', 10)
            pdf.set_fill_color(41, 128, 185) # Blue header
            pdf.set_text_color(255, 255, 255)
            pdf.set_draw_color(41, 128, 185)
            
            pdf.cell(70, 8, "Product Name", 1, 0, 'L', True)
            pdf.cell(50, 8, "Category", 1, 0, 'L', True)
            pdf.cell(30, 8, "Status", 1, 0, 'C', True)
            pdf.cell(40, 8, "Price", 1, 1, 'R', True) 
            
            # Rows
            pdf.set_font("Helvetica", '', 9)
            pdf.set_text_color(44, 62, 80)
            
            for i, item in enumerate(items):
                # item: name, cat, stock, price, unit, mode, avail
                name, cat, price = item[0], item[1], item[3]
                avail = item[6]
                
                if i % 2 == 1: pdf.set_fill_color(245, 245, 245)
                else: pdf.set_fill_color(255, 255, 255)
                
                name_clean = str(name).encode('latin-1', 'replace').decode('latin-1')[:35]
                cat_clean = str(cat).encode('latin-1', 'replace').decode('latin-1')[:20]
                
                pdf.cell(70, 7, f" {name_clean}", 1, 0, 'L', True)
                pdf.cell(50, 7, f" {cat_clean}", 1, 0, 'L', True)
                
                # Status
                pdf.set_font("Helvetica", 'B', 9)
                is_avail = (str(avail)=='1' or str(avail)=='True')
                status_txt = "Available" if is_avail else "Not Available"
                
                if is_avail: pdf.set_text_color(39, 174, 96)
                else: pdf.set_text_color(192, 57, 43)
                
                pdf.cell(30, 7, status_txt, 1, 0, 'C', True)
                
                pdf.set_text_color(44, 62, 80) # Reset
                pdf.set_font("Helvetica", '', 9)
                
                pdf.cell(40, 7, f"{price:,.2f}", 1, 1, 'R', True)
            pdf.ln(8)

        # Draw all sections
        draw_section("Order Types", data.get('types', {}), "")
        draw_section("Sold Items (Products)", data.get('products', {}), "")
        draw_section("Sold Add-ons (Modifiers)", data.get('addons', {}), "")
        draw_section("Ingredients Used", data.get('ingredients', {}), "")
        
        # Render separated inventory
        draw_inv_stock(data.get('inv_stock', []))
        draw_inv_avail(data.get('inv_avail', []))
        
        # Footer note
        pdf.ln(5)
        pdf.set_font("Helvetica", 'I', 9)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 5, "This report shows the total quantity of products sold, add-ons/modifiers used, and ingredients consumed during the selected period.", align='C')
        
        path = f"{filename}.pdf"
        pdf.output(path)
        return path

    def generate_product_report(self, report_type, output_format="html"):
        """
        Generates a detailed product sales and inventory usage report.
        report_type: 'today', 'week', 'month', 'all'
        output_format: 'csv' or 'html'
        """
        start_date, end_date = self._get_date_range(report_type)
        
        # 1. Fetch Transactions
        if report_type == 'all':
             query = "SELECT id, created_at FROM transactions"
             params = ()
        else:
             query = "SELECT id, created_at FROM transactions WHERE DATE(created_at) BETWEEN ? AND ?"
             params = (start_date, end_date)
             
        self.db.cursor.execute(query, params)
        transactions = self.db.cursor.fetchall()
        
        # 2. Aggregate Data
        # Map: ProductID -> {name, qty_sold, revenue, ingredients: {name: usage}, modifiers: {name: count}}
        product_stats = {}
        # Global Mod Stats: ModName -> {count, linked_usage: {name: qty}}
        # But user wants "show all the pattys and buns linked to that".
        # So we want hierarchy under the Product.
        
        # Pre-fetch lookup maps
        # Ingredients Map: ProductID -> [(IngredientName, QtyPerProduct)]
        ing_map = {}
        self.db.cursor.execute("""
            SELECT pi.product_id, p.name, pi.quantity 
            FROM product_ingredients pi
            JOIN products p ON pi.ingredient_id = p.id
        """)
        for row in self.db.cursor.fetchall():
            pid, name, qty = row
            if pid not in ing_map: ing_map[pid] = []
            ing_map[pid].append((name, qty))
            
        # Global Modifiers Map: Name -> (LinkedProductName, DeductQty)
        mod_map = {}
        self.db.cursor.execute("""
            SELECT m.name, p.name, COALESCE(m.deduct_quantity, 1)
            FROM global_modifiers m
            LEFT JOIN products p ON m.linked_product_id = p.id
        """)
        for row in self.db.cursor.fetchall():
            m_name, p_name, d_qty = row
            if p_name: # Only map if linked
                mod_map[m_name] = (p_name, d_qty)

        # Process Transactions
        for txn in transactions:
            txn_id = txn[0]
            items = self.db.get_transaction_items(txn_id)
            for item in items:
                # transaction_items columns: id, transaction_id, product_id, product_name, quantity, unit_price, subtotal, variant_id, variant_name, modifiers
                pid = item[2]           # product_id
                name = item[3]          # product_name (was incorrectly item[4])
                qty = item[4]           # quantity (was incorrectly item[6])
                unit_price = item[5]
                subtotal = item[6]      # (was incorrectly item[7])
                variant_id = item[7] if len(item) > 7 else None
                variant_name = item[8] if len(item) > 8 else None
                mods_str = item[9] if len(item) > 9 else None  # modifiers (was incorrectly item[8])
                
                if pid not in product_stats:
                    product_stats[pid] = {
                        'name': name, 'qty': 0, 'revenue': 0.0, 
                        'modifiers_sold': {} # Name -> Count
                    }
                
                p_data = product_stats[pid]
                p_data['qty'] += qty
                p_data['revenue'] += subtotal
                
                # Count Modifiers
                if mods_str:
                    # Split by comma
                    # Note: PaymentDialog joins with ", "
                    for mod in mods_str.split(", "):
                        mod_clean = mod.strip()
                        if mod_clean:
                            p_data['modifiers_sold'][mod_clean] = p_data['modifiers_sold'].get(mod_clean, 0) + 1

        # 3. Build Report Data Structure
        report_rows = [] # flattened for CSV / structured for HTML
        
        for pid, data in product_stats.items():
            # Main Product Row
            report_rows.append({
                'type': 'product',
                'name': data['name'],
                'sold': data['qty'],
                'revenue': data['revenue']
            })
            
            # Derived Ingredients
            if pid in ing_map:
                for ing_name, ing_qty in ing_map[pid]:
                    total_used = ing_qty * data['qty']
                    report_rows.append({
                        'type': 'ingredient',
                        'name': f"Used: {ing_name}",
                        'qty': total_used,
                        'info': f"({ing_qty} per item)"
                    })
            
            # Modifiers
            for mod_name, mod_count in data['modifiers_sold'].items():
                report_rows.append({
                    'type': 'modifier',
                    'name': f"Add-on: {mod_name}",
                    'sold': mod_count,
                    'revenue': 0 # Included in product revenue usually? or separate?
                                 # In current DB, subtotal includes modifier price.
                                 # So we don't separate revenue easily here without more lookups.
                })
                
                # Modifier Ingredients
                if mod_name in mod_map:
                    link_name, d_qty = mod_map[mod_name]
                    total_mod_used = d_qty * mod_count
                    report_rows.append({
                        'type': 'mod_ingredient',
                        'name': f"  -> Used: {link_name}",
                        'qty': total_mod_used,
                        'info': f"(via Add-on)"
                    })

        # 4. output
        filename = f"product_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if output_format == 'csv':
            return self._export_csv(filename, report_rows)
        else:
            return self._export_html(filename, report_rows, start_date, end_date)

    def _get_date_range(self, report_type):
        today = datetime.now().date()
        if report_type == 'today':
            return today, today
        elif report_type == 'week':
            return today - timedelta(days=7), today
        elif report_type == 'month':
            return today - timedelta(days=30), today
        else:
            return datetime(2000, 1, 1).date(), today

    def _export_csv(self, filename, rows):
        path = f"{filename}.csv"
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Name/Details", "Quantity/Count", "Revenue/Info"])
            for r in rows:
                writer.writerow([
                    r['type'].upper(), 
                    r['name'], 
                    r.get('sold', r.get('qty', '')), 
                    r.get('revenue', r.get('info', ''))
                ])
        return path

    def _export_html(self, filename, rows, start, end):
        path = f"{filename}.html"
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                table {{ border-collapse: collapse; width: 100%; max_width: 800px; }}
                th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .product {{ background-color: #e9f5ff; font-weight: bold; }}
                .ingredient {{ padding-left: 30px; color: #555; }}
                .modifier {{ padding-left: 30px; font-style: italic; }}
                .mod-ingredient {{ padding-left: 60px; color: #777; font-size: 0.9em; }}
                h2 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h2>Product Sales & Inventory Usage Report</h2>
            <p>Period: {start} to {end}</p>
            <table>
                <tr>
                    <th>Item / Component</th>
                    <th>Qty Sold / Used</th>
                    <th>Revenue / Notes</th>
                </tr>
        """
        
        for r in rows:
            css_class = r['type'].replace('_', '-')
            name = r['name']
            qty = r.get('sold', r.get('qty', '-'))
            rev_or_info = r.get('revenue', r.get('info', ''))
            
            if isinstance(rev_or_info, float):
                rev_or_info = f"{rev_or_info:,.2f}"
            
            html += f"""
                <tr class="{css_class}">
                    <td>{name}</td>
                    <td>{qty}</td>
                    <td>{rev_or_info}</td>
                </tr>
            """
            
        html += """
            </table>
            <br><p>Generated by POS System</p>
        </body>
        </html>
        """
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return path
