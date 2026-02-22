# LaserCAM Pro v1.0

[![Demo](https://img.shields.io/badge/demo-live-success)](https://paulvern.free.nf/laser)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![JavaScript](https://img.shields.io/badge/language-JavaScript-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Languages](https://img.shields.io/badge/languages-10-blue.svg)](#-multi-language-support)

**LaserCAM Pro** is a powerful web-based CAM (Computer-Aided Manufacturing) application for laser cutting and engraving machines. It runs entirely in your browser with no installation required, supporting vector and raster operations, real-time machine control via Web Serial API, and advanced path editing capabilities.

🔗 **[Live Demo](https://paulvern.free.nf/laser)**

---

## ✨ Key Features

### 🎨 **Design & Import**
- **Image Import**: Load PNG, JPG, GIF, and other image formats
- **SVG Support**: Import vector graphics directly from SVG files
- **Text Tool**: Create text objects with customizable fonts and sizes
- **Automatic Vectorization**: Convert bitmap images to vector paths using ImageTracer.js
- **Multi-Object Canvas**: Manage multiple objects with drag, resize, and transform tools

### ⚙️ **G-Code Generation**
- **Vector Mode**: Generate optimized G-Code for cutting/engraving vector paths
- **Raster Mode**: Create raster scan G-Code for image engraving with adjustable resolution (2-20 lines/mm)
- **Bidirectional Raster**: Optional bidirectional scanning for faster engraving
- **Multi-Pass Support**: Configure multiple passes for deeper cuts
- **Statistics**: Real-time calculation of lines, distance, and estimated time

### 🎮 **Machine Control**
- **Web Serial API**: Direct connection to CNC/laser controllers (GRBL, Marlin, etc.)
- **Real-Time Control**: Start, pause, resume, and emergency stop
- **Jog Control**: Manual axis movement with adjustable step sizes (0.1mm, 1mm, 10mm)
- **Frame Job**: Preview work area boundaries with laser pointer
- **Home Position**: Set and save custom home position
- **Console**: Send manual G-Code commands and monitor responses

### 🎬 **Simulation**
- **Real-Time Preview**: Visualize laser path before running
- **Speed Control**: Adjust simulation speed (1x-100x)
- **Laser Indicator**: Visual laser on/off states with glow effects
- **Progress Tracking**: Monitor position, progress percentage, and elapsed time
- **Mixed Mode**: Supports both vector and raster simulation

### ✂️ **Advanced Path Editor**
- **Path Selection**: Click and select individual paths
- **Path Deletion**: Remove unwanted paths
- **Small Path Cleanup**: Auto-delete paths shorter than 3mm
- **Color-Coded Paths**: Visual distinction between different paths
- **Path Length Display**: See length in mm for each path

### 💾 **Project Management**
- **Save Projects**: Export complete projects as `.lcp` files
- **Load Projects**: Restore all objects, settings, and configurations
- **Material Presets**: Save and load power/speed settings for different materials
- **Machine Profiles**: Store work area dimensions and configurations

### 🌍 **Multi-Language Support**
Complete translations available in **10 languages**:
- 🇬🇧 **English**
- 🇮🇹 **Italiano**
- 🇫🇷 **Français**
- 🇩🇪 **Deutsch**
- 🇪🇸 **Español**
- 🇧🇷 **Português**
- 🇩🇰 **Dansk**
- 🇷🇺 **Русский**
- 🇨🇳 **中文 (Chinese)**
- 🇯🇵 **日本語 (Japanese)**

Switch languages instantly with one click!

---

## 📋 Requirements

### Browser Support
- **Chrome/Edge 89+** (recommended) - Required for Web Serial API
- **Opera 75+**
- **Brave (Chromium-based)**

⚠️ **Firefox and Safari do not support Web Serial API** and cannot control machines directly. They can still be used for design and G-Code generation.

### Hardware
- **Laser/CNC Machine**: GRBL-compatible controller, Marlin, or similar
- **USB Connection**: Serial connection to machine (typically via USB)

---

## 🚀 Installation

### Option 1: Use Live Demo
Simply visit **[https://paulvern.free.nf/laser](https://paulvern.free.nf/laser)** - no installation needed!

### Option 2: Self-Host

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/lasercam-pro.git
cd lasercam-pro
```

2. **Files included**:
   - `index.html` - Main application
   - `lang.js` - Language translations (10 languages pre-configured)

3. **Serve with any web server**:

```bash
# Python 3
python -m http.server 8000

# Node.js (http-server)
npx http-server

# PHP
php -S localhost:8000
```

4. **Open in browser**:
```
http://localhost:8000
```

### Option 3: GitHub Pages
1. Fork this repository
2. Enable GitHub Pages in repository settings
3. Access at `https://yourusername.github.io/lasercam-pro`

---

## 📖 Usage Guide

### 1️⃣ **Setup Machine Profile**

1. Set your work area dimensions in **Machine Settings** (left panel)
   - Default: 300mm × 300mm
   - Adjust to match your laser bed size
2. Click **Save Profile** to persist settings

### 2️⃣ **Set Home Position**

1. Enter coordinates or use **Context Menu** (right-click) → "Set Home Here"
2. Home position is marked with green crosshair (H)
3. Use **Go Home** button to return machine to this position

### 3️⃣ **Import Design**

**Option A: Image**
1. Click **Import Image** in left panel
2. Select PNG/JPG file
3. Image appears centered on canvas

**Option B: SVG**
1. Click **Import Image** and select SVG file
2. Vector paths are automatically extracted

**Option C: Text**
1. Click **Add Text**
2. Enter text, choose font and size
3. Click **Create**

### 4️⃣ **Adjust Object Properties**

Select object and adjust in **Properties** panel:
- **Position**: X, Y coordinates
- **Size**: Width, Height (lock aspect ratio)
- **Power**: Laser power 1-100%
- **Speed**: Feed rate in mm/min (100-6000)
- **Passes**: Number of repetitions

### 5️⃣ **Vectorize Images** (Optional)

For bitmap images:
1. Select image object
2. Adjust **Vectorization** settings:
   - **Threshold**: 1-255 (black/white cutoff)
   - **Border Margin**: Pixels to consider as border
   - **Remove Borders**: Auto-remove edge artifacts
3. Click **Vectorize**
4. New vector object is created

### 6️⃣ **Edit Paths** (Advanced)

For vector objects:
1. Select vector object
2. Click **✂️ Edit Paths** button (toolbar)
3. Click paths to select them
4. Delete individual paths or all small paths
5. Click **Exit** when done

### 7️⃣ **Generate G-Code**

**Vector Mode:**
1. Click **📄 G-Code** button (toolbar)
2. Review code in modal
3. **Copy**, **Download**, or **Send to Machine**

**Raster Mode:**
1. Select bitmap/text object
2. Set **Raster Resolution** (lines/mm)
3. Enable/disable **Bidirectional** scanning
4. Click **Raster G-Code**
5. Switch to **Raster** tab in modal

### 8️⃣ **Simulate**

1. Click **🎬 Simulate** button
2. Adjust speed with slider (1x-100x)
3. Watch laser path animation
4. Use **Pause** or **Stop** controls

### 9️⃣ **Connect Machine**

1. Select **Baud Rate** (usually 115200 for GRBL)
2. Click **Connect**
3. Choose serial port from browser dialog
4. Status indicator turns green when connected

### 🔟 **Run Job**

**Method 1: From Toolbar**
1. Generate G-Code (step 7)
2. Click **Send to Machine** in modal

**Method 2: Direct Start**
1. Ensure objects are ready
2. Click **▶ START JOB** (right panel)
3. Monitor progress bar

**Emergency Stop:** Click 🛑 **STOP** button at any time

---

## 🛠️ Advanced Features

### 🎯 Context Menu
Right-click on canvas for quick actions:
- Set Home Here
- Select / Select All
- Duplicate / Delete
- Center Object
- Vectorize
- Generate G-Code
- Edit Paths
- Simulate
- Frame Job

### 🎨 Material Presets
Save common power/speed settings:
1. Click **New Preset** (left panel)
2. Enter name, power, speed
3. Click preset to apply to selected object(s)

Built-in presets:
- **Wood**: 70% / 1500 mm/min
- **Acrylic**: 100% / 400 mm/min
- **Paper**: 25% / 3000 mm/min

### 🖼️ Canvas Tools
- **📐 Fit**: Reset zoom and pan to default
- **🗑️ Delete**: Remove selected object
- **📋 Duplicate**: Clone selected object
- **🔲 Frame**: Preview work area on machine
- **✂️ Edit Paths**: Enter path editing mode

### 📟 Console
1. Click **📟** button (footer)
2. View sent/received G-Code
3. Send manual commands
4. Monitor machine responses

### ⌨️ Keyboard Shortcuts
- **Drag**: Move objects
- **Resize Handles**: Scale objects (corners)
- **Mouse Wheel**: Zoom in/out
- **Right-Click**: Context menu

---

## ⚙️ Configuration

### Language System

The `lang.js` file is **already included** with 10 complete translations. The language selector appears in the top-right header and switches the entire UI instantly.

**Structure of `lang.js`:**
```javascript
const LANG = {
    en: {
        _flag: '🇬🇧',
        _name: 'English',
        btn_connect: 'Connect',
        btn_start: '▶ START',
        // ... 100+ translation keys
    },
    it: { /* Italian */ },
    fr: { /* French */ },
    de: { /* German */ },
    es: { /* Spanish */ },
    pt: { /* Portuguese */ },
    da: { /* Danish */ },
    ru: { /* Russian */ },
    zh: { /* Chinese */ },
    ja: { /* Japanese */ }
};
```

**Adding a New Language:**
1. Edit `lang.js`
2. Copy an existing language object (e.g., `en`)
3. Add new language code (e.g., `nl` for Dutch):
```javascript
nl: {
    _flag: '🇳🇱',
    _name: 'Nederlands',
    btn_connect: 'Verbinden',
    // ... translate all keys
}
```
4. Refresh the page - language selector updates automatically!

### Machine Settings
Default settings in `localStorage`:
- `laserMachine`: Work area dimensions
- `laserHome`: Home position coordinates
- `laserPresets`: Material presets
- `laserLang`: Selected language

### G-Code Customization
Edit in code (line ~680 in HTML):
```javascript
generateVectorGCode() {
    let gcode = [
        '; LaserCAM v1.0 - Vector',
        'G21',  // Metric units
        'G90',  // Absolute positioning
        'M5',   // Laser off
        ''
    ];
    // ... modify as needed
}
```

---

## 🎨 Supported Formats

### Import
- **Images**: PNG, JPG, GIF, BMP, WEBP
- **Vectors**: SVG (path elements)
- **Projects**: `.lcp` (LaserCAM Project)

### Export
- **G-Code**: `.gcode`, `.nc`, `.txt`
- **Projects**: `.lcp` (JSON format)

---

## 🧪 Technical Details

### Technologies Used
- **HTML5 Canvas**: Rendering and visualization
- **Web Serial API**: Direct machine communication
- **ImageTracer.js**: Automatic vectorization ([github.com/jankovicsandras/imagetracerjs](https://github.com/jankovicsandras/imagetracerjs))
- **LocalStorage**: Persistent settings
- **CSS Grid**: Responsive layout
- **Vanilla JavaScript**: No frameworks, 100% standalone

### Architecture
```
┌─────────────────┬────────────────┬─────────────────┐
│  Left Panel     │  Canvas Area   │  Right Panel    │
│  - Project      │  - Objects     │  - Object List  │
│  - Machine      │  - Rulers      │  - Properties   │
│  - Import       │  - Grid        │  - Jog Control  │
│  - Vectorize    │  - Tools       │  - Start Job    │
│  - Presets      │  - Simulation  │                 │
└─────────────────┴────────────────┴─────────────────┘
└────────────────── Footer / Console ─────────────────┘
```

### File Structure
```
lasercam-pro/
├── index.html          # Main application (self-contained)
├── lang.js            # 10 language translations
├── README.md          # This file
└── LICENSE            # MIT License
```

### Data Flow
```
Image Import → Canvas Object → Vectorize (optional) → 
G-Code Generation → Simulation / Machine Control
```

---

## 🐛 Troubleshooting

### "Web Serial API not supported"
- Use Chrome/Edge/Opera browser
- Enable experimental features: `chrome://flags/#enable-web-serial`

### Machine doesn't respond
- Check baud rate (115200 for GRBL, 250000 for Marlin)
- Verify USB connection
- Try sending `$X` (GRBL unlock) or `M112` (Marlin emergency stop reset)

### Vectorization produces too many paths
- Increase **Threshold** value
- Enable **Remove Borders**
- Increase **Border Margin**
- Use **Delete Small Paths** in edit mode

### G-Code coordinates are wrong
- Verify **Machine Profile** dimensions match your laser bed
- Check **Home Position** is set correctly
- Ensure objects are within work area (0,0 to max X,Y)

### Simulation is too fast/slow
- Adjust **Speed** slider (1x-100x)
- Reduce point density by simplifying paths

### Language not switching
- Ensure `lang.js` is loaded (check browser console)
- Clear browser cache and refresh
- Check `LANG` object is defined: open console and type `LANG`

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Translation Contributors
Help translate LaserCAM to your language! The `lang.js` file contains ~150 keys. Simply:
1. Copy an existing language object
2. Translate all values (keep keys unchanged)
3. Submit a Pull Request

**Current languages**: English, Italian, French, German, Spanish, Portuguese, Danish, Russian, Chinese, Japanese

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👏 Credits

- **ImageTracer.js**: [github.com/jankovicsandras/imagetracerjs](https://github.com/jankovicsandras/imagetracerjs) - András Jankovics
- **Web Serial API**: [developer.mozilla.org/Web_Serial_API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API)
- **Icons**: Unicode emoji
- **Translation Contributors**: Community contributors for 10 language translations

---

## 📞 Support

- **Live Demo**: [https://paulvern.free.nf/laser](https://paulvern.free.nf/laser)
- **Issues**: [GitHub Issues](https://github.com/yourusername/lasercam-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lasercam-pro/discussions)

---

## ⚠️ Safety Warning

**Laser safety is paramount!**

- ⚠️ Never leave a running laser unattended
- 👓 Always use proper eye protection (wavelength-specific)
- 🌬️ Ensure adequate ventilation
- 🧯 Keep fire extinguisher nearby
- 🧪 Test on scrap material first
- 📍 Verify coordinates before starting jobs
- 🛑 Use emergency stop if anything goes wrong
- 📖 Read your machine's manual thoroughly

**This software is provided "as is" without warranty. Users are responsible for safe operation of their equipment.**

---

## 🗺️ Roadmap

- [ ] DXF file import
- [ ] Image filters (blur, sharpen, invert, etc.)
- [ ] Path optimization (TSP solver)
- [ ] Rotary axis support (cylindrical engraving)
- [ ] Camera alignment (vision positioning)
- [ ] Job queue management
- [ ] Material library expansion
- [ ] Offline PWA support
- [ ] Cloud project storage
- [ ] More language translations

---

## 📊 Project Stats

- **Lines of Code**: ~2,500 (HTML + JavaScript)
- **Languages**: 10 complete translations
- **Dependencies**: 1 (ImageTracer.js via CDN)
- **Browser Compatibility**: Chrome 89+, Edge 89+, Opera 75+
- **File Size**: ~120KB (uncompressed)
- **Development Time**: Professional-grade CAM software

---

<div align="center">

**Made with ❤️ for the maker community**

⭐ **Star this repo if you find it useful!**

[🔗 Live Demo](https://paulvern.free.nf/laser) | [🐛 Report Bug](https://github.com/yourusername/lasercam-pro/issues) | [✨ Request Feature](https://github.com/yourusername/lasercam-pro/issues)

---

### Quick Links

[Installation](#-installation) • [Usage Guide](#-usage-guide) • [Features](#-key-features) • [Languages](#-multi-language-support) • [Contributing](#-contributing)

---

**LaserCAM Pro** - Professional Laser Engraving in Your Browser

*No installation • 10 Languages • Open Source • Free Forever*

</div>