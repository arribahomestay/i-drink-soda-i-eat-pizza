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
        
        self.setup_receipt_tab(tabview.tab("Receipt Config"))
        self.setup_email_tab(tabview.tab("Email Settings"))
        self.setup_activity_log_tab(tabview.tab("Activity Logs"))
    
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
            command=lambda: messagebox.showinfo("Info", "Refresh - to be implemented"),
            width=80,
            height=30,
            fg_color=COLORS["secondary"]
        ).pack(side="right")
        
        # Scrollable List
        logs_list = ctk.CTkScrollableFrame(logs_frame, fg_color="transparent")
        logs_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        logs = self.database.get_activity_logs(limit=100)
        
        if logs:
            for log in logs:
                # log: 0:id, 1:user_id, 2:username, 3:action, 4:details, 5:created_at
                row = ctk.CTkFrame(logs_list, fg_color=COLORS["dark"], corner_radius=8)
                row.pack(fill="x", pady=5)
                
                content = ctk.CTkFrame(row, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)
                
                # Left: Action & User
                left = ctk.CTkFrame(content, fg_color="transparent")
                left.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(left, text=log[3], font=ctk.CTkFont(weight="bold"), text_color=COLORS["primary"]).pack(anchor="w")
                ctk.CTkLabel(left, text=f"User: {log[2]}", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(anchor="w")
                
                # Right: Details & Time
                right = ctk.CTkFrame(content, fg_color="transparent")
                right.pack(side="right")
                
                ctk.CTkLabel(right, text=(log[5] or "")[:16], font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"]).pack(anchor="e")
                ctk.CTkLabel(right, text=log[4] or "", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"], wraplength=400, justify="right").pack(anchor="e")
        else:
            ctk.CTkLabel(logs_list, text="No logs found", text_color=COLORS["text_secondary"]).pack(pady=20)
    
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
        
        # Form Container
        form = ctk.CTkFrame(left_frame, fg_color="transparent")
        form.pack(fill="x", padx=20)
        
        # Get current settings
        current_settings = self.database.get_receipt_settings()
        # Defaults
        s_name = current_settings[1] if current_settings and current_settings[1] else "My POS Store"
        s_addr = current_settings[2] if current_settings and current_settings[2] else ""
        s_phone = current_settings[3] if current_settings and current_settings[3] else ""
        s_email = current_settings[4] if current_settings and current_settings[4] else ""
        s_footer = current_settings[6] if current_settings and current_settings[6] else "Thank you for shopping!"
        
        # StringVars for live preview
        sv_name = ctk.StringVar(value=s_name)
        sv_addr = ctk.StringVar(value=s_addr)
        sv_phone = ctk.StringVar(value=s_phone)
        sv_email = ctk.StringVar(value=s_email)
        sv_footer = ctk.StringVar(value=s_footer)
        
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
                    logo_path="",
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
        
        # Initial call
        update_preview()
