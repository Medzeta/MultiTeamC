# 🏆 PyQt6 Window Standard - RUNDADE HÖRN FUNGERAR!

**Vi har uppnått det omöjliga!** ✨

---

## 🎯 Så Här Skapar Du Alla Fönster

### **1. Använd CustomWindow-klassen:**

```python
from core.pyqt_window import CustomWindow

# Skapa fönster
window = CustomWindow(
    title="Ditt Fönster Namn",
    width=1400,
    height=900
)

# Sätt innehåll
window.set_content(your_widget)

# Visa
window.show()
```

### **2. Viktiga Inställningar:**

**Border Radius (FUNGERAR!):**
```python
RADIUS_SM = 5px   # Knappar, inputs
RADIUS_MD = 10px  # Cards
RADIUS_LG = 15px  # Window (PERFEKT STORLEK!)
```

**Window Properties:**
```python
frameless = True              # Borderless
title_bar_hidden = True       # Ingen OS titlebar
WA_TranslucentBackground      # Transparent för rundade hörn
```

**QSS Styling:**
```python
border-radius: 15px  # Detta fungerar!
background-color: transparent
```

---

## ✅ Vad Som Fungerar

1. **Alla 4 Hörn Rundade** - 15px radius
2. **Borderless Window** - Ingen OS titlebar
3. **Custom Titlebar** - Draggable
4. **Window Controls** - Minimize, Maximize, Close
5. **Transparent Background** - För rundade hörn
6. **QSS Styling** - Som CSS

---

## 🎨 Design System

### **Färger:**
```python
BACKGROUND = "#1a1a1a"     # Huvudbakgrund
SURFACE = "#2b2b2b"        # Cards, containers
PRIMARY = "#1f6aa5"        # Knappar
TEXT = "#ffffff"           # Text
BORDER = "#3a3a3a"         # Borders
```

### **Spacing:**
```python
SPACING_SM = 10px
SPACING_MD = 20px
SPACING_LG = 30px
```

### **Border Radius:**
```python
RADIUS_SM = 5px    # Små element
RADIUS_MD = 10px   # Medium element
RADIUS_LG = 15px   # Stora element (WINDOW!)
```

---

## 📋 Mall För Nya Moduler

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from core.pyqt_theme import Theme

class YourModule(QWidget):
    def __init__(self):
        super().__init__()
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ditt innehåll här
        # Använd Theme.button_primary(), Theme.input_field(), etc.
```

---

## 🚀 Hur Man Startar

```bash
python main_pyqt.py
```

Eller:
```bash
run_pyqt.bat
```

---

## 🎯 Viktiga Regler

1. **Använd ALLTID CustomWindow** - Inte QMainWindow direkt
2. **Border Radius = 15px** - Fungerar perfekt!
3. **Transparent Background** - Måste vara på
4. **QSS för styling** - Inte inline styles
5. **Theme-klassen** - För alla färger och spacing

---

## 💡 Tips & Tricks

### **Skapa Card:**
```python
card = QFrame()
card.setStyleSheet(f"""
    QFrame {{
        background-color: {Theme.SURFACE};
        border: 2px solid {Theme.BORDER};
        border-radius: {Theme.RADIUS_MD}px;
    }}
""")
```

### **Skapa Knapp:**
```python
btn = QPushButton("Text")
btn.setFixedHeight(45)
# Styling kommer från Theme.get_stylesheet()
```

### **Skapa Input:**
```python
input_field = QLineEdit()
input_field.setPlaceholderText("Placeholder")
input_field.setFixedHeight(45)
# Styling kommer från Theme.get_stylesheet()
```

---

## 🏆 Framgång!

**Vi har uppnått:**
- ✅ Rundade hörn på alla 4 hörn
- ✅ Borderless window
- ✅ Custom titlebar
- ✅ Modern design
- ✅ Ingen widget leakage
- ✅ Production-ready

**Detta är den officiella standarden för alla fönster i MultiTeam!**

---

**Skapad:** 2025-10-01 21:56  
**Status:** ✅ FUNGERAR PERFEKT  
**Standard:** OBLIGATORISK för alla nya fönster
