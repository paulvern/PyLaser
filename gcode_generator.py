#!/usr/bin/env python3
"""
gcode_generator.py
Modulo di generazione GCode per PyLaser v0.9

Supporta:
- Generazione da percorsi vettoriali (contorni, centerline, hatching, raster vettoriale)
- Generazione diretta da immagine raster (PWM grayscale, dithering, threshold)
- Parsing di file GCode esistenti
- Controllo risoluzione e ottimizzazione velocità

Autore: PyLaser Team
Versione: 1.0
"""

import re
import math
import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Tuple

# ══════════════════════════════════════════════════════════════════════════════
#  COSTANTI
# ══════════════════════════════════════════════════════════════════════════════
APP_VERSION = "0.9"


# ══════════════════════════════════════════════════════════════════════════════
#  ENUMERAZIONI
# ══════════════════════════════════════════════════════════════════════════════
class GCodeSource(Enum):
    """Origine dei dati per la generazione GCode."""
    VECTOR = auto()      # Da percorsi vettoriali (contorni, centerline, etc.)
    IMAGE = auto()       # Direttamente dall'immagine raster (modulazione PWM)


class RasterDirection(Enum):
    """Direzione di scansione raster."""
    HORIZONTAL = auto()   # Scansione orizzontale (X)
    VERTICAL = auto()     # Scansione verticale (Y)
    DIAGONAL = auto()     # Scansione diagonale (futuro)


class RasterMode(Enum):
    """Modalità di scansione raster."""
    UNIDIRECTIONAL = auto()  # Sempre nella stessa direzione
    BIDIRECTIONAL = auto()   # Serpentina (più veloce)


# ══════════════════════════════════════════════════════════════════════════════
#  STRUTTURE DATI GCODE
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class GCodeMove:
    """Rappresenta un singolo movimento GCode."""
    x: float = 0.0
    y: float = 0.0
    laser_on: bool = False
    is_rapid: bool = False
    power: int = 0  # Potenza S (0-255), utile per grayscale


@dataclass
class GCodeProgram:
    """Programma GCode completo con metadati."""
    moves: List[GCodeMove] = field(default_factory=list)
    raw_lines: List[str] = field(default_factory=list)
    width_mm: float = 0.0
    height_mm: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    source: GCodeSource = GCodeSource.VECTOR
    
    # Metadati aggiuntivi
    estimated_time_seconds: float = 0.0
    total_distance_mm: float = 0.0
    laser_on_distance_mm: float = 0.0
    
    def bounds(self) -> Tuple[float, float, float, float]:
        """Restituisce i bounds (min_x, min_y, max_x, max_y)."""
        if not self.moves:
            return 0, 0, 0, 0
        xs = [m.x for m in self.moves]
        ys = [m.y for m in self.moves]
        return min(xs), min(ys), max(xs), max(ys)
    
    def translated_lines(self) -> List[str]:
        """Restituisce le righe GCode con offset applicato."""
        out = []
        for line in self.raw_lines:
            line = line.strip()
            if line.startswith(";") or not line:
                out.append(line)
                continue
            line = _replace_coord(line, "X", self.offset_x)
            line = _replace_coord(line, "Y", self.offset_y)
            out.append(line)
        return out
    
    def calculate_statistics(self, feed_rate: float = 1000.0):
        """
        Calcola statistiche del programma.
        
        Args:
            feed_rate: Velocità di avanzamento in mm/min
        """
        self.total_distance_mm = 0.0
        self.laser_on_distance_mm = 0.0
        
        prev_x, prev_y = 0.0, 0.0
        for move in self.moves:
            dist = math.sqrt((move.x - prev_x)**2 + (move.y - prev_y)**2)
            self.total_distance_mm += dist
            if move.laser_on:
                self.laser_on_distance_mm += dist
            prev_x, prev_y = move.x, move.y
        
        # Stima tempo (semplificata, non considera accelerazioni)
        if feed_rate > 0:
            self.estimated_time_seconds = (self.total_distance_mm / feed_rate) * 60


