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
        
        # Header with Summary Button
        header_frame = ctk.CTkFrame(step2_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(15, 10), padx=20)
        
        ctk.CTkLabel(
            header_frame,
            text="STEP 2: Choose Report Type & Export",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="📧 Send Full Summary (PDF/HTML)",
            command=self.email_summary_report,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#e67e22", # Orange/Warning color
            hover_color="#d35400",
            height=35
        ).pack(side="right")
        
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
            
            ctk.CTkButton(
                btn_frame,
                text="📧 Email",
                command=lambda rid=report_id: self.email_report(rid),
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

    def email_report(self, report_id):
        """Generate and email report"""
        # 1. Check if email is configured
        settings = self.database.get_email_settings()
        # settings: id, sender, password, receiver, server, port, updated_at
        if not settings or not settings[1] or not settings[3]:
             messagebox.showwarning("Email Setup", "Please configure Sender and Receiver emails in Settings page first.")
             return
             
        try:
             # 2. Generate Report
             from .report_generator import DetailedReportGenerator
             gen = DetailedReportGenerator(self.database)
             path = None
             report_name = ""
             
             if report_id == "product_sales":
                 path = gen.generate_product_report(self.selected_report_type, "html")
                 report_name = "Product Sales"
             # Add other types here when implemented in report_generator
             
             if path:
                 # 3. Send
                 import sys
                 sys.path.append(r"c:\Users\USER\Documents\POINTOFSALE")
                 from email_sender import send_email_with_attachment
                 
                 period = self.get_date_range_text()
                 subject = f"POS Report: {report_name} ({period})"
                 body = f"Attached is the {report_name} report for {period}.\n\nGenerated by Admin POS System."
                 
                 # Show loading... (optional, but UI will freeze briefly)
                 success, msg = send_email_with_attachment(settings, path, subject, body)
                 
                 if success:
                     messagebox.showinfo("Email Sent", f"Report emailed to {settings[3]} successfully!")
                 else:
                     messagebox.showerror("Sending Failed", msg)
             else:
                 messagebox.showinfo("Info", f"Email reporting for '{report_id}' is coming soon!")
                 
        except Exception as e:
            messagebox.showerror("Error", f"Failed to email report: {str(e)}")

    def email_summary_report(self):
        """Generate and email the comprehensive summary"""
        # 1. Check if email is configured
        settings = self.database.get_email_settings()
        if not settings or not settings[1] or not settings[3]:
             messagebox.showwarning("Email Setup", "Please configure Sender and Receiver emails in Settings first.")
             return
             
        try:
             from .report_generator import DetailedReportGenerator
             gen = DetailedReportGenerator(self.database)
             path = gen.generate_summary_report(self.selected_report_type, "pdf")
             
             # Send
             import sys
             import os
             # Ensure root path is in sys.path mainly for email_sender import
             # Assumes this file is in views/admin/
             current_dir = os.path.dirname(os.path.abspath(__file__))
             root_dir = os.path.dirname(os.path.dirname(current_dir))
             if root_dir not in sys.path:
                 sys.path.append(root_dir)
                 
             from email_sender import send_email_with_attachment
             
             period = self.get_date_range_text()
             subject = f"POS Summary: Sales, Ingredients & Add-ons ({period})"
             body = f"Attached is the comprehensive summary report for {period}, including sold items, ingredients used, and add-ons sold.\n\nGenerated by POS System."
             
             success, msg = send_email_with_attachment(settings, path, subject, body)
             
             if success:
                 messagebox.showinfo("Success", f"Summary Report emailed to {settings[3]}!")
             else:
                 messagebox.showerror("Failed", msg)
                 
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
