
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
             query = "SELECT id, created_at FROM transactions"
             params = ()
        else:
             query = "SELECT id, created_at FROM transactions WHERE DATE(created_at) BETWEEN ? AND ?"
             params = (start_date, end_date)
             
        self.db.cursor.execute(query, params)
        transactions = self.db.cursor.fetchall()
        
        # Data Containers
        products_sold = {} # Name -> Qty
        addons_sold = {}   # Name -> Qty
        ingredients_used = {} # Name -> Qty
        
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
            items = self.db.get_transaction_items(txn[0])
            for item in items:
                # item: id, txn_id, prod_id, variant, name, price, qty, subtotal, modifiers
                pid = item[2]
                p_name = item[4]
                qty = item[6]
                mods_str = item[8]
                
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
                        # Legacy String
                        for m_str in mods_str.split(", "):
                             m_clean = m_str.strip()
                             if m_clean:
                                 addons_sold[m_clean] = addons_sold.get(m_clean, 0) + 1
                                 if m_clean in mod_map:
                                     link_name, link_qty = mod_map[m_clean]
                                     ingredients_used[link_name] = ingredients_used.get(link_name, 0) + link_qty

        # Generate Output
        filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if output_format == 'pdf':
            return self._export_pdf(filename, 
                {'products': products_sold, 'addons': addons_sold, 'ingredients': ingredients_used},
                start_date, end_date)
        
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
            </style>
        </head>
        <body>
            <h1>📊 Comprehensive Sales Summary</h1>
            <p><strong>Date Range:</strong> {start_date} to {end_date}</p>
            <p><strong>Generated On:</strong> {datetime.now().strftime('%B %d, %Y %I:%M %p')}</p>
            
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
            
        </body>
        </html>
        """
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return path

    def _export_pdf(self, filename, data, start, end):
        """Generate PDF report using FPDF"""
        try:
            from fpdf import FPDF
        except ImportError:
            return None
            
        class PDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 16)
                self.cell(0, 10, 'Comprehensive Sales Summary', align='C', new_x="LMARGIN", new_y="NEXT")
                self.set_font('Helvetica', '', 10)
                self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C', new_x="LMARGIN", new_y="NEXT")
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

        pdf = PDF()
        pdf.add_page()
        
        # Period Info
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, f"Period: {start} to {end}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Helper to draw table
        def draw_section(title, items):
            if not items: return

            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Table Header
            pdf.set_font("Helvetica", 'B', 10)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(140, 8, "Item Name", border=1, fill=True)
            pdf.cell(40, 8, "Quantity", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", '', 10)
            for name, qty in sorted(items.items()):
                clean_name = str(name).encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(140, 8, clean_name, border=1)
                pdf.cell(40, 8, str(qty), border=1, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(8)

        draw_section("Sold Items (Products)", data.get('products', {}))
        draw_section("Sold Add-ons (Modifiers)", data.get('addons', {}))
        draw_section("Sold Ingredients", data.get('ingredients', {}))
        
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
                # item: id, txn_id, prod_id, variant_id, name, price, qty, subtotal, modifiers
                pid = item[2]
                name = item[4]
                qty = item[6]
                subtotal = item[7]
                mods_str = item[8]
                
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
