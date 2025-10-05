"""
License Activation - Standard Tkinter Implementation
Uses standard Tkinter to avoid CustomTkinter widget leakage bug
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.debug_logger import debug, info, error
from core.license_activation import LicenseActivation


class LicenseActivationTkinter(tk.Toplevel):
    """License activation window using standard Tkinter"""
    
    def __init__(self, parent, on_success=None):
        """
        Initialize license activation window
        
        Args:
            parent: Parent window
            on_success: Callback when activation succeeds
        """
        super().__init__(parent)
        
        self.on_success = on_success
        self.activation_system = LicenseActivation()
        
        debug("LicenseActivationTkinter", "Initializing license activation window")
        
        self._setup_window()
        self._setup_style()
        self._create_ui()
        
        info("LicenseActivationTkinter", "License activation window initialized")
    
    def _setup_window(self):
        """Setup window properties"""
        debug("LicenseActivationTkinter", "Setting up window")
        
        # Window title
        self.title("🔑 License Activation")
        
        # Window size
        window_width = 800
        window_height = 600
        
        # Center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Window properties
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self._handle_close)
    
    def _setup_style(self):
        """Setup ttk styling to match CustomTkinter"""
        debug("LicenseActivationTkinter", "Setting up styling")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styling
        style.configure('TFrame', background='#2b2b2b')
        style.configure('Card.TFrame', background='#1f1f1f', relief='flat')
        
        # Label styling
        style.configure('TLabel', 
                       background='#2b2b2b', 
                       foreground='#ffffff',
                       font=('Segoe UI', 11))
        
        style.configure('Title.TLabel',
                       background='#2b2b2b',
                       foreground='#ffffff',
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#2b2b2b',
                       foreground='#888888',
                       font=('Segoe UI', 12))
        
        style.configure('Small.TLabel',
                       background='#1f1f1f',
                       foreground='#888888',
                       font=('Segoe UI', 10))
        
        # Button styling
        style.configure('TButton',
                       background='#1f6aa5',
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11))
        
        style.map('TButton',
                 background=[('active', '#1557a0'), ('pressed', '#144a8a')])
        
        style.configure('Secondary.TButton',
                       background='#3a3a3a',
                       foreground='#ffffff')
        
        style.map('Secondary.TButton',
                 background=[('active', '#4a4a4a'), ('pressed', '#2a2a2a')])
        
        # Entry styling
        style.configure('TEntry',
                       fieldbackground='#1f1f1f',
                       foreground='#ffffff',
                       borderwidth=1,
                       relief='solid',
                       insertcolor='#ffffff')
    
    def _create_ui(self):
        """Create UI"""
        debug("LicenseActivationTkinter", "Creating UI")
        
        # Main container
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔑 MultiTeam License Activation",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Activate your license to continue",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Machine ID Card
        machine_uid = self.activation_system.get_machine_uid()
        
        card_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
        card_frame.pack(fill='x', pady=(0, 30))
        
        ttk.Label(
            card_frame,
            text="Machine ID:",
            style='Small.TLabel'
        ).pack(anchor='w')
        
        machine_entry = tk.Entry(
            card_frame,
            bg='#1f1f1f',
            fg='#ffffff',
            font=('Consolas', 11),
            relief='flat',
            state='readonly',
            readonlybackground='#1f1f1f'
        )
        machine_entry.pack(fill='x', pady=(5, 0))
        machine_entry.insert(0, machine_uid)
        
        # Company Name Input
        ttk.Label(
            main_frame,
            text="Company Name:",
            style='TLabel'
        ).pack(anchor='w', pady=(0, 5))
        
        self.company_entry = tk.Entry(
            main_frame,
            bg='#1f1f1f',
            fg='#ffffff',
            font=('Segoe UI', 11),
            relief='solid',
            borderwidth=1,
            insertbackground='#ffffff'
        )
        self.company_entry.pack(fill='x', pady=(0, 15))
        self.company_entry.focus()
        
        # License Key Input
        ttk.Label(
            main_frame,
            text="License Key:",
            style='TLabel'
        ).pack(anchor='w', pady=(0, 5))
        
        self.key_entry = tk.Entry(
            main_frame,
            bg='#1f1f1f',
            fg='#ffffff',
            font=('Consolas', 11),
            relief='solid',
            borderwidth=1,
            insertbackground='#ffffff'
        )
        self.key_entry.pack(fill='x', pady=(0, 30))
        
        # Bind Enter key
        self.company_entry.bind('<Return>', lambda e: self.key_entry.focus())
        self.key_entry.bind('<Return>', lambda e: self._activate())
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill='x')
        
        activate_btn = ttk.Button(
            button_frame,
            text="Activate License",
            command=self._activate,
            style='TButton'
        )
        activate_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._handle_close,
            style='Secondary.TButton'
        )
        cancel_btn.pack(side='left')
    
    def _activate(self):
        """Activate license"""
        company = self.company_entry.get().strip()
        key = self.key_entry.get().strip().upper()
        
        debug("LicenseActivationTkinter", f"Activating license for company: {company}")
        
        # Validate input
        if not company:
            messagebox.showerror("Error", "Please enter your company name", parent=self)
            self.company_entry.focus()
            return
        
        if not key:
            messagebox.showerror("Error", "Please enter a license key", parent=self)
            self.key_entry.focus()
            return
        
        # Get machine UID
        machine_uid = self.activation_system.get_machine_uid()
        
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
            
            # Check if license exists with matching company
            cursor.execute("""
                SELECT * FROM license_applications
                WHERE license_key = ? 
                  AND LOWER(company) = LOWER(?)
                  AND status = 'approved' 
                  AND payment_status = 'paid'
            """, (key, company))
            
            app_data = cursor.fetchone()
            
            if not app_data:
                conn.close()
                messagebox.showerror(
                    "Invalid License",
                    "License key or company name is incorrect.\n\n"
                    "Please check:\n"
                    "- License key format\n"
                    "- Company name spelling\n"
                    "- License status (must be approved and paid)",
                    parent=self
                )
                return
            
            # Check if already activated on this machine
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
                
                info("LicenseActivationTkinter", f"License activated for {company}: {key}")
            
            conn.close()
            
            # Show success
            messagebox.showinfo(
                "License Activated!",
                f"Company: {app_data['company']}\n"
                f"Tier: {app_data['requested_tier']}\n\n"
                f"License successfully activated!",
                parent=self
            )
            
            # Call success callback and close
            if self.on_success:
                self.on_success()
            
            self._handle_close()
            
        except Exception as e:
            error("LicenseActivationTkinter", f"License activation error: {e}")
            messagebox.showerror("Error", f"Activation failed: {e}", parent=self)
    
    def _handle_close(self):
        """Handle window close"""
        debug("LicenseActivationTkinter", "Closing window")
        
        try:
            self.grab_release()
        except:
            pass
        
        try:
            self.destroy()
        except:
            pass
        
        info("LicenseActivationTkinter", "Window closed")


if __name__ == "__main__":
    # Test window
    root = tk.Tk()
    root.geometry("400x300")
    root.title("Test Parent")
    root.configure(bg="#2b2b2b")
    
    def show_window():
        window = LicenseActivationTkinter(
            root,
            on_success=lambda: print("Success!")
        )
    
    btn = tk.Button(root, text="Open License Activation", command=show_window)
    btn.pack(pady=50)
    
    root.mainloop()
