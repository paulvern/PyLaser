#!/usr/bin/env python3
"""
help_content.py
Contenuto dell'help multilingua per Laser Engraver Pro v3.0
"""

from dataclasses import dataclass


@dataclass
class HelpContent:
    """Contenuto dell'help per una lingua."""
    
    # ── Titoli sezioni ────────────────────────────────────────────────────────
    title_main           : str = ""
    title_getting_started: str = ""
    title_image          : str = ""
    title_vectorize      : str = ""
    title_position       : str = ""
    title_laser          : str = ""
    title_simulation     : str = ""
    title_shortcuts      : str = ""
    title_troubleshooting: str = ""
    title_gcode          : str = ""
    title_safety         : str = ""
    
    # ── Contenuti ─────────────────────────────────────────────────────────────
    getting_started      : str = ""
    image_section        : str = ""
    vectorize_section    : str = ""
    position_section     : str = ""
    laser_section        : str = ""
    simulation_section   : str = ""
    shortcuts_section    : str = ""
    troubleshooting      : str = ""
    gcode_section        : str = ""
    safety_section       : str = ""


# ══════════════════════════════════════════════════════════════════════════════
#  HELP ITALIANO
# ══════════════════════════════════════════════════════════════════════════════
HELP_IT = HelpContent(
    title_main           = "Guida Laser Engraver Pro",
    title_getting_started= "🚀 Guida Rapida",
    title_image          = "🖼 Gestione Immagini",
    title_vectorize      = "✏ Vettorizzazione",
    title_position       = "📍 Posizionamento",
    title_laser          = "🔥 Controllo Laser",
    title_simulation     = "🎬 Simulazione",
    title_shortcuts      = "⌨ Scorciatoie",
    title_troubleshooting= "🔧 Risoluzione Problemi",
    title_gcode          = "📄 Comandi GCode",
    title_safety         = "⚠ Sicurezza",
    
    getting_started = """
GUIDA RAPIDA - PRIMI PASSI
══════════════════════════════════════════════════════════════

1️⃣  CARICA UN'IMMAGINE
    • Clicca "Apri immagine" o usa File → Apri immagine
    • Formati supportati: PNG, JPG, BMP, TIFF, GIF, WebP

2️⃣  REGOLA L'IMMAGINE
    • Usa la soglia (threshold) per controllare il bianco/nero
    • Ruota o specchia l'immagine se necessario
    • Attiva "Inverti colori" per immagini su sfondo scuro

3️⃣  IMPOSTA LE DIMENSIONI
    • Vai alla scheda "Vettorizza"
    • Inserisci larghezza e altezza in millimetri
    • Scegli il metodo di vettorizzazione

4️⃣  GENERA IL GCODE
    • Clicca "🚀 Genera GCode"
    • Controlla l'anteprima nell'area di lavoro
    • Sposta il modello trascinandolo con il mouse

5️⃣  TESTA CON LA SIMULAZIONE
    • Prima di incidere, usa "▶ Avvia sim."
    • Verifica che il percorso sia corretto

6️⃣  CONNETTI IL LASER
    • Vai alla scheda "Laser"
    • Seleziona la porta COM
    • Clicca "Connetti"

7️⃣  INCIDI!
    • Posiziona il materiale sotto il laser
    • Usa "📦 Invia contorno" per verificare l'area
    • Clicca "▶ Avvia incisione"
""",
    
    image_section = """
GESTIONE IMMAGINI
══════════════════════════════════════════════════════════════

📂 IMPORTAZIONE
    • Formati supportati: PNG, JPG, JPEG, BMP, TIFF, WebP, GIF
    • Le immagini vengono convertite in scala di grigi
    • La risoluzione originale viene mantenuta

🔄 ROTAZIONE
    • ↺ 90° SX - Ruota in senso antiorario
    • ↻ 90° DX - Ruota in senso orario
    • ↕ 180° - Capovolgi l'immagine
    • La rotazione è cumulativa

↔ SPECCHIATURA
    • Orizzontale - Specchia sinistra/destra
    • Verticale - Specchia sopra/sotto

⚙ PRE-ELABORAZIONE
    
    Soglia (Threshold): 0-255
    • Valori bassi = più nero (più incisione)
    • Valori alti = più bianco (meno incisione)
    • Tipico: 100-150 per foto, 128 per grafica
    
    Sfocatura (Blur): 0-10
    • Riduce il rumore e i dettagli troppo fini
    • 0 = nessuna sfocatura
    • 2-3 = consigliato per la maggior parte delle immagini
    
    Inverti colori:
    • Scambia bianco e nero
    • Utile per loghi su sfondo scuro
    
    Riduci rumore (Denoise):
    • Rimuove il rumore dalle foto
    • Rallenta l'elaborazione
    • Consigliato per foto scansionate
""",
    
    vectorize_section = """
METODI DI VETTORIZZAZIONE
══════════════════════════════════════════════════════════════

📐 CONTORNI
    • Segue i bordi delle forme
    • Ideale per: loghi, testo, forme geometriche
    • Veloce, tracciato pulito
    • Parametro "Semplificazione": riduce i punti

📏 CENTERLINE (Linea Centrale)
    • Trova lo "scheletro" delle forme
    • Ideale per: testo sottile, linee singole
    • Passata singola al centro delle linee
    • Buono per incisione veloce di scritte

▤ RASTER (Scansione)
    • Riempie le aree come una stampante
    • Ideale per: foto, sfumature, riempimenti solidi
    • Movimento a serpentina (bidirezionale)
    • Parametro "Gap": distanza tra le linee

⟋ HATCHING (Tratteggio)
    • Riempimento con linee inclinate
    • Ideale per: effetti artistici, texture
    • Parametro "Angolo": inclinazione delle linee
    • Parametro "Gap": spaziatura

═══════════════════════════════════════════════════════════════

PARAMETRI COMUNI

    Larghezza/Altezza (mm):
    • Dimensioni finali dell'incisione
    • "Mantieni proporzioni" scala proporzionalmente
    
    Velocità (mm/min): 100-6000
    • Bassa (500-1000) = incisione profonda, legno duro
    • Media (1500-2500) = uso generale
    • Alta (3000-5000) = marcatura leggera, veloce
    
    Potenza S (0-255):
    • 0 = laser spento
    • 255 = massima potenza
    • Consigliato: inizia basso e aumenta
    
    Passate:
    • Numero di ripetizioni del percorso
    • Più passate = incisione più profonda
    • Utile per materiali spessi
""",
    
    position_section = """
POSIZIONAMENTO DEL MODELLO
══════════════════════════════════════════════════════════════

🗺 AREA DI LAVORO
    • Imposta le dimensioni della tua macchina
    • L'area grigia rappresenta il piano di lavoro
    • Le coordinate partono da HOME (0,0)

📍 SPOSTAMENTO MODELLO
    
    Con il mouse:
    • Trascina il modello nell'area di lavoro
    • Il bounding box giallo mostra l'ingombro
    
    Manualmente:
    • Inserisci le coordinate X e Y
    • Clicca "Applica posizione"

⊞ POSIZIONAMENTO RAPIDO
    • Centro - Centra il modello nell'area
    • Angoli - Posiziona negli angoli con margine 5mm

📦 ANTEPRIMA CONTORNO FISICO
    • Muove il laser SPENTO lungo il perimetro
    • Permette di verificare la posizione reale
    • Utile per allineare il materiale
    • Regola la velocità di anteprima

🖱 CONTROLLI CANVAS
    • Trascina (sin.) = sposta modello
    • Trascina (des.) = pan della vista
    • Rotella = zoom
    • I numeri sulla griglia sono in mm
""",
    
    laser_section = """
CONTROLLO LASER E CONNESSIONE
══════════════════════════════════════════════════════════════

🔌 CONNESSIONE
    
    Porta COM:
    • Windows: COM1, COM2, COM3...
    • Linux: /dev/ttyUSB0, /dev/ttyACM0
    • Mac: /dev/tty.usbserial-*
    
    Baud Rate:
    • 115200 - Standard per Grbl
    • 250000 - Alcuni controller veloci
    • Se non funziona, prova 9600
    
    Simulazione:
    • Attiva per testare senza hardware
    • Tutti i comandi vengono simulati

🏠 IMPOSTAZIONE HOME
    
    JOG (Movimento manuale):
    • Usa le frecce ▲▼◄► per muovere il laser
    • Imposta il passo (0.1 - 50 mm)
    • Imposta la velocità F
    
    "Imposta Home qui":
    • Definisce la posizione corrente come origine (0,0)
    • Invia il comando G92 X0 Y0
    • Tutti i movimenti saranno relativi a questo punto
    
    "Vai all'Home":
    • Muove il laser alla posizione 0,0
    • Utile per verificare l'allineamento

💻 COMANDI MANUALI
    • Inserisci qualsiasi comando GCode
    • Premi Invio o "Invia"
    • La risposta appare nel log

🚨 EMERGENCY STOP
    • Invia un soft-reset al controller (Ctrl-X)
    • Ferma immediatamente il laser
    • Dopo l'uso, esegui "Unlock" ($X)
""",
    
    simulation_section = """
SIMULAZIONE
══════════════════════════════════════════════════════════════

🎬 SIMULAZIONE VISIVA
    • Mostra il percorso del laser animato
    • Punto rosso = laser acceso
    • Punto grigio = movimento rapido
    
    Velocità (×1 - ×50):
    • ×1 = più lento, dettagliato
    • ×50 = molto veloce
    
    Controlli:
    • "▶ Avvia sim." - Inizia la simulazione
    • "⏹ Stop sim." - Ferma la simulazione

🔍 ANTEPRIMA VETTORIALE
    • Finestra separata con zoom/pan
    • Mostra tutto il percorso statico
    • Colori:
        - Rosso = incisione (laser ON)
        - Grigio = movimento rapido
        - Giallo = bounding box
        - Verde = origine/home

📊 STATISTICHE
    • Numero totale di movimenti
    • Movimenti con laser ON/OFF
    • Dimensioni area di incisione

💡 CONSIGLI
    • Usa sempre la simulazione prima di incidere
    • Verifica che non ci siano movimenti fuori area
    • Controlla che il percorso sia logico
""",
    
    shortcuts_section = """
SCORCIATOIE DA TASTIERA E MOUSE
══════════════════════════════════════════════════════════════

🖱 MOUSE (Canvas Area di Lavoro)
    Tasto sinistro + trascina    Sposta il modello
    Tasto destro + trascina      Pan della vista
    Rotella                      Zoom in/out

⌨ TASTIERA
    Ctrl + O                     Apri immagine
    Ctrl + S                     Salva GCode
    Ctrl + L                     Carica GCode
    F1                           Mostra questa guida
    Escape                       Chiudi finestra modale

🔢 JOG (Tab Laser)
    ▲                            Muovi Y+
    ▼                            Muovi Y-
    ◄                            Muovi X-
    ►                            Muovi X+
    ●                            Vai a Home (0,0)
""",
    
    troubleshooting = """
RISOLUZIONE PROBLEMI
══════════════════════════════════════════════════════════════

❌ "Nessuna porta COM trovata"
    • Verifica che il cavo USB sia collegato
    • Installa i driver CH340/CP2102 se necessario
    • Su Linux: aggiungi l'utente al gruppo 'dialout'
      sudo usermod -a -G dialout $USER

❌ "Connessione fallita"
    • Verifica che nessun altro programma usi la porta
    • Prova un baud rate diverso
    • Scollega e ricollega il cavo USB
    • Riavvia il controller

❌ "ALARM" durante l'invio
    • Il controller ha rilevato un errore
    • Esegui "Unlock" ($X)
    • Verifica i limiti di corsa
    • Controlla che non ci siano ostacoli

❌ Il laser non si accende
    • Verifica il valore S (potenza)
    • Controlla il comando M3/M5
    • Verifica l'alimentazione del laser
    • Alcuni laser richiedono PWM specifico

❌ L'incisione è sfalsata
    • Verifica che il materiale sia fisso
    • Controlla la tensione delle cinghie
    • Riduci la velocità di incisione
    • Verifica che il "Home" sia corretto

❌ L'immagine appare invertita
    • Usa "Specchia" orizzontale/verticale
    • Verifica l'orientamento del laser
    • Controlla la direzione degli assi

❌ Troppi dettagli/poco definito
    • Regola la soglia (threshold)
    • Aumenta la sfocatura (blur)
    • Prova un metodo di vettorizzazione diverso
    • Aumenta la semplificazione (contorni)
""",
    
    gcode_section = """
COMANDI GCODE COMUNI
══════════════════════════════════════════════════════════════

📋 MOVIMENTO
    G0 X10 Y20      Movimento rapido a X=10, Y=20
    G1 X10 Y20      Movimento lineare (incisione)
    G1 X10 Y20 F500 Movimento con velocità 500 mm/min
    
📋 MODALITÀ
    G20             Unità: pollici
    G21             Unità: millimetri
    G90             Coordinate assolute
    G91             Coordinate relative
    G92 X0 Y0       Imposta posizione corrente come origine

📋 LASER
    M3              Accende il laser
    M3 S100         Accende con potenza 100
    M5              Spegne il laser
    
📋 PROGRAMMA
    M2              Fine programma
    M0              Pausa (attende conferma)

📋 GRBL SPECIFICI
    $H              Homing automatico
    $X              Sblocca ALARM
    ?               Richiede stato
    !               Feed hold (pausa)
    ~               Resume (riprende)
    Ctrl-X          Soft reset

📋 ESEMPIO MINIMO
    G21             ; Millimetri
    G90             ; Assoluto
    G0 X0 Y0        ; Vai a origine
    G0 X10 Y10      ; Vai a posizione
    M3 S200         ; Laser ON
    G1 X50 Y10 F1000; Incidi
    G1 X50 Y50
    G1 X10 Y50
    G1 X10 Y10
    M5              ; Laser OFF
    G0 X0 Y0        ; Torna a origine
    M2              ; Fine
""",
    
    safety_section = """
⚠ AVVERTENZE DI SICUREZZA ⚠
══════════════════════════════════════════════════════════════

👓 PROTEZIONE OCCHI
    • Indossa SEMPRE occhiali di protezione adeguati
    • Gli occhiali devono essere specifici per la lunghezza
      d'onda del tuo laser (es. 445nm, 10600nm)
    • NON guardare MAI direttamente il raggio laser
    • Attenzione ai riflessi su superfici metalliche

🔥 RISCHIO INCENDIO
    • Non lasciare MAI il laser incustodito durante il lavoro
    • Tieni un estintore a portata di mano
    • Evita materiali altamente infiammabili
    • Assicura una ventilazione adeguata

💨 VENTILAZIONE
    • Molti materiali producono fumi tossici
    • Usa un aspiratore con filtro appropriato
    • Lavora in ambiente ventilato
    • MAI incidere PVC, vinile, ABS (fumi tossici!)

⚡ SICUREZZA ELETTRICA
    • Verifica che l'alimentazione sia adeguata
    • Non modificare il cablaggio se non sei esperto
    • Scollega l'alimentazione prima di manutenzione

🛡 MATERIALI SICURI
    ✅ Legno, MDF, compensato
    ✅ Carta, cartone
    ✅ Pelle (naturale)
    ✅ Acrilico (PMMA)
    ✅ Tessuti naturali (cotone, lino)
    
🚫 MATERIALI DA EVITARE
    ❌ PVC, Vinile (produce cloro!)
    ❌ ABS (fumi tossici)
    ❌ Polistirolo (infiammabile)
    ❌ Fibra di vetro
    ❌ Materiali contenenti alogeni

🚨 IN CASO DI EMERGENZA
    1. Premi EMERGENCY STOP o scollega l'alimentazione
    2. Non tentare di spegnere con acqua
    3. Usa estintore a CO2 o polvere
    4. Ventila l'ambiente
    5. In caso di esposizione fumi, esci all'aria aperta
"""
)


