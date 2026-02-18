#!/usr/bin/env python3
"""
themes.py
Sistema di temi per Laser Engraver Pro v3.0
Temi disponibili: Dark, Light, Pastel, Nord, Solarized
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Definizione di un tema colori."""
    
    name: str
    
    # Sfondi principali
    base: str           # Sfondo principale finestre
    mantle: str         # Sfondo header/footer
    surface0: str       # Sfondo elementi (entry, combo)
    surface1: str       # Hover/bordi
    surface2: str       # Selezione
    
    # Testo
    text: str           # Testo principale
    subtext: str        # Testo secondario
    
    # Colori accento
    blue: str           # Accento primario
    green: str          # Successo / conferma
    red: str            # Errore / pericolo
    yellow: str         # Avviso / attenzione
    teal: str           # Info / secondario
    mauve: str          # Hover accento
    peach: str          # Alternativo
    pink: str           # Decorativo
    
    # Canvas specifici
    canvas_bg: str      # Sfondo canvas
    canvas_grid: str    # Griglia
    laser_on: str       # Traccia laser acceso
    laser_off: str      # Traccia laser spento
    rapid: str          # Movimento rapido
    bbox: str           # Bounding box
    home: str           # Marcatore home
    
    # Log
    log_bg: str         # Sfondo log
    log_text: str       # Testo log


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA SCURO (Dark - Catppuccin Mocha)
# ══════════════════════════════════════════════════════════════════════════════
DARK = Theme(
    name        = "Dark",
    
    base        = "#1e1e2e",
    mantle      = "#181825",
    surface0    = "#313244",
    surface1    = "#45475a",
    surface2    = "#585b70",
    
    text        = "#cdd6f4",
    subtext     = "#a6adc8",
    
    blue        = "#89b4fa",
    green       = "#a6e3a1",
    red         = "#f38ba8",
    yellow      = "#f9e2af",
    teal        = "#94e2d5",
    mauve       = "#cba6f7",
    peach       = "#fab387",
    pink        = "#f5c2e7",
    
    canvas_bg   = "#11111b",
    canvas_grid = "#313244",
    laser_on    = "#f38ba8",
    laser_off   = "#45475a",
    rapid       = "#6c7086",
    bbox        = "#f9e2af",
    home        = "#a6e3a1",
    
    log_bg      = "#11111b",
    log_text    = "#a6e3a1",
)


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA CHIARO (Light - Catppuccin Latte)
# ══════════════════════════════════════════════════════════════════════════════
LIGHT = Theme(
    name        = "Light",
    
    base        = "#eff1f5",
    mantle      = "#e6e9ef",
    surface0    = "#ccd0da",
    surface1    = "#bcc0cc",
    surface2    = "#acb0be",
    
    text        = "#4c4f69",
    subtext     = "#6c6f85",
    
    blue        = "#1e66f5",
    green       = "#40a02b",
    red         = "#d20f39",
    yellow      = "#df8e1d",
    teal        = "#179299",
    mauve       = "#8839ef",
    peach       = "#fe640b",
    pink        = "#ea76cb",
    
    canvas_bg   = "#dce0e8",
    canvas_grid = "#bcc0cc",
    laser_on    = "#d20f39",
    laser_off   = "#9ca0b0",
    rapid       = "#8c8fa1",
    bbox        = "#df8e1d",
    home        = "#40a02b",
    
    log_bg      = "#e6e9ef",
    log_text    = "#40a02b",
)


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA PASTELLO (Pastel - Rosé Pine Dawn)
# ══════════════════════════════════════════════════════════════════════════════
PASTEL = Theme(
    name        = "Pastel",
    
    base        = "#faf4ed",
    mantle      = "#f2e9e1",
    surface0    = "#f4ede8",
    surface1    = "#dfdad9",
    surface2    = "#cecacd",
    
    text        = "#575279",
    subtext     = "#797593",
    
    blue        = "#56949f",
    green       = "#86a47a",
    red         = "#b4637a",
    yellow      = "#ea9d34",
    teal        = "#56949f",
    mauve       = "#907aa9",
    peach       = "#d7827e",
    pink        = "#d7827e",
    
    canvas_bg   = "#fffaf3",
    canvas_grid = "#dfdad9",
    laser_on    = "#b4637a",
    laser_off   = "#9893a5",
    rapid       = "#9893a5",
    bbox        = "#ea9d34",
    home        = "#86a47a",
    
    log_bg      = "#f2e9e1",
    log_text    = "#286983",
)


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA NORD (Nordic)
# ══════════════════════════════════════════════════════════════════════════════
NORD = Theme(
    name        = "Nord",
    
    base        = "#2e3440",
    mantle      = "#242933",
    surface0    = "#3b4252",
    surface1    = "#434c5e",
    surface2    = "#4c566a",
    
    text        = "#eceff4",
    subtext     = "#d8dee9",
    
    blue        = "#88c0d0",
    green       = "#a3be8c",
    red         = "#bf616a",
    yellow      = "#ebcb8b",
    teal        = "#8fbcbb",
    mauve       = "#b48ead",
    peach       = "#d08770",
    pink        = "#b48ead",
    
    canvas_bg   = "#242933",
    canvas_grid = "#3b4252",
    laser_on    = "#bf616a",
    laser_off   = "#4c566a",
    rapid       = "#4c566a",
    bbox        = "#ebcb8b",
    home        = "#a3be8c",
    
    log_bg      = "#242933",
    log_text    = "#a3be8c",
)


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA SOLARIZED DARK
# ══════════════════════════════════════════════════════════════════════════════
SOLARIZED_DARK = Theme(
    name        = "Solarized Dark",
    
    base        = "#002b36",
    mantle      = "#001e26",
    surface0    = "#073642",
    surface1    = "#094654",
    surface2    = "#0b5567",
    
    text        = "#839496",
    subtext     = "#657b83",
    
    blue        = "#268bd2",
    green       = "#859900",
    red         = "#dc322f",
    yellow      = "#b58900",
    teal        = "#2aa198",
    mauve       = "#6c71c4",
    peach       = "#cb4b16",
    pink        = "#d33682",
    
    canvas_bg   = "#001e26",
    canvas_grid = "#073642",
    laser_on    = "#dc322f",
    laser_off   = "#586e75",
    rapid       = "#586e75",
    bbox        = "#b58900",
    home        = "#859900",
    
    log_bg      = "#001e26",
    log_text    = "#859900",
)


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA SOLARIZED LIGHT
# ══════════════════════════════════════════════════════════════════════════════
SOLARIZED_LIGHT = Theme(
    name        = "Solarized Light",
    
    base        = "#fdf6e3",
    mantle      = "#eee8d5",
    surface0    = "#e4ddc8",
    surface1    = "#d5cdb6",
    surface2    = "#c5bea4",
    
    text        = "#657b83",
    subtext     = "#839496",
    
    blue        = "#268bd2",
    green       = "#859900",
    red         = "#dc322f",
    yellow      = "#b58900",
    teal        = "#2aa198",
    mauve       = "#6c71c4",
    peach       = "#cb4b16",
    pink        = "#d33682",
    
    canvas_bg   = "#eee8d5",
    canvas_grid = "#d5cdb6",
    laser_on    = "#dc322f",
    laser_off   = "#93a1a1",
    rapid       = "#93a1a1",
    bbox        = "#b58900",
    home        = "#859900",
    
    log_bg      = "#eee8d5",
    log_text    = "#859900",
)


