#!/usr/bin/env python3
"""
canvas_widgets.py
Widget canvas per PyLaser

Include:
- WorkAreaCanvas: Canvas principale con area di lavoro
- VectorPreviewWindow: Finestra anteprima vettoriale
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from typing import Optional, Callable, List
from dataclasses import dataclass

# Import locali
try:
    from gcode_generator import GCodeMove, GCodeProgram
except ImportError:
    # Fallback per definizioni inline
    @dataclass
    class GCodeMove:
        x: float = 0.0
        y: float = 0.0
        laser_on: bool = False
        is_rapid: bool = False
        power: int = 0
    
    @dataclass
    class GCodeProgram:
        moves: list = None
        
        def __post_init__(self):
            if self.moves is None:
                self.moves = []
        
        def bounds(self):
            if not self.moves:
                return 0, 0, 0, 0
            xs = [m.x for m in self.moves]
            ys = [m.y for m in self.moves]
            return min(xs), min(ys), max(xs), max(ys)


# ══════════════════════════════════════════════════════════════════════════════
#  WORK AREA CANVAS
# ══════════════════════════════════════════════════════════════════════════════
class WorkAreaCanvas(tk.Canvas):
    """
    Canvas per visualizzazione e interazione con l'area di lavoro.
    
    Features:
    - Visualizzazione griglia millimetrata
    - Zoom e pan con mouse
    - Drag del modello GCode
    - Simulazione animata percorso
    - Anteprima bbox fisica
    """
    
    def __init__(self, parent, 
                 work_w: float = 400, 
                 work_h: float = 400,
                 theme=None, 
                 strings=None,
                 log_cb: Optional[Callable] = None, 
                 **kwargs):
        """
        Inizializza il canvas.
        
        Args:
            parent: Widget padre
            work_w: Larghezza area di lavoro in mm
            work_h: Altezza area di lavoro in mm
            theme: Oggetto tema colori
            strings: Oggetto stringhe localizzate
            log_cb: Callback per logging
        """
        self.theme = theme
        bg_color = theme.canvas_bg if theme else "#11111b"
        
        super().__init__(parent, bg=bg_color, highlightthickness=0, **kwargs)
        
        self.log = log_cb or print
        self.s = strings
        self.work_w_mm = work_w
        self.work_h_mm = work_h
        
        # Stato
        self.moves: List[GCodeMove] = []
        self.model_x_mm = 0.0
        self.model_y_mm = 0.0
        
        # Visualizzazione
        self._scale = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        
        # Interazione
        self._drag_start = None
        self._drag_model_start = None
        self._pan_start = None
        
        # Simulazione
        self._sim_thread = None
        self._sim_stop = threading.Event()
        
        # Callback
        self._pos_cb = None
        
        # Binding eventi
        self.bind("<Configure>", self._on_resize)
        self.bind("<ButtonPress-1>", self._on_lb_down)
        self.bind("<B1-Motion>", self._on_lb_move)
        self.bind("<ButtonRelease-1>", self._on_lb_up)
        self.bind("<ButtonPress-3>", self._on_rb_down)
        self.bind("<B3-Motion>", self._on_rb_move)
        self.bind("<ButtonPress-2>", self._on_rb_down)
        self.bind("<B2-Motion>", self._on_rb_move)
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Button-4>", self._on_wheel)
        self.bind("<Button-5>", self._on_wheel)
    
    # ══════════════════════════════════════════════════════════════════════════
    #  CONFIGURAZIONE
    # ══════════════════════════════════════════════════════════════════════════
    def set_theme(self, theme):
        """Imposta il tema colori."""
        self.theme = theme
        self.configure(bg=theme.canvas_bg)
        self._redraw()
    
    def set_strings(self, strings):
        """Imposta le stringhe localizzate."""
        self.s = strings
    
    def set_work_area(self, w_mm: float, h_mm: float):
        """Imposta le dimensioni dell'area di lavoro."""
        self.work_w_mm = w_mm
        self.work_h_mm = h_mm
        self._fit_view()
    
    def set_program(self, moves: List[GCodeMove]):
        """Imposta i movimenti da visualizzare."""
        self.moves = moves if moves else []
        self._fit_view()
    
    def set_model_position(self, x_mm: float, y_mm: float):
        """Imposta la posizione del modello."""
        self.model_x_mm = x_mm
        self.model_y_mm = y_mm
        self._redraw()
    
    def set_position_callback(self, cb: Callable):
        """Imposta callback per movimento modello."""
        self._pos_cb = cb
    
    # ══════════════════════════════════════════════════════════════════════════
    #  CONVERSIONI COORDINATE
    # ══════════════════════════════════════════════════════════════════════════
    def _to_px(self, mm_x: float, mm_y: float):
        """Converte coordinate mm in pixel canvas."""
        px = self._pan_x + mm_x * self._scale
        py = self._pan_y + (self.work_h_mm - mm_y) * self._scale
        return px, py
    
    def _to_mm(self, px: float, py: float):
        """Converte pixel canvas in coordinate mm."""
        mm_x = (px - self._pan_x) / self._scale
        mm_y = self.work_h_mm - (py - self._pan_y) / self._scale
        return mm_x, mm_y
    
    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING
    # ══════════════════════════════════════════════════════════════════════════
    def _fit_view(self):
        """Adatta la vista all'area di lavoro."""
        self.update_idletasks()
        cw, ch = self.winfo_width(), self.winfo_height()
        if cw < 10 or ch < 10:
            return
        
        margin = 30
        sx = (cw - 2 * margin) / self.work_w_mm
        sy = (ch - 2 * margin) / self.work_h_mm
        self._scale = min(sx, sy)
        self._pan_x = margin
        self._pan_y = margin
        self._redraw()
    
    def fit(self):
        """Adatta la vista (metodo pubblico)."""
        self._fit_view()
    
    def _redraw(self):
        """Ridisegna tutto il canvas."""
        self.delete("all")
        t = self.theme
        
        if t:
            self._draw_grid(t)
            self._draw_work_area(t)
            self._draw_origin(t)
            self._draw_paths(t)
            self._draw_bbox(t)
    
    def _draw_grid(self, t):
        """Disegna la griglia millimetrata."""
        cw, ch = self.winfo_width(), self.winfo_height()
        
        # Linee verticali
        x = 0.0
        while x <= self.work_w_mm + 10:
            px, _ = self._to_px(x, 0)
            col = t.surface1 if x % 50 == 0 else t.canvas_grid
            self.create_line(px, 0, px, ch, fill=col, width=1)
            
            if x % 50 == 0 and 0 < px < cw:
                self.create_text(px + 2, ch - 14, text=f"{int(x)}",
                                fill=t.subtext, font=("Consolas", 7), anchor="w")
            x += 10
        
        # Linee orizzontali
        y = 0.0
        while y <= self.work_h_mm + 10:
            _, py = self._to_px(0, y)
            col = t.surface1 if y % 50 == 0 else t.canvas_grid
            self.create_line(0, py, cw, py, fill=col, width=1)
            
            if y % 50 == 0 and 0 < py < ch:
                self.create_text(4, py - 2, text=f"{int(y)}",
                                fill=t.subtext, font=("Consolas", 7), anchor="w")
            y += 10
    
    def _draw_work_area(self, t):
        """Disegna il contorno dell'area di lavoro."""
        x0, y0 = self._to_px(0, 0)
        x1, y1 = self._to_px(self.work_w_mm, self.work_h_mm)
        
        # Ombra (solo temi scuri)
        lum = self._get_luminance(t.base)
        if lum < 0.5:
            self.create_rectangle(x0 + 4, y1 + 4, x1 + 4, y0 + 4,
                                 fill="#000000", outline="")
        
        self.create_rectangle(x0, y1, x1, y0,
                             fill=t.base, outline=t.surface1, width=2)
        
        # Etichetta
        label = f"Area: {self.work_w_mm}×{self.work_h_mm} mm"
        if self.s:
            label = self.s.canvas_area_label.format(w=self.work_w_mm, h=self.work_h_mm)
        
        self.create_text(x0 + 4, y0 + 4, text=label,
                        fill=t.subtext, font=("Consolas", 8), anchor="nw")
    
    def _draw_origin(self, t):
        """Disegna il marcatore origine/home."""
        ox, oy = self._to_px(0, 0)
        r = 6
        
        # Croce
        self.create_line(ox - r, oy, ox + r, oy, fill=t.home, width=2)
        self.create_line(ox, oy - r, ox, oy + r, fill=t.home, width=2)
        
        # Cerchio
        self.create_oval(ox - r, oy - r, ox + r, oy + r, outline=t.home, width=2)
        
        # Etichetta
        label = self.s.canvas_home_label if self.s else "HOME"
        self.create_text(ox + 10, oy - 10, text=label,
                        fill=t.home, font=("Consolas", 8, "bold"))
    
    def _draw_paths(self, t):
        """Disegna i percorsi GCode."""
        if not self.moves:
            return
        
        prev_x = prev_y = 0.0
        
        for mv in self.moves:
            wx = mv.x + self.model_x_mm
            wy = mv.y + self.model_y_mm
            
            px0, py0 = self._to_px(prev_x + self.model_x_mm, prev_y + self.model_y_mm)
            px1, py1 = self._to_px(wx, wy)
            
            # Determina stile linea
            if mv.is_rapid:
                col, dash, w = t.rapid, (3, 4), 1
            elif mv.laser_on:
                col, dash, w = t.laser_on, (), 1
            else:
                col, dash, w = t.laser_off, (2, 3), 1
            
            self.create_line(px0, py0, px1, py1,
                            fill=col, width=w, dash=dash, tags="path")
            
            prev_x, prev_y = mv.x, mv.y
    
    def _draw_bbox(self, t):
        """Disegna il bounding box del modello."""
        if not self.moves:
            return
        
        prog = GCodeProgram()
        prog.moves = self.moves
        mn_x, mn_y, mx_x, mx_y = prog.bounds()
        
        x0 = mn_x + self.model_x_mm
        y0 = mn_y + self.model_y_mm
        x1 = mx_x + self.model_x_mm
        y1 = mx_y + self.model_y_mm
        
        px0, py0 = self._to_px(x0, y0)
        px1, py1 = self._to_px(x1, y1)
        
        # Rettangolo bbox con fill semitrasparente
        # Tkinter non supporta alpha channel (#RRGGBBAA), quindi blend manualmente
        bbox_fill = self._blend_color(t.bbox, t.base, 0.15)  # 15% bbox, 85% background
        
        self.create_rectangle(px0, py1, px1, py0,
                             outline=t.bbox, fill=bbox_fill,
                             width=2, dash=(6, 3), tags="bbox")
        
        # Dimensioni
        w_mm = mx_x - mn_x
        h_mm = mx_y - mn_y
        self.create_text((px0 + px1) // 2, py1 - 10,
                        text=f"{w_mm:.1f} × {h_mm:.1f} mm",
                        fill=t.bbox, font=("Consolas", 8, "bold"), tags="bbox")
        
        # Corner handles
        for ax, ay in [(px0, py0), (px1, py0), (px0, py1), (px1, py1)]:
            self.create_rectangle(ax - 3, ay - 3, ax + 3, ay + 3,
                                 fill=t.bbox, outline="", tags="bbox")
    
    # ══════════════════════════════════════════════════════════════════════════
    #  UTILITY COLORI
    # ══════════════════════════════════════════════════════════════════════════
    def _get_luminance(self, hex_color: str) -> float:
        """
        Calcola la luminanza di un colore hex.
        
        Args:
            hex_color: Colore in formato #RRGGBB
        
        Returns:
            Luminanza da 0.0 (nero) a 1.0 (bianco)
        """
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    def _blend_color(self, fg_hex: str, bg_hex: str, alpha: float) -> str:
        """
        Miscela due colori hex simulando trasparenza (alpha blending).
        
        Tkinter non supporta colori con canale alfa (#RRGGBBAA), quindi
        questa funzione calcola il colore risultante miscelando RGB.
        
        Args:
            fg_hex: Colore in primo piano (es. "#f9e2af")
            bg_hex: Colore di sfondo (es. "#1e1e2e")
            alpha: Opacità del primo piano (0.0 = trasparente, 1.0 = opaco)
        
        Returns:
            Colore hex miscelato (es. "#2a2838")
        """
        # Rimuovi '#' se presente
        fg_hex = fg_hex.lstrip('#')
        bg_hex = bg_hex.lstrip('#')
        
        # Converti in RGB
        fg_r, fg_g, fg_b = [int(fg_hex[i:i+2], 16) for i in (0, 2, 4)]
        bg_r, bg_g, bg_b = [int(bg_hex[i:i+2], 16) for i in (0, 2, 4)]
        
        # Alpha blending: result = fg * alpha + bg * (1 - alpha)
        r = int(fg_r * alpha + bg_r * (1 - alpha))
        g = int(fg_g * alpha + bg_g * (1 - alpha))
        b = int(fg_b * alpha + bg_b * (1 - alpha))
        
        # Clamp a 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        # Converti in hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # ══════════════════════════════════════════════════════════════════════════
    #  EVENTI MOUSE
    # ══════════════════════════════════════════════════════════════════════════
    def _on_resize(self, event):
        """Gestisce il ridimensionamento del canvas."""
        self.after(50, self._fit_view)
    
    def _on_lb_down(self, e):
        """Inizio drag modello (tasto sinistro)."""
        self._drag_start = (e.x, e.y)
        self._drag_model_start = (self.model_x_mm, self.model_y_mm)
    
    def _on_lb_move(self, e):
        """Drag modello in corso."""
        if not self._drag_start:
            return
        
        dx_mm = (e.x - self._drag_start[0]) / self._scale
        dy_mm = -(e.y - self._drag_start[1]) / self._scale
        
        nx = self._drag_model_start[0] + dx_mm
        ny = self._drag_model_start[1] + dy_mm
        
        # Limita ai bordi dell'area di lavoro
        if self.moves:
            prog = GCodeProgram()
            prog.moves = self.moves
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            
            # Impedisci di uscire dall'area
            nx = max(-mn_x, min(nx, self.work_w_mm - (mx_x - mn_x) - mn_x))
            ny = max(-mn_y, min(ny, self.work_h_mm - (mx_y - mn_y) - mn_y))
        
        self.model_x_mm = nx
        self.model_y_mm = ny
        self._redraw()
    
    def _on_lb_up(self, e):
        """Fine drag modello."""
        self._drag_start = None
        if self._pos_cb:
            self._pos_cb(self.model_x_mm, self.model_y_mm)
    
    def _on_rb_down(self, e):
        """Inizio pan (tasto destro o centrale)."""
        self._pan_start = (e.x, e.y, self._pan_x, self._pan_y)
    
    def _on_rb_move(self, e):
        """Pan in corso."""
        if not self._pan_start:
            return
        sx, sy, px0, py0 = self._pan_start
        self._pan_x = px0 + (e.x - sx)
        self._pan_y = py0 + (e.y - sy)
        self._redraw()
    
    def _on_wheel(self, e):
        """Zoom con rotella mouse."""
        # Determina direzione scroll (cross-platform)
        if e.num == 4 or e.delta > 0:
            factor = 1.1  # Zoom in
        else:
            factor = 0.9  # Zoom out
        
        # Zoom centrato sul cursore
        mx, my = self._to_mm(e.x, e.y)
        self._scale *= factor
        self._pan_x = e.x - mx * self._scale
        self._pan_y = e.y - (self.work_h_mm - my) * self._scale
        self._redraw()
    
    # ══════════════════════════════════════════════════════════════════════════
    #  SIMULAZIONE
    # ══════════════════════════════════════════════════════════════════════════
    def start_simulation(self, speed_mult: int = 10, done_cb: Optional[Callable] = None):
        """
        Avvia la simulazione animata del percorso.
        
        Args:
            speed_mult: Moltiplicatore velocità (1 = lento, 50 = veloce)
            done_cb: Callback da chiamare al termine
        """
        if not self.moves:
            return
        
        self.stop_simulation()
        self._sim_stop.clear()
        
        t = self.theme
        
        def run():
            self.delete("sim")
            self.delete("sim_dot")
            
            prev_x = prev_y = 0.0
            dot_id = None
            
            for mv in self.moves:
                if self._sim_stop.is_set():
                    break
                
                wx = mv.x + self.model_x_mm
                wy = mv.y + self.model_y_mm
                
                px0, py0 = self._to_px(prev_x + self.model_x_mm, prev_y + self.model_y_mm)
                px1, py1 = self._to_px(wx, wy)
                
                # Disegna linea
                col = t.laser_on if mv.laser_on else (t.rapid if mv.is_rapid else t.laser_off)
                self.create_line(px0, py0, px1, py1,
                                fill=col, width=2 if mv.laser_on else 1, tags="sim")
                
                # Rimuovi dot precedente
                if dot_id:
                    self.delete(dot_id)
                
                # Disegna nuovo dot
                r = 4 if mv.laser_on else 2
                fc = t.red if mv.laser_on else t.subtext
                dot_id = self.create_oval(px1 - r, py1 - r, px1 + r, py1 + r,
                                         fill=fc, outline=t.text, width=1, tags="sim_dot")
                self.tag_raise("sim_dot")
                
                prev_x, prev_y = mv.x, mv.y
                time.sleep(0.005 / max(speed_mult, 1))
            
            # Cleanup
            if dot_id:
                self.after(0, self.delete, dot_id)
            if done_cb:
                self.after(0, done_cb)
        
        self._sim_thread = threading.Thread(target=run, daemon=True)
        self._sim_thread.start()
    
    def stop_simulation(self):
        """Ferma la simulazione in corso."""
        self._sim_stop.set()
        if self._sim_thread and self._sim_thread.is_alive():
            self._sim_thread.join(timeout=1.0)
        self.delete("sim")
        self.delete("sim_dot")
    
    # ══════════════════════════════════════════════════════════════════════════
    #  BBOX FISICO
    # ══════════════════════════════════════════════════════════════════════════
    def send_bbox_to_laser(self, controller, feed: int = 500, 
                           strings=None, done_cb: Optional[Callable] = None):
        """
        Invia il contorno bbox al laser (laser SPENTO).
        
        Args:
            controller: Istanza LaserController
            feed: Velocità movimento (mm/min)
            strings: Oggetto stringhe
            done_cb: Callback al termine
        """
        if not self.moves:
            return
        
        prog = GCodeProgram()
        prog.moves = self.moves
        mn_x, mn_y, mx_x, mx_y = prog.bounds()
        
        ox, oy = self.model_x_mm, self.model_y_mm
        
        # Comandi per tracciare il rettangolo
        cmds = [
            "M5",  # Laser OFF
            f"F{feed}",
            f"G0 X{mn_x + ox:.3f} Y{mn_y + oy:.3f}",
            f"G1 X{mx_x + ox:.3f} Y{mn_y + oy:.3f}",
            f"G1 X{mx_x + ox:.3f} Y{mx_y + oy:.3f}",
            f"G1 X{mn_x + ox:.3f} Y{mx_y + oy:.3f}",
            f"G1 X{mn_x + ox:.3f} Y{mn_y + oy:.3f}",
            "M5",
        ]
        
        def run():
            for cmd in cmds:
                controller.send_command(cmd)
                time.sleep(0.05)
            if done_cb:
                done_cb()
        
        threading.Thread(target=run, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  VECTOR PREVIEW WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class VectorPreviewWindow(tk.Toplevel):
    """
    Finestra di anteprima vettoriale completa.
    
    Mostra tutti i movimenti GCode con statistiche e legenda.
    """
    
    def __init__(self, parent, moves: List[GCodeMove],
                 work_w: float = 400, work_h: float = 400,
                 theme=None, strings=None, log_cb=None):
        """
        Inizializza la finestra preview.
        
        Args:
            parent: Finestra padre
            moves: Lista movimenti GCode
            work_w: Larghezza area lavoro
            work_h: Altezza area lavoro
            theme: Tema colori
            strings: Stringhe localizzate
            log_cb: Callback log
        """
        super().__init__(parent)
        
        self.theme = theme
        self.s = strings
        t = theme
        
        self.title(strings.preview_title if strings else "Vector Preview")
        self.geometry("840x680")
        self.configure(bg=t.base if t else "#1e1e2e")
        
        frm = tk.Frame(self, bg=t.base if t else "#1e1e2e")
        frm.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Toolbar
        tb = tk.Frame(frm, bg=t.base if t else "#1e1e2e")
        tb.pack(fill="x", pady=(0, 4))
        
        hint = strings.preview_hint if strings else "🔍 Zoom: wheel | 🖱 Pan: right click"
        tk.Label(tb, text=hint, bg=t.base if t else "#1e1e2e",
                fg=t.subtext if t else "#a6adc8",
                font=("Segoe UI", 8)).pack(side="left")
        
        fit_lbl = strings.preview_btn_fit if strings else "⊡ Fit"
        tk.Button(tb, text=fit_lbl,
                 bg=t.surface0 if t else "#313244",
                 fg=t.text if t else "#cdd6f4",
                 relief="flat",
                 command=lambda: canvas.fit()).pack(side="right")
        
        # Statistiche
        laser_on = sum(1 for m in moves if m.laser_on)
        laser_off = len(moves) - laser_on
        
        if strings:
            stats = strings.preview_stats.format(total=len(moves), on=laser_on, off=laser_off)
        else:
            stats = f"Total: {len(moves)} | ON: {laser_on} | OFF: {laser_off}"
        
        tk.Label(frm, text=stats,
                bg=t.base if t else "#1e1e2e",
                fg=t.teal if t else "#94e2d5",
                font=("Consolas", 8)).pack(anchor="w")
        
        # Canvas principale
        canvas = WorkAreaCanvas(frm, work_w=work_w, work_h=work_h,
                               theme=theme, strings=strings, log_cb=log_cb)
        canvas.pack(fill="both", expand=True)
        canvas.set_program(moves)
        self.after(100, canvas.fit)
        
        # Legenda
        leg = tk.Frame(self, bg=t.mantle if t else "#181825")
        leg.pack(fill="x")
        
        items = [
            (strings.legend_laser_on if strings else "━━ Laser ON", 
             t.laser_on if t else "#f38ba8"),
            (strings.legend_rapid if strings else "╌╌ Rapid", 
             t.rapid if t else "#6c7086"),
            (strings.legend_bbox if strings else "□  BBox", 
             t.bbox if t else "#f9e2af"),
            (strings.legend_origin if strings else "⊕  Origin", 
             t.home if t else "#a6e3a1"),
        ]
        
        for lbl, col in items:
            tk.Label(leg, text=f" {lbl} ",
                    bg=t.mantle if t else "#181825",
                    fg=col,
                    font=("Consolas", 8)).pack(side="left", padx=4, pady=4)


# ══════════════════════════════════════════════════════════════════════════════
#  TEST / DEMO
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    """Test standalone del modulo canvas."""
    
    print("=== Test Canvas Widgets ===\n")
    
    # Crea dati di test
    test_moves = [
        GCodeMove(0, 0, False, True),
        GCodeMove(10, 0, False, True),
        GCodeMove(10, 0, True, False),
        GCodeMove(50, 0, True, False),
        GCodeMove(50, 50, True, False),
        GCodeMove(10, 50, True, False),
        GCodeMove(10, 0, True, False),
        GCodeMove(10, 0, False, False),
    ]
    
    # Crea finestra test
    root = tk.Tk()
    root.title("Canvas Test")
    root.geometry("800x600")
    
    # Mock theme
    class MockTheme:
        base = "#1e1e2e"
        mantle = "#181825"
        surface0 = "#313244"
        surface1 = "#45475a"
        text = "#cdd6f4"
        subtext = "#a6adc8"
        blue = "#89b4fa"
        green = "#a6e3a1"
        red = "#f38ba8"
        yellow = "#f9e2af"
        teal = "#94e2d5"
        canvas_bg = "#11111b"
        canvas_grid = "#313244"
        laser_on = "#f38ba8"
        laser_off = "#45475a"
        rapid = "#6c7086"
        bbox = "#f9e2af"
        home = "#a6e3a1"
    
    theme = MockTheme()
    
    # Crea canvas
    canvas = WorkAreaCanvas(root, work_w=100, work_h=100, theme=theme)
    canvas.pack(fill="both", expand=True)
    canvas.set_program(test_moves)
    
    # Toolbar
    toolbar = tk.Frame(root, bg=theme.base)
    toolbar.pack(fill="x")
    
    tk.Button(toolbar, text="Fit View", command=canvas.fit,
             bg=theme.surface0, fg=theme.text).pack(side="left", padx=5, pady=5)
    
    tk.Button(toolbar, text="Start Sim", 
             command=lambda: canvas.start_simulation(speed_mult=5),
             bg=theme.green, fg=theme.base).pack(side="left", padx=5)
    
    tk.Button(toolbar, text="Stop Sim", command=canvas.stop_simulation,
             bg=theme.red, fg=theme.base).pack(side="left", padx=5)
    
    print("Canvas di test avviato")
    print("- Trascina: muovi modello")
    print("- Rotella: zoom")
    print("- Tasto destro: pan")
    
    root.mainloop()