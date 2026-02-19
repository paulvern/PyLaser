# PyLaser v0.93

For a simple yet complete HTML version:
https://paulvern.free.nf/laser/

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**PyLaser** is a complete laser engraving application with image vectorization, real-time simulation, and GCode control for CNC/laser machines.

**PyLaser** è un'applicazione completa per incisione laser con vettorizzazione immagini, simulazione in tempo reale e controllo GCode per macchine CNC/laser.

---

## 📑 Table of Contents / Indice

- [English Documentation](#english-documentation)
  - [Features](#-features)
  - [Installation](#-installation)
  - [Quick Start](#-quick-start)
  - [Keyboard Shortcuts](#-keyboard-shortcuts)
  - [Safety Guidelines](#-safety-guidelines)
  - [Troubleshooting](#-troubleshooting)
- [Documentazione Italiana](#documentazione-italiana)
  - [Caratteristiche](#-caratteristiche)
  - [Installazione](#-installazione-1)
  - [Guida Rapida](#-guida-rapida)
  - [Scorciatoie Tastiera](#-scorciatoie-tastiera)
  - [Norme di Sicurezza](#-norme-di-sicurezza)
  - [Risoluzione Problemi](#-risoluzione-problemi)

---

# English Documentation

## 🌟 Features

### 🖼️ Image Processing
- **Multi-format support**: PNG, JPG, BMP, TIFF, WebP, GIF
- **Advanced preprocessing**: threshold, blur, inversion, denoising
- **Rotation & flip**: 90°, 180°, 270° rotation and horizontal/vertical flip
- **Real-time preview**: original and processed image side-by-side

### 🎨 Vectorization Strategies
1. **Contours** - traces object outlines (best for logos/icons)
2. **Centerline** - skeleton tracing (ideal for drawings/sketches)
3. **Raster** - horizontal scanning (photos/gradients)
4. **Hatching** - diagonal fill patterns (artistic effects)

### 📐 Positioning & Work Area
- **Visual canvas** with grid, zoom, and pan
- **Drag & drop** model positioning
- **Quick alignment**: center, corners (TL/TR/BL/BR)
- **BBox preview**: send bounding box to laser for alignment
- **Configurable work area**: custom dimensions (mm)

### 🔧 GCode Generation
- **Customizable parameters**: feed rate, laser power, passes
- **Offset control**: X/Y translation
- **Multi-pass support**: automatic repetition for deeper engraving
- **GCode preview**: text viewer with syntax

### 🎬 Simulation
- **Visual playback**: see laser path before engraving
- **Speed control**: 1x to 50x simulation speed
- **Color-coded paths**:
  - 🔴 Red = Laser ON
  - 🔵 Blue = Rapid movements
  - ⚪ Gray = Laser OFF

### 🔌 Laser Control
- **Serial communication**: GRBL/Marlin compatible
- **Manual jogging**: X/Y axis control with custom step size
- **Home management**: set/goto home position
- **Emergency stop**: immediate halt with alarm reset
- **Simulation mode**: test without hardware connection
- **Real-time progress**: live progress bar during engraving

### 🌐 Multi-language Support
- 🇬🇧 **English**
- 🇮🇹 **Italiano**
- 🇪🇸 **Español**
- 🇩🇪 **Deutsch**

### 🎨 Themes
- **Catppuccin Mocha** (dark)
- **Catppuccin Latte** (light)
- **Dracula** (dark)
- **Nord** (cool dark)
- **Solarized Light/Dark**
- **Gruvbox Light/Dark**

---

## 📦 Installation

### Requirements
- **Python 3.8+**
- **Required libraries**:
  ```bash
  pip install Pillow numpy opencv-python pyserial
  ```

### Download
```bash
git clone https://github.com/yourusername/pylaser.git
cd pylaser
```

### Run
```bash
python main.py
```

---

## 🚀 Quick Start

### 1. Open Image (`Ctrl+O`)
- Select an image file
- Adjust rotation/flip if needed

### 2. Preprocess
- Set threshold (0-255)
- Apply blur/denoise
- Toggle invert if needed
- Click **Update Preview**

### 3. Vectorize
- Choose strategy (Contours/Centerline/Raster/Hatching)
- Set dimensions (mm)
- Configure feed rate, power, passes
- Click **Generate GCode**

### 4. Position Model
- Drag on canvas or use quick position buttons
- Send BBox to laser for physical preview (optional)

### 5. Simulate *(optional)*
- Click **Start Simulation** to preview
- Adjust speed with slider

### 6. Connect to Laser
- Select COM port and baudrate
- Click **Connect**
- Use manual jog to position laser head
- Click **Set Home**

### 7. Engrave
- Click **Start Engraving**
- Monitor progress bar
- Use **Emergency Stop** if needed

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Image |
| `Ctrl+S` | Save GCode |
| `F1` | Show Help |

---

## 📂 Project Structure

```
pylaser/
├── main.py              # Main application
├── strings.py           # Localized strings
├── themes.py            # Theme definitions
├── help_content.py      # Help documentation
└── .engraver_config.json  # User settings (auto-generated)
```

---

## 🛠️ Configuration

Settings are saved automatically in `.engraver_config.json`:
- Language preference
- Theme selection
- Work area dimensions
- Last used port/baudrate
- Feed rate and power defaults

**Change settings**: Menu → ⚙ Settings → 🌐🎨 Preferences

---

## ⚠️ Safety Guidelines

- ⚠️ **Always wear safety goggles** when operating laser equipment
- 🔥 **Never leave laser unattended** during operation
- 🧯 **Keep fire extinguisher nearby**
- 💨 **Ensure proper ventilation** for fume extraction
- 🧪 **Test on scrap material** before final engraving
- 🛑 **Use Emergency Stop** if needed
- 📏 **Verify work area bounds** with BBox preview

---

## 🐛 Troubleshooting

### "Port not found"
- Check USB connection
- Verify driver installation
- Try different USB port
- Use **Simulation Mode** for testing

### "Image not processing"
- Ensure image is valid format
- Check image isn't corrupted
- Try different threshold value

### "GCode not generating"
- Verify preprocessed image exists
- Check dimensions are > 0
- Ensure vectorization method is selected

### "Laser not responding"
- Verify serial connection
- Check baudrate matches firmware
- Try sending `$X` (unlock) command
- Reset controller

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/pylaser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pylaser/discussions)

---

# Documentazione Italiana

## 🌟 Caratteristiche

### 🖼️ Elaborazione Immagini
- **Supporto multi-formato**: PNG, JPG, BMP, TIFF, WebP, GIF
- **Preprocessamento avanzato**: soglia, sfocatura, inversione, riduzione rumore
- **Rotazione e ribaltamento**: rotazione 90°/180°/270° e flip orizzontale/verticale
- **Anteprima in tempo reale**: immagine originale ed elaborata affiancate

### 🎨 Strategie di Vettorizzazione
1. **Contorni** - traccia i contorni degli oggetti (ottimo per loghi/icone)
2. **Linea centrale** - tracciamento scheletro (ideale per disegni/schizzi)
3. **Raster** - scansione orizzontale (foto/sfumature)
4. **Tratteggio** - riempimento con pattern diagonali (effetti artistici)

### 📐 Posizionamento e Area di Lavoro
- **Canvas visuale** con griglia, zoom e pan
- **Drag & drop** per posizionamento modello
- **Allineamento rapido**: centro, angoli (AS/AD/BS/BD)
- **Anteprima BBox**: invia rettangolo di delimitazione al laser per allineamento
- **Area configurabile**: dimensioni personalizzate (mm)

### 🔧 Generazione GCode
- **Parametri personalizzabili**: velocità, potenza laser, passate
- **Controllo offset**: traslazione X/Y
- **Supporto multi-passata**: ripetizione automatica per incisioni profonde
- **Anteprima GCode**: visualizzatore testo con sintassi

### 🎬 Simulazione
- **Riproduzione visiva**: visualizza percorso laser prima dell'incisione
- **Controllo velocità**: simulazione da 1x a 50x
- **Percorsi color-coded**:
  - 🔴 Rosso = Laser ACCESO
  - 🔵 Blu = Movimenti rapidi
  - ⚪ Grigio = Laser SPENTO

### 🔌 Controllo Laser
- **Comunicazione seriale**: compatibile GRBL/Marlin
- **Jogging manuale**: controllo assi X/Y con passo personalizzabile
- **Gestione home**: imposta/vai a posizione home
- **Arresto emergenza**: stop immediato con reset allarme
- **Modalità simulazione**: test senza connessione hardware
- **Progresso in tempo reale**: barra avanzamento durante incisione

### 🌐 Supporto Multi-lingua
- 🇬🇧 **English**
- 🇮🇹 **Italiano**
- 🇪🇸 **Español**
- 🇩🇪 **Deutsch**

### 🎨 Temi
- **Catppuccin Mocha** (scuro)
- **Catppuccin Latte** (chiaro)
- **Dracula** (scuro)
- **Nord** (scuro freddo)
- **Solarized Light/Dark**
- **Gruvbox Light/Dark**

---

## 📦 Installazione

### Requisiti
- **Python 3.8+**
- **Librerie richieste**:
  ```bash
  pip install Pillow numpy opencv-python pyserial
  ```

### Download
```bash
git clone https://github.com/tuousername/pylaser.git
cd pylaser
```

### Avvio
```bash
python main.py
```

---

## 🚀 Guida Rapida

### 1. Apri Immagine (`Ctrl+O`)
- Seleziona file immagine
- Regola rotazione/ribaltamento se necessario

### 2. Preprocessa
- Imposta soglia (0-255)
- Applica sfocatura/riduzione rumore
- Attiva inversione se necessario
- Clicca **Aggiorna Anteprima**

### 3. Vettorizza
- Scegli strategia (Contorni/Linea centrale/Raster/Tratteggio)
- Imposta dimensioni (mm)
- Configura velocità, potenza, passate
- Clicca **Genera GCode**

### 4. Posiziona Modello
- Trascina su canvas o usa pulsanti posizionamento rapido
- Invia BBox al laser per anteprima fisica (opzionale)

### 5. Simula *(opzionale)*
- Clicca **Avvia Simulazione** per anteprima
- Regola velocità con slider

### 6. Connetti al Laser
- Seleziona porta COM e baudrate
- Clicca **Connetti**
- Usa jogging manuale per posizionare testina laser
- Clicca **Imposta Home**

### 7. Incidi
- Clicca **Avvia Incisione**
- Monitora barra di avanzamento
- Usa **Arresto Emergenza** se necessario

---

## ⌨️ Scorciatoie Tastiera

| Scorciatoia | Azione |
|-------------|--------|
| `Ctrl+O` | Apri Immagine |
| `Ctrl+S` | Salva GCode |
| `F1` | Mostra Aiuto |

---

## 📂 Struttura Progetto

```
pylaser/
├── main.py              # Applicazione principale
├── strings.py           # Stringhe localizzate
├── themes.py            # Definizioni temi
├── help_content.py      # Documentazione aiuto
└── .engraver_config.json  # Impostazioni utente (auto-generato)
```

---

## 🛠️ Configurazione

Le impostazioni sono salvate automaticamente in `.engraver_config.json`:
- Preferenza lingua
- Selezione tema
- Dimensioni area di lavoro
- Ultima porta/baudrate utilizzati
- Valori predefiniti velocità e potenza

**Modifica impostazioni**: Menu → ⚙ Settings → 🌐🎨 Preferences

---

## ⚠️ Norme di Sicurezza

- ⚠️ **Indossa sempre occhiali protettivi** quando operi con apparecchiature laser
- 🔥 **Non lasciare mai il laser incustodito** durante il funzionamento
- 🧯 **Tieni un estintore nelle vicinanze**
- 💨 **Assicura ventilazione adeguata** per estrazione fumi
- 🧪 **Testa su materiale di scarto** prima dell'incisione finale
- 🛑 **Usa Arresto Emergenza** se necessario
- 📏 **Verifica limiti area di lavoro** con anteprima BBox

---

## 🐛 Risoluzione Problemi

### "Porta non trovata"
- Controlla connessione USB
- Verifica installazione driver
- Prova porta USB diversa
- Usa **Modalità Simulazione** per test

### "Immagine non elaborata"
- Assicurati che l'immagine sia in formato valido
- Verifica che l'immagine non sia corrotta
- Prova valore soglia diverso

### "GCode non generato"
- Verifica che esista immagine preprocessata
- Controlla che dimensioni siano > 0
- Assicurati che metodo vettorizzazione sia selezionato

### "Laser non risponde"
- Verifica connessione seriale
- Controlla che baudrate corrisponda al firmware
- Prova inviare comando `$X` (sblocco)
- Resetta controller

---

## 📝 Licenza

Licenza MIT - vedi file [LICENSE](LICENSE) per dettagli

---

## 🤝 Contributi

Contributi benvenuti! Per favore:
1. Fai fork del repository
2. Crea branch feature (`git checkout -b feature/fantastica`)
3. Committa modifiche (`git commit -m 'Aggiungi feature fantastica'`)
4. Push al branch (`git push origin feature/fantastica`)
5. Apri Pull Request

---

## 📧 Contatti

- **Issues**: [GitHub Issues](https://github.com/tuousername/pylaser/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/tuousername/pylaser/discussions)

---

**Made with ❤️ and ☕ | Realizzato con ❤️ e ☕**
