#!/usr/bin/env python3
"""
vectorizer.py
Modulo di vettorizzazione immagini per PyLaser

Metodi supportati:
- Contorni (contour tracing)
- Centerline (skeletonization)
- Raster (scansione lineare)
- Hatching (tratteggio angolato)
"""

import math
from typing import List, Optional, Callable

# ══════════════════════════════════════════════════════════════════════════════
#  DIPENDENZE OPZIONALI
# ══════════════════════════════════════════════════════════════════════════════
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
#  CLASSE VECTORIZER
# ══════════════════════════════════════════════════════════════════════════════
class Vectorizer:
    """
    Converte immagini binarie in percorsi vettoriali per incisione laser.
    
    Metodi disponibili:
    - preprocess(): Converte immagine in binario
    - contour_paths(): Estrae i contorni
    - centerline_paths(): Estrae le linee centrali (skeleton)
    - raster_paths(): Genera scansione raster
    - hatch_paths(): Genera tratteggio angolato
    """
    
    def __init__(self, log_cb: Optional[Callable] = None):
        """
        Inizializza il vettorizzatore.
        
        Args:
            log_cb: Callback per logging (opzionale)
        """
        self.log = log_cb or print
        self._strings = None
    
    def set_strings(self, strings):
        """Imposta le stringhe localizzate."""
        self._strings = strings
    
    # ══════════════════════════════════════════════════════════════════════════
    #  PREPROCESSING
    # ══════════════════════════════════════════════════════════════════════════
    def preprocess(self, pil_image, 
                   threshold: int = 128,
                   blur_radius: int = 2, 
                   invert: bool = False, 
                   denoise: bool = False) -> 'np.ndarray':
        """
        Pre-elabora un'immagine PIL convertendola in binario.
        
        Args:
            pil_image: Immagine PIL (qualsiasi formato)
            threshold: Soglia per binarizzazione (0-255)
            blur_radius: Raggio sfocatura gaussiana
            invert: Se True, inverte bianco/nero
            denoise: Se True, applica riduzione rumore
        
        Returns:
            Array numpy binario (0 o 255)
        """
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy richiesto per preprocessing")
        
        # Converti in grayscale
        img = np.array(pil_image.convert("L"))
        
        # Riduzione rumore
        if denoise and CV2_AVAILABLE:
            img = cv2.fastNlMeansDenoising(img, h=10)
        
        # Sfocatura gaussiana
        if blur_radius > 0 and CV2_AVAILABLE:
            k = blur_radius * 2 + 1
            img = cv2.GaussianBlur(img, (k, k), 0)
        
        # Binarizzazione
        if CV2_AVAILABLE:
            _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        else:
            binary = np.where(img > threshold, np.uint8(255), np.uint8(0))
        
        # Inversione
        if invert:
            binary = (255 - binary).astype(np.uint8)
        
        return binary
    
    # ══════════════════════════════════════════════════════════════════════════
    #  METODO: CONTORNI
    # ══════════════════════════════════════════════════════════════════════════
    def contour_paths(self, binary: 'np.ndarray', 
                      width_mm: float, 
                      height_mm: float, 
                      simplify: float = 1.0) -> List[str]:
        """
        Estrae i contorni dall'immagine binaria.
        
        Args:
            binary: Immagine binaria (numpy array)
            width_mm: Larghezza target in mm
            height_mm: Altezza target in mm
            simplify: Fattore di semplificazione (0-10)
        
        Returns:
            Lista di comandi GCode
        """
        if not CV2_AVAILABLE:
            self.log("⚠ OpenCV richiesto per contorni")
            return []
        
        h_px, w_px = binary.shape
        scale_x = width_mm / w_px
        scale_y = height_mm / h_px
        
        # Trova contorni
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
        )
        
        lines = []
        for cnt in contours:
            if len(cnt) < 2:
                continue
            
            # Semplifica contorno
            epsilon = simplify * cv2.arcLength(cnt, True) / max(len(cnt), 1)
            cnt = cv2.approxPolyDP(cnt, epsilon, closed=True)
            
            pts = cnt.reshape(-1, 2)
            
            # Primo punto (movimento rapido)
            x0 = pts[0, 0] * scale_x
            y0 = (h_px - pts[0, 1]) * scale_y
            lines.append(f"G0 X{x0:.3f} Y{y0:.3f}")
            lines.append("M3 S{lp}")
            
            # Punti successivi (incisione)
            for pt in pts[1:]:
                x = pt[0] * scale_x
                y = (h_px - pt[1]) * scale_y
                lines.append(f"G1 X{x:.3f} Y{y:.3f}")
            
            # Chiudi contorno
            lines.append(f"G1 X{x0:.3f} Y{y0:.3f}")
            lines.append("M5")
        
        if self._strings:
            self.log(self._strings.log_contours_found.format(n=len(contours)))
        else:
            self.log(f"Contorni trovati: {len(contours)}")
        
        return lines
    
    # ══════════════════════════════════════════════════════════════════════════
    #  METODO: RASTER
    # ══════════════════════════════════════════════════════════════════════════
    def raster_paths(self, binary: 'np.ndarray', 
                     width_mm: float, 
                     height_mm: float, 
                     gap_mm: float = 0.1) -> List[str]:
        """
        Genera percorso raster (scansione lineare bidirezionale).
        
        Args:
            binary: Immagine binaria
            width_mm: Larghezza target in mm
            height_mm: Altezza target in mm
            gap_mm: Distanza tra le linee di scansione
        
        Returns:
            Lista di comandi GCode
        """
        h_px, w_px = binary.shape
        
        # Calcola dimensioni griglia
        cols = max(1, int(width_mm / max(gap_mm, 0.01)))
        rows = max(1, int(height_mm / max(gap_mm, 0.01)))
        
        # Ridimensiona immagine
        if CV2_AVAILABLE:
            img = cv2.resize(binary, (cols, rows), interpolation=cv2.INTER_AREA)
        else:
            img = binary  # Fallback senza resize
        
        scale_x = width_mm / cols
        scale_y = height_mm / rows
        
        lines = []
        for row in range(rows):
            y = row * scale_y
            
            # Direzione alternata (serpentina)
            if row % 2 == 0:
                col_range = range(cols)
            else:
                col_range = range(cols - 1, -1, -1)
            
            laser_on = False
            for col in col_range:
                pixel_on = img[row, col] > 127
                x = col * scale_x
                
                if pixel_on and not laser_on:
                    lines.append(f"G0 X{x:.3f} Y{y:.3f}")
                    lines.append("M3 S{lp}")
                    laser_on = True
                elif not pixel_on and laser_on:
                    lines.append(f"G1 X{x:.3f} Y{y:.3f}")
                    lines.append("M5")
                    laser_on = False
                elif pixel_on:
                    lines.append(f"G1 X{x:.3f} Y{y:.3f}")
            
            if laser_on:
                lines.append("M5")
        
        return lines
    
    # ══════════════════════════════════════════════════════════════════════════
    #  METODO: CENTERLINE
    # ══════════════════════════════════════════════════════════════════════════
    def centerline_paths(self, binary: 'np.ndarray', 
                         width_mm: float, 
                         height_mm: float) -> List[str]:
        """
        Estrae le linee centrali (skeleton) dall'immagine.
        
        Args:
            binary: Immagine binaria
            width_mm: Larghezza target in mm
            height_mm: Altezza target in mm
        
        Returns:
            Lista di comandi GCode
        """
        if not CV2_AVAILABLE:
            self.log("⚠ OpenCV richiesto per centerline")
            return []
        
        # Skeletonization
        try:
            skel = cv2.ximgproc.thinning(binary)
        except AttributeError:
            skel = self._morph_skeleton(binary)
        
        h_px, w_px = skel.shape
        scale_x = width_mm / w_px
        scale_y = height_mm / h_px
        
        return self._trace_skeleton(skel, scale_x, scale_y, h_px)
    
    def _morph_skeleton(self, binary: 'np.ndarray') -> 'np.ndarray':
        """Skeletonization usando operazioni morfologiche."""
        img = binary.copy()
        skel = np.zeros_like(img)
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        
        while True:
            eroded = cv2.erode(img, kernel)
            temp = cv2.subtract(img, cv2.dilate(eroded, kernel))
            skel = cv2.bitwise_or(skel, temp)
            img = eroded
            if cv2.countNonZero(img) == 0:
                break
        
        return skel
    
    def _trace_skeleton(self, skel: 'np.ndarray', 
                        scale_x: float, 
                        scale_y: float, 
                        h_px: int) -> List[str]:
        """Traccia lo skeleton generando comandi GCode."""
        visited = np.zeros(skel.shape, dtype=bool)
        lines = []
        
        # Trova tutti i pixel dello skeleton
        ys, xs = np.where(skel > 0)
        
        def get_neighbors(x, y):
            neighbors = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < skel.shape[1] and 
                        0 <= ny < skel.shape[0] and
                        skel[ny, nx] > 0 and 
                        not visited[ny, nx]):
                        neighbors.append((nx, ny))
            return neighbors
        
        for x0, y0 in zip(xs.tolist(), ys.tolist()):
            if visited[y0, x0]:
                continue
            
            cx, cy = x0, y0
            first = True
            
            while True:
                if visited[cy, cx]:
                    break
                visited[cy, cx] = True
                
                gx = cx * scale_x
                gy = (h_px - cy) * scale_y
                
                if first:
                    lines.append(f"G0 X{gx:.3f} Y{gy:.3f}")
                    lines.append("M3 S{lp}")
                    first = False
                else:
                    lines.append(f"G1 X{gx:.3f} Y{gy:.3f}")
                
                neighbors = get_neighbors(cx, cy)
                if not neighbors:
                    break
                cx, cy = neighbors[0]
            
            if not first:
                lines.append("M5")
        
        return lines
    
    # ══════════════════════════════════════════════════════════════════════════
    #  METODO: HATCHING
    # ══════════════════════════════════════════════════════════════════════════
    def hatch_paths(self, binary: 'np.ndarray', 
                    width_mm: float, 
                    height_mm: float, 
                    angle: float = 45.0, 
                    gap_mm: float = 0.2) -> List[str]:
        """
        Genera tratteggio (hatching) con linee angolate.
        
        Args:
            binary: Immagine binaria
            width_mm: Larghezza target in mm
            height_mm: Altezza target in mm
            angle: Angolo delle linee in gradi
            gap_mm: Distanza tra le linee
        
        Returns:
            Lista di comandi GCode
        """
        if not CV2_AVAILABLE:
            return self.raster_paths(binary, width_mm, height_mm, gap_mm)
        
        h_px, w_px = binary.shape
        scale_x = width_mm / w_px
        scale_y = height_mm / h_px
        
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        
        gap_px = max(1, int(gap_mm / min(scale_x, scale_y)))
        
        # Trova pixel attivi
        ys, xs = np.where(binary > 127)
        if len(xs) == 0:
            return []
        
        # Proiezione lungo la direzione perpendicolare
        proj = (xs * (-sin_a) + ys * cos_a).astype(int)
        
        lines = []
        for band in range(proj.min(), proj.max() + gap_px, gap_px):
            mask = (proj >= band) & (proj < band + gap_px)
            bx, by = xs[mask], ys[mask]
            
            if len(bx) == 0:
                continue
            
            # Ordina lungo la direzione dell'angolo
            order = np.argsort(bx * cos_a + by * sin_a)
            bx, by = bx[order], by[order]
            
            x0 = bx[0] * scale_x
            y0 = (h_px - by[0]) * scale_y
            
            lines.append(f"G0 X{x0:.3f} Y{y0:.3f}")
            lines.append("M3 S{lp}")
            
            for i in range(1, len(bx)):
                x = bx[i] * scale_x
                y = (h_px - by[i]) * scale_y
                lines.append(f"G1 X{x:.3f} Y{y:.3f}")
            
            lines.append("M5")
        
        return lines