# ══════════════════════════════════════════════════════════════════════════════
#  HELP ENGLISH
# ══════════════════════════════════════════════════════════════════════════════
HELP_EN = HelpContent(
    title_main           = "Laser Engraver Pro Help",
    title_getting_started= "🚀 Quick Start",
    title_image          = "🖼 Image Management",
    title_vectorize      = "✏ Vectorization",
    title_position       = "📍 Positioning",
    title_laser          = "🔥 Laser Control",
    title_simulation     = "🎬 Simulation",
    title_shortcuts      = "⌨ Shortcuts",
    title_troubleshooting= "🔧 Troubleshooting",
    title_gcode          = "📄 GCode Commands",
    title_safety         = "⚠ Safety",
    
    getting_started = """
QUICK START GUIDE
══════════════════════════════════════════════════════════════

1️⃣  LOAD AN IMAGE
    • Click "Open image" or use File → Open image
    • Supported formats: PNG, JPG, BMP, TIFF, GIF, WebP

2️⃣  ADJUST THE IMAGE
    • Use threshold to control black/white levels
    • Rotate or flip the image if needed
    • Enable "Invert colors" for images on dark backgrounds

3️⃣  SET DIMENSIONS
    • Go to "Vectorize" tab
    • Enter width and height in millimeters
    • Choose vectorization method

4️⃣  GENERATE GCODE
    • Click "🚀 Generate GCode"
    • Check preview in work area
    • Drag the model with the mouse to position it

5️⃣  TEST WITH SIMULATION
    • Before engraving, use "▶ Start sim."
    • Verify the path is correct

6️⃣  CONNECT THE LASER
    • Go to "Laser" tab
    • Select COM port
    • Click "Connect"

7️⃣  ENGRAVE!
    • Place material under laser
    • Use "📦 Send outline" to verify area
    • Click "▶ Start engraving"
""",
    
    image_section = """
IMAGE MANAGEMENT
══════════════════════════════════════════════════════════════

📂 IMPORT
    • Supported formats: PNG, JPG, JPEG, BMP, TIFF, WebP, GIF
    • Images are converted to grayscale
    • Original resolution is maintained

🔄 ROTATION
    • ↺ 90° Left - Rotate counter-clockwise
    • ↻ 90° Right - Rotate clockwise
    • ↕ 180° - Flip upside down
    • Rotation is cumulative

↔ MIRROR
    • Horizontal - Mirror left/right
    • Vertical - Mirror top/bottom

⚙ PRE-PROCESSING
    
    Threshold: 0-255
    • Low values = more black (more engraving)
    • High values = more white (less engraving)
    • Typical: 100-150 for photos, 128 for graphics
    
    Blur: 0-10
    • Reduces noise and too-fine details
    • 0 = no blur
    • 2-3 = recommended for most images
    
    Invert colors:
    • Swaps black and white
    • Useful for logos on dark backgrounds
    
    Denoise:
    • Removes noise from photos
    • Slows processing
    • Recommended for scanned photos
""",
    
    vectorize_section = """
VECTORIZATION METHODS
══════════════════════════════════════════════════════════════

📐 CONTOURS
    • Follows shape edges
    • Ideal for: logos, text, geometric shapes
    • Fast, clean path
    • "Simplification" parameter: reduces points

📏 CENTERLINE
    • Finds the "skeleton" of shapes
    • Ideal for: thin text, single lines
    • Single pass through center of lines
    • Good for fast text engraving

▤ RASTER (Scan)
    • Fills areas like a printer
    • Ideal for: photos, gradients, solid fills
    • Serpentine movement (bidirectional)
    • "Gap" parameter: distance between lines

⟋ HATCHING
    • Fill with angled lines
    • Ideal for: artistic effects, textures
    • "Angle" parameter: line inclination
    • "Gap" parameter: spacing

═══════════════════════════════════════════════════════════════

COMMON PARAMETERS

    Width/Height (mm):
    • Final engraving dimensions
    • "Keep ratio" scales proportionally
    
    Speed (mm/min): 100-6000
    • Low (500-1000) = deep engraving, hardwood
    • Medium (1500-2500) = general use
    • High (3000-5000) = light marking, fast
    
    Power S (0-255):
    • 0 = laser off
    • 255 = maximum power
    • Recommended: start low and increase
    
    Passes:
    • Number of path repetitions
    • More passes = deeper engraving
    • Useful for thick materials
""",
    
    position_section = """
MODEL POSITIONING
══════════════════════════════════════════════════════════════

🗺 WORK AREA
    • Set your machine dimensions
    • Gray area represents work surface
    • Coordinates start from HOME (0,0)

📍 MOVING THE MODEL
    
    With mouse:
    • Drag the model in work area
    • Yellow bounding box shows footprint
    
    Manually:
    • Enter X and Y coordinates
    • Click "Apply position"

⊞ QUICK POSITIONING
    • Center - Center model in area
    • Corners - Position in corners with 5mm margin

📦 PHYSICAL OUTLINE PREVIEW
    • Moves laser OFF along perimeter
    • Allows verifying real position
    • Useful for aligning material
    • Adjust preview speed

🖱 CANVAS CONTROLS
    • Drag (left) = move model
    • Drag (right) = pan view
    • Wheel = zoom
    • Grid numbers are in mm
""",
    
    laser_section = """
LASER CONTROL AND CONNECTION
══════════════════════════════════════════════════════════════

🔌 CONNECTION
    
    COM Port:
    • Windows: COM1, COM2, COM3...
    • Linux: /dev/ttyUSB0, /dev/ttyACM0
    • Mac: /dev/tty.usbserial-*
    
    Baud Rate:
    • 115200 - Standard for Grbl
    • 250000 - Some fast controllers
    • If not working, try 9600
    
    Simulation:
    • Enable to test without hardware
    • All commands are simulated

🏠 HOME SETTING
    
    JOG (Manual movement):
    • Use arrows ▲▼◄► to move laser
    • Set step (0.1 - 50 mm)
    • Set speed F
    
    "Set Home here":
    • Defines current position as origin (0,0)
    • Sends G92 X0 Y0 command
    • All movements will be relative to this point
    
    "Go to Home":
    • Moves laser to position 0,0
    • Useful for verifying alignment

💻 MANUAL COMMANDS
    • Enter any GCode command
    • Press Enter or "Send"
    • Response appears in log

🚨 EMERGENCY STOP
    • Sends soft-reset to controller (Ctrl-X)
    • Immediately stops laser
    • After use, run "Unlock" ($X)
""",
    
    simulation_section = """
SIMULATION
══════════════════════════════════════════════════════════════

🎬 VISUAL SIMULATION
    • Shows animated laser path
    • Red dot = laser on
    • Gray dot = rapid movement
    
    Speed (×1 - ×50):
    • ×1 = slower, detailed
    • ×50 = very fast
    
    Controls:
    • "▶ Start sim." - Start simulation
    • "⏹ Stop sim." - Stop simulation

🔍 VECTOR PREVIEW
    • Separate window with zoom/pan
    • Shows complete static path
    • Colors:
        - Red = engraving (laser ON)
        - Gray = rapid movement
        - Yellow = bounding box
        - Green = origin/home

📊 STATISTICS
    • Total number of movements
    • Movements with laser ON/OFF
    • Engraving area dimensions

💡 TIPS
    • Always use simulation before engraving
    • Verify no movements outside area
    • Check that path is logical
""",
    
    shortcuts_section = """
KEYBOARD AND MOUSE SHORTCUTS
══════════════════════════════════════════════════════════════

🖱 MOUSE (Work Area Canvas)
    Left button + drag       Move model
    Right button + drag      Pan view
    Wheel                    Zoom in/out

⌨ KEYBOARD
    Ctrl + O                 Open image
    Ctrl + S                 Save GCode
    Ctrl + L                 Load GCode
    F1                       Show this help
    Escape                   Close modal window

🔢 JOG (Laser Tab)
    ▲                        Move Y+
    ▼                        Move Y-
    ◄                        Move X-
    ►                        Move X+
    ●                        Go to Home (0,0)
""",
    
    troubleshooting = """
TROUBLESHOOTING
══════════════════════════════════════════════════════════════

❌ "No COM port found"
    • Verify USB cable is connected
    • Install CH340/CP2102 drivers if needed
    • On Linux: add user to 'dialout' group
      sudo usermod -a -G dialout $USER

❌ "Connection failed"
    • Verify no other program is using the port
    • Try a different baud rate
    • Disconnect and reconnect USB cable
    • Restart controller

❌ "ALARM" during sending
    • Controller detected an error
    • Run "Unlock" ($X)
    • Check travel limits
    • Check for obstructions

❌ Laser doesn't turn on
    • Verify S value (power)
    • Check M3/M5 command
    • Verify laser power supply
    • Some lasers require specific PWM

❌ Engraving is offset
    • Verify material is secured
    • Check belt tension
    • Reduce engraving speed
    • Verify "Home" is correct

❌ Image appears reversed
    • Use horizontal/vertical "Mirror"
    • Verify laser orientation
    • Check axis direction

❌ Too much detail/undefined
    • Adjust threshold
    • Increase blur
    • Try different vectorization method
    • Increase simplification (contours)
""",
    
    gcode_section = """
COMMON GCODE COMMANDS
══════════════════════════════════════════════════════════════

📋 MOVEMENT
    G0 X10 Y20      Rapid move to X=10, Y=20
    G1 X10 Y20      Linear move (engraving)
    G1 X10 Y20 F500 Move with speed 500 mm/min
    
📋 MODES
    G20             Units: inches
    G21             Units: millimeters
    G90             Absolute coordinates
    G91             Relative coordinates
    G92 X0 Y0       Set current position as origin

📋 LASER
    M3              Turn laser on
    M3 S100         Turn on with power 100
    M5              Turn laser off
    
📋 PROGRAM
    M2              End program
    M0              Pause (waits for confirmation)

📋 GRBL SPECIFIC
    $H              Auto homing
    $X              Unlock ALARM
    ?               Request status
    !               Feed hold (pause)
    ~               Resume
    Ctrl-X          Soft reset

📋 MINIMAL EXAMPLE
    G21             ; Millimeters
    G90             ; Absolute
    G0 X0 Y0        ; Go to origin
    G0 X10 Y10      ; Go to position
    M3 S200         ; Laser ON
    G1 X50 Y10 F1000; Engrave
    G1 X50 Y50
    G1 X10 Y50
    G1 X10 Y10
    M5              ; Laser OFF
    G0 X0 Y0        ; Return to origin
    M2              ; End
""",
    
    safety_section = """
⚠ SAFETY WARNINGS ⚠
══════════════════════════════════════════════════════════════

👓 EYE PROTECTION
    • ALWAYS wear appropriate safety glasses
    • Glasses must be specific to your laser wavelength
      (e.g., 445nm, 10600nm)
    • NEVER look directly at laser beam
    • Beware of reflections on metallic surfaces

🔥 FIRE RISK
    • NEVER leave laser unattended during operation
    • Keep fire extinguisher within reach
    • Avoid highly flammable materials
    • Ensure adequate ventilation

💨 VENTILATION
    • Many materials produce toxic fumes
    • Use extractor with appropriate filter
    • Work in ventilated environment
    • NEVER engrave PVC, vinyl, ABS (toxic fumes!)

⚡ ELECTRICAL SAFETY
    • Verify power supply is adequate
    • Don't modify wiring unless expert
    • Disconnect power before maintenance

🛡 SAFE MATERIALS
    ✅ Wood, MDF, plywood
    ✅ Paper, cardboard
    ✅ Leather (natural)
    ✅ Acrylic (PMMA)
    ✅ Natural fabrics (cotton, linen)
    
🚫 MATERIALS TO AVOID
    ❌ PVC, Vinyl (produces chlorine!)
    ❌ ABS (toxic fumes)
    ❌ Polystyrene (flammable)
    ❌ Fiberglass
    ❌ Materials containing halogens

🚨 IN CASE OF EMERGENCY
    1. Press EMERGENCY STOP or disconnect power
    2. Don't try to extinguish with water
    3. Use CO2 or powder extinguisher
    4. Ventilate the area
    5. If exposed to fumes, go outside for fresh air
"""
)