# ══════════════════════════════════════════════════════════════════════════════
#  TEMA HIGH CONTRAST (Accessibilità)
# ══════════════════════════════════════════════════════════════════════════════
HIGH_CONTRAST = Theme(
    name        = "High Contrast",
    
    base        = "#000000",
    mantle      = "#0a0a0a",
    surface0    = "#1a1a1a",
    surface1    = "#333333",
    surface2    = "#4d4d4d",
    
    text        = "#ffffff",
    subtext     = "#e0e0e0",
    
    blue        = "#00bfff",
    green       = "#00ff00",
    red         = "#ff0000",
    yellow      = "#ffff00",
    teal        = "#00ffff",
    mauve       = "#ff00ff",
    peach       = "#ff8c00",
    pink        = "#ff69b4",
    
    canvas_bg   = "#000000",
    canvas_grid = "#333333",
    laser_on    = "#ff0000",
    laser_off   = "#666666",
    rapid       = "#666666",
    bbox        = "#ffff00",
    home        = "#00ff00",
    
    log_bg      = "#0a0a0a",
    log_text    = "#00ff00",
)


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTRO TEMI
# ══════════════════════════════════════════════════════════════════════════════
THEMES: Dict[str, Theme] = {
    "Dark"            : DARK,
    "Light"           : LIGHT,
    "Pastel"          : PASTEL,
    "Nord"            : NORD,
    "Solarized Dark"  : SOLARIZED_DARK,
    "Solarized Light" : SOLARIZED_LIGHT,
    "High Contrast"   : HIGH_CONTRAST,
}

DEFAULT_THEME = "Dark"


def get_theme(name: str = DEFAULT_THEME) -> Theme:
    """Restituisce il tema richiesto o quello di default."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def available_themes() -> list[str]:
    """Restituisce la lista dei nomi dei temi disponibili."""
    return list(THEMES.keys())


def is_dark_theme(theme: Theme) -> bool:
    """Determina se un tema è scuro basandosi sulla luminosità del colore base."""
    # Converte hex in RGB e calcola luminosità
    hex_color = theme.base.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5