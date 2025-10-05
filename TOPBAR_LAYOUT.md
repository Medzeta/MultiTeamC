# 📊 TOPBAR LAYOUT - Multi Team -C

## Visuell Layout (75px höjd)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Multi Team -C v0.26                                    ●●● [Logga ut]       │
│ Användarnamn ●                                                              │
│ DESKTOP-ABC | UID: aa:bb:cc:dd:ee:ff                                        │
│ Team: 3/5 online • Peers: 12/18 online                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Rad-för-Rad Beskrivning

### **Rad 1: App Titel + Version + Controls**
- **Vänster:** `Multi Team -C v0.26`
  - Font: 14px, font-weight: 500
  - Färg: #ffffff (TEXT)
  - **Version hämtas dynamiskt från `core/version.py`**
  
- **Höger:** Window Controls
  - **Färgade cirklar:** Grön (Minimize) • Gul (Maximize) • Röd (Close)
  - **Logout knapp:** 90x25px, under cirklarna

### **Rad 2: Användarnamn + Login Status**
- **Text:** Användarnamn (eller "Ej inloggad")
  - Font: 11px
  - Färg: #b0b0b0 (TEXT_SECONDARY)
  
- **Status indikator:** ●
  - Grön (#388e3c) - Online
  - Gul (#f5c542) - Away
  - Röd (#d32f2f) - Offline
  - Grå (#888888) - Ej inloggad

### **Rad 3: Machine UID**
- **Format:** `DESKTOP-ABC | UID: aa:bb:cc:dd:ee:ff`
  - Font: 10px
  - Färg: #b0b0b0 (TEXT_SECONDARY)
  - **Datornamn:** Hämtas från `platform.node()`
  - **MAC-adress:** Hämtas från `uuid.getnode()`

### **Rad 4: Team & Peers Status**
- **Format:** `Team: 3/5 online • Peers: 12/18 online`
  - Font: 9px
  - Färg: #b0b0b0 (TEXT_SECONDARY)
  - **Team:** Antal online i teamet / Totalt antal i teamet
  - **Peers:** Antal online peers / Totalt antal peers
  - **Färgkodning:**
    - Online siffror: Grön (#388e3c)
    - Offline siffror: Grå (#666666)

## Teknisk Implementation

### Version Display
```python
from core.version import get_version

app_version = get_version()  # Hämtar från APP_VERSION i version.py
title_with_version = f"Multi Team -C v{app_version}"
```

### Dynamisk Uppdatering
- **Version:** Hämtas vid titlebar initialization
- **Username:** Uppdateras via `update_user_info(username, status)`
- **Team/Peers:** Uppdateras via `update_peer_stats(team_online, team_total, peers_online, peers_total)`
- **Machine UID:** Sätts en gång vid initialization

## Exempel på Olika States

### **Ej Inloggad:**
```
Multi Team -C v0.26                                    ●●● [Logga ut]
Ej inloggad ●
DESKTOP-ABC | UID: aa:bb:cc:dd:ee:ff
Team: 1/1 online • Peers: 1/1 online
```

### **Inloggad (SuperAdmin):**
```
Multi Team -C v0.26                                    ●●● [Logga ut]
SuperAdmin ●
DESKTOP-ABC | UID: aa:bb:cc:dd:ee:ff
Team: 3/5 online • Peers: 12/18 online
```

### **Inloggad (Normal User):**
```
Multi Team -C v0.26                                    ●●● [Logga ut]
John Doe ●
DESKTOP-ABC | UID: aa:bb:cc:dd:ee:ff
Team: 3/5 online • Peers: 12/18 online
```

## Styling Detaljer

### Färgschema
- **Background:** #1a1a1a (BACKGROUND)
- **Text Primary:** #ffffff (TEXT)
- **Text Secondary:** #b0b0b0 (TEXT_SECONDARY)
- **Status Online:** #388e3c (SUCCESS)
- **Status Away:** #f5c542 (WARNING)
- **Status Offline:** #d32f2f (ERROR)
- **Status Unknown:** #888888

### Spacing
- **Höjd:** 75px (fast)
- **Padding:** 15px left, 8px top
- **Rad-spacing:** 1px mellan rader
- **Border-radius:** 15px (endast top corners)

### Window Controls
- **Cirklar:** 18x18px
- **Spacing:** 12px mellan cirklar
- **Logout knapp:** 90x25px
- **Container höjd:** 65px (för att hela knappen ska synas)

## Auto-Update Integration

När en ny version finns tillgänglig:
1. **Auto-Update Manager** kollar GitHub API
2. **Tvingande popup** visas med progress bar
3. **Uppdatering laddas ner** och installeras
4. **App startar om** automatiskt
5. **Ny version** visas i topbaren efter omstart

Exempel: `Multi Team -C v0.26` → `Multi Team -C v0.27` efter uppdatering

## Framtida Förbättringar

- [ ] Real-time P2P network stats (ersätt simulerade värden)
- [ ] Klickbar version för att visa changelog
- [ ] Tooltip med mer detaljerad versionsinformation
- [ ] Animerad övergång när version uppdateras
- [ ] Notification badge för tillgängliga uppdateringar
