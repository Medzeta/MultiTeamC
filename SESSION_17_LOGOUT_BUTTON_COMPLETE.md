# SESSION 17 - LOGOUT-KNAPP IMPLEMENTATION KOMPLETT

**Datum:** 2025-10-05  
**Status:** ✅ KOMPLETT

---

## HUVUDUPPGIFT

### **Uppgift:**
Implementera en subtil logout-knapp i titelbaren som använder exakt samma globala design som alla andra knappar i applikationen.

### **Krav:**
- Placerad under de färgade cirklarna (Grön-Gul-Röd)
- Använd Theme.setup_login_button() - ingen custom styling
- Exakt samma storlek som alla globala knappar (90x25px)
- Hela knappen inklusive ram måste synas (ingen clipping)
- Funktionalitet: Logga ut användare och visa login-skärm

---

## IMPLEMENTATION

### **1. Titlebar Layout Omstrukturerad:**

```python
# Vertikal layout för cirklar + logout
controls_container = QWidget()
controls_container.setFixedHeight(65)  # Tillräckligt för cirklar + knapp + margin
controls_main_layout = QVBoxLayout(controls_container)
controls_main_layout.setContentsMargins(0, 0, 0, 10)  # 10px bottom margin
controls_main_layout.setSpacing(8)  # 8px mellan cirklar och logout

# Färgade cirklar överst
circles_widget = QWidget()
circles_layout = QHBoxLayout(circles_widget)
circles_layout.addWidget(minimize_btn)
circles_layout.addWidget(maximize_btn)
circles_layout.addWidget(close_btn)

# Logout-knapp under
self.logout_btn = QPushButton("Logga ut")
Theme.setup_login_button(self.logout_btn, width=90)  # Global funktion!
self.logout_btn.clicked.connect(self.logout_clicked.emit)
controls_main_layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignRight)
```

### **2. Signal System:**

```python
# CustomTitleBar
logout_clicked = pyqtSignal()  # Signal för logout

# main_pyqt.py
self.window.titlebar.logout_clicked.connect(self._handle_logout)

def _handle_logout(self):
    # Clear current user
    self.current_user = None
    
    # Reset titlebar user info
    self.window.titlebar.update_user_info(None)
    
    # Show login module
    self._show_login()
```

---

## TEKNISKA DETALJER

### **Container Dimensioner:**

- **Total höjd:** 65px
- **Cirklar:** 18px höjd
- **Spacing:** 8px mellan cirklar och knapp
- **Knapp:** 25px höjd (Theme.setup_login_button standard)
- **Bottom margin:** 10px (för att hela knappen ska synas)
- **Extra utrymme:** 4px

**Beräkning:** 18 + 8 + 25 + 10 + 4 = 65px

### **Knapp Specifikation:**

```python
# Från Theme.setup_login_button(width=90)
Storlek: 90x25px
Bakgrund: rgba(58, 58, 58, 0.2) - 20% transparent
Border: 1px solid rgba(58, 58, 58, 0.3)
Border-radius: 8px
Font: 14px, weight 400
Padding: 1px 6px
Hover: #2b2b2b solid
Press: #1a1a1a solid
```

### **Alignment:**

- **Horisontell:** AlignRight (höger-justerad)
- **Vertikal:** Under färgade cirklar
- **Container:** AlignTop i titlebar

---

## ITERATIONSPROCESS

### **Försök 1 - Custom Styling (70px bredd):**
- **Problem:** Texten "Logga ut" klipptes av
- **Lösning:** Ökade bredd till 80px

### **Försök 2 - Custom Styling (80px bredd):**
- **Problem:** Texten syntes men knappen var för låg (25px)
- **Lösning:** Ökade höjd till 30px

### **Försök 3 - Custom Styling (100x30px):**
- **Problem:** Knappen blev för stor och såg inte bra ut
- **Feedback:** "nu blev knappen sämre"
- **Lösning:** Återgå till global funktion

### **Försök 4 - Global Funktion (90x25px):**
- **Problem:** Texten "Logga ut" klipptes av i 90px bredd
- **Lösning:** Ökade bredd till 100px

### **Försök 5 - Global Funktion (100x25px):**
- **Problem:** Knappen klipptes av i botten (container för låg)
- **Lösning:** Ökade container från 55px till 60px + 5px bottom margin

### **Försök 6 - Global Funktion (100x25px, 60px container):**
- **Problem:** Fortfarande inte hela knappen synlig
- **Feedback:** "man ser fortfarande inte hela knappen men det blev bättre"
- **Lösning:** Ökade container till 65px + 10px bottom margin