# ══════════════════════════════════════════════════════════════════════════════
#  FUNZIONI DI UTILITÀ
# ══════════════════════════════════════════════════════════════════════════════
def check_dependencies() -> dict:
    """Verifica le dipendenze disponibili."""
    return {
        'numpy': NUMPY_AVAILABLE,
        'opencv': CV2_AVAILABLE,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  TEST
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== Test Vectorizer Module ===\n")
    
    deps = check_dependencies()
    print(f"Dipendenze: {deps}\n")
    
    if NUMPY_AVAILABLE:
        # Crea immagine di test
        test_img = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(test_img, (20, 20), (80, 80), 255, -1) if CV2_AVAILABLE else None
        
        vec = Vectorizer()
        
        if CV2_AVAILABLE:
            # Test contorni
            paths = vec.contour_paths(test_img, 50, 50, simplify=1.0)
            print(f"Contorni: {len(paths)} comandi")
            
            # Test raster
            paths = vec.raster_paths(test_img, 50, 50, gap_mm=0.5)
            print(f"Raster: {len(paths)} comandi")
            
            # Test hatching
            paths = vec.hatch_paths(test_img, 50, 50, angle=45, gap_mm=0.5)
            print(f"Hatching: {len(paths)} comandi")
    
    print("\n=== Test completati ===")