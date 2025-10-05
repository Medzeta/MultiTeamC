"""
Quick script to open License Management dialog
Kör detta script för att snabbt öppna License Management
"""

import customtkinter as ctk
from core.license_activation import LicenseActivation
from core.custom_window import CustomDialog
from core.ui_components import CustomFrame, CustomLabel, CustomButton, MessageBox
from core.debug_logger import debug, info, error

def open_license_management():
    """Open license management dialog"""
    info("LicenseManagement", "Opening license management")
    
    # Skapa root window
    root = ctk.CTk()
    root.withdraw()  # Dölj root window
    
    try:
        # Skapa activation system
        activation_system = LicenseActivation()
        machine_uid = activation_system.get_machine_uid()
        
        # Skapa dialog för license management
        dialog = CustomDialog(root, title="🔑 License Management", width=600, height=400)
        
        # Content
        content = CustomFrame(dialog.content_frame, transparent=True)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        CustomLabel(
            content,
            text="🔑 License Management",
            size=18,
            bold=True
        ).pack(pady=(0, 10))
        
        # Machine ID
        CustomLabel(
            content,
            text=f"Machine ID: {machine_uid}",
            size=11,
            color=("#888888", "#888888")
        ).pack(pady=(0, 20))
        
        # Enter License Key button
        def show_enter_key():
            dialog._close_dialog()
            show_enter_key_dialog(root, activation_system)
        
        CustomButton(
            content,
            text="🔑 Enter License Key",
            command=show_enter_key,
            width=300,
            height=45,
            style="primary"
        ).pack(pady=10)
        
        # Apply for License button
        CustomButton(
            content,
            text="📝 Apply for License",
            command=lambda: MessageBox.show_info(root, "Apply", "Application form coming soon"),
            width=300,
            height=45,
            style="secondary"
        ).pack(pady=10)
        
        info("LicenseManagement", "License management dialog opened")
        
        root.mainloop()
        
    except Exception as e:
        error("LicenseManagement", f"Error: {e}")
        import traceback
        traceback.print_exc()

def show_enter_key_dialog(root, activation_system):
    """Show enter license key dialog"""
    dialog = ctk.CTkToplevel(root)
    dialog.title("Enter License Key")
    dialog.geometry("500x320")
    dialog.configure(fg_color=("#2b2b2b", "#2b2b2b"))
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - 250
    y = (dialog.winfo_screenheight() // 2) - 160
    dialog.geometry(f"500x320+{x}+{y}")
    
    # Make modal
    dialog.transient(root)
    dialog.grab_set()
    
    # Content
    content = CustomFrame(dialog, transparent=True)
    content.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Title
    CustomLabel(
        content,
        text="Enter License Key",
        size=18,
        bold=True
    ).pack(pady=(0, 20))
    
    # Key entry
    CustomLabel(
        content,
        text="License Key:",
        size=12
    ).pack(anchor="w")
    
    key_entry = ctk.CTkEntry(
        content,
        width=400,
        height=40,
        placeholder_text="XXXX-XXXX-XXXX-XXXX",
        fg_color=("#2b2b2b", "#2b2b2b"),
        text_color=("#ffffff", "#ffffff"),
        placeholder_text_color=("#666666", "#666666"),
        border_width=1,
        border_color=("#3a3a3a", "#3a3a3a"),
        corner_radius=5,
        font=("Consolas", 12)
    )
    key_entry.pack(pady=10)
    
    # Force focus
    dialog.after(200, lambda: key_entry.focus_set())
    dialog.after(250, lambda: key_entry.focus_force())
    
    # Buttons
    btn_frame = CustomFrame(content, transparent=True)
    btn_frame.pack(pady=20)
    
    def activate_key(event=None):
        key = key_entry.get().strip().upper()
        if not key:
            MessageBox.show_error(dialog, "Error", "Please enter a license key")
            return
        
        # Get machine UID
        machine_uid = activation_system.get_machine_uid()
        
        # Activate license
        import sqlite3
        import hashlib
        from datetime import datetime
        
        try:
            conn = sqlite3.connect('data/license_applications.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Hash license key
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            
            # Check if license exists
            cursor.execute("""
                SELECT * FROM license_applications
                WHERE license_key = ? AND status = 'approved' AND payment_status = 'paid'
            """, (key,))
            
            app_data = cursor.fetchone()
            
            if not app_data:
                conn.close()
                MessageBox.show_error(dialog, "Invalid License", 
                                    "License key not found or not approved")
                return
            
            # Check if already activated
            cursor.execute("""
                SELECT * FROM active_licenses
                WHERE license_key_hash = ? AND machine_uid = ?
            """, (key_hash, machine_uid))
            
            existing = cursor.fetchone()
            
            if not existing:
                # Activate for first time
                cursor.execute("""
                    INSERT INTO active_licenses (
                        license_key, license_key_hash, machine_uid,
                        email, company, tier, activated_at,
                        last_validated, application_id, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    key, key_hash, machine_uid,
                    app_data['email'], app_data['company'], app_data['requested_tier'],
                    datetime.now().isoformat(), datetime.now().isoformat(),
                    app_data['id']
                ))
                conn.commit()
            
            conn.close()
            
            dialog.destroy()
            MessageBox.show_success(
                root,
                "License Activated!",
                f"License activated: {app_data['requested_tier']}"
            )
            
        except Exception as e:
            error("LicenseActivation", f"License activation error: {e}")
            MessageBox.show_error(dialog, "Error", f"Activation failed: {e}")
    
    CustomButton(
        btn_frame,
        text="Activate",
        command=activate_key,
        width=120,
        height=35,
        style="primary"
    ).pack(side="left", padx=5)
    
    CustomButton(
        btn_frame,
        text="Cancel",
        command=dialog.destroy,
        width=100,
        height=35,
        style="secondary"
    ).pack(side="left", padx=5)
    
    # Bind Enter key
    key_entry.bind("<Return>", activate_key)

if __name__ == "__main__":
    print("=" * 60)
    print("Opening License Management...")
    print("=" * 60)
    open_license_management()
