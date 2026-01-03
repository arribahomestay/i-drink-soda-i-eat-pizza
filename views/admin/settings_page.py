"""
Settings page for admin view
"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from PIL import Image
from receipt_renderer import ReceiptRenderer


class SettingsPage:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database
    
    def show(self):
        """Show settings page with Tabs"""
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Tabs
        tabview = ctk.CTkTabview(self.parent, fg_color="transparent", corner_radius=15)
        tabview.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        tabview.add("Receipt Config")
        tabview.add("Email Settings")
        tabview.add("Activity Logs")
        tabview.add("Other Settings")
        
        self.setup_receipt_tab(tabview.tab("Receipt Config"))
        self.setup_email_tab(tabview.tab("Email Settings"))
        self.setup_activity_log_tab(tabview.tab("Activity Logs"))
        self.setup_other_settings_tab(tabview.tab("Other Settings"))
    
    def setup_email_tab(self, parent_frame):
        """Setup Email Configuration tab"""
        # Container
        container = ctk.CTkFrame(parent_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(
            header,
            text="📧 Email Reporting Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Form
        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(fill="x", padx=30)
        
        # Load Settings
        settings = self.database.get_email_settings()
        # Defaults
        current_sender = settings[1] if settings else ""
        current_password = settings[2] if settings else ""
        current_receiver = settings[3] if settings else ""
        current_server = settings[4] if settings else "smtp.gmail.com"
        current_port = settings[5] if settings else 587
        
        # Sender Email
        ctk.CTkLabel(form, text="Sender Email (Gmail/Outlook)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        sender_entry = ctk.CTkEntry(form, width=400, height=35)
        sender_entry.pack(anchor="w", pady=(0, 5))
        sender_entry.insert(0, current_sender or "")
        
        # App Password
        ctk.CTkLabel(form, text="App Password (Not your login password)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        pwd_entry = ctk.CTkEntry(form, width=400, height=35, show="*")
        pwd_entry.pack(anchor="w", pady=(0, 5))
        pwd_entry.insert(0, current_password or "")
        
        # Help Text
        help_lbl = ctk.CTkLabel(
            form, 
            text="For Gmail: Use 'App Password' generated from Google Account Security settings.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=COLORS["text_secondary"]
        )
        help_lbl.pack(anchor="w", pady=(0, 15))
        
        # Receiver Email
        ctk.CTkLabel(form, text="Receiver Email (Where reports go)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        receiver_entry = ctk.CTkEntry(form, width=400, height=35)
        receiver_entry.pack(anchor="w", pady=(0, 20))
        receiver_entry.insert(0, current_receiver or "")
        
        # Advanced (Server/Port) - Collapsible or just shown
        adv_frame = ctk.CTkFrame(form, fg_color="transparent")
        adv_frame.pack(anchor="w", fill="x", pady=10)
        
        ctk.CTkLabel(adv_frame, text="SMTP Server:").pack(side="left", padx=(0, 10))
        server_entry = ctk.CTkEntry(adv_frame, width=200)
        server_entry.pack(side="left", padx=(0, 20))
        server_entry.insert(0, current_server)
        
        ctk.CTkLabel(adv_frame, text="Port:").pack(side="left", padx=(0, 10))
        port_entry = ctk.CTkEntry(adv_frame, width=80)
        port_entry.pack(side="left")
        port_entry.insert(0, str(current_port))
        
        def save_email_config():
            try:
                self.database.save_email_settings(
                    sender=sender_entry.get().strip(),
                    password=pwd_entry.get().strip(),
                    receiver=receiver_entry.get().strip(),
                    server=server_entry.get().strip(),
                    port=int(port_entry.get().strip())
                )
                messagebox.showinfo("Success", "Email settings saved!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
                
        def test_email():
            # Import here to avoid circular
            import sys
            sys.path.append(r"c:\Users\USER\Documents\POINTOFSALE")
            from email_sender import send_email_with_attachment
            
            # Temporary construct settings
            s_settings = (0, 
                sender_entry.get().strip(),
                pwd_entry.get().strip(),
                receiver_entry.get().strip(),
                server_entry.get().strip(),
                int(port_entry.get().strip())
            )
            
            success, msg = send_email_with_attachment(
                s_settings, 
                None, 
                "POS System Test Email", 
                "This is a test email from your POS system. If you see this, configuration is correct!"
            )
            
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Failed", msg)
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            btn_frame, text="Test Configuration", command=test_email,
            fg_color=COLORS["info"], width=150
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame, text="Save Settings", command=save_email_config,
            fg_color=COLORS["success"], width=150
        ).pack(side="left")

    def setup_activity_log_tab(self, parent_frame):
        """Setup Activity Logs tab"""
        # Activity Logs List
        logs_frame = ctk.CTkFrame(parent_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(logs_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="System Activity Logs",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            command=lambda: self.refresh_logs(logs_list_frame),
            width=80,
            height=30,
            fg_color=COLORS["secondary"]
        ).pack(side="right")
        
        # Table Header
        table_header = ctk.CTkFrame(logs_frame, fg_color=COLORS["dark"], height=35)
        table_header.pack(fill="x", padx=20, pady=(0, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="Action",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(15, 10))
        
        ctk.CTkLabel(
            table_header,
            text="User",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            table_header,
            text="Details",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkLabel(
            table_header,
            text="Time",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"],
            width=130,
            anchor="e"
        ).pack(side="right", padx=(10, 15))
        
        # Scrollable List
        logs_list_frame = ctk.CTkScrollableFrame(logs_frame, fg_color="transparent")
        logs_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.load_activity_logs(logs_list_frame)
    
    def load_activity_logs(self, logs_list_frame):
        """Load and display activity logs in simple list format"""
        # Clear existing
        for widget in logs_list_frame.winfo_children():
            widget.destroy()
        
        logs = self.database.get_activity_logs(limit=100)
        
        if logs:
            for idx, log in enumerate(logs):
                # log: 0:id, 1:user_id, 2:username, 3:action, 4:details, 5:created_at
                
                # Alternating row colors
                row_color = COLORS["dark"] if idx % 2 == 0 else "transparent"
                
                row = ctk.CTkFrame(logs_list_frame, fg_color=row_color, height=30)
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                
                # Action
                ctk.CTkLabel(
                    row,
                    text=log[3],
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["primary"],
                    width=150,
                    anchor="w"
                ).pack(side="left", padx=(15, 10))
                
                # User
                ctk.CTkLabel(
                    row,
                    text=log[2],
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"],
                    width=100,
                    anchor="w"
                ).pack(side="left", padx=10)
                
                # Details
                details_text = (log[4] or "")[:80] + "..." if log[4] and len(log[4]) > 80 else (log[4] or "")
                ctk.CTkLabel(
                    row,
                    text=details_text,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True, padx=10)
                
                # Time
                ctk.CTkLabel(
                    row,
                    text=(log[5] or "")[:16],
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"],
                    width=130,
                    anchor="e"
                ).pack(side="right", padx=(10, 15))
        else:
            ctk.CTkLabel(
                logs_list_frame,
                text="No logs found",
                text_color=COLORS["text_secondary"]
            ).pack(pady=20)
    
    def refresh_logs(self, logs_list_frame):
        """Refresh the activity logs"""
        self.load_activity_logs(logs_list_frame)
    
    def setup_receipt_tab(self, parent_frame):
        """Setup Receipt Configuration tab"""
        # Main Layout: 2 Columns (Form | Preview)
        main_layout = ctk.CTkFrame(parent_frame, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # --- LEFT: Form Section ---
        left_frame = ctk.CTkFrame(main_layout, fg_color=COLORS["card_bg"], corner_radius=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        ctk.CTkLabel(
            left_frame,
            text="🧾 Receipt Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Form Container - SCROLLABLE
        form_scroll = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        form = ctk.CTkFrame(form_scroll, fg_color="transparent")
        form.pack(fill="x")
        
        # Get current settings
        current_settings = self.database.get_receipt_settings()
        # Defaults
        s_name = current_settings[1] if current_settings and current_settings[1] else "My POS Store"
        s_addr = current_settings[2] if current_settings and current_settings[2] else ""
        s_phone = current_settings[3] if current_settings and current_settings[3] else ""
        s_email = current_settings[4] if current_settings and current_settings[4] else ""
        s_footer = current_settings[6] if current_settings and current_settings[6] else "Thank you for shopping!"
        s_logo = current_settings[7] if current_settings and len(current_settings) > 7 and current_settings[7] else ""
        
        # StringVars for live preview
        sv_name = ctk.StringVar(value=s_name)
        sv_addr = ctk.StringVar(value=s_addr)
        sv_phone = ctk.StringVar(value=s_phone)
        sv_email = ctk.StringVar(value=s_email)
        sv_footer = ctk.StringVar(value=s_footer)
        sv_logo = ctk.StringVar(value=s_logo)
        
        # Logo Upload Section
        ctk.CTkLabel(form, text="Store Logo (Optional)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        logo_frame = ctk.CTkFrame(form, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(0, 5))
        
        import os

        # Define Label (Unpacked)
        display_text = os.path.basename(s_logo) if s_logo else "No logo selected"
        logo_path_label = ctk.CTkLabel(
            logo_frame, 
            text=display_text,
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        
        def upload_logo():
            from tkinter import filedialog
            import shutil
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select Logo Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                try:
                    # Create logos directory if it doesn't exist
                    logos_dir = os.path.abspath("logos")
                    os.makedirs(logos_dir, exist_ok=True)
                    
                    # Copy file to logos directory
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(logos_dir, f"store_logo_{filename}")
                    shutil.copy2(file_path, dest_path)
                    
                    # Update the path
                    sv_logo.set(dest_path)
                    logo_path_label.configure(text=os.path.basename(dest_path))
                    
                    # Update preview
                    update_preview()
                    
                    messagebox.showinfo("Success", "Logo uploaded successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to upload logo: {str(e)}")

        def remove_logo():
            sv_logo.set("")
            logo_path_label.configure(text="No logo selected")
            update_preview()
        
        # Pack Buttons FIRST (Right side)
        ctk.CTkButton(
            logo_frame, 
            text="Remove", 
            command=remove_logo,
            width=80,
            height=30,
            fg_color=COLORS["danger"]
        ).pack(side="right")

        ctk.CTkButton(
            logo_frame, 
            text="Upload Logo", 
            command=upload_logo,
            width=100,
            height=30,
            fg_color=COLORS["info"]
        ).pack(side="right", padx=(5, 5))
        
        # Pack Label LAST (Left side, taking remaining space)
        logo_path_label.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            form,
            text="Logo will be converted to black & white for thermal printing",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Store Name
        ctk.CTkLabel(form, text="Store Name").pack(anchor="w", pady=(10, 5))
        name_entry = ctk.CTkEntry(form, width=300, height=35, textvariable=sv_name)
        name_entry.pack(fill="x", pady=(0, 5))
        
        # Store Address
        ctk.CTkLabel(form, text="Store Address").pack(anchor="w", pady=(10, 5))
        addr_entry = ctk.CTkEntry(form, width=300, height=35, textvariable=sv_addr)
        addr_entry.pack(fill="x", pady=(0, 5))
        
        # Phone
        ctk.CTkLabel(form, text="Phone Number").pack(anchor="w", pady=(10, 5))
        phone_entry = ctk.CTkEntry(form, width=300, height=35, textvariable=sv_phone)
        phone_entry.pack(fill="x", pady=(0, 5))
        
        # Email
        ctk.CTkLabel(form, text="Email").pack(anchor="w", pady=(10, 5))
        email_entry = ctk.CTkEntry(form, width=300, height=35, textvariable=sv_email)
        email_entry.pack(fill="x", pady=(0, 5))
        
        # Receipt Footer Message
        ctk.CTkLabel(form, text="Footer Message").pack(anchor="w", pady=(10, 5))
        footer_entry = ctk.CTkEntry(form, width=300, height=35, textvariable=sv_footer)
        footer_entry.pack(fill="x", pady=(0, 20))
        
        def save_settings():
            try:
                # Force tax to 0.0 since we removed the field
                new_tax = 0.0
                self.database.update_receipt_settings(
                    name=name_entry.get(),
                    address=addr_entry.get(),
                    phone=phone_entry.get(),
                    email=email_entry.get(),
                    tax_rate=new_tax,
                    footer=footer_entry.get(),
                    logo_path=sv_logo.get(),  # Save logo path
                    paper_width=80
                )
                messagebox.showinfo("Success", "Settings saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        
        ctk.CTkButton(
            left_frame, text="Save Settings", command=save_settings,
            height=45, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["success"], corner_radius=10
        ).pack(fill="x", padx=20, pady=(0, 20))
        
        # --- RIGHT: Preview Section ---
        right_frame = ctk.CTkFrame(main_layout, fg_color=COLORS["card_bg"], corner_radius=15, width=350)
        right_frame.pack(side="right", fill="y", padx=(20, 0))
        right_frame.pack_propagate(False)  # Fixed width
        
        ctk.CTkLabel(
            right_frame,
            text="👁️ Live Preview",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(20, 10))
        
        preview_container = ctk.CTkFrame(right_frame, fg_color="#F0F0F0", corner_radius=0)
        preview_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        preview_label = ctk.CTkLabel(preview_container, text="")
        preview_label.pack(expand=True)
        
        def update_preview(*args):
            # Create a mock settings list (tuple-like) matching DB constraints
            temp_settings = [None] * 10
            temp_settings[1] = sv_name.get()
            temp_settings[2] = sv_addr.get()
            temp_settings[3] = sv_phone.get()
            temp_settings[4] = sv_email.get()
            temp_settings[6] = sv_footer.get()
            temp_settings[7] = sv_logo.get()  # Include logo path
            
            renderer = ReceiptRenderer(temp_settings)
            
            # Generate preview image
            try:
                pil_img = renderer.generate_image(None, None, preview=True)
                
                # Resize for display if needed (max width 300)
                aspect = pil_img.height / pil_img.width
                display_w = 280
                display_h = int(display_w * aspect)
                pil_img = pil_img.resize((display_w, display_h), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(display_w, display_h))
                
                preview_label.configure(image=ctk_img)
                preview_label.image = ctk_img  # Keep ref
            except Exception as e:
                print(f"Preview Error: {e}")
        
        # Bind changes
        sv_name.trace_add("write", update_preview)
        sv_addr.trace_add("write", update_preview)
        sv_phone.trace_add("write", update_preview)
        sv_footer.trace_add("write", update_preview)
        sv_logo.trace_add("write", update_preview)  # Bind logo changes
        
        # Initial call
        update_preview()
    
    def setup_other_settings_tab(self, parent_frame):
        """Setup Other Settings tab - Maintenance & Utilities"""
        # Container
        container = ctk.CTkFrame(parent_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(
            header,
            text="🛠️ System Maintenance",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30)
        
        # Optimization Box
        opt_frame = ctk.CTkFrame(content, fg_color=COLORS.get("dark", "#2C3E50"), corner_radius=10)
        opt_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
             opt_frame, 
             text="System Optimizer", 
             font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
             opt_frame, 
             text="Performs database cleanup (VACUUM/ANALYZE) and deletes old temporary receipt images.", 
             text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=(0, 15))

        def run_opt():
             try:
                 # Import here to avoid circular dependencies if any
                 from system_optimizer import SystemOptimizer
                 opt = SystemOptimizer()
                 opt.run_all()
                 messagebox.showinfo("Optimization Complete", "System optimization finished successfully.\n\n- Database compacted\n- Old receipts cleaned")
             except Exception as e:
                 messagebox.showerror("Error", f"Optimization failed: {e}")
        
        ctk.CTkButton(
            opt_frame, 
            text="🚀 Run Optimization Now", 
            command=run_opt,
            height=40,
            fg_color=COLORS["primary"],
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=20, pady=(0, 20), anchor="w")