# ══════════════════════════════════════════════════════════════════════════════
#  HELP ESPAÑOL
# ══════════════════════════════════════════════════════════════════════════════
HELP_ES = HelpContent(
    title_main           = "Ayuda de Laser Engraver Pro",
    title_getting_started= "🚀 Inicio Rápido",
    title_image          = "🖼 Gestión de Imágenes",
    title_vectorize      = "✏ Vectorización",
    title_position       = "📍 Posicionamiento",
    title_laser          = "🔥 Control del Láser",
    title_simulation     = "🎬 Simulación",
    title_shortcuts      = "⌨ Atajos",
    title_troubleshooting= "🔧 Solución de Problemas",
    title_gcode          = "📄 Comandos GCode",
    title_safety         = "⚠ Seguridad",
    
    getting_started = """
GUÍA DE INICIO RÁPIDO
══════════════════════════════════════════════════════════════

1️⃣  CARGA UNA IMAGEN
    • Haz clic en "Abrir imagen" o usa Archivo → Abrir imagen
    • Formatos soportados: PNG, JPG, BMP, TIFF, GIF, WebP

2️⃣  AJUSTA LA IMAGEN
    • Usa el umbral (threshold) para controlar blanco/negro
    • Rota o voltea la imagen si es necesario
    • Activa "Invertir colores" para imágenes con fondo oscuro

3️⃣  CONFIGURA LAS DIMENSIONES
    • Ve a la pestaña "Vectorizar"
    • Introduce ancho y alto en milímetros
    • Elige el método de vectorización

4️⃣  GENERA EL GCODE
    • Haz clic en "🚀 Generar GCode"
    • Revisa la vista previa en el área de trabajo
    • Arrastra el modelo con el ratón para posicionarlo

5️⃣  PRUEBA CON LA SIMULACIÓN
    • Antes de grabar, usa "▶ Iniciar sim."
    • Verifica que el recorrido sea correcto

6️⃣  CONECTA EL LÁSER
    • Ve a la pestaña "Láser"
    • Selecciona el puerto COM
    • Haz clic en "Conectar"

7️⃣  ¡GRABA!
    • Coloca el material bajo el láser
    • Usa "📦 Enviar contorno" para verificar el área
    • Haz clic en "▶ Iniciar grabado"
""",
    
    image_section = "Ver documentación en inglés/italiano para detalles completos.",
    vectorize_section = "Ver documentación en inglés/italiano para detalles completos.",
    position_section = "Ver documentación en inglés/italiano para detalles completos.",
    laser_section = "Ver documentación en inglés/italiano para detalles completos.",
    simulation_section = "Ver documentación en inglés/italiano para detalles completos.",
    shortcuts_section = "Ver documentación en inglés/italiano para detalles completos.",
    troubleshooting = "Ver documentación en inglés/italiano para detalles completos.",
    gcode_section = "Ver documentación en inglés/italiano para detalles completos.",
    safety_section = "Ver documentación en inglés/italiano para detalles completos.",
)