### **Försök 7 - Global Funktion (90x25px, 65px container):**
- **Resultat:** ✅ PERFEKT!
- **Feedback:** "nu syns den perfekt"
- **Slutlig lösning:** Theme.setup_login_button(width=90) med 65px container och 10px bottom margin

---

## SLUTLIG LÖSNING

### **Knapp:**
```python
self.logout_btn = QPushButton("Logga ut")
Theme.setup_login_button(self.logout_btn, width=90)  # Exakt global funktion
self.logout_btn.clicked.connect(self.logout_clicked.emit)
```

### **Container:**
```python
controls_container.setFixedHeight(65)  # Tillräckligt utrymme
controls_main_layout.setContentsMargins(0, 0, 0, 10)  # 10px bottom margin
controls_main_layout.setSpacing(8)  # 8px mellan cirklar och logout
```

### **Funktionalitet:**
```python
def _handle_logout(self):
    self.current_user = None
    self.window.titlebar.update_user_info(None)
    self._show_login()
```

---

## RESULTAT

### **Visuellt:**

✅ **90x25px** - Exakt samma storlek som alla globala knappar  
✅ **Hela knappen syns** - Ingen clipping av text eller ram  
✅ **Global styling** - Theme.setup_login_button() används  
✅ **Subtil placering** - Under färgade cirklar  
✅ **Höger-justerad** - AlignRight alignment  

### **Funktionellt:**

✅ **Logout signal** - pyqtSignal() system  
✅ **Rensar användare** - current_user = None  
✅ **Återställer titlebar** - "Ej inloggad" status  
✅ **Visar login** - Tillbaka till login-skärm  
✅ **Signal-baserad** - Clean separation of concerns  

### **Tekniskt:**

✅ **100% global kod** - Ingen custom styling  
✅ **Konsistent design** - Samma som alla knappar  
✅ **Korrekt spacing** - 65px container med 10px margin  
✅ **Debug logging** - Komplett logging av logout  

---

## FILER MODIFIERADE

### **core/pyqt_window_new.py:**
- Lagt till `logout_clicked` signal i CustomTitleBar
- Omstrukturerat controls layout till vertikal (cirklar + logout)
- Implementerat logout-knapp med Theme.setup_login_button()
- Justerat container-höjd till 65px med 10px bottom margin

### **main_pyqt.py:**
- Kopplat `logout_clicked` signal till `_handle_logout()`
- Implementerat `_handle_logout()` funktion
- Rensar current_user och återställer titlebar
- Visar login-modul efter logout

### **GLOBAL_DESIGN.md:**
- Dokumenterat logout-knapp specifikation
- Placering, storlek, funktion och alignment
- Container-dimensioner och margin-krav

### **ROADMAP.md:**
- Uppdaterat "PERFEKT RUNDADE HÖRN" sektion
- Lagt till "Logout-Knapp Implementation" undersektion
- Dokumenterat alla tekniska detaljer

---

## LESSONS LEARNED

### **Global Design är Viktigt:**
- Custom styling blev "sämre" enligt användaren
- Global funktion ger konsistent design
- Använd alltid Theme.setup_* funktioner

### **Container Sizing:**
- Behöver extra utrymme för margins
- 10px bottom margin krävdes för att hela knappen skulle synas
- 65px container = 18 (cirklar) + 8 (spacing) + 25 (knapp) + 10 (margin) + 4 (extra)

### **Iterativ Process:**
- 7 försök innan perfekt lösning
- Viktigt att lyssna på användarfeedback
- "nu syns den perfekt" = rätt lösning

### **Signal/Slot System:**
- Clean separation mellan UI och logik
- Lätt att testa och underhålla
- Modulärt och återanvändbart

---

## FRAMTIDA ANVÄNDNING

### **Alla Knappar i Titlebar:**
- Använd samma container-approach
- 65px höjd med 10px bottom margin
- Theme.setup_login_button() för styling

### **Andra Window Controls:**
- Samma vertikal layout-pattern
- Cirklar överst, knappar under
- Konsistent spacing (8px)

### **Signal System:**
- Använd pyqtSignal för alla window-actions
- Koppla i main_pyqt.py
- Håll UI och logik separerad

---

## STATUS

✅ **Logout-knapp:** Perfekt implementerad med global styling  
✅ **Placering:** Under färgade cirklar, höger-justerad  
✅ **Storlek:** 90x25px - exakt samma som alla knappar  
✅ **Funktionalitet:** Loggar ut och visar login-skärm  
✅ **Dokumentation:** GLOBAL_DESIGN.md och ROADMAP uppdaterade  

**SLUTSTATUS:** Logout-knapp komplett implementerad med 100% global styling enligt Theme.setup_login_button() - användaren bekräftade "nu syns den perfekt"!
