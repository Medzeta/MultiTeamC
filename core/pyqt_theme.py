"""
PyQt6 Global Design System
Centralized theme constants and styling functions
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QHBoxLayout
from core.debug_logger import debug


class Theme:
    """Global design system for PyQt6 - UPPDATERAD VERSION"""
    # Colors
    BACKGROUND = "#1a1a1a"
    SURFACE = "#2b2b2b"
    SURFACE_VARIANT = "#1f1f1f"
    PRIMARY = "#1f6aa5"
    PRIMARY_HOVER = "#2980b9"  # Uppdaterad hover färg
    PRIMARY_PRESSED = "#1557a0"
    SECONDARY = "#3a3a3a"
    SECONDARY_HOVER = "#4a4a4a"
    TEXT = "#ffffff"
    TEXT_SECONDARY = "#888888"
    ERROR = "#d32f2f"
    SUCCESS = "#388e3c"
    WARNING = "#f57c00"
    # Nya färger för uppdaterad design
    INPUT_HOVER = "#5a5a5a"
    CHECKBOX_HOVER = "#4a4a4a"
    BORDER = "#3a3a3a"  # Border färg som saknades
    
    # Spacing constants
    SPACING_XS = 3   # Extremt minimal spacing
    SPACING_SM = 5   # Minimal spacing
    SPACING_MD = 8   # Medium spacing mellan element
    SPACING_LG = 10  # Större spacing
    SPACING_XL = 15  # Maximal spacing
    
    # Title spacing constants
    TITLE_TO_SUBTITLE = -45  # Tight spacing mellan titel och undertitel
    SUBTITLE_TO_SECTION = 5   # Spacing från undertitel till section header (mycket tight som login)
    SECTION_TO_CONTENT = -15  # Tight spacing från section header till innehåll
    SECTION_TO_FIELDS = -30  # Extremt negativ spacing för stor synlig skillnad
    
    # Padding - KOMPAKT
    CARD_PADDING = 20
    CARD_SPACING = 8
    
    # DASHBOARD AUTO-REFRESH SETTINGS
    DASHBOARD_REFRESH_INTERVAL = 5000  # 5000ms = 5 sekunder
    DASHBOARD_ASSETS_DIR = "assets"     # Assets-mapp relativ till projekt-root
    DASHBOARD_SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    
    # GLOBAL CARD SIZE - Alla moduler använder samma storlek
    CARD_WIDTH = 560
    CARD_HEIGHT = 640
    
    # Special spacing for compact layouts (login inputs)
    SPACING_COMPACT = 3  # 1/4 av SPACING_SM
    
    # Border Radius
    RADIUS_SM = 5
    RADIUS_MD = 10
    RADIUS_LG = 15
    
    # Font Sizes
    FONT_XS = 10
    FONT_SM = 11
    FONT_MD = 14
    FONT_XL = 20
    FONT_XXL = 24
    FONT_XXXL = 28
    
    @staticmethod
    def setup_text_field(text_field, placeholder="", height=35):
        """
        Konfigurerar ett textfält enligt UPPDATERAD GLOBAL_DESIGN.md standard
        
        Args:
            text_field: QLineEdit, QComboBox eller QTextEdit widget
            placeholder: Placeholder text (valfritt)
            height: Fixed height för widget (default 35px - standardhöjd för alla fält)
        """
        debug("Theme", f"setup_text_field: Konfigurerar NYTT textfält med placeholder='{placeholder}', height={height}")
        
        # Grundläggande inställningar
        if placeholder:
            text_field.setPlaceholderText(placeholder)
            debug("Theme", f"setup_text_field: Satt placeholder text till '{placeholder}'")
        
        # Sätt höjd för alla typer av widgets utom QTextEdit
        widget_type = type(text_field).__name__
        if widget_type != "QTextEdit":
            text_field.setFixedHeight(height)
            debug("Theme", f"setup_text_field: Satt fixed height till {height}px för {widget_type}")
        
        # GLOBAL STANDARDHÖJD styling - 35px för alla fält
        text_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: #555555;
                color: {Theme.TEXT};
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 35px;
                max-height: 35px;
            }}
            
            QLineEdit:focus {{
                background-color: #5f5f5f;
                border: none;
            }}
            
            QLineEdit:hover {{
                background-color: #5a5a5a;
            }}
            
            QLineEdit::placeholder {{
                color: #888888;
            }}
            
            QTextEdit {{
                background-color: #555555;
                color: {Theme.TEXT};
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 60px;
            }}
            
            QTextEdit:focus {{
                background-color: #5f5f5f;
                border: none;
            }}
            
            QTextEdit:hover {{
                background-color: #5a5a5a;
            }}
            
            QComboBox {{
                background-color: #606060;
                color: {Theme.TEXT};
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                padding-right: 30px;
                font-size: 14px;
                min-height: 35px;
                max-height: 35px;
            }}
            
            QComboBox:hover {{
                background-color: #6a6a6a;
            }}
            
            QComboBox:focus {{
                background-color: #707070;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 25px;
                background-color: transparent;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {Theme.TEXT};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: #606060;
                color: {Theme.TEXT};
                border: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                selection-background-color: #707070;
                selection-color: {Theme.TEXT};
                padding: 4px;
                outline: none;
                show-decoration-selected: 0;
            }}
            
            QComboBox QAbstractItemView::item {{
                min-height: 30px;
                padding: 4px 8px;
                border: none;
                border-radius: 4px;
                background-color: #606060;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: #6a6a6a;
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background-color: #707070;
            }}
            
            QComboBox QAbstractItemView::item:first {{
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }}
            
            QComboBox QAbstractItemView::item:last {{
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 0px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: transparent;
                border: none;
                width: 0px;
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: transparent;
                height: 0px;
                width: 0px;
            }}
            
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {{
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        debug("Theme", "setup_text_field: EXTREMT KOMPAKT - Rundade hörn 3px, minimal padding 4px 8px, höjd 26px")
    
    @staticmethod
    def setup_checkbox(checkbox, text=""):
        """
        Konfigurerar en checkbox enligt ny design som passar appens färger
        
        Args:
            checkbox: QCheckBox widget
            text: Checkbox text (valfritt)
        """
        debug("Theme", f"setup_checkbox: Konfigurerar checkbox med text='{text}'")
        
        if text:
            checkbox.setText(text)
            
        # Använd global stylesheet - ingen extra styling behövs
        debug("Theme", "setup_checkbox: Använder global checkbox styling")
    
    @staticmethod
    def setup_app_title(title_label, subtitle_label):
        """
        Konfigurerar app-titel och undertitel enligt GLOBAL_DESIGN.md
        
        Args:
            title_label: QLabel för huvudtitel
            subtitle_label: QLabel för undertitel
        """
        debug("Theme", "setup_app_title: Konfigurerar app-titel och undertitel")
        
        # Huvudtitel styling
        title_label.setFont(Theme.get_font(size=40, bold=True))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            font-size: 40px;
            font-weight: 900;
            margin: 0px;
            padding: 0px;
        """)
        
        # Undertitel styling med negativ margin för tight layout - subtil och kursiv
        subtitle_font = Theme.get_font(size=17)
        subtitle_font.setItalic(True)  # Kursiv stil
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # CSS styling utan margin - använd bara layout spacing
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.BORDER};
                font-size: 17px;
                font-style: italic;
                font-weight: normal;
                margin: 0px;
                padding: 0px;
            }}
        """)
        
        # Sätt opacity separat för att säkerställa att det appliceras
        subtitle_label.setWindowOpacity(0.7)
        
        debug("Theme", "setup_app_title: Titel konfigurerad (40px, font-weight 900)")
        debug("Theme", "setup_app_title: Undertitel konfigurerad (17px, italic, 70% opacity)")
    
    @staticmethod
    def setup_complete_header_sequence(layout, section_text):
        """
        Skapar HELA header-sekvensen med konsistent spacing
        Titel → Undertitel → Section Header med exakt samma spacing som login
        
        Args:
            layout: QVBoxLayout att lägga till headers i
            section_text: Text för section header ("Sign In", "Create Account" etc.)
        
        Returns:
            tuple: (title_label, subtitle_label, section_label)
        """
        debug("Theme", f"setup_complete_header_sequence: Skapar komplett header för '{section_text}'")
        
        # APP TITLE
        title_label = QLabel("Multi Team -C")
        title_label.setFont(Theme.get_font(size=40, bold=True))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            font-size: 40px;
            font-weight: 900;
            margin: 0px;
            padding: 0px;
        """)
        layout.addWidget(title_label)
        
        # TIGHT SPACING MELLAN TITEL OCH UNDERTITEL
        layout.addSpacing(-45)  # Hårdkodat som login använder
        
        # APP SUBTITLE
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        subtitle_font = Theme.get_font(size=17)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            color: {Theme.BORDER};
            font-size: 17px;
            font-style: italic;
            font-weight: normal;
            margin: 0px;
            padding: 0px;
        """)
        subtitle_label.setWindowOpacity(0.7)
        layout.addWidget(subtitle_label)
        
        # SPACING MELLAN UNDERTITEL OCH SECTION (EXAKT SOM LOGIN)
        layout.addSpacing(25)  # Hårdkodat som login ursprungligen hade
        
        # SECTION HEADER (samma styling som add_section_header)
        section_row = QHBoxLayout()
        section_row.addSpacing(-5)
        
        section_label = QLabel(section_text)
        section_label.setFont(Theme.get_font(size=20, bold=True))
        section_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        section_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            font-size: 20px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        section_row.addWidget(section_label)
        section_row.addStretch()
        
        layout.addLayout(section_row)
        
        debug("Theme", f"setup_complete_header_sequence: Komplett header skapad för '{section_text}'")
        return (title_label, subtitle_label, section_label)
    
    @staticmethod
    def add_section_header(layout, text):
        """
        GLOBAL SECTION HEADER FUNKTION
        Lägger till en section header direkt i layout med korrekt spacing
        
        Args:
            layout: QVBoxLayout att lägga till header i
            text: Header text ("Sign In", "Create Account" etc.)
        
        Returns:
            QLabel: Den skapade header-labeln
        """
        debug("Theme", "="*60)
        debug("Theme", f"add_section_header: STARTAR global section header creation")
        debug("Theme", f"add_section_header: Header text: '{text}'")
        debug("Theme", f"add_section_header: Layout type: {type(layout).__name__}")
        debug("Theme", f"add_section_header: Layout spacing: {layout.spacing()}px")
        debug("Theme", f"add_section_header: Layout margins: {layout.contentsMargins()}")
        
        # Skapa header label med global styling
        debug("Theme", f"add_section_header: Skapar QLabel för '{text}'")
        header_label = QLabel(text)
        
        # Konfigurera font
        debug("Theme", f"add_section_header: Konfigurerar font (20px, bold)")
        font = Theme.get_font(size=20, bold=True)
        header_label.setFont(font)
        debug("Theme", f"add_section_header: Font satt - Family: {font.family()}, Size: {font.pointSize()}, Bold: {font.bold()}")
        
        # Konfigurera alignment
        debug("Theme", f"add_section_header: Sätter alignment till AlignLeft")
        header_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Konfigurera CSS styling
        debug("Theme", f"add_section_header: Applicerar CSS styling")
        css_style = f"""
            color: {Theme.TEXT};
            margin: 0px;
            padding: 0px;
            font-size: 20px;
            font-weight: bold;
        """
        header_label.setStyleSheet(css_style)
        debug("Theme", f"add_section_header: CSS applicerad - Color: {Theme.TEXT}, Size: 20px, Weight: bold")
        
        # Lägg till header i layout
        debug("Theme", f"add_section_header: Lägger till header i layout")
        layout.addWidget(header_label)
        debug("Theme", f"add_section_header: Header tillagd i layout - Widget count: {layout.count()}")
        
        # Lägg till ett enterslag mellanrum (15px)
        debug("Theme", f"add_section_header: Lägger till 15px spacing efter header")
        layout.addSpacing(15)
        debug("Theme", f"add_section_header: Spacing tillagt - Total layout items: {layout.count()}")
        
        # Verifiera header-label egenskaper
        debug("Theme", f"add_section_header: VERIFIERING - Header text: '{header_label.text()}'")
        debug("Theme", f"add_section_header: VERIFIERING - Header font size: {header_label.font().pointSize()}px")
        debug("Theme", f"add_section_header: VERIFIERING - Header alignment: {header_label.alignment()}")
        debug("Theme", f"add_section_header: VERIFIERING - Header visible: {header_label.isVisible()}")
        debug("Theme", f"add_section_header: VERIFIERING - Header size hint: {header_label.sizeHint()}")
        
        debug("Theme", f"add_section_header: ✅ SLUTFÖRD - Global section header '{text}' skapad och tillagd")
        debug("Theme", f"add_section_header: ✅ RESULTAT - 20px bold vänsterjusterad header + 15px spacing")
        debug("Theme", "="*60)
        
        return header_label
    
    @staticmethod
    def setup_secondary_text(label, size=11, margin_bottom=None):
        """
        GLOBAL SECONDARY TEXT STYLING
        För instruktioner, beskrivningar och hjälptext
        
        Args:
            label: QLabel att styla
            size: Font storlek (default 11)
            margin_bottom: Bottom margin i px (optional)
        """
        debug("Theme", f"setup_secondary_text: Styling secondary text (size={size})")
        
        label.setFont(Theme.get_font(size=size))
        
        style = f"color: {Theme.TEXT_SECONDARY};"
        if margin_bottom is not None:
            style += f" margin-bottom: {margin_bottom}px;"
        
        label.setStyleSheet(style)
        label.setWordWrap(True)
        
        debug("Theme", f"setup_secondary_text: Secondary text styled with size {size}")
    
    @staticmethod
    def setup_info_box(widget, padding=8):
        """
        GLOBAL INFO BOX STYLING
        För QR kod areas, backup codes, etc.
        
        Args:
            widget: QLabel eller QTextEdit att styla
            padding: Padding i px (default 8)
        """
        debug("Theme", f"setup_info_box: Styling info box with padding {padding}px")
        
        widget.setStyleSheet(f"""
            QLabel, QTextEdit {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: {padding}px;
                color: {Theme.TEXT};
            }}
        """)
        
        debug("Theme", f"setup_info_box: Info box styled")
    
    @staticmethod
    def setup_field_label(label, width=80):
        """
        GLOBAL FIELD LABEL STYLING
        För "Name:", "Email:", etc. labels
        
        Args:
            label: QLabel att styla
            width: Min width i px (default 80)
        """
        debug("Theme", f"setup_field_label: Styling field label with width {width}px")
        
        label.setFont(Theme.get_font(size=12))
        label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: {width}px;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        debug("Theme", f"setup_field_label: Field label styled")
    
    @staticmethod
    def setup_scroll_area(scroll_area):
        """
        GLOBAL SCROLL AREA STYLING
        För transparent scroll areas
        
        Args:
            scroll_area: QScrollArea att styla
        """
        debug("Theme", f"setup_scroll_area: Styling scroll area")
        
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        debug("Theme", f"setup_scroll_area: Scroll area styled")

    @staticmethod
    def setup_login_button(button, width=90):
        """
        Konfigurerar en login-knapp enligt GLOBAL_DESIGN.md standard
        
        Args:
            button: QPushButton widget
            width: Knappens bredd (default 90px)
        """
        debug("Theme", f"setup_login_button: Konfigurerar login-knapp (width={width}px)")
        
        # Sätt storlek och cursor
        button.setFixedSize(width, 25)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Subtil button styling - ljusgrå med 20% transparens, mörk vid hover/press
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(58, 58, 58, 0.2);
                color: {Theme.TEXT};
                border: 1px solid rgba(58, 58, 58, 0.3);
                border-radius: 8px;
                font-size: 14px;
                font-weight: 400;
                padding: 1px 6px;
                min-height: 25px;
                max-height: 25px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                color: {Theme.TEXT};
            }}
            QPushButton:pressed {{
                background-color: {Theme.BACKGROUND};
                border: 1px solid {Theme.BORDER};
            }}
        """)
        
        debug("Theme", "setup_login_button: Login-knapp konfigurerad (90x25px, 8px radius, 20% transparent)")
    
    @staticmethod
    def setup_tall_button(button, width=90, height=50):
        """
        Konfigurerar en hög knapp för flerrads-text enligt GLOBAL_DESIGN.md
        Dubbelt så hög som vanliga knappar (25px -> 50px)
        
        Args:
            button: QPushButton widget
            width: Knappens bredd (default 90px - samma som vanliga knappar)
            height: Knappens höjd (default 50px - dubbelt så hög som vanliga)
        """
        debug("Theme", f"setup_tall_button: Konfigurerar hög knapp (width={width}px, height={height}px)")
        
        # Sätt storlek och cursor - samma logik som setup_login_button men dubbel höjd
        button.setFixedSize(width, height)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Tall button styling - samma som login button men dubbel höjd
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(58, 58, 58, 0.2);
                color: {Theme.TEXT};
                border: 1px solid rgba(58, 58, 58, 0.3);
                border-radius: 8px;
                font-size: 14px;
                font-weight: 400;
                padding: 4px 6px;
                min-height: {height}px;
                max-height: {height}px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                color: {Theme.TEXT};
            }}
            QPushButton:pressed {{
                background-color: {Theme.BACKGROUND};
                border: 1px solid {Theme.BORDER};
            }}
        """)
        
        debug("Theme", f"setup_tall_button: Hög knapp konfigurerad ({width}x{height}px, dubbel höjd för flerrads-text)")
    
    @staticmethod
    def get_compact_card_settings():
        """
        Returnerar kompakta card-inställningar
        
        Returns:
            dict: Card inställningar
        """
        return {
            'width': 420,
            'height': 520,  # Uppdaterad för att inkludera Multi Team -C title + subtitle
            'padding': Theme.CARD_PADDING,
            'spacing': Theme.CARD_SPACING,
            'border_radius': 12
        }
    
    @staticmethod
    def get_stylesheet():
        """
        Get global QSS stylesheet
{{ ... }}
        
        Returns:
            str: Complete QSS stylesheet
        """
        debug("Theme", "Generating global stylesheet")
        
        return f"""
            /* Global */
            * {{
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: {Theme.FONT_MD}px;
            }}
            
            /* Main Window */
            QMainWindow {{
                background-color: {Theme.BACKGROUND};
            }}
            
            /* Frames/Containers */
            QFrame {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_MD}px;
            }}
            
            QFrame[transparent="true"] {{
                background-color: transparent;
                border: none;
            }}
            
            /* Labels */
            QLabel {{
                color: {Theme.TEXT};
                background-color: transparent;
                border: none;
            }}
            
            QLabel[heading="true"] {{
                font-size: {Theme.FONT_XXL}px;
                font-weight: bold;
            }}
            
            QLabel[title="true"] {{
                font-size: {Theme.FONT_XL}px;
                font-weight: bold;
            }}
            
            QLabel[caption="true"] {{
                font-size: {Theme.FONT_SM}px;
                color: {Theme.TEXT_SECONDARY};
            }}
            
            /* Buttons - UPPDATERAD DESIGN */
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.TEXT};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-height: 45px;
            }}
            
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
            
            QPushButton:pressed {{
                background-color: {Theme.PRIMARY_PRESSED};
            }}
            
            QPushButton[secondary="true"] {{
                background-color: {Theme.SECONDARY};
                color: {Theme.TEXT};
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                min-height: 42px;
            }}
            
            QPushButton[secondary="true"]:hover {{
                background-color: {Theme.SECONDARY_HOVER};
            }}
            
            QPushButton[secondary="true"]:pressed {{
                background-color: #2a2a2a;
            }}
            
            QPushButton[danger="true"] {{
                background-color: {Theme.ERROR};
            }}
            
            QPushButton[success="true"] {{
                background-color: {Theme.SUCCESS};
            }}
            
            /* Input Fields - EXTREMT KOMPAKT DESIGN */
            QLineEdit {{
                background-color: #555555;
                color: {Theme.TEXT};
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 26px;
                max-height: 26px;
            }}
            
            QLineEdit:focus {{
                background-color: #5f5f5f;
                border: none;
            }}
            
            QLineEdit:hover {{
                background-color: #5a5a5a;
            }}
            
            QTextEdit {{
                background-color: #555555;
                color: {Theme.TEXT};
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 60px;
            }}
            
            QTextEdit:focus {{
                background-color: #5f5f5f;
                border: none;
            }}
            QTextEdit:hover {{
                background-color: #5a5a5a;
            }}
            
            /* Checkboxes - NY DESIGN SOM PASSAR APPENS FÄRGER */
            QCheckBox {{
                color: {Theme.TEXT};
                font-size: 14px;
                spacing: 8px;
                padding: 6px 0px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #555555;
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid #666666;
                background-color: #5a5a5a;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: #888888;
                border: 2px solid #999999;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTEiIHZpZXdCb3g9IjAgMCAxNCAxMSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEgNS41TDUgOS41TDEzIDEuNSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjIuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
            
            QCheckBox::indicator:checked:hover {{
                background-color: #999999;
                border: 2px solid #aaaaaa;
            }}
            
            /* Scrollbars - FULLT OSYNLIG MEN FUNGERANDE */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 0px;
                border: none;
                margin: 0px;
                background-color: transparent;
                border: none;
                border-radius: 0px;
                min-height: 0px;
                max-height: 0px;
                width: 0px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: transparent;
                border: none;
                width: 0px;
            }}
            
            QScrollBar::add-line:vertical {{
                background-color: transparent;
                border: none;
                height: 0px;
                width: 0px;
            }}
            
            QScrollBar::sub-line:vertical {{
                background-color: transparent;
                border: none;
                height: 0px;
                width: 0px;
            }}
            
            QScrollBar::add-page:vertical {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollBar::sub-page:vertical {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollBar:horizontal {{
                background-color: transparent;
                height: 0px;
                border: none;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: transparent;
                border: none;
                border-radius: 0px;
                min-width: 0px;
                max-width: 0px;
                height: 0px;
            }}
            
            /* Scroll Area */
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            /* Combo Box */
            QComboBox {{
                background-color: {Theme.SURFACE_VARIANT};
                color: {Theme.TEXT};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_SM}px;
                padding: 8px;
            }}
            
            QComboBox:focus {{
                border: 1px solid {Theme.PRIMARY};
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT};
                selection-background-color: {Theme.PRIMARY};
                border: 1px solid {Theme.BORDER};
            }}
        """
    
    @staticmethod
    def setup_invisible_scrollbar(scroll_area):
        """
        Konfigurerar en QScrollArea med helt osynlig scrollbar
        
        Args:
            scroll_area: QScrollArea objekt att konfigurera
        """
        # Stäng av scrollbar policies helt
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Applicera expressiv QSS styling för att dölja alla scrollbar-element
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            /* Helt osynlig scrollbar */
            QScrollBar:vertical {
                background-color: transparent !important;
                width: 0px !important;
                border: none !important;
                margin: 0px !important;
            }
            
            QScrollBar::handle:vertical {
                background-color: transparent !important;
                border: none !important;
                border-radius: 0px !important;
                min-height: 0px !important;
                max-height: 0px !important;
                width: 0px !important;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: transparent !important;
                border: none !important;
                width: 0px !important;
            }
            
            QScrollBar::add-line:vertical {
                background-color: transparent !important;
                border: none !important;
                height: 0px !important;
                width: 0px !important;
            }
            
            QScrollBar::sub-line:vertical {
                background-color: transparent !important;
                border: none !important;
                height: 0px !important;
                width: 0px !important;
            }
            
            QScrollBar::add-page:vertical {
                background-color: transparent !important;
                border: none !important;
            }
            
            QScrollBar::sub-page:vertical {
                background-color: transparent !important;
                border: none !important;
            }
            
            /* Samma för horizontal scrollbar */
            QScrollBar:horizontal {
                background-color: transparent !important;
                height: 0px !important;
                border: none !important;
                margin: 0px !important;
            }
            
            QScrollBar::handle:horizontal {
                background-color: transparent !important;
                border: none !important;
                border-radius: 0px !important;
                min-width: 0px !important;
                max-width: 0px !important;
                height: 0px !important;
            }
        """)

    @staticmethod
    def get_font(size=FONT_MD, bold=False):
        """
        Get Font with specified properties
        
        Args:
            size: Font size
            bold: Bold font
            
        Returns:
            Font: Configured font
        """
        font = QFont("Segoe UI", size)
        if bold:
            font.setBold(True)
        return font
    
    @staticmethod
    def create_login_card_style():
        """
        Skapar CSS för login card enligt uppdaterad GLOBAL_DESIGN.md
        UTAN border men MED ljusare bakgrund för att synas som kort
        
        Returns:
            str: CSS styling för login card
        """
        return f"""
            QFrame {{
                background-color: {Theme.SURFACE};
                border: none;
                border-radius: 12px;
            }}
        """


# Export
__all__ = ['Theme']
