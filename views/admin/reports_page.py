"""
Reports and export page for admin view
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
from config import COLORS, CURRENCY_SYMBOL


class ReportsPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
        self.selected_report_type = "today"
        self.date_buttons = {}
        self.selected_period_label = None
    
    def show(self):
        """Show reports page with export functionality"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="📈 Sales Reports & Export",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Single panel with simple layout
        main_panel = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=15)
        main_panel.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Step 1: Date Range Selection
        step1_frame = ctk.CTkFrame(main_panel, fg_color=COLORS["dark"], corner_radius=10)
        step1_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            step1_frame,
            text="STEP 1: Select Time Period",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 10), padx=20)
        
        # Date buttons in a grid
        date_buttons_frame = ctk.CTkFrame(step1_frame, fg_color="transparent")
        date_buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        date_options = [
            ("📅 Today", "today"),
            ("📅 Last 7 Days", "week"),
            ("📅 Last 30 Days", "month"),
            ("📅 All Time", "all")
        ]
        
        for idx, (text, report_type) in enumerate(date_options):
            btn = ctk.CTkButton(
                date_buttons_frame,
                text=text,
                command=lambda rt=report_type: self.select_date_range(rt),
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=COLORS["primary"] if report_type == "today" else COLORS["card_bg"],
                hover_color=COLORS["primary"],
                corner_radius=10,
                border_width=2,
                border_color=COLORS["primary"] if report_type == "today" else COLORS["dark"]
            )
            btn.grid(row=0, column=idx, padx=5, sticky="ew")
            date_buttons_frame.grid_columnconfigure(idx, weight=1)
            self.date_buttons[report_type] = btn
        
        # Selected period display
        self.selected_period_label = ctk.CTkLabel(
            step1_frame,
            text=f"✓ Selected: {datetime.now().strftime('%B %d, %Y')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["success"]
        )
        self.selected_period_label.pack(pady=(5, 15))
        
        # Step 2: Report Type Selection
        step2_frame = ctk.CTkFrame(main_panel, fg_color=COLORS["dark"], corner_radius=10)
        step2_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            step2_frame,
            text="STEP 2: Choose Report Type & Export",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(15, 10), padx=20)
        
        # Report buttons with export options
        reports_grid = ctk.CTkFrame(step2_frame, fg_color="transparent")
        reports_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        report_types = [
            ("💰 Sales Summary", "sales_summary", COLORS["success"]),
            ("📋 Transaction List", "transactions", COLORS["info"]),
            ("📦 Product Report", "product_sales", COLORS["warning"]),
            ("👤 Cashier Report", "cashier_performance", COLORS["primary"]),
            ("📊 Category Report", "category_analysis", COLORS["secondary"]),
        ]
        
        for idx, (text, report_id, color) in enumerate(report_types):
            # Report card
            card = ctk.CTkFrame(reports_grid, fg_color=COLORS["card_bg"], corner_radius=10)
            card.grid(row=idx//2, column=idx%2, padx=10, pady=10, sticky="ew")
            
            # Report name
            ctk.CTkLabel(
                card,
                text=text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=color
            ).pack(pady=(15, 10), padx=15)
            
            # Export buttons
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            ctk.CTkButton(
                btn_frame,
                text="📄 CSV",
                command=lambda rid=report_id: self.quick_export(rid, "csv"),
                height=35,
                width=100,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=color,
                hover_color=COLORS["primary"],
                corner_radius=8
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text="📝 Word",
                command=lambda rid=report_id: self.quick_export(rid, "word"),
                height=35,
                width=100,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=color,
                hover_color=COLORS["primary"],
                corner_radius=8
            ).pack(side="left", padx=5)
        
        reports_grid.grid_columnconfigure(0, weight=1)
        reports_grid.grid_columnconfigure(1, weight=1)
        
        # Instructions
        info_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Click CSV or Word button to instantly download the report",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack()
    
    def select_date_range(self, report_type):
        """Select date range and update UI"""
        self.selected_report_type = report_type
        
        # Update button colors
        for rt, btn in self.date_buttons.items():
            if rt == report_type:
                btn.configure(
                    fg_color=COLORS["primary"],
                    border_color=COLORS["primary"]
                )
            else:
                btn.configure(
                    fg_color=COLORS["card_bg"],
                    border_color=COLORS["dark"]
                )
        
        # Update selected period label
        period_text = self.get_date_range_text()
        self.selected_period_label.configure(text=f"✓ Selected: {period_text}")
    
    def get_date_range_text(self):
        """Get human-readable date range text"""
        if self.selected_report_type == "today":
            return datetime.now().strftime("%B %d, %Y")
        elif self.selected_report_type == "week":
            return "Last 7 Days"
        elif self.selected_report_type == "month":
            return "Last 30 Days"
        else:
            return "All Time"
    
    def quick_export(self, report_id, export_type):
        """Quick export"""
        try:
            if report_id == "product_sales":
                from .report_generator import DetailedReportGenerator
                import os
                
                # output format: force html for word (nicer layout), csv for csv
                fmt = "csv" if export_type == "csv" else "html"
                
                gen = DetailedReportGenerator(self.database)
                path = gen.generate_product_report(self.selected_report_type, fmt)
                
                # Open the file automatically
                try:
                    os.startfile(path)
                except:
                    pass # Linux/Mac might fail here
                    
                messagebox.showinfo("Export Success", f"Report generated:\n{path}")
            else:
                messagebox.showinfo("Info", f"Export logic for {report_id} is coming soon!")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate report: {str(e)}")