def _replace_coord(line: str, axis: str, offset: float) -> str:
    """
    Sostituisce una coordinata applicando l'offset.
    
    Args:
        line: Riga GCode
        axis: Asse ('X' o 'Y')
        offset: Offset da applicare
    
    Returns:
        Riga modificata
    """
    pattern = rf"({axis})([-+]?\d*\.?\d+)"
    def replacer(m):
        val = float(m.group(2)) + offset
        return f"{axis}{val:.3f}"
    return re.sub(pattern, replacer, line, flags=re.IGNORECASE)


# ══════════════════════════════════════════════════════════════════════════════
#  PARSER GCODE
# ══════════════════════════════════════════════════════════════════════════════
class GCodeParser:
    """Parser per file GCode esistenti."""
    
    @staticmethod
    def parse(lines: List[str]) -> List[GCodeMove]:
        """
        Parsa una lista di righe GCode e restituisce i movimenti.
        
        Args:
            lines: Lista di righe GCode
        
        Returns:
            Lista di GCodeMove
        """
        moves = []
        cur_x = cur_y = 0.0
        laser_on = False
        mode_g = 0
        current_power = 0
        
        for line in lines:
            line = line.strip().upper()
            if not line or line.startswith(";"):
                continue
            
            # Rimuovi commenti inline
            if ";" in line:
                line = line[:line.index(";")]
            
            # Controlla comandi laser
            if "M3" in line:
                laser_on = True
                # Estrai potenza S se presente
                s_match = re.search(r"S(\d+)", line)
                if s_match:
                    current_power = int(s_match.group(1))
            if "M5" in line:
                laser_on = False
                current_power = 0
            
            # Controlla modalità movimento
            if re.search(r"\bG0\b", line):
                mode_g = 0
            if re.search(r"\bG1\b", line):
                mode_g = 1
            
            # Estrai coordinate
            mx = re.search(r"X([-+]?\d*\.?\d+)", line)
            my = re.search(r"Y([-+]?\d*\.?\d+)", line)
            
            if mx or my:
                new_x = float(mx.group(1)) if mx else cur_x
                new_y = float(my.group(1)) if my else cur_y
                moves.append(GCodeMove(
                    x=new_x,
                    y=new_y,
                    laser_on=laser_on,
                    is_rapid=(mode_g == 0),
                    power=current_power
                ))
                cur_x, cur_y = new_x, new_y
        
        return moves
    
    @staticmethod
    def parse_file(filepath: str) -> GCodeProgram:
        """
        Parsa un file GCode completo.
        
        Args:
            filepath: Percorso del file
        
        Returns:
            GCodeProgram
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        prog = GCodeProgram()
        prog.raw_lines = [l.rstrip('\n') for l in lines]
        prog.moves = GCodeParser.parse(prog.raw_lines)
        
        if prog.moves:
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            prog.width_mm = mx_x - mn_x
            prog.height_mm = mx_y - mn_y
        
        return prog


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATORE GCODE DA VETTORI
# ══════════════════════════════════════════════════════════════════════════════
class VectorGCodeGenerator:
    """
    Generatore GCode da percorsi vettoriali.
    Usato con: contorni, centerline, raster vettoriale, hatching.
    """
    
    def __init__(self, feed: int = 1000, power: int = 200, passes: int = 1):
        """
        Inizializza il generatore vettoriale.
        
        Args:
            feed: Velocità di avanzamento (mm/min)
            power: Potenza laser (0-255)
            passes: Numero di passate
        """
        self.feed = feed
        self.power = power
        self.passes = passes
        self.rapid_feed = 3000  # Velocità movimenti rapidi
    
    def build(self, path_lines: List[str], 
              offset_x: float = 0.0, 
              offset_y: float = 0.0,
              header_comment: str = "") -> GCodeProgram:
        """
        Costruisce un programma GCode da linee di percorso vettoriale.
        
        Args:
            path_lines: Lista di comandi GCode base (G0, G1, M3, M5)
            offset_x: Offset X da applicare
            offset_y: Offset Y da applicare
            header_comment: Commento opzionale per l'header
        
        Returns:
            GCodeProgram completo
        """
        # Sostituisci placeholder potenza
        resolved = [l.replace("{lp}", str(self.power)) for l in path_lines]
        
        # Costruisci header
        raw = [
            f"; PyLaser v{APP_VERSION}",
            f"; Source: VECTOR",
            f"; Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Feed: {self.feed} mm/min",
            f"; Power: {self.power}",
            f"; Passes: {self.passes}",
            f"; Offset: X={offset_x:.3f} Y={offset_y:.3f}",
        ]
        
        if header_comment:
            raw.append(f"; {header_comment}")
        
        raw.extend([
            "",
            "; === INIZIALIZZAZIONE ===",
            "G21          ; Unità: millimetri",
            "G90          ; Coordinate assolute",
            "G92 X0 Y0    ; Imposta origine",
            f"F{self.feed}       ; Velocità di lavoro",
            "M5           ; Laser OFF (sicurezza)",
            "",
            "; === INIZIO PERCORSO ===",
        ])
        
        # Aggiungi percorsi per ogni passata
        for p in range(self.passes):
            if self.passes > 1:
                raw.append(f"")
                raw.append(f"; --- Passata {p + 1}/{self.passes} ---")
            raw.extend(resolved)
        
        # Footer
        raw.extend([
            "",
            "; === FINE ===",
            "M5           ; Laser OFF",
            "G0 X0 Y0     ; Torna a home",
            "M2           ; Fine programma",
        ])
        
        # Crea programma
        prog = GCodeProgram()
        prog.raw_lines = raw
        prog.moves = GCodeParser.parse(raw)
        prog.offset_x = offset_x
        prog.offset_y = offset_y
        prog.source = GCodeSource.VECTOR
        
        if prog.moves:
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            prog.width_mm = mx_x - mn_x
            prog.height_mm = mx_y - mn_y
        
        prog.calculate_statistics(self.feed)
        
        return prog


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATORE GCODE DA IMMAGINE (RASTER DIRETTO)
# ══════════════════════════════════════════════════════════════════════════════
class ImageGCodeGenerator:
    """
    Generatore GCode direttamente da immagine raster.
    Non richiede vettorizzazione - modula la potenza del laser
    in base ai valori di grigio dell'immagine.
    
    Modalità supportate:
    - Grayscale PWM: modula S in base al grigio (più scuro = più potenza)
    - Dithering: converte in pattern on/off con Floyd-Steinberg
    - Threshold: semplice soglia on/off
    """
    
    class Mode(Enum):
        """Modalità di conversione immagine."""
        GRAYSCALE = auto()    # Modula potenza in base al grigio
        DITHERING = auto()    # Floyd-Steinberg dithering
        THRESHOLD = auto()    # Semplice soglia
    
    def __init__(self, 
                 feed: int = 1000,
                 max_power: int = 255,
                 min_power: int = 0,
                 passes: int = 1):
        """
        Inizializza il generatore da immagine.
        
        Args:
            feed: Velocità di avanzamento (mm/min)
            max_power: Potenza massima (0-255)
            min_power: Potenza minima (0-255)
            passes: Numero di passate
        """
        self.feed = feed
        self.max_power = max_power
        self.min_power = min_power
        self.passes = passes
        self.rapid_feed = 3000
    
    # ══════════════════════════════════════════════════════════════════════════
    #  FUNZIONI STATICHE DI CALCOLO
    # ══════════════════════════════════════════════════════════════════════════
    @staticmethod
    def calculate_resolution(width_mm: float, height_mm: float, 
                            max_lines: int, direction: RasterDirection) -> Tuple[float, int, int]:
        """
        Calcola risoluzione ottimale in base al numero massimo di righe.
        
        Args:
            width_mm: Larghezza in mm
            height_mm: Altezza in mm
            max_lines: Numero massimo di righe di scansione
            direction: RasterDirection (HORIZONTAL o VERTICAL)
        
        Returns:
            (resolution_mm, actual_lines, pixels_per_line)
        """
        if direction == RasterDirection.HORIZONTAL:
            resolution_mm = height_mm / max_lines
            actual_lines = max_lines
            pixels_per_line = max(1, int(width_mm / resolution_mm))
        else:
            resolution_mm = width_mm / max_lines
            actual_lines = max_lines
            pixels_per_line = max(1, int(height_mm / resolution_mm))
        
        return resolution_mm, actual_lines, pixels_per_line
    
    @staticmethod
    def preview_image(image_array, width_mm: float, height_mm: float,
                     max_lines: int, direction: RasterDirection):
        """
        Genera anteprima dell'immagine ridimensionata per la generazione GCode.
        
        Args:
            image_array: Array numpy grayscale (0-255)
            width_mm: Larghezza target in mm
            height_mm: Altezza target in mm
            max_lines: Numero massimo righe
            direction: Direzione scansione
        
        Returns:
            (preview_array, resolution_mm, total_lines, estimated_moves)
        """
        import numpy as np
        
        resolution_mm, actual_lines, pixels_per_line = \
            ImageGCodeGenerator.calculate_resolution(width_mm, height_mm, max_lines, direction)
        
        # Calcola dimensioni preview
        if direction == RasterDirection.HORIZONTAL:
            preview_h = actual_lines
            preview_w = pixels_per_line
        else:
            preview_w = actual_lines
            preview_h = pixels_per_line
        
        # Ridimensiona immagine
        try:
            import cv2
            preview = cv2.resize(image_array, (preview_w, preview_h),
                               interpolation=cv2.INTER_AREA)
        except ImportError:
            from PIL import Image
            pil_img = Image.fromarray(image_array)
            pil_img = pil_img.resize((preview_w, preview_h), Image.LANCZOS)
            preview = np.array(pil_img)
        
        # Stima numero comandi (approssimativo)
        # In media, ogni riga genera ~10-50% dei pixel come comandi
        estimated_moves = actual_lines * pixels_per_line // 10
        
        return preview, resolution_mm, actual_lines, estimated_moves
    
    # ══════════════════════════════════════════════════════════════════════════
    #  GENERAZIONE PRINCIPALE
    # ══════════════════════════════════════════════════════════════════════════
    def build_from_array(self,
                         image_array,
                         width_mm: float,
                         height_mm: float,
                         max_lines: int = 200,
                         mode: Optional['ImageGCodeGenerator.Mode'] = None,
                         direction: RasterDirection = RasterDirection.HORIZONTAL,
                         raster_mode: RasterMode = RasterMode.BIDIRECTIONAL,
                         invert: bool = True,
                         offset_x: float = 0.0,
                         offset_y: float = 0.0,
                         threshold: int = 128) -> GCodeProgram:
        """
        Genera GCode direttamente da un array immagine.
        
        Args:
            image_array: Array numpy grayscale (0=nero, 255=bianco)
            width_mm: Larghezza finale in mm
            height_mm: Altezza finale in mm
            max_lines: Numero massimo di righe di scansione (controlla risoluzione)
            mode: Modalità di conversione (GRAYSCALE, DITHERING, THRESHOLD)
            direction: Direzione di scansione
            raster_mode: Unidirezionale o bidirezionale
            invert: Se True, nero=laser ON (tipico per incisione)
            offset_x: Offset X
            offset_y: Offset Y
            threshold: Soglia per modalità THRESHOLD
        
        Returns:
            GCodeProgram completo
        """
        import numpy as np
        
        if mode is None:
            mode = self.Mode.GRAYSCALE
        
        # Calcola risoluzione in base a max_lines
        resolution_mm, actual_lines, pixels_per_line = \
            self.calculate_resolution(width_mm, height_mm, max_lines, direction)
        
        # Ridimensiona immagine alla risoluzione target
        if direction == RasterDirection.HORIZONTAL:
            target_w, target_h = pixels_per_line, actual_lines
        else:
            target_w, target_h = actual_lines, pixels_per_line
        
        try:
            import cv2
            img_resized = cv2.resize(image_array, (target_w, target_h),
                                    interpolation=cv2.INTER_AREA)
        except ImportError:
            from PIL import Image
            pil_img = Image.fromarray(image_array)
            pil_img = pil_img.resize((target_w, target_h), Image.LANCZOS)
            img_resized = np.array(pil_img)
        
        # Applica dithering se richiesto
        if mode == self.Mode.DITHERING:
            img_resized = self._floyd_steinberg_dithering(img_resized.astype(np.float32))
        
        # Genera header
        raw = self._generate_header(width_mm, height_mm, resolution_mm, mode, direction)
        raw.append(f"; Max Lines Limit: {max_lines}")
        raw.append(f"; Actual Lines: {actual_lines}")
        raw.append(f"; Pixels per Line: {pixels_per_line}")
        raw.append(f"; Raster Mode: {raster_mode.name}")
        raw.append("")
        
        # Genera percorsi per ogni passata
        for p in range(self.passes):
            if self.passes > 1:
                raw.append(f"")
                raw.append(f"; --- Passata {p + 1}/{self.passes} ---")
            
            if direction == RasterDirection.HORIZONTAL:
                raw.extend(self._generate_horizontal_raster(
                    img_resized, width_mm, height_mm, resolution_mm,
                    mode, raster_mode, invert, threshold))
            else:
                raw.extend(self._generate_vertical_raster(
                    img_resized, width_mm, height_mm, resolution_mm,
                    mode, raster_mode, invert, threshold))
        
        raw.extend(self._generate_footer())
        
        # Crea programma
        prog = GCodeProgram()
        prog.raw_lines = raw
        prog.moves = GCodeParser.parse(raw)
        prog.offset_x = offset_x
        prog.offset_y = offset_y
        prog.width_mm = width_mm
        prog.height_mm = height_mm
        prog.source = GCodeSource.IMAGE
        prog.calculate_statistics(self.feed)
        
        return prog
    
    # ══════════════════════════════════════════════════════════════════════════
    #  GENERAZIONE HEADER/FOOTER
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_header(self, width_mm, height_mm, resolution, mode, direction) -> List[str]:
        """Genera header GCode."""
        return [
            f"; PyLaser v{APP_VERSION}",
            f"; Source: IMAGE (Direct Raster)",
            f"; Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Mode: {mode.name}",
            f"; Direction: {direction.name}",
            f"; Size: {width_mm:.2f} x {height_mm:.2f} mm",
            f"; Resolution: {resolution:.3f} mm/line",
            f"; Feed: {self.feed} mm/min",
            f"; Max Power: {self.max_power}",
            f"; Min Power: {self.min_power}",
            f"; Passes: {self.passes}",
            "",
            "; === INIZIALIZZAZIONE ===",
            "G21          ; Unità: millimetri",
            "G90          ; Coordinate assolute",
            "G92 X0 Y0    ; Imposta origine",
            f"F{self.feed}       ; Velocità di lavoro",
            "M5           ; Laser OFF (sicurezza)",
            "",
            "; === INIZIO RASTER ===",
        ]
    
    def _generate_footer(self) -> List[str]:
        """Genera footer GCode."""
        return [
            "",
            "; === FINE ===",
            "M5           ; Laser OFF",
            "G0 X0 Y0     ; Torna a home",
            "M2           ; Fine programma",
        ]
    
    # ══════════════════════════════════════════════════════════════════════════
    #  GENERAZIONE RASTER ORIZZONTALE
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_horizontal_raster(self, img, width_mm, height_mm, resolution,
                                     mode, raster_mode, invert, threshold) -> List[str]:
        """Genera scansione raster orizzontale."""
        lines = []
        num_rows, num_cols = img.shape
        
        for row in range(num_rows):
            y = height_mm - (row * resolution)  # Dall'alto verso il basso
            
            # Direzione X alternata per bidirezionale
            if raster_mode == RasterMode.BIDIRECTIONAL and row % 2 == 1:
                x_range = range(num_cols - 1, -1, -1)
                x_start = width_mm
            else:
                x_range = range(num_cols)
                x_start = 0.0
            
            # Vai all'inizio della riga (movimento rapido)
            lines.append(f"G0 X{x_start:.3f} Y{y:.3f}")
            
            # Scansiona la riga
            if mode == self.Mode.GRAYSCALE:
                lines.extend(self._raster_line_grayscale(
                    img[row, :], x_range, y, resolution, width_mm, invert))
            else:
                lines.extend(self._raster_line_threshold(
                    img[row, :], x_range, y, resolution, width_mm, invert, threshold))
        
        return lines
    
    def _raster_line_grayscale(self, row_data, x_range, y, resolution, width_mm, invert) -> List[str]:
        """Genera linea raster con modulazione grayscale PWM."""
        lines = []
        laser_was_on = False
        last_power = -1
        
        for i, col_idx in enumerate(x_range):
            pixel = row_data[col_idx]
            
            # Calcola potenza (inverte se necessario)
            if invert:
                # Nero (0) = max potenza, Bianco (255) = min potenza
                power = int(self.max_power - (pixel / 255.0) * (self.max_power - self.min_power))
            else:
                power = int(self.min_power + (pixel / 255.0) * (self.max_power - self.min_power))
            
            # Calcola coordinata X
            if isinstance(x_range, range):
                if x_range.step > 0:  # Range normale
                    x = col_idx * resolution
                else:  # Range inverso
                    x = col_idx * resolution
            else:
                x = i * resolution
            
            # Ottimizzazione: salta pixel quasi bianchi (risparmia comandi)
            if power <= self.min_power + 5:
                if laser_was_on:
                    lines.append("M5")
                    laser_was_on = False
                continue
            
            # Cambia potenza solo se diversa (ottimizzazione)
            if power != last_power:
                if laser_was_on:
                    lines.append(f"M3 S{power}")
                else:
                    lines.append(f"M3 S{power}")
                    laser_was_on = True
                last_power = power
            
            lines.append(f"G1 X{x:.3f} Y{y:.3f}")
        
        if laser_was_on:
            lines.append("M5")
        
        return lines
    
    def _raster_line_threshold(self, row_data, x_range, y, resolution, width_mm, invert, threshold) -> List[str]:
        """Genera linea raster con soglia semplice (on/off)."""
        lines = []
        laser_on = False
        
        for i, col_idx in enumerate(x_range):
            pixel = row_data[col_idx]
            
            # Determina se laser deve essere acceso
            if invert:
                should_be_on = pixel < threshold  # Scuro = ON
            else:
                should_be_on = pixel >= threshold  # Chiaro = ON
            
            # Calcola coordinata X
            if isinstance(x_range, range):
                x = col_idx * resolution
            else:
                x = i * resolution
            
            if should_be_on and not laser_on:
                lines.append(f"G0 X{x:.3f} Y{y:.3f}")
                lines.append(f"M3 S{self.max_power}")
                laser_on = True
            elif not should_be_on and laser_on:
                lines.append(f"G1 X{x:.3f} Y{y:.3f}")
                lines.append("M5")
                laser_on = False
            elif laser_on:
                lines.append(f"G1 X{x:.3f} Y{y:.3f}")
        
        if laser_on:
            lines.append("M5")
        
        return lines
    
    # ══════════════════════════════════════════════════════════════════════════
    #  GENERAZIONE RASTER VERTICALE
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_vertical_raster(self, img, width_mm, height_mm, resolution,
                                   mode, raster_mode, invert, threshold) -> List[str]:
        """Genera scansione raster verticale."""
        lines = []
        num_rows, num_cols = img.shape
        
        for col in range(num_cols):
            x = col * resolution
            
            # Direzione Y alternata per bidirezionale
            if raster_mode == RasterMode.BIDIRECTIONAL and col % 2 == 1:
                y_range = range(num_rows - 1, -1, -1)
                y_start = 0.0
            else:
                y_range = range(num_rows)
                y_start = height_mm
            
            # Vai all'inizio della colonna
            lines.append(f"G0 X{x:.3f} Y{y_start:.3f}")
            
            # Scansiona la colonna
            if mode == self.Mode.GRAYSCALE:
                lines.extend(self._raster_col_grayscale(
                    img[:, col], y_range, x, height_mm, resolution, invert))
            else:
                lines.extend(self._raster_col_threshold(
                    img[:, col], y_range, x, height_mm, resolution, invert, threshold))
        
        return lines
    
    def _raster_col_grayscale(self, col_data, y_range, x, height_mm, resolution, invert) -> List[str]:
        """Genera colonna raster con modulazione grayscale."""
        lines = []
        laser_was_on = False
        last_power = -1
        
        for row_idx in y_range:
            pixel = col_data[row_idx]
            
            if invert:
                power = int(self.max_power - (pixel / 255.0) * (self.max_power - self.min_power))
            else:
                power = int(self.min_power + (pixel / 255.0) * (self.max_power - self.min_power))
            
            y = height_mm - (row_idx * resolution)
            
            if power <= self.min_power + 5:
                if laser_was_on:
                    lines.append("M5")
                    laser_was_on = False
                continue
            
            if power != last_power:
                if not laser_was_on:
                    lines.append(f"M3 S{power}")
                    laser_was_on = True
                else:
                    lines.append(f"M3 S{power}")
                last_power = power
            
            lines.append(f"G1 X{x:.3f} Y{y:.3f}")
        
        if laser_was_on:
            lines.append("M5")
        
        return lines
    
    def _raster_col_threshold(self, col_data, y_range, x, height_mm, resolution, invert, threshold) -> List[str]:
        """Genera colonna raster con soglia."""
        lines = []
        laser_on = False
        
        for row_idx in y_range:
            pixel = col_data[row_idx]
            y = height_mm - (row_idx * resolution)
            
            if invert:
                should_be_on = pixel < threshold
            else:
                should_be_on = pixel >= threshold
            
            if should_be_on and not laser_on:
                lines.append(f"G0 X{x:.3f} Y{y:.3f}")
                lines.append(f"M3 S{self.max_power}")
                laser_on = True
            elif not should_be_on and laser_on:
                lines.append(f"G1 X{x:.3f} Y{y:.3f}")
                lines.append("M5")
                laser_on = False
            elif laser_on:
                lines.append(f"G1 X{x:.3f} Y{y:.3f}")
        
        if laser_on:
            lines.append("M5")
        
        return lines
    
    # ══════════════════════════════════════════════════════════════════════════
    #  DITHERING
    # ══════════════════════════════════════════════════════════════════════════
    def _floyd_steinberg_dithering(self, img) -> 'np.ndarray':
        """
        Applica Floyd-Steinberg dithering all'immagine.
        Crea un effetto halftone con pattern di punti.
        
        Args:
            img: Array numpy float32
        
        Returns:
            Array numpy uint8 dithered
        """
        import numpy as np
        
        h, w = img.shape
        result = img.copy()
        
        for y in range(h):
            for x in range(w):
                old_pixel = result[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                result[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                # Distribuisci errore ai pixel vicini
                if x + 1 < w:
                    result[y, x + 1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        result[y + 1, x - 1] += error * 3 / 16
                    result[y + 1, x] += error * 5 / 16
                    if x + 1 < w:
                        result[y + 1, x + 1] += error * 1 / 16
        
        return np.clip(result, 0, 255).astype(np.uint8)


# ══════════════════════════════════════════════════════════════════════════════
#  FACTORY / FACADE
# ══════════════════════════════════════════════════════════════════════════════
class GCodeFactory:
    """
    Factory per creare generatori GCode.
    Semplifica la scelta tra generazione vettoriale e da immagine.
    """
    
    @staticmethod
    def create_vector_generator(feed: int = 1000, 
                                 power: int = 200, 
                                 passes: int = 1) -> VectorGCodeGenerator:
        """Crea un generatore per percorsi vettoriali."""
        return VectorGCodeGenerator(feed=feed, power=power, passes=passes)
    
    @staticmethod
    def create_image_generator(feed: int = 1000,
                                max_power: int = 255,
                                min_power: int = 0,
                                passes: int = 1) -> ImageGCodeGenerator:
        """Crea un generatore per immagini raster."""
        return ImageGCodeGenerator(
            feed=feed,
            max_power=max_power,
            min_power=min_power,
            passes=passes
        )
    
    @staticmethod
    def generate(source: GCodeSource,
                 data,  # path_lines per VECTOR, image_array per IMAGE
                 width_mm: float,
                 height_mm: float,
                 feed: int = 1000,
                 power: int = 200,
                 passes: int = 1,
                 offset_x: float = 0.0,
                 offset_y: float = 0.0,
                 **kwargs) -> GCodeProgram:
        """
        Metodo unificato per generare GCode da qualsiasi sorgente.
        
        Args:
            source: GCodeSource.VECTOR o GCodeSource.IMAGE
            data: Lista di path lines (VECTOR) o numpy array (IMAGE)
            width_mm: Larghezza in mm
            height_mm: Altezza in mm
            feed: Velocità mm/min
            power: Potenza (0-255)
            passes: Numero passate
            offset_x: Offset X
            offset_y: Offset Y
            **kwargs: Parametri aggiuntivi per il generatore specifico
                      IMAGE: max_lines, mode, direction, raster_mode, invert, threshold
        
        Returns:
            GCodeProgram
        """
        if source == GCodeSource.VECTOR:
            gen = VectorGCodeGenerator(feed=feed, power=power, passes=passes)
            return gen.build(data, offset_x=offset_x, offset_y=offset_y)
        
        elif source == GCodeSource.IMAGE:
            gen = ImageGCodeGenerator(
                feed=feed,
                max_power=power,
                min_power=kwargs.get('min_power', 0),
                passes=passes
            )
            return gen.build_from_array(
                data,
                width_mm=width_mm,
                height_mm=height_mm,
                max_lines=kwargs.get('max_lines', 200),
                mode=kwargs.get('mode', ImageGCodeGenerator.Mode.GRAYSCALE),
                direction=kwargs.get('direction', RasterDirection.HORIZONTAL),
                raster_mode=kwargs.get('raster_mode', RasterMode.BIDIRECTIONAL),
                invert=kwargs.get('invert', True),
                offset_x=offset_x,
                offset_y=offset_y,
                threshold=kwargs.get('threshold', 128)
            )
        
        else:
            raise ValueError(f"Sorgente GCode non supportata: {source}")


# ══════════════════════════════════════════════════════════════════════════════
#  COMPATIBILITÀ CON CODICE ESISTENTE
# ══════════════════════════════════════════════════════════════════════════════
# Alias per retrocompatibilità con main.py esistente
GCodeGenerator = VectorGCodeGenerator


# ══════════════════════════════════════════════════════════════════════════════
#  TEST / ESEMPIO
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== Test GCode Generator Module ===\n")
    
    # Test 1: Generatore vettoriale
    print("1. Test VectorGCodeGenerator:")
    vec_gen = VectorGCodeGenerator(feed=1500, power=180, passes=2)
    test_paths = [
        "G0 X10 Y10",
        "M3 S{lp}",
        "G1 X50 Y10",
        "G1 X50 Y50",
        "G1 X10 Y50",
        "G1 X10 Y10",
        "M5"
    ]
    prog = vec_gen.build(test_paths, offset_x=5, offset_y=5)
    print(f"   Linee generate: {len(prog.raw_lines)}")
    print(f"   Movimenti: {len(prog.moves)}")
    print(f"   Bounds: {prog.bounds()}")
    print(f"   Distanza totale: {prog.total_distance_mm:.2f} mm")
    print(f"   Tempo stimato: {prog.estimated_time_seconds:.1f} s")
    
    # Test 2: Parser
    print("\n2. Test GCodeParser:")
    moves = GCodeParser.parse(prog.raw_lines)
    print(f"   Movimenti parsati: {len(moves)}")
    laser_on_moves = sum(1 for m in moves if m.laser_on)
    print(f"   Movimenti laser ON: {laser_on_moves}")
    
    # Test 3: Factory
    print("\n3. Test GCodeFactory:")
    prog2 = GCodeFactory.generate(
        source=GCodeSource.VECTOR,
        data=test_paths,
        width_mm=100,
        height_mm=100,
        feed=2000,
        power=200
    )
    print(f"   Programma generato: {len(prog2.raw_lines)} linee")
    
    # Test 4: Generatore immagine (richiede numpy)
    print("\n4. Test ImageGCodeGenerator:")
    try:
        import numpy as np
        
        # Crea immagine di test (gradiente)
        test_img = np.zeros((20, 20), dtype=np.uint8)
        for i in range(20):
            test_img[i, :] = int(255 * i / 19)
        
        # Test calcolo risoluzione
        res, lines, ppl = ImageGCodeGenerator.calculate_resolution(
            20, 20, 10, RasterDirection.HORIZONTAL)
        print(f"   Risoluzione: {res:.2f} mm, Righe: {lines}, Pixel/riga: {ppl}")
        
        # Test anteprima
        preview, res, lines, est = ImageGCodeGenerator.preview_image(
            test_img, 20, 20, 10, RasterDirection.HORIZONTAL)
        print(f"   Preview: {preview.shape}, Movimenti stimati: {est}")
        
        # Test generazione
        img_gen = ImageGCodeGenerator(feed=1000, max_power=255, min_power=0)
        prog3 = img_gen.build_from_array(
            test_img,
            width_mm=20,
            height_mm=20,
            max_lines=10,
            mode=ImageGCodeGenerator.Mode.GRAYSCALE
        )
        print(f"   Linee generate: {len(prog3.raw_lines)}")
        print(f"   Source: {prog3.source.name}")
        print(f"   Tempo stimato: {prog3.estimated_time_seconds:.1f} s")
        
    except ImportError:
        print("   (numpy non disponibile, test saltato)")
    
    print("\n=== Test completati ===")