# ══════════════════════════════════════════════════════════════════════════════
#  HELP DEUTSCH
# ══════════════════════════════════════════════════════════════════════════════
HELP_DE = HelpContent(
    title_main           = "Laser Engraver Pro Hilfe",
    title_getting_started= "🚀 Schnellstart",
    title_image          = "🖼 Bildverwaltung",
    title_vectorize      = "✏ Vektorisierung",
    title_position       = "📍 Positionierung",
    title_laser          = "🔥 Lasersteuerung",
    title_simulation     = "🎬 Simulation",
    title_shortcuts      = "⌨ Tastenkürzel",
    title_troubleshooting= "🔧 Fehlerbehebung",
    title_gcode          = "📄 GCode-Befehle",
    title_safety         = "⚠ Sicherheit",
    
    getting_started = """
SCHNELLSTART-ANLEITUNG
══════════════════════════════════════════════════════════════

1️⃣  BILD LADEN
    • Klicke "Bild öffnen" oder verwende Datei → Bild öffnen
    • Unterstützte Formate: PNG, JPG, BMP, TIFF, GIF, WebP

2️⃣  BILD ANPASSEN
    • Verwende den Schwellenwert für Schwarz/Weiß-Steuerung
    • Drehe oder spiegele das Bild bei Bedarf
    • Aktiviere "Farben invertieren" für Bilder mit dunklem Hintergrund

3️⃣  ABMESSUNGEN EINSTELLEN
    • Gehe zum Tab "Vektorisieren"
    • Gib Breite und Höhe in Millimetern ein
    • Wähle die Vektorisierungsmethode

4️⃣  GCODE GENERIEREN
    • Klicke "🚀 GCode generieren"
    • Überprüfe die Vorschau im Arbeitsbereich
    • Ziehe das Modell mit der Maus zum Positionieren

5️⃣  MIT SIMULATION TESTEN
    • Vor dem Gravieren "▶ Sim. starten" verwenden
    • Überprüfe, ob der Pfad korrekt ist

6️⃣  LASER VERBINDEN
    • Gehe zum Tab "Laser"
    • Wähle COM-Port
    • Klicke "Verbinden"

7️⃣  GRAVIEREN!
    • Platziere Material unter dem Laser
    • Verwende "📦 Umriss senden" zur Überprüfung
    • Klicke "▶ Gravur starten"
""",
    
    image_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    vectorize_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    position_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    laser_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    simulation_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    shortcuts_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    troubleshooting = "Siehe englische/italienische Dokumentation für vollständige Details.",
    gcode_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
    safety_section = "Siehe englische/italienische Dokumentation für vollständige Details.",
)


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTRO HELP
# ══════════════════════════════════════════════════════════════════════════════
HELP_CONTENT: dict[str, HelpContent] = {
    "Italiano" : HELP_IT,
    "English"  : HELP_EN,
    "Español"  : HELP_ES,
    "Deutsch"  : HELP_DE,
}


def get_help(language: str = "Italiano") -> HelpContent:
    """Restituisce il contenuto help per la lingua richiesta."""
    return HELP_CONTENT.get(language, HELP_CONTENT["English"])