#!/usr/bin/env python3
"""
PyLaser v0.93 - main.py
Applicazione principale modulare con scrollbar pannello controlli.

Moduli richiesti:
    - gcode_generator.py  (generazione GCode vettoriale e da immagine)
    - vectorizer.py       (vettorizzazione immagini)
    - laser_controller.py (comunicazione seriale)
    - canvas_widgets.py   (canvas e preview)
    - dialogs.py          (finestre dialogo)
    - strings.py          (localizzazione)
    - themes.py           (temi grafici)
    - help_content.py     (contenuto help)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import sys
import json
from pathlib import Path
from typing import Optional

# ══════════════════════════════════════════════════════════════════════════════
#  IMPORTA MODULI LOCALI
# ══════════════════════════════════════════════════════════════════════════════
try:
    from strings import get_strings, available_languages, DEFAULT_LANGUAGE
except ImportError:
    print("❌ ERRORE: strings.py non trovato!")
    sys.exit(1)

try:
    from themes import get_theme, available_themes, DEFAULT_THEME
except ImportError:
    print("❌ ERRORE: themes.py non trovato!")
    sys.exit(1)

try:
    from help_content import get_help
except ImportError:
    print("❌ ERRORE: help_content.py non trovato!")
    sys.exit(1)

try:
    from gcode_generator import (
        GCodeFactory, GCodeSource, GCodeProgram, GCodeParser,
        ImageGCodeGenerator, VectorGCodeGenerator,
        RasterDirection, RasterMode
    )
except ImportError:
    print("❌ ERRORE: gcode_generator.py non trovato!")
    sys.exit(1)

try:
    from vectorizer import Vectorizer
except ImportError:
    print("❌ ERRORE: vectorizer.py non trovato!")
    sys.exit(1)

try:
    from laser_controller import LaserController, ControllerType
except ImportError:
    print("❌ ERRORE: laser_controller.py non trovato!")
    sys.exit(1)

try:
    from canvas_widgets import WorkAreaCanvas, VectorPreviewWindow
except ImportError:
    print("❌ ERRORE: canvas_widgets.py non trovato!")
    sys.exit(1)

try:
    from dialogs import (
        PreferencesDialog, HelpWindow,
        MaterialPresetDialog, MaterialPresetManager,
        EditPresetDialog, MaterialPreset
    )
except ImportError:
    print("❌ ERRORE: dialogs.py non trovato!")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
#  DIPENDENZE ESTERNE
# ══════════════════════════════════════════════════════════════════════════════
try:
    from PIL import Image, ImageTk, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  COSTANTI
# ══════════════════════════════════════════════════════════════════════════════
APP_VERSION = "0.93"
BAUDRATES   = [9600, 19200, 38400, 57600, 115200, 250000]
CONFIG_FILE = Path(__file__).parent / ".pylaser_config.json"


# ══════════════════════════════════════════════════════════════════════════════
#  GESTIONE CONFIGURAZIONE
# ══════════════════════════════════════════════════════════════════════════════
def load_config() -> dict:
    """Carica la configurazione salvata."""
    defaults = {
        "language"      : DEFAULT_LANGUAGE,
        "theme"         : DEFAULT_THEME,
        "work_area_w"   : 400.0,
        "work_area_h"   : 400.0,
        "last_port"     : "",
        "last_baud"     : 115200,
        "feed_rate"     : 1000,
        "power"         : 200,
        "passes"        : 1,
        "last_source"   : "vector",
        "max_lines"     : 200,
        "img_mode"      : "grayscale",
        "img_direction" : "horizontal",
        "method"        : "Contours",
        "width_mm"      : 100.0,
        "height_mm"     : 100.0,
    }
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            defaults.update(data)
    except Exception:
        pass
    return defaults


def save_config(config: dict):
    """Salva la configurazione su file."""
    try:
        CONFIG_FILE.write_text(
            json.dumps(config, indent=2), encoding="utf-8")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  SCROLLABLE FRAME HELPER
# ══════════════════════════════════════════════════════════════════════════════
class ScrollableFrame(ttk.Frame):
    """
    Frame con scrollbar verticale per contenere widget che eccedono lo schermo.
    """
    def __init__(self, parent, theme, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.theme = theme
        
        # Canvas per lo scroll
        self.canvas = tk.Canvas(
            self, 
            bg=theme.base,
            highlightthickness=0,
            borderwidth=0
        )
        
        # Scrollbar verticale
        self.scrollbar = ttk.Scrollbar(
            self, 
            orient="vertical", 
            command=self.canvas.yview
        )
        
        # Frame interno che conterrà i widget
        self.inner_frame = ttk.Frame(self.canvas)
        
        # Configura il canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.inner_frame, 
            anchor="nw"
        )
        
        # Collega scrollbar al canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind eventi
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Scroll con rotella del mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)
    
    def _on_frame_configure(self, event=None):
        """Aggiorna la scrollregion quando il contenuto cambia."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Ridimensiona il frame interno alla larghezza del canvas."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """Gestisce scroll con rotella mouse (Windows/Mac)."""
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget and self._is_child(widget):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_mousewheel_linux(self, event):
        """Gestisce scroll con rotella mouse (Linux)."""
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget and self._is_child(widget):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
    
    def _is_child(self, widget):
        """Verifica se un widget è figlio di questo ScrollableFrame."""
        while widget:
            if widget == self:
                return True
            widget = widget.master
        return False
    
    def get_frame(self):
        """Ritorna il frame interno dove aggiungere i widget."""
        return self.inner_frame
    
    def unbind_mousewheel(self):
        """Rimuove i binding della rotella mouse."""
        try:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        except:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  APP PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    """Applicazione principale PyLaser v0.93."""

    def __init__(self):
        super().__init__()

        # ── Configurazione ─────────────────────────────────────────────────
        self.config_data = load_config()
        self._lang       = self.config_data["language"]
        self._theme_name = self.config_data["theme"]

        self.s = get_strings(self._lang)
        self.t = get_theme(self._theme_name)
        self.h = get_help(self._lang)

        self.title(
            f"{self.s.app_title}  "
            f"{self.s.app_version_prefix}{APP_VERSION}")
        
        # ── Fullscreen ─────────────────────────────────────────────────────
        self.geometry("1380x900")
        self.minsize(1100, 700)
        
        # Massimizza la finestra
        try:
            self.state('zoomed')  # Windows
        except:
            try:
                self.attributes('-zoomed', True)  # Linux
            except:
                screen_w = self.winfo_screenwidth()
                screen_h = self.winfo_screenheight()
                self.geometry(f"{screen_w}x{screen_h}+0+0")
        
        self.configure(bg=self.t.base)

        # ── Stato applicazione ─────────────────────────────────────────────
        self.original_image : Optional[Image.Image] = None
        self.binary_np      : Optional["np.ndarray"] = None
        self.gcode_program  : Optional[GCodeProgram] = None
        self.rotation       = 0
        self._stop_event    = threading.Event()
        self._photo_orig    = None
        self._photo_proc    = None
        self._ar_updating   = False

        # ── Moduli ────────────────────────────────────────────────────────
        self.vec        = Vectorizer(log_cb=self._log)
        self.vec.set_strings(self.s)
        self.ctrl       = LaserController(log_cb=self._log)
        self.preset_mgr = MaterialPresetManager()

        # ── Build UI ───────────────────────────────────────────────────────
        self._build_styles()
        self._build_menu()
        self._build_ui()

        # ── Init ───────────────────────────────────────────────────────────
        self._refresh_ports()
        self.after(4000, self._port_watcher)
        self.protocol("WM_DELETE_WINDOW", self._quit)

        # ── Shortcuts ─────────────────────────────────────────────────────
        self.bind("<F1>",        lambda _: self._show_help())
        self.bind("<Control-o>", lambda _: self._open_image())
        self.bind("<Control-s>", lambda _: self._save_gcode())
        self.bind("<Control-g>", lambda _: self._generate_gcode())

    # ══════════════════════════════════════════════════════════════════════
    #  STILI TTK
    # ══════════════════════════════════════════════════════════════════════
    def _build_styles(self):
        """Configura gli stili ttk in base al tema corrente."""
        t  = self.t
        st = ttk.Style(self)
        st.theme_use("clam")

        st.configure(".",
                     background=t.base, foreground=t.text,
                     font=("Segoe UI", 9), borderwidth=0)
        st.configure("TFrame",       background=t.base)
        st.configure("TLabel",       background=t.base, foreground=t.text)
        st.configure("TCheckbutton", background=t.base, foreground=t.text)
        st.configure("TRadiobutton", background=t.base, foreground=t.text)
        st.configure("TSeparator",   background=t.surface1)
        st.configure("TLabelframe",
                     background=t.base, foreground=t.blue,
                     relief="solid", borderwidth=1,
                     font=("Segoe UI", 9, "bold"))
        st.configure("TLabelframe.Label",
                     background=t.base, foreground=t.blue)
        st.configure("TButton",
                     background=t.surface0, foreground=t.text,
                     relief="flat", padding=(8, 4))
        st.map("TButton",
               background=[("active", t.surface1), ("pressed", t.blue)],
               foreground=[("active", t.text)])

        for name, bg, fg in [
            ("Blue",   t.blue,   t.base),
            ("Green",  t.green,  t.base),
            ("Red",    t.red,    t.base),
            ("Yellow", t.yellow, t.base),
            ("Teal",   t.teal,   t.base),
            ("Orange", t.peach,  t.base),
        ]:
            st.configure(f"{name}.TButton",
                         background=bg, foreground=fg,
                         font=("Segoe UI", 9, "bold"), padding=(8, 5))
            st.map(f"{name}.TButton",
                   background=[("active", t.mauve)])

        st.configure("TNotebook",     background=t.base, borderwidth=0)
        st.configure("TNotebook.Tab",
                     background=t.mantle, foreground=t.subtext,
                     padding=(12, 5))
        st.map("TNotebook.Tab",
               background=[("selected", t.surface0)],
               foreground=[("selected", t.blue)])
        st.configure("TCombobox",
                     fieldbackground=t.surface0,
                     background=t.surface0, foreground=t.text)
        st.configure("TEntry",
                     fieldbackground=t.surface0,
                     foreground=t.text, insertcolor=t.text)
        st.configure("TScale",
                     background=t.base,
                     troughcolor=t.surface0, sliderthickness=16)
        st.configure("TProgressbar",
                     troughcolor=t.surface0, background=t.green,
                     borderwidth=0, thickness=14)

    # ══════════════════════════════════════════════════════════════════════
    #  MENU
    # ══════════════════════════════════════════════════════════════════════
    def _build_menu(self):
        """Costruisce il menu principale."""
        t, s = self.t, self.s

        def mk(parent):
            return tk.Menu(parent, tearoff=0,
                           bg=t.mantle, fg=t.text,
                           activebackground=t.blue,
                           activeforeground=t.base)

        mb = mk(self)
        self.config(menu=mb)

        fm = mk(mb)
        mb.add_cascade(label=s.menu_file, menu=fm)
        fm.add_command(label=s.menu_open_image,
                       command=self._open_image,  accelerator="Ctrl+O")
        fm.add_command(label=s.menu_save_gcode,
                       command=self._save_gcode,  accelerator="Ctrl+S")
        fm.add_command(label=s.menu_load_gcode,
                       command=self._load_gcode)
        fm.add_separator()
        fm.add_command(label=s.menu_exit, command=self._quit)

        vm = mk(mb)
        mb.add_cascade(label=s.menu_view, menu=vm)
        vm.add_command(label=s.menu_vector_preview,
                       command=self._open_vector_preview)
        vm.add_command(label=s.menu_gcode_text,
                       command=self._show_gcode_text)
        vm.add_command(label=s.menu_fit_view,
                       command=lambda: self.work_canvas.fit())

        lm = mk(mb)
        mb.add_cascade(label=s.menu_laser, menu=lm)
        lm.add_command(label=s.menu_send_bbox,
                       command=self._send_bbox)
        lm.add_command(label=s.menu_emergency_stop,
                       command=self._emergency_stop)

        tm = mk(mb)
        mb.add_cascade(label="🛠 Tools", menu=tm)
        tm.add_command(label="📦 Material Presets…",
                       command=self._show_material_presets)
        tm.add_separator()
        tm.add_command(label="⚙ Preferences…",
                       command=self._show_preferences)

        hm = mk(mb)
        mb.add_cascade(label="❓ Help", menu=hm)
        hm.add_command(label="📚 Help / Guida",
                       command=self._show_help, accelerator="F1")
        hm.add_separator()
        hm.add_command(label="ℹ About", command=self._show_about)

    # ══════════════════════════════════════════════════════════════════════
    #  UI PRINCIPALE
    # ══════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        """Costruisce l'interfaccia utente principale."""
        s, t = self.s, self.t

        # ── Header ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=t.mantle)
        hdr.pack(fill="x")

        tk.Label(hdr, text="🔥",
                 bg=t.mantle,
                 font=("Segoe UI", 16)).pack(
            side="left", padx=(10, 4), pady=6)
        tk.Label(hdr, text=s.app_title,
                 bg=t.mantle, fg=t.blue,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(hdr,
                 text=f" {s.app_version_prefix}{APP_VERSION}",
                 bg=t.mantle, fg=t.subtext).pack(side="left")

        self.v_controller_info = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self.v_controller_info,
                 bg=t.mantle, fg=t.teal,
                 font=("Consolas", 8)).pack(side="right", padx=12)

        self.v_status = tk.StringVar(value=s.status_ready)
        tk.Label(hdr, textvariable=self.v_status,
                 bg=t.mantle, fg=t.yellow,
                 font=("Consolas", 9)).pack(side="right", padx=12)

        info_text = f"🌐 {self._lang}  |  🎨 {self._theme_name}"
        self._pref_label = tk.Label(
            hdr, text=info_text,
            bg=t.mantle, fg=t.teal,
            font=("Segoe UI", 8), cursor="hand2")
        self._pref_label.pack(side="right", padx=8)
        self._pref_label.bind("<Button-1>",
                              lambda _: self._show_preferences())

        # ── Body ────────────────────────────────────────────────────────
        body = tk.PanedWindow(self, orient="horizontal",
                              bg=t.base, sashwidth=5)
        body.pack(fill="both", expand=True, padx=4, pady=4)

        # ── Pannello sinistro con SCROLLBAR ─────────────────────────────
        left_container = ttk.Frame(body)
        body.add(left_container, minsize=360)
        
        self.scroll_frame = ScrollableFrame(left_container, theme=t)
        self.scroll_frame.pack(fill="both", expand=True)
        
        left = self.scroll_frame.get_frame()

        nb = ttk.Notebook(left)
        nb.pack(fill="both", expand=True, padx=2, pady=2)

        t_img = ttk.Frame(nb)
        t_vec = ttk.Frame(nb)
        t_pos = ttk.Frame(nb)
        t_las = ttk.Frame(nb)

        nb.add(t_img, text=s.tab_image)
        nb.add(t_vec, text=s.tab_vectorize)
        nb.add(t_pos, text=s.tab_position)
        nb.add(t_las, text=s.tab_laser)

        self._tab_image(t_img)
        self._tab_vectorize(t_vec)
        self._tab_position(t_pos)
        self._tab_laser(t_las)

        # Pannello destro: canvas + bottom
        right = tk.PanedWindow(body, orient="vertical",
                               bg=t.base, sashwidth=5)
        body.add(right, minsize=680)

        # Canvas area lavoro
        work_frm = ttk.LabelFrame(
            right, text=s.canvas_work_area_title, padding=4)
        right.add(work_frm, minsize=420)

        self.work_canvas = WorkAreaCanvas(
            work_frm,
            work_w=self.config_data["work_area_w"],
            work_h=self.config_data["work_area_h"],
            theme=self.t, strings=self.s, log_cb=self._log)
        self.work_canvas.pack(fill="both", expand=True)
        self.work_canvas.set_position_callback(self._on_model_moved)

        # Pannello inferiore
        bottom = ttk.Frame(right)
        right.add(bottom, minsize=200)
        self._build_bottom(bottom)

        self.after(200, self.work_canvas.fit)

    def _build_bottom(self, parent):
        """Costruisce il pannello inferiore (preview + log)."""
        s, t = self.s, self.t

        paned = tk.PanedWindow(parent, orient="horizontal",
                               bg=t.base, sashwidth=4)
        paned.pack(fill="both", expand=True)

        # Preview originale
        f1 = ttk.LabelFrame(paned, text=s.preview_original, padding=2)
        paned.add(f1, minsize=160)
        self.canvas_orig = tk.Canvas(
            f1, bg=t.mantle, highlightthickness=0, height=190)
        self.canvas_orig.pack(fill="both", expand=True)

        # Preview elaborata / GCode
        f2 = ttk.LabelFrame(paned, text=s.preview_processed, padding=2)
        paned.add(f2, minsize=160)
        self.canvas_proc = tk.Canvas(
            f2, bg=t.mantle, highlightthickness=0, height=190)
        self.canvas_proc.pack(fill="both", expand=True)

        # Log
        f3 = ttk.LabelFrame(paned, text=s.lbl_log, padding=2)
        paned.add(f3, minsize=300)
        self.log_box = scrolledtext.ScrolledText(
            f3, height=9, wrap="word",
            bg=t.log_bg, fg=t.log_text,
            font=("Consolas", 8),
            insertbackground=t.text,
            borderwidth=0, relief="flat")
        self.log_box.pack(fill="both", expand=True)
        ttk.Button(f3, text=s.btn_clear_log,
                   command=lambda: self.log_box.delete("1.0", "end")
                   ).pack(anchor="e", padx=2, pady=1)

    # ══════════════════════════════════════════════════════════════════════
    #  TAB IMMAGINE
    # ══════════════════════════════════════════════════════════════════════
    def _tab_image(self, p):
        """Costruisce il tab Immagine."""
        s, t = self.s, self.t

        f = self._lf(p, s.lf_import)
        ttk.Button(f, text=s.btn_open_image,
                   command=self._open_image,
                   style="Blue.TButton").pack(fill="x", pady=(0, 4))
        self.v_img_info = tk.StringVar(value=s.lbl_no_image)
        ttk.Label(f, textvariable=self.v_img_info,
                  foreground=t.subtext,
                  wraplength=280, justify="left").pack(fill="x")

        f2 = self._lf(p, s.lf_rotation)
        rf = ttk.Frame(f2)
        rf.pack(fill="x")
        ttk.Button(rf, text=s.btn_rot_left,
                   command=lambda: self._rotate(-90),
                   style="Teal.TButton").pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(rf, text=s.btn_rot_right,
                   command=lambda: self._rotate(90),
                   style="Teal.TButton").pack(
            side="left", expand=True, fill="x", padx=(2, 0))
        ttk.Button(f2, text=s.btn_rot_180,
                   command=lambda: self._rotate(180)).pack(
            fill="x", pady=2)
        self.v_rotation = tk.StringVar(value=s.lbl_rotation)
        ttk.Label(f2, textvariable=self.v_rotation,
                  foreground=t.teal).pack()

        f3 = self._lf(p, s.lf_flip)
        ff = ttk.Frame(f3)
        ff.pack(fill="x")
        ttk.Button(ff, text=s.btn_flip_h,
                   command=lambda: self._flip("h")).pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(ff, text=s.btn_flip_v,
                   command=lambda: self._flip("v")).pack(
            side="left", expand=True, fill="x", padx=(2, 0))

        f4 = self._lf(p, s.lf_preprocess)
        self.v_threshold = self._slider(f4, s.lbl_threshold, 0, 255, 128)
        self.v_blur      = self._slider(f4, s.lbl_blur, 0, 10, 2)
        self.v_invert    = tk.BooleanVar(value=False)
        self.v_denoise   = tk.BooleanVar(value=False)
        ttk.Checkbutton(f4, text=s.chk_invert,
                        variable=self.v_invert,
                        command=self._update_proc).pack(anchor="w")
        ttk.Checkbutton(f4, text=s.chk_denoise,
                        variable=self.v_denoise,
                        command=self._update_proc).pack(anchor="w")
        ttk.Button(f4, text=s.btn_update_preview,
                   command=self._update_proc).pack(fill="x", pady=(6, 0))

    # ══════════════════════════════════════════════════════════════════════
    #  TAB VETTORIZZA
    # ══════════════════════════════════════════════════════════════════════
    def _tab_vectorize(self, p):
        """Costruisce il tab Vettorizza / Genera GCode."""
        s, t = self.s, self.t

        # ── Sorgente GCode ───────────────────────────────────────────────
        f0 = self._lf(p, "🎯 Sorgente GCode")
        self.v_gcode_source = tk.StringVar(
            value=self.config_data.get("last_source", "vector"))
        ttk.Radiobutton(
            f0,
            text="📐 Vettoriale  (contorni / raster / hatching)",
            variable=self.v_gcode_source, value="vector",
            command=self._on_source_changed).pack(anchor="w", pady=1)
        ttk.Radiobutton(
            f0,
            text="🖼 Immagine diretta  (PWM / grayscale)",
            variable=self.v_gcode_source, value="image",
            command=self._on_source_changed).pack(anchor="w", pady=1)

        # ── Opzioni VETTORIALE ───────────────────────────────────────────
        self.f_method = self._lf(p, s.lf_method)
        ttk.Label(self.f_method, text=s.lbl_strategy).pack(anchor="w")
        self.v_method = tk.StringVar(
            value=self.config_data.get("method", s.method_contours))
        self.method_combo = ttk.Combobox(
            self.f_method, textvariable=self.v_method,
            values=[s.method_contours, s.method_centerline,
                    s.method_raster, s.method_hatching],
            state="readonly")
        self.method_combo.pack(fill="x", pady=(2, 4))

        # ── Opzioni IMMAGINE ─────────────────────────────────────────────
        self.f_image_opts = self._lf(p, "🖼 Opzioni Immagine")

        ttk.Label(self.f_image_opts,
                  text="Modalità:",
                  foreground=t.subtext).pack(anchor="w")
        self.v_image_mode = tk.StringVar(
            value=self.config_data.get("img_mode", "grayscale"))
        for txt, val in [("Grayscale (PWM)", "grayscale"),
                          ("Dithering",       "dithering"),
                          ("Threshold",       "threshold")]:
            ttk.Radiobutton(self.f_image_opts, text=txt,
                            variable=self.v_image_mode,
                            value=val).pack(anchor="w")

        ttk.Separator(self.f_image_opts,
                      orient="horizontal").pack(fill="x", pady=6)

        self.v_max_lines = self._slider(
            self.f_image_opts, "Max righe scansione",
            50, 1000,
            self.config_data.get("max_lines", 200), res=10)
        tk.Label(self.f_image_opts,
                 text="↑ Più righe = più dettaglio, più lento",
                 bg=t.base, fg=t.yellow,
                 font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 4))

        ttk.Button(self.f_image_opts,
                   text="👁 Anteprima immagine ridimensionata",
                   command=self._preview_image_resolution,
                   style="Blue.TButton").pack(fill="x", pady=(0, 4))

        ttk.Separator(self.f_image_opts,
                      orient="horizontal").pack(fill="x", pady=4)

        ttk.Label(self.f_image_opts,
                  text="Direzione scansione:",
                  foreground=t.subtext).pack(anchor="w")
        self.v_img_direction = tk.StringVar(
            value=self.config_data.get("img_direction", "horizontal"))
        for txt, val in [("↔ Orizzontale", "horizontal"),
                          ("↕ Verticale",   "vertical")]:
            ttk.Radiobutton(self.f_image_opts, text=txt,
                            variable=self.v_img_direction,
                            value=val).pack(anchor="w")

        # ── Dimensioni output ────────────────────────────────────────────
        f2 = self._lf(p, s.lf_dimensions)

        ttk.Label(f2, text=s.lbl_width_mm).grid(
            row=0, column=0, sticky="w", pady=2)
        self.v_width = tk.DoubleVar(
            value=self.config_data.get("width_mm", 100.0))
        e_width = ttk.Entry(f2, textvariable=self.v_width, width=9)
        e_width.grid(row=0, column=1, padx=4)

        ttk.Label(f2, text=s.lbl_height_mm).grid(
            row=1, column=0, sticky="w", pady=2)
        self.v_height = tk.DoubleVar(
            value=self.config_data.get("height_mm", 100.0))
        e_height = ttk.Entry(f2, textvariable=self.v_height, width=9)
        e_height.grid(row=1, column=1, padx=4)

        self.v_keep_ratio = tk.BooleanVar(value=True)
        ttk.Checkbutton(f2, text=s.chk_keep_ratio,
                        variable=self.v_keep_ratio).grid(
            row=2, columnspan=2, sticky="w")

        # Aspect ratio automatico
        def _on_width_changed(*_):
            if self._ar_updating or not self.v_keep_ratio.get():
                return
            if self.original_image is None:
                return
            try:
                self._ar_updating = True
                iw, ih = self.original_image.size
                if iw:
                    self.v_height.set(
                        round(self.v_width.get() * ih / iw, 2))
            finally:
                self._ar_updating = False

        def _on_height_changed(*_):
            if self._ar_updating or not self.v_keep_ratio.get():
                return
            if self.original_image is None:
                return
            try:
                self._ar_updating = True
                iw, ih = self.original_image.size
                if ih:
                    self.v_width.set(
                        round(self.v_height.get() * iw / ih, 2))
            finally:
                self._ar_updating = False

        self.v_width.trace_add("write",  _on_width_changed)
        self.v_height.trace_add("write", _on_height_changed)

        # ── Parametri avanzati ───────────────────────────────────────────
        f3 = self._lf(p, s.lf_advanced)
        self.v_simplify  = self._slider(
            f3, s.lbl_simplify,    0,  10,    2)
        self.v_gap       = self._slider(
            f3, s.lbl_gap,         1,  20,    2)
        self.v_hatch_ang = self._slider(
            f3, s.lbl_hatch_angle, 0, 180,   45)
        self.v_feed_rate = self._slider(
            f3, s.lbl_feed_rate, 100, 6000,
            self.config_data["feed_rate"], res=100)
        self.v_power     = self._slider(
            f3, s.lbl_power, 0, 255,
            self.config_data["power"])
        self.v_passes    = self._slider(
            f3, s.lbl_passes, 1, 10,
            self.config_data.get("passes", 1))

        # ── Preset ──────────────────────────────────────────────────────
        pb = ttk.Frame(p)
        pb.pack(fill="x", padx=6, pady=(4, 0))
        ttk.Button(pb, text="📦 Preset materiale",
                   command=self._load_material_preset,
                   style="Teal.TButton").pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(pb, text="💾 Salva preset",
                   command=self._save_current_as_preset,
                   style="Orange.TButton").pack(
            side="left", expand=True, fill="x", padx=(2, 0))

        # ── Genera ──────────────────────────────────────────────────────
        ttk.Button(p, text=s.btn_generate_gcode,
                   command=self._generate_gcode,
                   style="Green.TButton").pack(
            fill="x", padx=6, pady=6)

        # ── Info GCode ───────────────────────────────────────────────────
        f4 = self._lf(p, s.lf_gcode_info)
        self.v_gcode_info = tk.StringVar(value=s.lbl_no_gcode)
        ttk.Label(f4, textvariable=self.v_gcode_info,
                  foreground=t.subtext,
                  wraplength=280, justify="left").pack(fill="x")

        # ── Output ───────────────────────────────────────────────────────
        br = ttk.Frame(p)
        br.pack(fill="x", padx=6)
        ttk.Button(br, text=s.btn_save_gcode,
                   command=self._save_gcode).pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(br, text=s.btn_gcode_text,
                   command=self._show_gcode_text).pack(
            side="left", expand=True, fill="x", padx=2)
        ttk.Button(br, text=s.btn_vector_preview,
                   command=self._open_vector_preview,
                   style="Blue.TButton").pack(
            side="left", expand=True, fill="x", padx=(2, 0))

        # ── Simulazione ──────────────────────────────────────────────────
        f5 = self._lf(p, s.lf_simulation)
        self.v_sim_speed = self._slider(f5, s.lbl_sim_speed, 1, 50, 10)
        sr = ttk.Frame(f5)
        sr.pack(fill="x", pady=2)
        ttk.Button(sr, text=s.btn_start_sim,
                   command=self._start_sim,
                   style="Green.TButton").pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(sr, text=s.btn_stop_sim,
                   command=self._stop_sim,
                   style="Red.TButton").pack(
            side="left", expand=True, fill="x", padx=(2, 0))

        # Applica visibilità iniziale
        self._on_source_changed()

    def _on_source_changed(self):
        """Mostra/nasconde i frame in base alla sorgente selezionata."""
        source = self.v_gcode_source.get()
        if source == "vector":
            self.f_image_opts.pack_forget()
            self.f_method.pack(fill="x", padx=6, pady=3)
        else:
            self.f_method.pack_forget()
            self.f_image_opts.pack(fill="x", padx=6, pady=3)

    # ══════════════════════════════════════════════════════════════════════
    #  TAB POSIZIONE
    # ══════════════════════════════════════════════════════════════════════
    def _tab_position(self, p):
        """Costruisce il tab Posizione."""
        s, t = self.s, self.t

        f = self._lf(p, s.lf_work_area)
        for label, attr, cfg_key, row in [
            (s.lbl_work_width,  "v_work_w", "work_area_w", 0),
            (s.lbl_work_height, "v_work_h", "work_area_h", 1),
        ]:
            ttk.Label(f, text=label).grid(
                row=row, column=0, sticky="w", pady=2)
            var = tk.DoubleVar(
                value=self.config_data.get(cfg_key, 400.0))
            setattr(self, attr, var)
            ttk.Entry(f, textvariable=var, width=8).grid(
                row=row, column=1, padx=4)
        ttk.Button(f, text=s.btn_apply_work_area,
                   command=self._apply_work_area).grid(
            row=2, columnspan=2, sticky="ew", pady=4)

        f2 = self._lf(p, s.lf_model_position)
        for label, attr, row in [
            (s.lbl_model_x, "v_model_x", 0),
            (s.lbl_model_y, "v_model_y", 1),
        ]:
            ttk.Label(f2, text=label).grid(
                row=row, column=0, sticky="w", pady=2)
            var = tk.DoubleVar(value=0.0)
            setattr(self, attr, var)
            ttk.Entry(f2, textvariable=var, width=9).grid(
                row=row, column=1, padx=4)
        ttk.Button(f2, text=s.btn_apply_position,
                   command=self._apply_model_pos,
                   style="Blue.TButton").grid(
            row=2, columnspan=2, sticky="ew", pady=4)

        f3 = self._lf(p, s.lf_quick_position)
        for label, where in [
            (s.btn_pos_center, "center"),
            (s.btn_pos_tl,     "tl"),
            (s.btn_pos_tr,     "tr"),
            (s.btn_pos_bl,     "bl"),
            (s.btn_pos_br,     "br"),
        ]:
            ttk.Button(f3, text=label,
                       command=lambda w=where: self._quick_pos(w)
                       ).pack(fill="x", pady=1)

        f4 = self._lf(p, s.lf_bbox_preview)
        ttk.Label(f4, text=s.lbl_bbox_desc,
                  foreground=t.subtext, wraplength=280).pack(fill="x")
        self.v_bbox_feed = self._slider(
            f4, s.lbl_bbox_feed, 100, 3000, 500, res=100)
        ttk.Button(f4, text=s.btn_send_bbox,
                   command=self._send_bbox,
                   style="Yellow.TButton").pack(fill="x", pady=(6, 0))

        f5 = self._lf(p, s.lf_model_info)
        self.v_model_info = tk.StringVar(value=s.lbl_no_model)
        ttk.Label(f5, textvariable=self.v_model_info,
                  foreground=t.teal,
                  font=("Consolas", 8),
                  wraplength=280, justify="left").pack(fill="x")

    # ══════════════════════════════════════════════════════════════════════
    #  TAB LASER
    # ══════════════════════════════════════════════════════════════════════
    def _tab_laser(self, p):
        """Costruisce il tab Laser."""
        s, t = self.s, self.t

        f = self._lf(p, s.lf_connection)
        r1 = ttk.Frame(f)
        r1.pack(fill="x", pady=2)
        ttk.Label(r1, text=s.lbl_port, width=7).pack(side="left")
        self.v_port = tk.StringVar(
            value=self.config_data.get("last_port", ""))
        self.combo_port = ttk.Combobox(
            r1, textvariable=self.v_port, width=12, state="readonly")
        self.combo_port.pack(side="left", fill="x",
                             expand=True, padx=4)
        ttk.Button(r1, text="↻", width=3,
                   command=self._refresh_ports).pack(side="left")

        r2 = ttk.Frame(f)
        r2.pack(fill="x", pady=2)
        ttk.Label(r2, text=s.lbl_baud, width=7).pack(side="left")
        self.v_baud = tk.IntVar(
            value=self.config_data.get("last_baud", 115200))
        ttk.Combobox(r2, textvariable=self.v_baud,
                     values=BAUDRATES, width=10,
                     state="readonly").pack(side="left", padx=4)

        self.v_simulate = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text=s.chk_simulation,
                        variable=self.v_simulate,
                        command=self._toggle_sim_mode).pack(
            anchor="w", pady=2)

        r3 = ttk.Frame(f)
        r3.pack(fill="x", pady=4)
        self.btn_conn = ttk.Button(r3, text=s.btn_connect,
                                    command=self._connect,
                                    style="Blue.TButton")
        self.btn_conn.pack(side="left", expand=True,
                           fill="x", padx=(0, 2))
        self.btn_disc = ttk.Button(r3, text=s.btn_disconnect,
                                    command=self._disconnect)
        self.btn_disc.pack(side="left", expand=True,
                           fill="x", padx=(2, 0))
        self.btn_disc.state(["disabled"])

        self.v_conn_lbl = tk.StringVar(value=s.lbl_not_connected)
        ttk.Label(f, textvariable=self.v_conn_lbl,
                  foreground=t.subtext).pack()

        f2 = self._lf(p, s.lf_home)
        ttk.Label(f2, text=s.lbl_home_desc,
                  foreground=t.subtext,
                  wraplength=280).pack(fill="x")

        self.v_jog_dist = tk.DoubleVar(value=10.0)
        self.v_jog_feed = tk.IntVar(value=1000)
        jc = ttk.Frame(f2)
        jc.pack(fill="x", pady=4)
        ttk.Label(jc, text=s.lbl_jog_step).pack(side="left")
        ttk.Combobox(jc, textvariable=self.v_jog_dist,
                     values=[0.1, 0.5, 1, 5, 10, 25, 50],
                     width=7).pack(side="left", padx=4)
        ttk.Label(jc, text=s.lbl_jog_feed).pack(side="left")
        ttk.Entry(jc, textvariable=self.v_jog_feed,
                  width=6).pack(side="left", padx=2)

        jg = tk.Frame(f2, bg=t.base)
        jg.pack(pady=4)
        ttk.Button(jg, text="▲",
                   command=lambda: self._jog("Y", +1),
                   width=4).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(jg, text="◄",
                   command=lambda: self._jog("X", -1),
                   width=4).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(jg, text="●",
                   command=self._jog_zero,
                   width=4).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(jg, text="►",
                   command=lambda: self._jog("X", +1),
                   width=4).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(jg, text="▼",
                   command=lambda: self._jog("Y", -1),
                   width=4).grid(row=2, column=1, padx=2, pady=2)

        ttk.Button(f2, text=s.btn_set_home,
                   command=self._set_home,
                   style="Green.TButton").pack(fill="x", pady=(4, 0))
        ttk.Button(f2, text=s.btn_goto_home,
                   command=self._goto_home).pack(fill="x", pady=2)
        ttk.Button(f2, text=s.btn_unlock,
                   command=lambda: self.ctrl.unlock()
                   ).pack(fill="x", pady=2)

        f3 = self._lf(p, s.lf_manual_cmd)
        cr = ttk.Frame(f3)
        cr.pack(fill="x")
        self.v_cmd = tk.StringVar()
        e = ttk.Entry(cr, textvariable=self.v_cmd)
        e.pack(side="left", fill="x", expand=True, padx=(0, 4))
        e.bind("<Return>", lambda _: self._cmd_send())
        ttk.Button(cr, text=s.btn_send_cmd,
                   command=self._cmd_send).pack(side="left")

        f4 = self._lf(p, s.lf_send_gcode)
        self.v_progress     = tk.DoubleVar(value=0)
        self.v_progress_lbl = tk.StringVar(value=s.lbl_waiting)
        ttk.Progressbar(f4, variable=self.v_progress,
                        maximum=100).pack(fill="x", pady=4)
        ttk.Label(f4, textvariable=self.v_progress_lbl,
                  foreground=t.subtext).pack()

        r4 = ttk.Frame(f4)
        r4.pack(fill="x", pady=(6, 2))
        ttk.Button(r4, text=s.btn_start_engraving,
                   command=self._start_engraving,
                   style="Green.TButton").pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(r4, text=s.btn_stop_engraving,
                   command=self._stop_engraving,
                   style="Red.TButton").pack(
            side="left", expand=True, fill="x", padx=(2, 0))
        ttk.Button(f4, text=s.btn_emergency_stop,
                   command=self._emergency_stop,
                   style="Red.TButton").pack(fill="x", pady=2)

    # ══════════════════════════════════════════════════════════════════════
    #  HELPER WIDGET
    # ══════════════════════════════════════════════════════════════════════
    def _lf(self, parent, text, padding=8) -> ttk.LabelFrame:
        """Crea un LabelFrame standard."""
        f = ttk.LabelFrame(parent, text=text, padding=padding)
        f.pack(fill="x", padx=6, pady=3)
        return f

    def _slider(self, parent, label: str,
                from_: float, to: float,
                default: float, res: float = 1) -> tk.DoubleVar:
        """Crea uno slider con etichetta e valore corrente."""
        ttk.Label(parent, text=label,
                  foreground=self.t.subtext).pack(anchor="w")
        var = tk.DoubleVar(value=default)
        row = ttk.Frame(parent)
        row.pack(fill="x")
        lbl = ttk.Label(row, text=str(int(default)),
                        width=6, foreground=self.t.blue)
        lbl.pack(side="right")
        ttk.Scale(row, from_=from_, to=to, variable=var,
                  orient="horizontal",
                  command=lambda v, l=lbl:
                  l.config(text=f"{float(v):.0f}")
                  ).pack(side="left", fill="x", expand=True)
        return var

    # ══════════════════════════════════════════════════════════════════════
    #  LOG
    # ══════════════════════════════════════════════════════════════════════
    def _log(self, msg: str):
        """Aggiunge un messaggio al log (thread-safe)."""
        ts = time.strftime("%H:%M:%S")
        self.after(0, self._append_log, f"[{ts}] {msg}\n")

    def _append_log(self, line: str):
        """Append al widget log nel thread principale."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", line)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════
    #  DIALOGHI
    # ══════════════════════════════════════════════════════════════════════
    def _show_preferences(self):
        dlg = PreferencesDialog(
            self, self._lang, self._theme_name, self.t,
            available_languages(), available_themes())
        changed = (dlg.result_lang  != self._lang or
                   dlg.result_theme != self._theme_name)
        if changed:
            self.config_data["language"] = dlg.result_lang
            self.config_data["theme"]    = dlg.result_theme
            save_config(self.config_data)
            msg = {
                "Italiano": "Riavvia per applicare le modifiche.",
                "English":  "Please restart to apply changes.",
                "Español":  "Reinicia para aplicar los cambios.",
                "Deutsch":  "Bitte neu starten.",
            }.get(dlg.result_lang, "Restart to apply changes.")
            messagebox.showinfo("Preferences", msg)

    def _show_help(self):
        HelpWindow(self, self.t, self.h, APP_VERSION)

    def _show_about(self):
        messagebox.showinfo(
            "About PyLaser",
            f"PyLaser  v{APP_VERSION}\n\n"
            f"Laser engraving application\n"
            f"with vectorization, direct image GCode,\n"
            f"simulation and serial control.\n\n"
            f"Theme    : {self._theme_name}\n"
            f"Language : {self._lang}\n\n"
            f"© 2024 – Open Source")

    def _show_material_presets(self):
        MaterialPresetDialog(
            self, self.preset_mgr, self.t, self.s,
            on_apply=self._apply_material_preset)

    def _load_material_preset(self):
        self._show_material_presets()

    def _save_current_as_preset(self):
        preset = MaterialPreset(
            name="Nuovo preset",
            feed_rate=int(self.v_feed_rate.get()),
            power=int(self.v_power.get()),
            passes=int(self.v_passes.get()),
            resolution=self.v_max_lines.get() / 1000.0,
            method=self.v_method.get(),
            notes="")
        EditPresetDialog(self, self.preset_mgr, self.t,
                         preset=preset,
                         on_save=lambda: self._log("💾 Preset salvato"))

    def _apply_material_preset(self, preset):
        self.v_feed_rate.set(preset.feed_rate)
        self.v_power.set(preset.power)
        self.v_passes.set(preset.passes)
        self.v_max_lines.set(
            max(50, min(1000, int(preset.resolution * 1000))))
        method_map = {
            "Contours"  : self.s.method_contours,
            "Centerline": self.s.method_centerline,
            "Raster"    : self.s.method_raster,
            "Hatching"  : self.s.method_hatching,
        }
        self.v_method.set(
            method_map.get(preset.method, self.s.method_contours))
        self._log(f"📦 Preset '{preset.name}' caricato")

    # ══════════════════════════════════════════════════════════════════════
    #  PORTE SERIALI
    # ══════════════════════════════════════════════════════════════════════
    def _refresh_ports(self):
        ports = LaserController.list_ports()
        self.combo_port["values"] = ports
        if ports and not self.v_port.get():
            self.v_port.set(ports[0])

    def _port_watcher(self):
        if not self.ctrl.is_connected():
            self._refresh_ports()
        self.after(4000, self._port_watcher)

    # ══════════════════════════════════════════════════════════════════════
    #  IMMAGINE
    # ══════════════════════════════════════════════════════════════════════
    def _open_image(self):
        """Apre un file immagine e aggiorna le dimensioni output."""
        path = filedialog.askopenfilename(
            title=self.s.btn_open_image,
            filetypes=[
                ("Images",
                 "*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.gif"),
                ("All", "*.*")])
        if not path:
            return
        try:
            self.original_image = Image.open(path).convert("RGB")
            self.rotation = 0
            iw, ih = self.original_image.size
            self.v_img_info.set(
                f"📄 {Path(path).name}\n    {iw}×{ih} px")
            self._log(self.s.log_image_opened.format(path=path))

            # Aggiorna altezza mantenendo aspect ratio
            self._ar_updating = True
            try:
                if iw:
                    self.v_height.set(
                        round(self.v_width.get() * ih / iw, 2))
            finally:
                self._ar_updating = False

            self._show_on_canvas(self.canvas_orig, self.original_image)
            self._update_proc()
        except Exception as e:
            messagebox.showerror(
                self.s.error,
                self.s.err_image_open.format(err=e))

    def _rotate(self, deg: int):
        """Ruota l'immagine aggiornando l'aspect ratio."""
        if self.original_image is None:
            return
        self.rotation = (self.rotation + deg) % 360
        self.original_image = self.original_image.rotate(
            -deg, expand=True)
        self.v_rotation.set(
            self.s.lbl_rotation.replace("0°", f"{self.rotation}°"))
        self._log(self.s.log_rotated.format(
            deg=deg, total=self.rotation))

        # Ricalcola aspect ratio dopo rotazione 90/270
        if abs(deg) in (90, 270):
            self._ar_updating = True
            try:
                iw, ih = self.original_image.size
                if iw:
                    self.v_height.set(
                        round(self.v_width.get() * ih / iw, 2))
            finally:
                self._ar_updating = False

        self._show_on_canvas(self.canvas_orig, self.original_image)
        self._update_proc()

    def _flip(self, direction: str):
        """Specchia l'immagine."""
        if self.original_image is None:
            return
        if direction == "h":
            self.original_image = ImageOps.mirror(self.original_image)
            self._log(self.s.log_flipped_h)
        else:
            self.original_image = ImageOps.flip(self.original_image)
            self._log(self.s.log_flipped_v)
        self._show_on_canvas(self.canvas_orig, self.original_image)
        self._update_proc()

    def _update_proc(self):
        """Aggiorna la preview elaborata (B/N)."""
        if self.original_image is None:
            return
        try:
            self.binary_np = self.vec.preprocess(
                self.original_image,
                threshold=int(self.v_threshold.get()),
                blur_radius=int(self.v_blur.get()),
                invert=self.v_invert.get(),
                denoise=self.v_denoise.get())
            pil = Image.fromarray(self.binary_np)
            self._show_on_canvas(self.canvas_proc, pil)
            # Se esiste già un GCode, ridisegna la sua preview
            if self.gcode_program and self.gcode_program.moves:
                self.after(300, self._show_gcode_on_proc_canvas)
        except Exception as e:
            self._log(self.s.log_preprocess_error.format(err=e))

    def _show_on_canvas(self, canvas: tk.Canvas, img: Image.Image):
        """Mostra un'immagine PIL su un canvas tkinter."""
        canvas.update_idletasks()
        cw = max(canvas.winfo_width(),  160)
        ch = max(canvas.winfo_height(), 140)
        thumb = img.copy()
        thumb.thumbnail((cw - 4, ch - 4), Image.LANCZOS)
        photo = ImageTk.PhotoImage(thumb)
        if canvas is self.canvas_orig:
            self._photo_orig = photo
        else:
            self._photo_proc = photo
        canvas.delete("all")
        canvas.create_image(cw // 2, ch // 2,
                            anchor="center", image=photo)

    # ══════════════════════════════════════════════════════════════════════
    #  PREVIEW GCODE NEL CANVAS PROC
    # ══════════════════════════════════════════════════════════════════════
    def _show_gcode_on_proc_canvas(self):
        """
        Renderizza il GCode generato nel canvas_proc (preview elaborata).
        Disegna i percorsi laser in miniatura con colori del tema.
        """
        if not self.gcode_program or not self.gcode_program.moves:
            return

        self.canvas_proc.update_idletasks()
        cw = max(self.canvas_proc.winfo_width(),  160)
        ch = max(self.canvas_proc.winfo_height(), 140)

        moves = self.gcode_program.moves
        t     = self.t

        # Calcola bounds del percorso
        xs    = [m.x for m in moves]
        ys    = [m.y for m in moves]
        mn_x  = min(xs);  mx_x = max(xs)
        mn_y  = min(ys);  mx_y = max(ys)
        w_mm  = mx_x - mn_x or 1.0
        h_mm  = mx_y - mn_y or 1.0

        # Scala per fit nel canvas
        margin = 12
        scale  = min((cw - 2 * margin) / w_mm,
                     (ch - 2 * margin - 16) / h_mm)

        def to_px(mm_x, mm_y):
            """Converte coordinate mm in pixel canvas."""
            px = margin + (mm_x - mn_x) * scale
            py = margin + (mx_y - mm_y) * scale   # Y invertita
            return px, py

        # Pulisci e ridisegna
        self.canvas_proc.delete("all")
        self.canvas_proc.configure(bg=t.canvas_bg)
        # Azzera riferimento immagine precedente
        self._photo_proc = None

        # Sfondo area di incisione
        bx0, by0 = to_px(mn_x, mn_y)
        bx1, by1 = to_px(mx_x, mx_y)
        self.canvas_proc.create_rectangle(
            bx0, by1, bx1, by0,
            fill=t.base, outline=t.surface1, width=1)

        # Disegna percorsi
        prev_x = prev_y = 0.0
        for mv in moves:
            px0, py0 = to_px(prev_x, prev_y)
            px1, py1 = to_px(mv.x, mv.y)

            # Salta segmenti troppo corti (ottimizzazione rendering)
            if abs(px1 - px0) < 0.5 and abs(py1 - py0) < 0.5:
                prev_x, prev_y = mv.x, mv.y
                continue

            if mv.is_rapid:
                col, dash, lw = t.rapid, (2, 3), 1
            elif mv.laser_on:
                col, dash, lw = t.laser_on, (), 1
            else:
                col, dash, lw = t.laser_off, (1, 2), 1

            self.canvas_proc.create_line(
                px0, py0, px1, py1,
                fill=col, width=lw, dash=dash)

            prev_x, prev_y = mv.x, mv.y

        # Marcatore origine
        ox, oy = to_px(0, 0)
        r = 4
        if 0 <= ox <= cw and 0 <= oy <= ch:
            self.canvas_proc.create_oval(
                ox - r, oy - r, ox + r, oy + r,
                outline=t.home, fill="", width=2)
            self.canvas_proc.create_line(
                ox - r, oy, ox + r, oy, fill=t.home, width=1)
            self.canvas_proc.create_line(
                ox, oy - r, ox, oy + r, fill=t.home, width=1)

        # Info dimensioni in basso
        on_moves  = sum(1 for m in moves if m.laser_on)
        src_label = (f"VECTOR:{self.v_method.get()}"
                     if self.gcode_program.source == GCodeSource.VECTOR
                     else f"IMAGE:{self.v_image_mode.get()}")
        self.canvas_proc.create_text(
            cw // 2, ch - 2,
            text=(f"{src_label}  "
                  f"{w_mm:.1f}×{h_mm:.1f}mm  "
                  f"ON:{on_moves}"),
            fill=t.subtext,
            font=("Consolas", 6),
            anchor="s")

    # ══════════════════════════════════════════════════════════════════════
    #  ANTEPRIMA RISOLUZIONE IMMAGINE
    # ══════════════════════════════════════════════════════════════════════
    def _preview_image_resolution(self):
        """Mostra l'immagine ridimensionata per la generazione GCode."""
        if self.original_image is None:
            messagebox.showwarning(self.s.warning, self.s.err_no_image)
            return

        w_mm      = self.v_width.get()
        h_mm      = self.v_height.get()
        max_lines = int(self.v_max_lines.get())
        direction = (RasterDirection.HORIZONTAL
                     if self.v_img_direction.get() == "horizontal"
                     else RasterDirection.VERTICAL)

        gray_img  = self.original_image.convert("L")
        img_array = np.array(gray_img)

        preview, resolution_mm, actual_lines, est_moves = \
            ImageGCodeGenerator.preview_image(
                img_array, w_mm, h_mm, max_lines, direction)

        t   = self.t
        win = tk.Toplevel(self)
        win.title("👁 Anteprima immagine ridimensionata")
        win.geometry("620x700")
        win.configure(bg=t.base)
        win.resizable(True, True)

        # Info
        info_frame = tk.Frame(win, bg=t.surface0)
        info_frame.pack(fill="x", padx=10, pady=10)

        orig_w, orig_h = img_array.shape[1], img_array.shape[0]
        px_per_line    = (preview.shape[1]
                          if direction == RasterDirection.HORIZONTAL
                          else preview.shape[0])

        for line in [
            f"  Immagine originale : {orig_w} × {orig_h} px",
            f"  Dimensioni output  : {w_mm:.1f} × {h_mm:.1f} mm",
            f"  Risoluzione        : {resolution_mm:.3f} mm/linea",
            f"  Righe di scansione : {actual_lines}",
            f"  Pixel per riga     : {px_per_line}",
            f"  Movimenti stimati  : ~{est_moves:,}",
            f"",
            f"  ⚡ Riduci 'Max righe' per velocità maggiore.",
        ]:
            tk.Label(info_frame, text=line,
                     bg=t.surface0, fg=t.text,
                     font=("Consolas", 9),
                     anchor="w").pack(fill="x", padx=8, pady=1)

        # Canvas preview
        canvas_outer = tk.Frame(win, bg=t.mantle,
                                relief="solid", borderwidth=1)
        canvas_outer.pack(fill="both", expand=True,
                          padx=10, pady=(0, 6))

        canvas = tk.Canvas(canvas_outer, bg=t.mantle,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=4, pady=4)

        win._preview_data = {
            "preview_array": preview,
            "pil_img"      : Image.fromarray(preview),
            "photo"        : None,
        }

        def draw_preview(event=None):
            canvas.update_idletasks()
            cw = max(canvas.winfo_width(),  200)
            ch = max(canvas.winfo_height(), 200)
            pil = win._preview_data["pil_img"].copy()
            pil.thumbnail((cw - 8, ch - 8), Image.NEAREST)
            photo = ImageTk.PhotoImage(pil)
            win._preview_data["photo"] = photo
            canvas.delete("all")
            canvas.create_image(cw // 2, ch // 2,
                                image=photo, anchor="center")
            # Griglia pixel se poche righe
            if max_lines <= 80:
                img_w, img_h = pil.size
                arr          = win._preview_data["preview_array"]
                ppx = img_w / arr.shape[1]
                ppy = img_h / arr.shape[0]
                ox  = (cw - img_w) // 2
                oy  = (ch - img_h) // 2
                for i in range(arr.shape[1] + 1):
                    x = ox + int(i * ppx)
                    canvas.create_line(x, oy, x, oy + img_h,
                                       fill=t.surface1, width=1)
                for i in range(arr.shape[0] + 1):
                    y = oy + int(i * ppy)
                    canvas.create_line(ox, y, ox + img_w, y,
                                       fill=t.surface1, width=1)

        canvas.bind("<Configure>", draw_preview)
        win.after(100, draw_preview)

        # Pulsanti
        btn_frame = tk.Frame(win, bg=t.base)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btn_frame,
                   text="✅ Usa questa risoluzione e genera GCode",
                   style="Green.TButton",
                   command=lambda: (
                       win.destroy(), self._generate_gcode())
                   ).pack(side="left", expand=True,
                          fill="x", padx=(0, 4))
        ttk.Button(btn_frame, text="✖ Chiudi",
                   command=win.destroy).pack(side="left")

    # ══════════════════════════════════════════════════════════════════════
    #  GENERAZIONE GCODE
    # ══════════════════════════════════════════════════════════════════════
    def _generate_gcode(self):
        """Dispatcher: genera GCode dalla sorgente selezionata."""
        if self.v_gcode_source.get() == "vector":
            self._generate_gcode_vector()
        else:
            self._generate_gcode_image()

    def _generate_gcode_vector(self):
        """Genera GCode da vettorizzazione immagine."""
        if self.binary_np is None:
            messagebox.showwarning(self.s.warning, self.s.err_no_image)
            return

        s      = self.s
        method = self.v_method.get()
        w_mm   = self.v_width.get()
        h_mm   = self.v_height.get()
        feed   = int(self.v_feed_rate.get())
        power  = int(self.v_power.get())
        passes = int(self.v_passes.get())
        gap    = self.v_gap.get() * 0.1
        angle  = self.v_hatch_ang.get()
        simp   = self.v_simplify.get()
        ox     = self.v_model_x.get()
        oy     = self.v_model_y.get()

        self._log(s.log_generating.format(
            method=method, w=w_mm, h=h_mm))
        self.v_status.set(s.status_generating)

        def _run():
            try:
                if method == s.method_contours:
                    paths = self.vec.contour_paths(
                        self.binary_np, w_mm, h_mm, simp)
                elif method == s.method_centerline:
                    paths = self.vec.centerline_paths(
                        self.binary_np, w_mm, h_mm)
                elif method == s.method_raster:
                    paths = self.vec.raster_paths(
                        self.binary_np, w_mm, h_mm, gap)
                else:
                    paths = self.vec.hatch_paths(
                        self.binary_np, w_mm, h_mm, angle, gap)

                prog = GCodeFactory.generate(
                    source=GCodeSource.VECTOR,
                    data=paths,
                    width_mm=w_mm, height_mm=h_mm,
                    feed=feed, power=power, passes=passes,
                    offset_x=ox, offset_y=oy)

                self.gcode_program = prog
                self._finalize_gcode_generation()

            except Exception as e:
                self._log(s.log_gen_error.format(err=e))
                self.after(0, self.v_status.set, s.status_gen_error)

        threading.Thread(target=_run, daemon=True).start()

    def _generate_gcode_image(self):
        """Genera GCode direttamente dall'immagine (PWM/grayscale)."""
        if self.original_image is None:
            messagebox.showwarning(self.s.warning, self.s.err_no_image)
            return

        s         = self.s
        w_mm      = self.v_width.get()
        h_mm      = self.v_height.get()
        feed      = int(self.v_feed_rate.get())
        power     = int(self.v_power.get())
        passes    = int(self.v_passes.get())
        max_lines = int(self.v_max_lines.get())
        ox        = self.v_model_x.get()
        oy        = self.v_model_y.get()

        mode_map = {
            "grayscale": ImageGCodeGenerator.Mode.GRAYSCALE,
            "dithering": ImageGCodeGenerator.Mode.DITHERING,
            "threshold": ImageGCodeGenerator.Mode.THRESHOLD,
        }
        mode = mode_map.get(self.v_image_mode.get(),
                            ImageGCodeGenerator.Mode.GRAYSCALE)
        direction = (RasterDirection.HORIZONTAL
                     if self.v_img_direction.get() == "horizontal"
                     else RasterDirection.VERTICAL)

        self._log(
            f"🖼 Genera GCode da immagine: "
            f"{mode.name} | {w_mm}×{h_mm} mm | "
            f"max {max_lines} righe")
        self.v_status.set(s.status_generating)

        def _run():
            try:
                img_array = np.array(
                    self.original_image.convert("L"))

                prog = GCodeFactory.generate(
                    source=GCodeSource.IMAGE,
                    data=img_array,
                    width_mm=w_mm, height_mm=h_mm,
                    feed=feed, power=power, passes=passes,
                    offset_x=ox, offset_y=oy,
                    max_lines=max_lines,
                    mode=mode,
                    direction=direction,
                    raster_mode=RasterMode.BIDIRECTIONAL,
                    invert=self.v_invert.get(),
                    threshold=int(self.v_threshold.get()))

                self.gcode_program = prog
                self._finalize_gcode_generation()

            except Exception as e:
                self._log(s.log_gen_error.format(err=e))
                self.after(0, self.v_status.set, s.status_gen_error)

        threading.Thread(target=_run, daemon=True).start()

    def _finalize_gcode_generation(self):
        """Aggiorna UI dopo la generazione GCode (chiamato dal thread)."""
        s    = self.s
        prog = self.gcode_program
        n    = len(prog.raw_lines)
        mvs  = len(prog.moves)
        on_m = sum(1 for m in prog.moves if m.laser_on)

        info = (
            s.gcode_lines.format(n=n, moves=mvs) + "\n" +
            s.gcode_laser_on.format(on=on_m) +
            s.gcode_laser_off.format(off=mvs - on_m) + "\n" +
            f"Sorgente: {prog.source.name}\n"
        )
        if prog.source == GCodeSource.VECTOR:
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            info += (s.gcode_area.format(
                w=mx_x - mn_x, h=mx_y - mn_y) + "\n")
        info += (
            s.gcode_feed.format(feed=int(self.v_feed_rate.get())) +
            s.gcode_power.format(power=int(self.v_power.get())) +
            s.gcode_passes.format(passes=int(self.v_passes.get()))
        )
        if prog.estimated_time_seconds > 0:
            m_ = int(prog.estimated_time_seconds // 60)
            s_ = int(prog.estimated_time_seconds % 60)
            info += f"\n⏱ Tempo stimato: {m_}m {s_}s"

        # Aggiorna tutti i widget nel thread principale
        self.after(0, self.v_gcode_info.set, info)
        self.after(0, self._update_model_info)
        self.after(0, self._update_work_canvas)
        self.after(0, self._show_gcode_on_proc_canvas)
        self.after(0, self.v_status.set, s.status_gcode_ready)
        self._log(s.log_gcode_generated.format(lines=n))

    def _update_work_canvas(self):
        """
        Aggiorna il WorkAreaCanvas con il GCode generato.
        """
        if not self.gcode_program:
            return
        self.work_canvas.set_program(self.gcode_program.moves)
        self.work_canvas.set_model_position(
            self.v_model_x.get(), self.v_model_y.get())
        self.work_canvas.fit()

    def _update_model_info(self):
        """Aggiorna il pannello info modello."""
        if not self.gcode_program:
            return
        s = self.s
        mn_x, mn_y, mx_x, mx_y = self.gcode_program.bounds()
        ox, oy = self.v_model_x.get(), self.v_model_y.get()
        self.v_model_info.set(
            s.info_model_size.format(
                w=mx_x - mn_x, h=mx_y - mn_y) + "\n" +
            s.info_model_origin.format(x=ox, y=oy) + "\n" +
            s.info_model_extent_x.format(
                x0=ox + mn_x, x1=ox + mx_x) + "\n" +
            s.info_model_extent_y.format(
                y0=oy + mn_y, y1=oy + mx_y))

    # ══════════════════════════════════════════════════════════════════════
    #  POSIZIONE MODELLO
    # ══════════════════════════════════════════════════════════════════════
    def _on_model_moved(self, x_mm: float, y_mm: float):
        """Callback: il modello è stato spostato nel canvas."""
        self.v_model_x.set(round(x_mm, 2))
        self.v_model_y.set(round(y_mm, 2))
        self._update_model_info()
        self.after(50, self._show_gcode_on_proc_canvas)

    def _apply_work_area(self):
        """Applica le dimensioni dell'area di lavoro."""
        w, h = self.v_work_w.get(), self.v_work_h.get()
        self.work_canvas.set_work_area(w, h)
        self.config_data["work_area_w"] = w
        self.config_data["work_area_h"] = h
        save_config(self.config_data)
        self._log(self.s.log_work_area_set.format(w=w, h=h))

    def _apply_model_pos(self):
        """Applica la posizione del modello."""
        x, y = self.v_model_x.get(), self.v_model_y.get()
        self.work_canvas.set_model_position(x, y)
        self._update_model_info()
        self._show_gcode_on_proc_canvas()
        self._log(self.s.log_model_position.format(x=x, y=y))

    def _quick_pos(self, where: str):
        """Posizionamento rapido del modello."""
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        mn_x, mn_y, mx_x, mx_y = self.gcode_program.bounds()
        w  = mx_x - mn_x
        h  = mx_y - mn_y
        ww = self.work_canvas.work_w_mm
        wh = self.work_canvas.work_h_mm
        mg = 5.0
        positions = {
            "center": ((ww - w) / 2 - mn_x, (wh - h) / 2 - mn_y),
            "tl"    : (mg - mn_x, wh - h - mg - mn_y),
            "tr"    : (ww - w - mg - mn_x, wh - h - mg - mn_y),
            "bl"    : (mg - mn_x, mg - mn_y),
            "br"    : (ww - w - mg - mn_x, mg - mn_y),
        }
        x, y = positions[where]
        self.v_model_x.set(round(x, 2))
        self.v_model_y.set(round(y, 2))
        self.work_canvas.set_model_position(x, y)
        self._update_model_info()
        self._log(self.s.log_quick_pos.format(
            where=where, x=x, y=y))

    # ══════════════════════════════════════════════════════════════════════
    #  SIMULAZIONE
    # ══════════════════════════════════════════════════════════════════════
    def _start_sim(self):
        """Avvia simulazione animata."""
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        speed = int(self.v_sim_speed.get())
        self._log(self.s.log_sim_started.format(speed=speed))
        self.v_status.set(self.s.status_simulation)
        self.work_canvas.start_simulation(
            speed_mult=speed,
            done_cb=lambda: (
                self._log(self.s.log_sim_completed),
                self.after(0, self.v_status.set,
                           self.s.status_sim_completed)))

    def _stop_sim(self):
        """Ferma la simulazione."""
        self.work_canvas.stop_simulation()
        self._log(self.s.log_sim_stopped)
        self.v_status.set(self.s.status_ready)

    # ══════════════════════════════════════════════════════════════════════
    #  PREVIEW / GCODE I/O
    # ══════════════════════════════════════════════════════════════════════
    def _open_vector_preview(self):
        """Apre finestra anteprima vettoriale a schermo intero."""
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        VectorPreviewWindow(
            self, self.gcode_program.moves,
            self.work_canvas.work_w_mm,
            self.work_canvas.work_h_mm,
            self.t, self.s, self._log)

    def _save_gcode(self):
        """Salva GCode su file."""
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        path = filedialog.asksaveasfilename(
            title=self.s.menu_save_gcode,
            defaultextension=".gcode",
            filetypes=[("GCode", "*.gcode *.nc *.cnc"),
                       ("All", "*.*")])
        if path:
            Path(path).write_text(
                "\n".join(self.gcode_program.translated_lines()),
                encoding="utf-8")
            self._log(self.s.log_saved.format(path=path))

    def _load_gcode(self):
        """Carica GCode da file."""
        path = filedialog.askopenfilename(
            title=self.s.menu_load_gcode,
            filetypes=[("GCode", "*.gcode *.nc *.cnc"),
                       ("All", "*.*")])
        if not path:
            return
        prog = GCodeParser.parse_file(path)
        self.gcode_program = prog
        self._update_work_canvas()
        self._update_model_info()
        self._show_gcode_on_proc_canvas()
        self._log(self.s.log_loaded.format(
            path=path,
            lines=len(prog.raw_lines),
            moves=len(prog.moves)))

    def _show_gcode_text(self):
        """Mostra GCode in una finestra di testo."""
        if not self.gcode_program:
            messagebox.showinfo(self.s.info, self.s.err_no_gcode)
            return
        t = self.t
        w = tk.Toplevel(self)
        w.title(self.s.gcode_view_title)
        w.geometry("720x580")
        w.configure(bg=t.base)
        txt = scrolledtext.ScrolledText(
            w, bg=t.surface0, fg=t.text,
            font=("Consolas", 9), borderwidth=0)
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert("end",
                   "\n".join(self.gcode_program.translated_lines()))
        txt.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════
    #  CONNESSIONE LASER
    # ══════════════════════════════════════════════════════════════════════
    def _connect(self):
        """Connette al controller laser."""
        sim = self.v_simulate.get()
        self.ctrl.set_simulation(sim)
        if sim:
            self._update_conn(True)
            return

        port = self.v_port.get()
        baud = int(self.v_baud.get())
        if not port or "(none)" in port.lower():
            messagebox.showwarning(self.s.warning, self.s.err_no_port)
            return

        self.config_data["last_port"] = port
        self.config_data["last_baud"] = baud
        save_config(self.config_data)

        def _do():
            ok = self.ctrl.connect(port, baud, self.s)
            self.after(0, self._update_conn, ok)
            if ok:
                info = self.ctrl.controller_info
                if info.type != ControllerType.UNKNOWN:
                    ctrl_str = f"🔧 {info.type.name}"
                    if info.version:
                        ctrl_str += f" v{info.version}"
                    self.after(0, self.v_controller_info.set, ctrl_str)

        threading.Thread(target=_do, daemon=True).start()

    def _disconnect(self):
        """Disconnette dal controller."""
        self.ctrl.disconnect(self.s)
        self.ctrl.set_simulation(False)
        self._update_conn(False)
        self.v_controller_info.set("")

    def _update_conn(self, ok: bool):
        """Aggiorna lo stato UI della connessione."""
        s = self.s
        if ok:
            lbl = (f"🟡  {s.simulation_mode}"
                   if self.ctrl.is_simulating
                   else f"🟢  {s.btn_connect} → {self.v_port.get()}")
            self.v_conn_lbl.set(lbl)
            self.btn_conn.state(["disabled"])
            self.btn_disc.state(["!disabled"])
        else:
            self.v_conn_lbl.set(s.lbl_not_connected)
            self.btn_conn.state(["!disabled"])
            self.btn_disc.state(["disabled"])

    def _toggle_sim_mode(self):
        """Abilita/disabilita campo porta in base alla simulazione."""
        if self.v_simulate.get():
            self.combo_port.state(["disabled"])
        else:
            self.combo_port.state(["!disabled"])

    # ══════════════════════════════════════════════════════════════════════
    #  JOG / HOME
    # ══════════════════════════════════════════════════════════════════════
    def _check_conn(self) -> bool:
        """Verifica che il controller sia connesso."""
        if not self.ctrl.is_connected():
            messagebox.showwarning(
                self.s.warning, self.s.err_not_connected)
            return False
        return True

    def _jog(self, axis: str, direction: int):
        """Esegue un movimento JOG."""
        if not self._check_conn():
            return
        dist = self.v_jog_dist.get() * direction
        feed = self.v_jog_feed.get()
        self.ctrl.jog(axis, dist, feed)
        self._log(self.s.log_jog.format(axis=axis, dist=dist))

    def _jog_zero(self):
        """Muove il laser a X0 Y0."""
        if not self._check_conn():
            return
        self.ctrl.go_to(0, 0)
        self._log(self.s.log_goto_home)

    def _set_home(self):
        """Imposta la posizione corrente come home."""
        if not self._check_conn():
            return
        self.ctrl.set_home(self.s)

    def _goto_home(self):
        """Muove il laser a home (0,0)."""
        if not self._check_conn():
            return
        self.ctrl.go_to(0, 0)
        self._log(self.s.log_goto_home)

    def _cmd_send(self):
        """Invia un comando manuale GCode."""
        if not self._check_conn():
            return
        cmd = self.v_cmd.get().strip()
        if cmd:
            resp = self.ctrl.send_command(cmd, self.s)
            self._log(f"→ {cmd}   ← {resp}")
            self.v_cmd.set("")

    # ══════════════════════════════════════════════════════════════════════
    #  BBOX FISICO
    # ══════════════════════════════════════════════════════════════════════
    def _send_bbox(self):
        """Invia il contorno bbox fisico al laser (laser OFF)."""
        if not self._check_conn():
            return
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        feed = int(self.v_bbox_feed.get())
        self._log(self.s.log_bbox_sending.format(feed=feed))
        self.work_canvas.send_bbox_to_laser(
            self.ctrl, feed=feed, strings=self.s,
            done_cb=lambda: self._log(self.s.log_bbox_done))

    # ══════════════════════════════════════════════════════════════════════
    #  INCISIONE
    # ══════════════════════════════════════════════════════════════════════
    def _start_engraving(self):
        """Avvia l'incisione."""
        if not self._check_conn():
            return
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return

        s = self.s
        mn_x, mn_y, mx_x, mx_y = self.gcode_program.bounds()
        ox, oy = self.v_model_x.get(), self.v_model_y.get()
        note   = (s.dlg_start_sim_note if self.ctrl.is_simulating
                  else s.dlg_start_safe_note)

        ok = messagebox.askyesno(
            s.dlg_start_title,
            s.dlg_start_body.format(
                w=mx_x - mn_x, h=mx_y - mn_y,
                ox=ox, oy=oy,
                lines=len(self.gcode_program.raw_lines)) + note)
        if not ok:
            return

        self._stop_event.clear()
        self.v_progress.set(0)
        self.v_progress_lbl.set(s.lbl_waiting)
        self.v_status.set(s.status_engraving)

        lines = self.gcode_program.translated_lines()

        def _prog(cur, tot):
            pct = cur / tot * 100
            self.after(0, self.v_progress.set, pct)
            self.after(0, self.v_progress_lbl.set,
                       f"{cur}/{tot}  ({pct:.1f}%)")

        def _run():
            ok2 = self.ctrl.send_gcode(
                lines, progress_cb=_prog,
                stop_event=self._stop_event, strings=self.s)
            self.after(0, self._engrave_done, ok2)

        threading.Thread(target=_run, daemon=True).start()

    def _engrave_done(self, ok: bool):
        """Callback al termine dell'incisione."""
        s = self.s
        if ok:
            self.v_status.set(s.status_completed)
            self.v_progress_lbl.set(f"✅  {s.completed}!")
            messagebox.showinfo(
                s.dlg_completed_title, s.dlg_completed_body)
        else:
            self.v_status.set(s.status_stopped)
            self.v_progress_lbl.set(f"⚠  {s.stopped}")

    def _stop_engraving(self):
        """Ferma l'incisione in corso."""
        self._stop_event.set()
        self._log(self.s.log_stop_requested)
        self.v_status.set(self.s.status_stopped)

    def _emergency_stop(self):
        """Emergency stop immediato."""
        self._stop_event.set()
        self.ctrl.emergency_stop(self.s)
        self.v_status.set(self.s.status_emergency)
        messagebox.showwarning(
            self.s.dlg_emergency_title,
            self.s.dlg_emergency_body)

    # ══════════════════════════════════════════════════════════════════════
    #  CHIUSURA
    # ══════════════════════════════════════════════════════════════════════
    def _quit(self):
        """Salva configurazione e chiude l'applicazione."""
        self.config_data.update({
            "feed_rate"     : int(self.v_feed_rate.get()),
            "power"         : int(self.v_power.get()),
            "passes"        : int(self.v_passes.get()),
            "last_source"   : self.v_gcode_source.get(),
            "max_lines"     : int(self.v_max_lines.get()),
            "img_mode"      : self.v_image_mode.get(),
            "img_direction" : self.v_img_direction.get(),
            "method"        : self.v_method.get(),
            "width_mm"      : self.v_width.get(),
            "height_mm"     : self.v_height.get(),
        })
        save_config(self.config_data)

        self._stop_event.set()
        self.work_canvas.stop_simulation()
        
        # Unbind eventi mousewheel per evitare errori alla chiusura
        if hasattr(self, 'scroll_frame'):
            self.scroll_frame.unbind_mousewheel()
        
        if self.ctrl.is_connected():
            self.ctrl.disconnect(self.s)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    """Entry point principale."""
    missing = []
    if not PIL_AVAILABLE:
        missing.append("Pillow  → pip install Pillow")
    if not NUMPY_AVAILABLE:
        missing.append("NumPy   → pip install numpy")
    if not CV2_AVAILABLE:
        missing.append("OpenCV  → pip install opencv-python")

    if missing:
        s = get_strings()
        print(f"❌ {s.err_missing_libs.format(libs=chr(10).join(missing))}")
        sys.exit(1)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()