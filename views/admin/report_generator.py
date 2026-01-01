
import csv
from datetime import datetime, timedelta
import os

class DetailedReportGenerator:
    def __init__(self, database):
        self.db = database

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
