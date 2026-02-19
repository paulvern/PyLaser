#!/usr/bin/env python3
"""
PyLaser  v0.9 - main.py
Applicazione principale con supporto multilingua, temi e help integrato.

Requires:
    - strings.py      (stringhe localizzate)
    - themes.py       (definizione temi)
    - help_content.py (contenuto help)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import math
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable

# ══════════════════════════════════════════════════════════════════════════════
#  IMPORTA MODULI LOCALI
# ══════════════════════════════════════════════════════════════════════════════
try:
    from strings import (
        get_strings, available_languages,
        DEFAULT_LANGUAGE, Strings
    )
except ImportError:
    print("ERRORE: strings.py non trovato!")
    sys.exit(1)

try:
    from themes import (
        get_theme, available_themes,
        DEFAULT_THEME, Theme, is_dark_theme
    )
except ImportError:
    print("ERRORE: themes.py non trovato!")
    sys.exit(1)

try:
    from help_content import get_help, HelpContent
except ImportError:
    print("ERRORE: help_content.py non trovato!")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
#  DIPENDENZE ESTERNE
# ══════════════════════════════════════════════════════════════════════════════
try:
    from PIL import Image, ImageTk, ImageFilter, ImageOps
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

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  COSTANTI
# ══════════════════════════════════════════════════════════════════════════════
APP_VERSION = "0.9"
BAUDRATES   = [9600, 19200, 38400, 57600, 115200, 250000]
CONFIG_FILE = Path(__file__).parent / ".engraver_config.json"


# ══════════════════════════════════════════════════════════════════════════════
#  GESTIONE CONFIGURAZIONE
# ══════════════════════════════════════════════════════════════════════════════
def load_config() -> dict:
    """Carica la configurazione salvata."""
    defaults = {
        "language": DEFAULT_LANGUAGE,
        "theme": DEFAULT_THEME,
        "work_area_w": 400.0,
        "work_area_h": 400.0,
        "last_port": "",
        "last_baud": 115200,
        "feed_rate": 1000,
        "power": 200,
    }
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text())
            defaults.update(data)
    except Exception:
        pass
    return defaults


def save_config(config: dict):
    """Salva la configurazione."""
    try:
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  STRUTTURE DATI GCODE
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class GCodeMove:
    x: float = 0.0
    y: float = 0.0
    laser_on: bool = False
    is_rapid: bool = False


@dataclass
class GCodeProgram:
    moves     : list[GCodeMove] = field(default_factory=list)
    raw_lines : list[str]       = field(default_factory=list)
    width_mm  : float = 0.0
    height_mm : float = 0.0
    offset_x  : float = 0.0
    offset_y  : float = 0.0

    def bounds(self):
        if not self.moves:
            return 0, 0, 0, 0
        xs = [m.x for m in self.moves]
        ys = [m.y for m in self.moves]
        return min(xs), min(ys), max(xs), max(ys)

    def translated_lines(self) -> list[str]:
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


def _replace_coord(line: str, axis: str, offset: float) -> str:
    import re
    pattern = rf"({axis})([-+]?\d*\.?\d+)"
    def replacer(m):
        val = float(m.group(2)) + offset
        return f"{axis}{val:.3f}"
    return re.sub(pattern, replacer, line, flags=re.IGNORECASE)


# ══════════════════════════════════════════════════════════════════════════════
#  PARSER GCODE
# ══════════════════════════════════════════════════════════════════════════════
class GCodeParser:
    @staticmethod
    def parse(lines: list[str]) -> list[GCodeMove]:
        import re
        moves    = []
        cur_x    = cur_y = 0.0
        laser_on = False
        mode_g   = 0

        for line in lines:
            line = line.strip().upper()
            if not line or line.startswith(";"): continue
            if ";" in line:
                line = line[:line.index(";")]
            if "M3" in line: laser_on = True
            if "M5" in line: laser_on = False
            if re.search(r"\bG0\b", line): mode_g = 0
            if re.search(r"\bG1\b", line): mode_g = 1
            mx = re.search(r"X([-+]?\d*\.?\d+)", line)
            my = re.search(r"Y([-+]?\d*\.?\d+)", line)
            if mx or my:
                new_x = float(mx.group(1)) if mx else cur_x
                new_y = float(my.group(1)) if my else cur_y
                moves.append(GCodeMove(
                    x=new_x, y=new_y,
                    laser_on=laser_on,
                    is_rapid=(mode_g == 0),
                ))
                cur_x, cur_y = new_x, new_y
        return moves


# ══════════════════════════════════════════════════════════════════════════════
#  VETTORIZZATORE
# ══════════════════════════════════════════════════════════════════════════════
class Vectorizer:
    def __init__(self, log_cb=None):
        self.log = log_cb or print
        self._s  = None

    def set_strings(self, s: Strings):
        self._s = s

    def preprocess(self, pil_image, threshold=128,
                   blur_radius=2, invert=False, denoise=False):
        img = np.array(pil_image.convert("L"))
        if denoise and CV2_AVAILABLE:
            img = cv2.fastNlMeansDenoising(img, h=10)
        if blur_radius > 0 and CV2_AVAILABLE:
            k = blur_radius * 2 + 1
            img = cv2.GaussianBlur(img, (k, k), 0)
        if CV2_AVAILABLE:
            _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        else:
            binary = np.where(img > threshold, np.uint8(255), np.uint8(0))
        if invert:
            binary = (255 - binary).astype(np.uint8)
        return binary

    def contour_paths(self, binary, w_mm, h_mm, simplify=1.0):
        if not CV2_AVAILABLE: return []
        h_px, w_px = binary.shape
        sx, sy = w_mm / w_px, h_mm / h_px
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        lines = []
        for cnt in contours:
            if len(cnt) < 2: continue
            eps = simplify * cv2.arcLength(cnt, True) / max(len(cnt), 1)
            cnt = cv2.approxPolyDP(cnt, eps, closed=True)
            pts = cnt.reshape(-1, 2)
            x0, y0 = pts[0,0]*sx, (h_px - pts[0,1])*sy
            lines += [f"G0 X{x0:.3f} Y{y0:.3f}", "M3 S{lp}"]
            for pt in pts[1:]:
                lines.append(f"G1 X{pt[0]*sx:.3f} Y{(h_px-pt[1])*sy:.3f}")
            lines += [f"G1 X{x0:.3f} Y{y0:.3f}", "M5"]
        if self._s:
            self.log(self._s.log_contours_found.format(n=len(contours)))
        return lines

    def raster_paths(self, binary, w_mm, h_mm, gap_mm=0.1):
        h_px, w_px = binary.shape
        cols = max(1, int(w_mm / max(gap_mm, 0.01)))
        rows = max(1, int(h_mm / max(gap_mm, 0.01)))
        img  = cv2.resize(binary, (cols, rows),
                           interpolation=cv2.INTER_AREA) \
               if CV2_AVAILABLE else binary
        sx, sy = w_mm / cols, h_mm / rows
        lines  = []
        for r in range(rows):
            y     = r * sy
            rng   = range(cols) if r % 2 == 0 else range(cols-1, -1, -1)
            laser = False
            for c in rng:
                on = img[r, c] > 127
                x  = c * sx
                if on and not laser:
                    lines += [f"G0 X{x:.3f} Y{y:.3f}", "M3 S{lp}"]
                    laser = True
                elif not on and laser:
                    lines += [f"G1 X{x:.3f} Y{y:.3f}", "M5"]
                    laser = False
                elif on:
                    lines.append(f"G1 X{x:.3f} Y{y:.3f}")
            if laser:
                lines.append("M5")
        return lines

    def centerline_paths(self, binary, w_mm, h_mm):
        if not CV2_AVAILABLE: return []
        try:
            skel = cv2.ximgproc.thinning(binary)
        except AttributeError:
            skel = self._morph_skeleton(binary)
        h_px, w_px = skel.shape
        sx, sy = w_mm / w_px, h_mm / h_px
        return self._trace_skel(skel, sx, sy, h_px)

    def _morph_skeleton(self, binary):
        img  = binary.copy()
        skel = np.zeros_like(img)
        kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        while True:
            er   = cv2.erode(img, kern)
            temp = cv2.subtract(img, cv2.dilate(er, kern))
            skel = cv2.bitwise_or(skel, temp)
            img  = er
            if cv2.countNonZero(img) == 0: break
        return skel

    def _trace_skel(self, skel, sx, sy, h_px):
        visited = np.zeros(skel.shape, bool)
        lines   = []
        ys, xs  = np.where(skel > 0)

        def nb(x, y):
            res = []
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx == 0 and dy == 0: continue
                    nx, ny = x+dx, y+dy
                    if (0 <= nx < skel.shape[1] and
                            0 <= ny < skel.shape[0] and
                            skel[ny,nx] > 0 and
                            not visited[ny,nx]):
                        res.append((nx,ny))
            return res

        for (x0,y0) in zip(xs.tolist(), ys.tolist()):
            if visited[y0,x0]: continue
            cx, cy = x0, y0
            first  = True
            while True:
                if visited[cy,cx]: break
                visited[cy,cx] = True
                gx = cx * sx
                gy = (h_px - cy) * sy
                if first:
                    lines += [f"G0 X{gx:.3f} Y{gy:.3f}", "M3 S{lp}"]
                    first = False
                else:
                    lines.append(f"G1 X{gx:.3f} Y{gy:.3f}")
                n = nb(cx, cy)
                if not n: break
                cx, cy = n[0]
            if not first:
                lines.append("M5")
        return lines

    def hatch_paths(self, binary, w_mm, h_mm, angle=45.0, gap_mm=0.2):
        if not CV2_AVAILABLE:
            return self.raster_paths(binary, w_mm, h_mm, gap_mm)
        h_px, w_px = binary.shape
        sx, sy  = w_mm / w_px, h_mm / h_px
        rad     = math.radians(angle)
        ca, sa  = math.cos(rad), math.sin(rad)
        gap_px  = max(1, int(gap_mm / min(sx, sy)))
        ys, xs  = np.where(binary > 127)
        if not len(xs): return []
        proj    = (xs*(-sa) + ys*ca).astype(int)
        lines   = []
        for band in range(proj.min(), proj.max()+gap_px, gap_px):
            mask    = (proj >= band) & (proj < band+gap_px)
            bx, by  = xs[mask], ys[mask]
            if not len(bx): continue
            order   = np.argsort(bx*ca + by*sa)
            bx, by  = bx[order], by[order]
            x0, y0  = bx[0]*sx, (h_px-by[0])*sy
            lines  += [f"G0 X{x0:.3f} Y{y0:.3f}", "M3 S{lp}"]
            for i in range(1, len(bx)):
                lines.append(f"G1 X{bx[i]*sx:.3f} Y{(h_px-by[i])*sy:.3f}")
            lines.append("M5")
        return lines


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATORE GCODE
# ══════════════════════════════════════════════════════════════════════════════
class GCodeGenerator:
    def __init__(self, feed=1000, power=200, passes=1):
        self.feed   = feed
        self.power  = power
        self.passes = passes

    def build(self, path_lines, offset_x=0.0, offset_y=0.0) -> GCodeProgram:
        resolved = [l.replace("{lp}", str(self.power)) for l in path_lines]
        raw = [
            f"; PyLaser v{APP_VERSION}",
            f"; Feed:{self.feed}  Power:{self.power}  Passes:{self.passes}",
            f"; OffsetX:{offset_x:.3f}  OffsetY:{offset_y:.3f}",
            "G21", "G90", "G92 X0 Y0", f"F{self.feed}", "M5", "",
        ]
        for _ in range(self.passes):
            raw.extend(resolved)
        raw += ["", "M5", "G0 X0 Y0", "M2"]

        prog           = GCodeProgram()
        prog.raw_lines = raw
        prog.moves     = GCodeParser.parse(raw)
        prog.offset_x  = offset_x
        prog.offset_y  = offset_y
        if prog.moves:
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            prog.width_mm  = mx_x - mn_x
            prog.height_mm = mx_y - mn_y
        return prog


# ══════════════════════════════════════════════════════════════════════════════
#  CONTROLLER SERIALE
# ══════════════════════════════════════════════════════════════════════════════
class LaserController:
    def __init__(self, log_cb=None):
        self.log         = log_cb or print
        self.ser         = None
        self._simulating = False

    @staticmethod
    def list_ports():
        if not SERIAL_AVAILABLE:
            return ["(simulated)"]
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports or ["(none)"]

    def connect(self, port, baud, s: Strings) -> bool:
        if self._simulating:
            self.log(s.log_simulation_on)
            return True
        if not SERIAL_AVAILABLE:
            return False
        try:
            self.ser = serial.Serial(
                port=port, baudrate=baud, timeout=5, write_timeout=5)
            time.sleep(2)
            self.ser.reset_input_buffer()
            greet = self.ser.read_all().decode(errors="ignore").strip()
            self.log(s.log_connected.format(port=port, baud=baud))
            if greet:
                self.log(s.log_fw.format(fw=greet[:80]))
            return True
        except Exception as e:
            self.log(s.log_connect_error.format(err=e))
            self.ser = None
            return False

    def disconnect(self, s: Strings):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.log(s.log_disconnected)

    def is_connected(self):
        return self._simulating or (self.ser is not None and self.ser.is_open)

    def send_command(self, cmd: str, s: Optional[Strings] = None) -> str:
        cmd = cmd.strip()
        if not cmd or cmd.startswith(";"): return "ok"
        if self._simulating:
            time.sleep(0.001)
            return "ok"
        try:
            self.ser.write((cmd + "\n").encode())
            resp = self.ser.readline().decode(errors="ignore").strip()
            while resp and not any(
                    resp.startswith(k) for k in ("ok","error","ALARM")):
                resp = self.ser.readline().decode(errors="ignore").strip()
            return resp
        except Exception as e:
            if s: self.log(s.log_tx_error.format(err=e))
            return "error"

    def send_gcode(self, lines, progress_cb=None,
                   stop_event=None, s: Optional[Strings] = None) -> bool:
        stop   = stop_event or threading.Event()
        total  = len(lines)
        errors = 0
        for i, line in enumerate(lines):
            if stop.is_set():
                self.send_command("M5")
                if s: self.log(s.log_send_stopped)
                return False
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                if progress_cb: progress_cb(i+1, total)
                continue
            resp = self.send_command(stripped, s)
            if "error" in resp.lower():
                errors += 1
            elif "alarm" in resp.lower():
                if s: self.log(s.log_alarm.format(resp=resp))
                self.send_command("M5")
                return False
            if progress_cb: progress_cb(i+1, total)
        if s: self.log(s.log_engraving_done.format(errors=errors))
        return errors == 0

    def emergency_stop(self, s: Strings):
        if self.ser and self.ser.is_open:
            self.ser.write(b"\x18")
        self.log(s.log_emergency)

    def home(self):         self.send_command("$H")
    def unlock(self):       self.send_command("$X")
    def get_status(self):   return self.send_command("?")

    def set_home(self, s: Strings):
        self.send_command("G92 X0 Y0")
        self.log(s.log_home_set)

    def jog(self, axis, dist, feed):
        self.send_command("G91")
        self.send_command(f"G0 {axis}{dist:.3f} F{feed}")
        self.send_command("G90")


# ══════════════════════════════════════════════════════════════════════════════
#  CANVAS AREA DI LAVORO
# ══════════════════════════════════════════════════════════════════════════════
class WorkAreaCanvas(tk.Canvas):
    def __init__(self, parent, work_w=400, work_h=400,
                 theme: Theme = None, s: Strings = None,
                 log_cb=None, **kwargs):
        self.theme = theme or get_theme()
        super().__init__(parent, bg=self.theme.canvas_bg,
                          highlightthickness=0, **kwargs)
        self.log        = log_cb or print
        self.s          = s
        self.work_w_mm  = work_w
        self.work_h_mm  = work_h
        self.moves      : list[GCodeMove] = []
        self.model_x_mm = 0.0
        self.model_y_mm = 0.0
        self._scale     = 1.0
        self._pan_x     = 0.0
        self._pan_y     = 0.0
        self._drag_start       = None
        self._drag_model_start = None
        self._pan_start        = None
        self._sim_thread       = None
        self._sim_stop         = threading.Event()
        self._pos_cb           = None

        self.bind("<Configure>",       self._on_resize)
        self.bind("<ButtonPress-1>",   self._on_lb_down)
        self.bind("<B1-Motion>",       self._on_lb_move)
        self.bind("<ButtonRelease-1>", self._on_lb_up)
        self.bind("<ButtonPress-3>",   self._on_rb_down)
        self.bind("<B3-Motion>",       self._on_rb_move)
        self.bind("<ButtonPress-2>",   self._on_rb_down)
        self.bind("<B2-Motion>",       self._on_rb_move)
        self.bind("<MouseWheel>",      self._on_wheel)
        self.bind("<Button-4>",        self._on_wheel)
        self.bind("<Button-5>",        self._on_wheel)

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.configure(bg=theme.canvas_bg)
        self._redraw()

    def set_strings(self, s: Strings):
        self.s = s

    def _to_px(self, mm_x, mm_y):
        px = self._pan_x + mm_x * self._scale
        py = self._pan_y + (self.work_h_mm - mm_y) * self._scale
        return px, py

    def _to_mm(self, px, py):
        mm_x = (px - self._pan_x) / self._scale
        mm_y = self.work_h_mm - (py - self._pan_y) / self._scale
        return mm_x, mm_y

    def _fit_view(self):
        self.update_idletasks()
        cw, ch = self.winfo_width(), self.winfo_height()
        if cw < 10 or ch < 10: return
        margin = 30
        sx = (cw - 2*margin) / self.work_w_mm
        sy = (ch - 2*margin) / self.work_h_mm
        self._scale = min(sx, sy)
        self._pan_x = margin
        self._pan_y = margin
        self._redraw()

    def _redraw(self):
        self.delete("all")
        t = self.theme
        self._draw_grid(t)
        self._draw_work_area(t)
        self._draw_origin(t)
        self._draw_paths(t)
        self._draw_bbox(t)

    def _draw_grid(self, t: Theme):
        cw, ch = self.winfo_width(), self.winfo_height()
        x = 0.0
        while x <= self.work_w_mm + 10:
            px, _ = self._to_px(x, 0)
            col = t.surface1 if x % 50 == 0 else t.canvas_grid
            self.create_line(px, 0, px, ch, fill=col, width=1)
            if x % 50 == 0 and 0 < px < cw:
                self.create_text(px+2, ch-14, text=f"{int(x)}",
                                  fill=t.subtext, font=("Consolas",7), anchor="w")
            x += 10
        y = 0.0
        while y <= self.work_h_mm + 10:
            _, py = self._to_px(0, y)
            col = t.surface1 if y % 50 == 0 else t.canvas_grid
            self.create_line(0, py, cw, py, fill=col, width=1)
            if y % 50 == 0 and 0 < py < ch:
                self.create_text(4, py-2, text=f"{int(y)}",
                                  fill=t.subtext, font=("Consolas",7), anchor="w")
            y += 10

    def _draw_work_area(self, t: Theme):
        x0, y0 = self._to_px(0, 0)
        x1, y1 = self._to_px(self.work_w_mm, self.work_h_mm)
        # Ombra
        if is_dark_theme(t):
            self.create_rectangle(x0+4, y1+4, x1+4, y0+4,
                                   fill="#000000", outline="")
        self.create_rectangle(x0, y1, x1, y0,
                               fill=t.base,
                               outline=t.surface1, width=2)
        label = (self.s.canvas_area_label.format(
                     w=self.work_w_mm, h=self.work_h_mm)
                 if self.s else
                 f"Area: {self.work_w_mm}×{self.work_h_mm} mm")
        self.create_text(x0+4, y0+4, text=label,
                          fill=t.subtext,
                          font=("Consolas",8), anchor="nw")

    def _draw_origin(self, t: Theme):
        ox, oy = self._to_px(0, 0)
        r = 6
        self.create_line(ox-r, oy, ox+r, oy, fill=t.home, width=2)
        self.create_line(ox, oy-r, ox, oy+r, fill=t.home, width=2)
        self.create_oval(ox-r, oy-r, ox+r, oy+r, outline=t.home, width=2)
        label = (self.s.canvas_home_label if self.s else "HOME")
        self.create_text(ox+10, oy-10, text=label,
                          fill=t.home, font=("Consolas",8,"bold"))

    def _draw_paths(self, t: Theme):
        if not self.moves: return
        prev_x = prev_y = 0.0
        for mv in self.moves:
            wx = mv.x + self.model_x_mm
            wy = mv.y + self.model_y_mm
            px0, py0 = self._to_px(prev_x+self.model_x_mm, prev_y+self.model_y_mm)
            px1, py1 = self._to_px(wx, wy)
            if mv.is_rapid:
                col, dash, w = t.rapid, (3,4), 1
            elif mv.laser_on:
                col, dash, w = t.laser_on, (), 1
            else:
                col, dash, w = t.laser_off, (2,3), 1
            self.create_line(px0, py0, px1, py1,
                              fill=col, width=w, dash=dash, tags="path")
            prev_x, prev_y = mv.x, mv.y

    def _draw_bbox(self, t: Theme):
        if not self.moves: return
        prog = GCodeProgram(moves=self.moves)
        mn_x, mn_y, mx_x, mx_y = prog.bounds()
        x0 = mn_x + self.model_x_mm
        y0 = mn_y + self.model_y_mm
        x1 = mx_x + self.model_x_mm
        y1 = mx_y + self.model_y_mm
        px0, py0 = self._to_px(x0, y0)
        px1, py1 = self._to_px(x1, y1)
        # Sfondo semitrasparente
        bbox_fill = t.bbox + "22"
        self.create_rectangle(px0, py1, px1, py0,
                               outline=t.bbox, fill=bbox_fill,
                               width=2, dash=(6,3), tags="bbox")
        w_mm, h_mm = mx_x - mn_x, mx_y - mn_y
        self.create_text((px0+px1)//2, py1-10,
                          text=f"{w_mm:.1f} × {h_mm:.1f} mm",
                          fill=t.bbox, font=("Consolas",8,"bold"), tags="bbox")
        for (ax,ay) in [(px0,py0),(px1,py0),(px0,py1),(px1,py1)]:
            self.create_rectangle(ax-3,ay-3,ax+3,ay+3,
                                   fill=t.bbox, outline="", tags="bbox")

    # Interazione
    def _on_resize(self, _): self.after(50, self._fit_view)

    def _on_lb_down(self, e):
        self._drag_start = (e.x, e.y)
        self._drag_model_start = (self.model_x_mm, self.model_y_mm)

    def _on_lb_move(self, e):
        if not self._drag_start: return
        dx_mm = (e.x - self._drag_start[0]) / self._scale
        dy_mm = -(e.y - self._drag_start[1]) / self._scale
        nx = self._drag_model_start[0] + dx_mm
        ny = self._drag_model_start[1] + dy_mm
        if self.moves:
            prog = GCodeProgram(moves=self.moves)
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            nx = max(-mn_x, min(nx, self.work_w_mm-(mx_x-mn_x)-mn_x))
            ny = max(-mn_y, min(ny, self.work_h_mm-(mx_y-mn_y)-mn_y))
        self.model_x_mm, self.model_y_mm = nx, ny
        self._redraw()

    def _on_lb_up(self, _):
        self._drag_start = None
        if self._pos_cb:
            self._pos_cb(self.model_x_mm, self.model_y_mm)

    def _on_rb_down(self, e):
        self._pan_start = (e.x, e.y, self._pan_x, self._pan_y)

    def _on_rb_move(self, e):
        if not self._pan_start: return
        sx, sy, px0, py0 = self._pan_start
        self._pan_x = px0 + (e.x - sx)
        self._pan_y = py0 + (e.y - sy)
        self._redraw()

    def _on_wheel(self, e):
        factor = 1.1 if (e.num == 4 or e.delta > 0) else 0.9
        mx, my = self._to_mm(e.x, e.y)
        self._scale *= factor
        self._pan_x = e.x - mx * self._scale
        self._pan_y = e.y - (self.work_h_mm - my) * self._scale
        self._redraw()

    # API
    def set_work_area(self, w_mm, h_mm):
        self.work_w_mm, self.work_h_mm = w_mm, h_mm
        self._fit_view()

    def set_program(self, moves):
        self.moves = moves
        self._fit_view()

    def set_model_position(self, x_mm, y_mm):
        self.model_x_mm, self.model_y_mm = x_mm, y_mm
        self._redraw()

    def set_position_callback(self, cb): self._pos_cb = cb
    def fit(self): self._fit_view()

    def start_simulation(self, speed_mult=10, done_cb=None):
        if not self.moves: return
        self.stop_simulation()
        self._sim_stop.clear()
        t = self.theme

        def _run():
            self.delete("sim")
            prev_x = prev_y = 0.0
            dot_id = None
            for mv in self.moves:
                if self._sim_stop.is_set(): break
                wx = mv.x + self.model_x_mm
                wy = mv.y + self.model_y_mm
                px0,py0 = self._to_px(prev_x+self.model_x_mm, prev_y+self.model_y_mm)
                px1,py1 = self._to_px(wx, wy)
                col = t.laser_on if mv.laser_on else (t.rapid if mv.is_rapid else t.laser_off)
                self.create_line(px0,py0,px1,py1,
                                  fill=col, width=2 if mv.laser_on else 1, tags="sim")
                if dot_id: self.delete(dot_id)
                r  = 4 if mv.laser_on else 2
                fc = t.red if mv.laser_on else t.subtext
                dot_id = self.create_oval(px1-r,py1-r,px1+r,py1+r,
                                           fill=fc, outline=t.text, width=1, tags="sim_dot")
                self.tag_raise("sim_dot")
                prev_x, prev_y = mv.x, mv.y
                time.sleep(0.005 / max(speed_mult, 1))
            if dot_id: self.after(0, self.delete, dot_id)
            if done_cb: self.after(0, done_cb)

        self._sim_thread = threading.Thread(target=_run, daemon=True)
        self._sim_thread.start()

    def stop_simulation(self):
        self._sim_stop.set()
        if self._sim_thread and self._sim_thread.is_alive():
            self._sim_thread.join(timeout=1.0)
        self.delete("sim")
        self.delete("sim_dot")

    def send_bbox_to_laser(self, controller, feed=500, s=None, done_cb=None):
        if not self.moves: return
        prog = GCodeProgram(moves=self.moves)
        mn_x, mn_y, mx_x, mx_y = prog.bounds()
        ox, oy = self.model_x_mm, self.model_y_mm
        cmds = [
            "M5", f"F{feed}",
            f"G0 X{mn_x+ox:.3f} Y{mn_y+oy:.3f}",
            f"G1 X{mx_x+ox:.3f} Y{mn_y+oy:.3f}",
            f"G1 X{mx_x+ox:.3f} Y{mx_y+oy:.3f}",
            f"G1 X{mn_x+ox:.3f} Y{mx_y+oy:.3f}",
            f"G1 X{mn_x+ox:.3f} Y{mn_y+oy:.3f}",
            "M5",
        ]
        def _run():
            for cmd in cmds:
                controller.send_command(cmd)
                time.sleep(0.05)
            if done_cb: done_cb()
        threading.Thread(target=_run, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  FINESTRA ANTEPRIMA VETTORIALE
# ══════════════════════════════════════════════════════════════════════════════
class VectorPreviewWindow(tk.Toplevel):
    def __init__(self, parent, moves, work_w=400, work_h=400,
                 theme: Theme = None, s: Strings = None, log_cb=None):
        super().__init__(parent)
        self.theme = theme or get_theme()
        self.s     = s
        t = self.theme

        self.title(s.preview_title if s else "Vector Preview")
        self.geometry("840x680")
        self.configure(bg=t.base)

        frm = tk.Frame(self, bg=t.base)
        frm.pack(fill="both", expand=True, padx=6, pady=6)

        # Toolbar
        tb = tk.Frame(frm, bg=t.base)
        tb.pack(fill="x", pady=(0,4))
        hint = s.preview_hint if s else ""
        tk.Label(tb, text=hint, bg=t.base, fg=t.subtext,
                  font=("Segoe UI",8)).pack(side="left")
        fit_lbl = s.preview_btn_fit if s else "⊡ Fit"
        tk.Button(tb, text=fit_lbl, bg=t.surface0, fg=t.text,
                   relief="flat", command=lambda: canvas.fit()
                   ).pack(side="right")

        # Stats
        laser_on  = sum(1 for m in moves if m.laser_on)
        laser_off = len(moves) - laser_on
        stats = (s.preview_stats.format(total=len(moves), on=laser_on, off=laser_off)
                 if s else f"Total: {len(moves)} | ON: {laser_on} | OFF: {laser_off}")
        tk.Label(frm, text=stats, bg=t.base, fg=t.teal,
                  font=("Consolas",8)).pack(anchor="w")

        # Canvas
        canvas = WorkAreaCanvas(frm, work_w=work_w, work_h=work_h,
                                 theme=t, s=s, log_cb=log_cb)
        canvas.pack(fill="both", expand=True)
        canvas.set_program(moves)
        self.after(100, canvas.fit)

        # Legenda
        leg = tk.Frame(self, bg=t.mantle)
        leg.pack(fill="x")
        items = [
            (s.legend_laser_on if s else "━━ Laser ON",  t.laser_on),
            (s.legend_rapid    if s else "╌╌ Rapid",     t.rapid),
            (s.legend_bbox     if s else "□  BBox",      t.bbox),
            (s.legend_origin   if s else "⊕  Origin",    t.home),
        ]
        for lbl, col in items:
            tk.Label(leg, text=f" {lbl} ", bg=t.mantle, fg=col,
                      font=("Consolas",8)).pack(side="left", padx=4, pady=4)


# ══════════════════════════════════════════════════════════════════════════════
#  FINESTRA HELP
# ══════════════════════════════════════════════════════════════════════════════
class HelpWindow(tk.Toplevel):
    def __init__(self, parent, theme: Theme, help_content: HelpContent):
        super().__init__(parent)
        t = self.theme = theme
        h = self.help  = help_content

        self.title(h.title_main)
        self.geometry("900x700")
        self.minsize(700, 500)
        self.configure(bg=t.base)

        # Pannello principale
        main_paned = tk.PanedWindow(self, orient="horizontal",
                                     bg=t.base, sashwidth=4)
        main_paned.pack(fill="both", expand=True, padx=6, pady=6)

        # Sidebar (indice)
        sidebar = tk.Frame(main_paned, bg=t.mantle)
        main_paned.add(sidebar, minsize=200)

        tk.Label(sidebar, text="📚 " + h.title_main,
                  bg=t.mantle, fg=t.blue,
                  font=("Segoe UI", 11, "bold")).pack(padx=8, pady=(12,8))

        # Sezioni
        self.sections = [
            (h.title_getting_started, h.getting_started),
            (h.title_image,           h.image_section),
            (h.title_vectorize,       h.vectorize_section),
            (h.title_position,        h.position_section),
            (h.title_laser,           h.laser_section),
            (h.title_simulation,      h.simulation_section),
            (h.title_shortcuts,       h.shortcuts_section),
            (h.title_gcode,           h.gcode_section),
            (h.title_troubleshooting, h.troubleshooting),
            (h.title_safety,          h.safety_section),
        ]

        self.section_btns = []
        for title, content in self.sections:
            btn = tk.Button(
                sidebar, text=title,
                bg=t.surface0, fg=t.text,
                activebackground=t.blue,
                activeforeground=t.base,
                relief="flat", anchor="w",
                padx=12, pady=6,
                font=("Segoe UI", 9),
                command=lambda c=content, ti=title: self._show_section(ti, c)
            )
            btn.pack(fill="x", padx=4, pady=1)
            self.section_btns.append(btn)

        # Contenuto
        content_frame = tk.Frame(main_paned, bg=t.base)
        main_paned.add(content_frame, minsize=450)

        self.content_title = tk.Label(
            content_frame, text=h.title_getting_started,
            bg=t.base, fg=t.blue,
            font=("Segoe UI", 12, "bold"))
        self.content_title.pack(anchor="w", padx=8, pady=(8,4))

        self.content_text = scrolledtext.ScrolledText(
            content_frame,
            bg=t.surface0, fg=t.text,
            font=("Consolas", 9),
            wrap="word", borderwidth=0,
            insertbackground=t.text,
            selectbackground=t.blue,
            selectforeground=t.base,
        )
        self.content_text.pack(fill="both", expand=True, padx=4, pady=4)

        # Mostra prima sezione
        self._show_section(h.title_getting_started, h.getting_started)

        # Footer
        footer = tk.Frame(self, bg=t.mantle)
        footer.pack(fill="x")
        tk.Label(footer,
                  text=f"Py Laser{APP_VERSION}",
                  bg=t.mantle, fg=t.subtext,
                  font=("Segoe UI", 8)).pack(side="left", padx=8, pady=6)
        tk.Button(footer, text="✕ Close", bg=t.surface0, fg=t.text,
                   relief="flat", padx=12,
                   command=self.destroy).pack(side="right", padx=8, pady=4)

    def _show_section(self, title: str, content: str):
        self.content_title.config(text=title)
        self.content_text.config(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", content)
        self.content_text.config(state="disabled")
        self.content_text.see("1.0")


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOGO PREFERENZE (Lingua + Tema)
# ══════════════════════════════════════════════════════════════════════════════
class PreferencesDialog(tk.Toplevel):
    def __init__(self, parent, current_lang: str, current_theme: str,
                 theme: Theme):
        super().__init__(parent)
        t = self.theme = theme

        self.result_lang  = current_lang
        self.result_theme = current_theme

        self.title("⚙ Preferences / Preferenze / Einstellungen")
        self.resizable(False, False)
        self.configure(bg=t.base)
        self.grab_set()

        # Lingua
        lf1 = tk.LabelFrame(self, text="🌐 Language / Lingua",
                             bg=t.base, fg=t.blue,
                             font=("Segoe UI", 10, "bold"))
        lf1.pack(fill="x", padx=16, pady=(16,8))

        self.lang_var = tk.StringVar(value=current_lang)
        for lang in available_languages():
            tk.Radiobutton(
                lf1, text=lang, variable=self.lang_var, value=lang,
                bg=t.base, fg=t.text, selectcolor=t.surface0,
                activebackground=t.base, activeforeground=t.blue,
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=8, pady=2)

        # Tema
        lf2 = tk.LabelFrame(self, text="🎨 Theme / Tema",
                             bg=t.base, fg=t.blue,
                             font=("Segoe UI", 10, "bold"))
        lf2.pack(fill="x", padx=16, pady=8)

        self.theme_var = tk.StringVar(value=current_theme)
        for theme_name in available_themes():
            tk.Radiobutton(
                lf2, text=theme_name, variable=self.theme_var, value=theme_name,
                bg=t.base, fg=t.text, selectcolor=t.surface0,
                activebackground=t.base, activeforeground=t.blue,
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=8, pady=2)

        # Nota riavvio
        tk.Label(self,
                  text="⚠ Changes require restart / Le modifiche richiedono riavvio",
                  bg=t.base, fg=t.yellow,
                  font=("Segoe UI", 8)).pack(pady=(8,4))

        # Pulsanti
        btn_frm = tk.Frame(self, bg=t.base)
        btn_frm.pack(pady=(8,16))

        tk.Button(btn_frm, text="✔  OK", bg=t.green, fg=t.base,
                   font=("Segoe UI", 9, "bold"), relief="flat",
                   padx=20, pady=6, command=self._ok
                   ).pack(side="left", padx=6)

        tk.Button(btn_frm, text="✘  Cancel", bg=t.surface0, fg=t.text,
                   font=("Segoe UI", 9), relief="flat",
                   padx=16, pady=6, command=self.destroy
                   ).pack(side="left", padx=6)

        self.transient(parent)
        self.wait_window()

    def _ok(self):
        self.result_lang  = self.lang_var.get()
        self.result_theme = self.theme_var.get()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  APP PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):

    def __init__(self):
        super().__init__()

        # Carica configurazione
        self.config_data = load_config()
        self._lang  = self.config_data["language"]
        self._theme_name = self.config_data["theme"]

        self.s = get_strings(self._lang)
        self.t = get_theme(self._theme_name)
        self.h = get_help(self._lang)

        self.title(f"{self.s.app_title}  {self.s.app_version_prefix}{APP_VERSION}")
        self.geometry("1320x860")
        self.minsize(1024, 700)
        self.configure(bg=self.t.base)

        # Stato
        self.original_image : Optional[Image.Image] = None
        self.binary_np      : Optional[np.ndarray]  = None
        self.gcode_program  : Optional[GCodeProgram] = None
        self.rotation       = 0
        self._stop_event    = threading.Event()
        self._photo_orig    = None
        self._photo_proc    = None

        # Moduli
        self.vec  = Vectorizer(log_cb=self._log)
        self.vec.set_strings(self.s)
        self.ctrl = LaserController(log_cb=self._log)

        self._build_styles()
        self._build_menu()
        self._build_ui()

        self._refresh_ports()
        self.after(4000, self._port_watcher)
        self.protocol("WM_DELETE_WINDOW", self._quit)

        # Binding tastiera
        self.bind("<F1>", lambda _: self._show_help())
        self.bind("<Control-o>", lambda _: self._open_image())
        self.bind("<Control-s>", lambda _: self._save_gcode())

    # ══════════════════════════════════════════════════════════════════════════
    #  STILI
    # ══════════════════════════════════════════════════════════════════════════
    def _build_styles(self):
        t  = self.t
        st = ttk.Style(self)
        st.theme_use("clam")

        def cfg(n, **kw): st.configure(n, **kw)
        def mp(n, **kw):  st.map(n, **kw)

        cfg(".",            background=t.base, foreground=t.text,
                            font=("Segoe UI",9), borderwidth=0)
        cfg("TFrame",       background=t.base)
        cfg("TLabel",       background=t.base, foreground=t.text)
        cfg("TCheckbutton", background=t.base, foreground=t.text)
        cfg("TSeparator",   background=t.surface1)
        cfg("TLabelframe",  background=t.base, foreground=t.blue,
                            relief="solid", borderwidth=1,
                            font=("Segoe UI",9,"bold"))
        cfg("TLabelframe.Label", background=t.base, foreground=t.blue)
        cfg("TButton",      background=t.surface0, foreground=t.text,
                            relief="flat", padding=(8,4))
        mp("TButton",       background=[("active",t.surface1),("pressed",t.blue)],
                            foreground=[("active",t.text)])

        for name, bg, fg in [
            ("Blue",   t.blue,   t.base),
            ("Green",  t.green,  t.base),
            ("Red",    t.red,    t.base),
            ("Yellow", t.yellow, t.base),
            ("Teal",   t.teal,   t.base),
        ]:
            cfg(f"{name}.TButton", background=bg, foreground=fg,
                font=("Segoe UI",9,"bold"), padding=(8,5))
            mp(f"{name}.TButton", background=[("active",t.mauve)])

        cfg("TNotebook",     background=t.base, borderwidth=0)
        cfg("TNotebook.Tab", background=t.mantle, foreground=t.subtext,
                             padding=(12,5))
        mp("TNotebook.Tab",  background=[("selected",t.surface0)],
                             foreground=[("selected",t.blue)])
        cfg("TCombobox",     fieldbackground=t.surface0,
                             background=t.surface0, foreground=t.text)
        cfg("TEntry",        fieldbackground=t.surface0,
                             foreground=t.text, insertcolor=t.text)
        cfg("TScale",        background=t.base, troughcolor=t.surface0,
                             sliderthickness=16)
        cfg("TProgressbar",  troughcolor=t.surface0, background=t.green,
                             borderwidth=0, thickness=14)

    # ══════════════════════════════════════════════════════════════════════════
    #  MENU
    # ══════════════════════════════════════════════════════════════════════════
    def _build_menu(self):
        t = self.t
        s = self.s

        def mk(parent):
            return tk.Menu(parent, tearoff=0,
                            bg=t.mantle, fg=t.text,
                            activebackground=t.blue,
                            activeforeground=t.base)

        mb = mk(self)
        self.config(menu=mb)

        # File
        fm = mk(mb)
        mb.add_cascade(label=s.menu_file, menu=fm)
        fm.add_command(label=s.menu_open_image,  command=self._open_image,
                        accelerator="Ctrl+O")
        fm.add_command(label=s.menu_save_gcode,  command=self._save_gcode,
                        accelerator="Ctrl+S")
        fm.add_command(label=s.menu_load_gcode,  command=self._load_gcode)
        fm.add_separator()
        fm.add_command(label=s.menu_exit,        command=self._quit)

        # View
        vm = mk(mb)
        mb.add_cascade(label=s.menu_view, menu=vm)
        vm.add_command(label=s.menu_vector_preview,
                        command=self._open_vector_preview)
        vm.add_command(label=s.menu_gcode_text,
                        command=self._show_gcode_text)
        vm.add_command(label=s.menu_fit_view,
                        command=lambda: self.work_canvas.fit())

        # Laser
        lm = mk(mb)
        mb.add_cascade(label=s.menu_laser, menu=lm)
        lm.add_command(label=s.menu_send_bbox,     command=self._send_bbox)
        lm.add_command(label=s.menu_emergency_stop,command=self._emergency_stop)

        # Settings
        sm = mk(mb)
        mb.add_cascade(label="⚙ Settings", menu=sm)
        sm.add_command(label="🌐🎨 Preferences...",
                        command=self._show_preferences)

        # Help
        hm = mk(mb)
        mb.add_cascade(label="❓ Help", menu=hm)
        hm.add_command(label="📚 Help / Guida", command=self._show_help,
                        accelerator="F1")
        hm.add_command(label="ℹ About",         command=self._show_about)

    # ══════════════════════════════════════════════════════════════════════════
    #  UI PRINCIPALE
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        s = self.s
        t = self.t

        # Header
        hdr = tk.Frame(self, bg=t.mantle)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔥", bg=t.mantle,
                  font=("Segoe UI",16)).pack(side="left", padx=(10,4), pady=6)
        tk.Label(hdr, text=s.app_title, bg=t.mantle, fg=t.blue,
                  font=("Segoe UI",13,"bold")).pack(side="left")
        tk.Label(hdr, text=f" {s.app_version_prefix}{APP_VERSION}",
                  bg=t.mantle, fg=t.subtext).pack(side="left")

        # Info lingua/tema
        info_text = f"🌐 {self._lang}  |  🎨 {self._theme_name}"
        self._pref_label = tk.Label(hdr, text=info_text,
                                     bg=t.mantle, fg=t.teal,
                                     font=("Segoe UI",8), cursor="hand2")
        self._pref_label.pack(side="right", padx=8)
        self._pref_label.bind("<Button-1>", lambda _: self._show_preferences())

        self.v_status = tk.StringVar(value=s.status_ready)
        tk.Label(hdr, textvariable=self.v_status, bg=t.mantle, fg=t.yellow,
                  font=("Consolas",9)).pack(side="right", padx=12)

        # Corpo
        body = tk.PanedWindow(self, orient="horizontal", bg=t.base, sashwidth=5)
        body.pack(fill="both", expand=True, padx=4, pady=4)

        # Colonna sinistra
        left = ttk.Frame(body)
        body.add(left, minsize=330)

        nb = ttk.Notebook(left)
        nb.pack(fill="both", expand=True)

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

        # Colonna destra
        right = tk.PanedWindow(body, orient="vertical", bg=t.base, sashwidth=5)
        body.add(right, minsize=620)

        work_frm = ttk.LabelFrame(right, text=s.canvas_work_area_title, padding=4)
        right.add(work_frm, minsize=380)

        self.work_canvas = WorkAreaCanvas(
            work_frm,
            work_w=self.config_data["work_area_w"],
            work_h=self.config_data["work_area_h"],
            theme=self.t, s=self.s, log_cb=self._log)
        self.work_canvas.pack(fill="both", expand=True)
        self.work_canvas.set_position_callback(self._on_model_moved)

        bottom = ttk.Frame(right)
        right.add(bottom, minsize=220)
        self._build_bottom(bottom)

        self.after(200, self.work_canvas.fit)

    def _build_bottom(self, parent):
        s = self.s
        t = self.t

        paned = tk.PanedWindow(parent, orient="horizontal", bg=t.base, sashwidth=4)
        paned.pack(fill="both", expand=True)

        # Preview originale
        f1 = ttk.LabelFrame(paned, text=s.preview_original, padding=2)
        paned.add(f1, minsize=140)
        self.canvas_orig = tk.Canvas(f1, bg=t.mantle,
                                      highlightthickness=0, height=180)
        self.canvas_orig.pack(fill="both", expand=True)

        # Preview elaborata
        f2 = ttk.LabelFrame(paned, text=s.preview_processed, padding=2)
        paned.add(f2, minsize=140)
        self.canvas_proc = tk.Canvas(f2, bg=t.mantle,
                                      highlightthickness=0, height=180)
        self.canvas_proc.pack(fill="both", expand=True)

        # Log
        f3 = ttk.LabelFrame(paned, text=s.lbl_log, padding=2)
        paned.add(f3, minsize=300)
        self.log_box = scrolledtext.ScrolledText(
            f3, height=9, wrap="word",
            bg=t.log_bg, fg=t.log_text,
            font=("Consolas",8),
            insertbackground=t.text,
            borderwidth=0, relief="flat")
        self.log_box.pack(fill="both", expand=True)
        ttk.Button(f3, text=s.btn_clear_log,
                   command=lambda: self.log_box.delete("1.0","end")
                   ).pack(anchor="e", padx=2, pady=1)

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB IMMAGINE
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_image(self, p):
        s = self.s

        f = self._lf(p, s.lf_import)
        ttk.Button(f, text=s.btn_open_image, command=self._open_image,
                   style="Blue.TButton").pack(fill="x", pady=(0,4))
        self.v_img_info = tk.StringVar(value=s.lbl_no_image)
        ttk.Label(f, textvariable=self.v_img_info, foreground=self.t.subtext,
                   wraplength=270, justify="left").pack(fill="x")

        f2 = self._lf(p, s.lf_rotation)
        rf = ttk.Frame(f2)
        rf.pack(fill="x")
        ttk.Button(rf, text=s.btn_rot_left, command=lambda: self._rotate(-90),
                   style="Teal.TButton").pack(side="left", expand=True, fill="x", padx=(0,2))
        ttk.Button(rf, text=s.btn_rot_right, command=lambda: self._rotate(90),
                   style="Teal.TButton").pack(side="left", expand=True, fill="x", padx=(2,0))
        ttk.Button(f2, text=s.btn_rot_180, command=lambda: self._rotate(180)
                   ).pack(fill="x", pady=2)
        self.v_rotation = tk.StringVar(value=s.lbl_rotation)
        ttk.Label(f2, textvariable=self.v_rotation, foreground=self.t.teal).pack()

        f3 = self._lf(p, s.lf_flip)
        ff = ttk.Frame(f3)
        ff.pack(fill="x")
        ttk.Button(ff, text=s.btn_flip_h, command=lambda: self._flip("h")
                   ).pack(side="left", expand=True, fill="x", padx=(0,2))
        ttk.Button(ff, text=s.btn_flip_v, command=lambda: self._flip("v")
                   ).pack(side="left", expand=True, fill="x", padx=(2,0))

        f4 = self._lf(p, s.lf_preprocess)
        self.v_threshold = self._slider(f4, s.lbl_threshold, 0, 255, 128)
        self.v_blur      = self._slider(f4, s.lbl_blur,      0,  10,   2)
        self.v_invert    = tk.BooleanVar(value=False)
        self.v_denoise   = tk.BooleanVar(value=False)
        ttk.Checkbutton(f4, text=s.chk_invert, variable=self.v_invert,
                        command=self._update_proc).pack(anchor="w")
        ttk.Checkbutton(f4, text=s.chk_denoise, variable=self.v_denoise,
                        command=self._update_proc).pack(anchor="w")
        ttk.Button(f4, text=s.btn_update_preview, command=self._update_proc
                   ).pack(fill="x", pady=(6,0))

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB VETTORIZZA
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_vectorize(self, p):
        s = self.s

        f = self._lf(p, s.lf_method)
        ttk.Label(f, text=s.lbl_strategy).pack(anchor="w")
        self.v_method = tk.StringVar(value=s.method_contours)
        self.method_combo = ttk.Combobox(
            f, textvariable=self.v_method,
            values=[s.method_contours, s.method_centerline,
                    s.method_raster, s.method_hatching],
            state="readonly")
        self.method_combo.pack(fill="x", pady=(2,6))

        f2 = self._lf(p, s.lf_dimensions)
        for label, attr, val, row in [
            (s.lbl_width_mm,  "v_width",  100.0, 0),
            (s.lbl_height_mm, "v_height", 100.0, 1),
        ]:
            ttk.Label(f2, text=label).grid(row=row, column=0, sticky="w", pady=2)
            var = tk.DoubleVar(value=val)
            setattr(self, attr, var)
            ttk.Entry(f2, textvariable=var, width=9).grid(row=row, column=1, padx=4)
        self.v_keep_ratio = tk.BooleanVar(value=True)
        ttk.Checkbutton(f2, text=s.chk_keep_ratio,
                        variable=self.v_keep_ratio).grid(row=2, columnspan=2, sticky="w")

        f3 = self._lf(p, s.lf_advanced)
        self.v_simplify  = self._slider(f3, s.lbl_simplify,    0,  10,  2)
        self.v_gap       = self._slider(f3, s.lbl_gap,         1,  20,  2)
        self.v_hatch_ang = self._slider(f3, s.lbl_hatch_angle, 0, 180, 45)
        self.v_feed_rate = self._slider(f3, s.lbl_feed_rate,
                                         100, 6000, self.config_data["feed_rate"], res=100)
        self.v_power     = self._slider(f3, s.lbl_power, 0, 255, self.config_data["power"])
        self.v_passes    = self._slider(f3, s.lbl_passes, 1, 10, 1)

        ttk.Button(p, text=s.btn_generate_gcode, command=self._generate_gcode,
                   style="Green.TButton").pack(fill="x", padx=6, pady=6)

        f4 = self._lf(p, s.lf_gcode_info)
        self.v_gcode_info = tk.StringVar(value=s.lbl_no_gcode)
        ttk.Label(f4, textvariable=self.v_gcode_info, foreground=self.t.subtext,
                   wraplength=270, justify="left").pack(fill="x")

        br = ttk.Frame(p)
        br.pack(fill="x", padx=6)
        ttk.Button(br, text=s.btn_save_gcode, command=self._save_gcode
                   ).pack(side="left", expand=True, fill="x", padx=(0,2))
        ttk.Button(br, text=s.btn_gcode_text, command=self._show_gcode_text
                   ).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(br, text=s.btn_vector_preview, command=self._open_vector_preview,
                   style="Blue.TButton").pack(side="left", expand=True, fill="x", padx=(2,0))

        f5 = self._lf(p, s.lf_simulation)
        self.v_sim_speed = self._slider(f5, s.lbl_sim_speed, 1, 50, 10)
        sr = ttk.Frame(f5)
        sr.pack(fill="x", pady=2)
        ttk.Button(sr, text=s.btn_start_sim, command=self._start_sim,
                   style="Green.TButton").pack(side="left", expand=True, fill="x", padx=(0,2))
        ttk.Button(sr, text=s.btn_stop_sim, command=self._stop_sim,
                   style="Red.TButton").pack(side="left", expand=True, fill="x", padx=(2,0))

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB POSIZIONE
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_position(self, p):
        s = self.s

        f = self._lf(p, s.lf_work_area)
        for label, attr, val, row in [
            (s.lbl_work_width,  "v_work_w", self.config_data["work_area_w"], 0),
            (s.lbl_work_height, "v_work_h", self.config_data["work_area_h"], 1),
        ]:
            ttk.Label(f, text=label).grid(row=row, column=0, sticky="w", pady=2)
            var = tk.DoubleVar(value=val)
            setattr(self, attr, var)
            ttk.Entry(f, textvariable=var, width=8).grid(row=row, column=1, padx=4)
        ttk.Button(f, text=s.btn_apply_work_area,
                   command=self._apply_work_area).grid(row=2, columnspan=2, sticky="ew", pady=4)

        f2 = self._lf(p, s.lf_model_position)
        for label, attr, val, row in [
            (s.lbl_model_x, "v_model_x", 0.0, 0),
            (s.lbl_model_y, "v_model_y", 0.0, 1),
        ]:
            ttk.Label(f2, text=label).grid(row=row, column=0, sticky="w", pady=2)
            var = tk.DoubleVar(value=val)
            setattr(self, attr, var)
            ttk.Entry(f2, textvariable=var, width=9).grid(row=row, column=1, padx=4)
        ttk.Button(f2, text=s.btn_apply_position, command=self._apply_model_pos,
                   style="Blue.TButton").grid(row=2, columnspan=2, sticky="ew", pady=4)

        f3 = self._lf(p, s.lf_quick_position)
        for label, where in [
            (s.btn_pos_center, "center"),
            (s.btn_pos_tl, "tl"), (s.btn_pos_tr, "tr"),
            (s.btn_pos_bl, "bl"), (s.btn_pos_br, "br"),
        ]:
            ttk.Button(f3, text=label, command=lambda w=where: self._quick_pos(w)
                       ).pack(fill="x", pady=1)

        f4 = self._lf(p, s.lf_bbox_preview)
        ttk.Label(f4, text=s.lbl_bbox_desc, foreground=self.t.subtext,
                   wraplength=270).pack(fill="x")
        self.v_bbox_feed = self._slider(f4, s.lbl_bbox_feed, 100, 3000, 500, res=100)
        ttk.Button(f4, text=s.btn_send_bbox, command=self._send_bbox,
                   style="Yellow.TButton").pack(fill="x", pady=(6,0))

        f5 = self._lf(p, s.lf_model_info)
        self.v_model_info = tk.StringVar(value=s.lbl_no_model)
        ttk.Label(f5, textvariable=self.v_model_info, foreground=self.t.teal,
                   font=("Consolas",8), wraplength=270, justify="left").pack(fill="x")

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB LASER
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_laser(self, p):
        s = self.s

        f = self._lf(p, s.lf_connection)
        r1 = ttk.Frame(f)
        r1.pack(fill="x", pady=2)
        ttk.Label(r1, text=s.lbl_port, width=7).pack(side="left")
        self.v_port = tk.StringVar(value=self.config_data.get("last_port",""))
        self.combo_port = ttk.Combobox(r1, textvariable=self.v_port, width=12, state="readonly")
        self.combo_port.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(r1, text="↻", width=3, command=self._refresh_ports).pack(side="left")

        r2 = ttk.Frame(f)
        r2.pack(fill="x", pady=2)
        ttk.Label(r2, text=s.lbl_baud, width=7).pack(side="left")
        self.v_baud = tk.IntVar(value=self.config_data.get("last_baud", 115200))
        ttk.Combobox(r2, textvariable=self.v_baud, values=BAUDRATES, width=10,
                     state="readonly").pack(side="left", padx=4)

        self.v_simulate = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text=s.chk_simulation, variable=self.v_simulate,
                        command=self._toggle_sim_mode).pack(anchor="w", pady=2)

        r3 = ttk.Frame(f)
        r3.pack(fill="x", pady=4)
        self.btn_conn = ttk.Button(r3, text=s.btn_connect, command=self._connect,
                                    style="Blue.TButton")
        self.btn_conn.pack(side="left", expand=True, fill="x", padx=(0,2))
        self.btn_disc = ttk.Button(r3, text=s.btn_disconnect, command=self._disconnect)
        self.btn_disc.pack(side="left", expand=True, fill="x", padx=(2,0))
        self.btn_disc.state(["disabled"])

        self.v_conn_lbl = tk.StringVar(value=s.lbl_not_connected)
        ttk.Label(f, textvariable=self.v_conn_lbl, foreground=self.t.subtext).pack()

        # Home manuale
        f2 = self._lf(p, s.lf_home)
        ttk.Label(f2, text=s.lbl_home_desc, foreground=self.t.subtext,
                   wraplength=270).pack(fill="x")

        self.v_jog_dist = tk.DoubleVar(value=10.0)
        self.v_jog_feed = tk.IntVar(value=1000)
        jc = ttk.Frame(f2)
        jc.pack(fill="x", pady=4)
        ttk.Label(jc, text=s.lbl_jog_step).pack(side="left")
        ttk.Combobox(jc, textvariable=self.v_jog_dist,
                     values=[0.1,0.5,1,5,10,25,50], width=7).pack(side="left", padx=4)
        ttk.Label(jc, text=s.lbl_jog_feed).pack(side="left")
        ttk.Entry(jc, textvariable=self.v_jog_feed, width=6).pack(side="left", padx=2)

        jg = tk.Frame(f2, bg=self.t.base)
        jg.pack(pady=4)
        ttk.Button(jg, text="▲", command=lambda: self._jog("Y",+1), width=4
                   ).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(jg, text="◄", command=lambda: self._jog("X",-1), width=4
                   ).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(jg, text="●", command=self._jog_zero, width=4
                   ).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(jg, text="►", command=lambda: self._jog("X",+1), width=4
                   ).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(jg, text="▼", command=lambda: self._jog("Y",-1), width=4
                   ).grid(row=2, column=1, padx=2, pady=2)

        ttk.Button(f2, text=s.btn_set_home, command=self._set_home,
                   style="Green.TButton").pack(fill="x", pady=(4,0))
        ttk.Button(f2, text=s.btn_goto_home, command=self._goto_home
                   ).pack(fill="x", pady=2)
        ttk.Button(f2, text=s.btn_unlock, command=lambda: self.ctrl.unlock()
                   ).pack(fill="x", pady=2)

        # Comando manuale
        f3 = self._lf(p, s.lf_manual_cmd)
        cr = ttk.Frame(f3)
        cr.pack(fill="x")
        self.v_cmd = tk.StringVar()
        e = ttk.Entry(cr, textvariable=self.v_cmd)
        e.pack(side="left", fill="x", expand=True, padx=(0,4))
        e.bind("<Return>", lambda _: self._cmd_send())
        ttk.Button(cr, text=s.btn_send_cmd, command=self._cmd_send).pack(side="left")

        # Invio GCode
        f4 = self._lf(p, s.lf_send_gcode)
        self.v_progress     = tk.DoubleVar(value=0)
        self.v_progress_lbl = tk.StringVar(value=s.lbl_waiting)
        ttk.Progressbar(f4, variable=self.v_progress, maximum=100).pack(fill="x", pady=4)
        ttk.Label(f4, textvariable=self.v_progress_lbl, foreground=self.t.subtext).pack()

        r4 = ttk.Frame(f4)
        r4.pack(fill="x", pady=(6,2))
        ttk.Button(r4, text=s.btn_start_engraving, command=self._start_engraving,
                   style="Green.TButton").pack(side="left", expand=True, fill="x", padx=(0,2))
        ttk.Button(r4, text=s.btn_stop_engraving, command=self._stop_engraving,
                   style="Red.TButton").pack(side="left", expand=True, fill="x", padx=(2,0))
        ttk.Button(f4, text=s.btn_emergency_stop, command=self._emergency_stop,
                   style="Red.TButton").pack(fill="x", pady=2)

    # ══════════════════════════════════════════════════════════════════════════
    #  HELPER WIDGET
    # ══════════════════════════════════════════════════════════════════════════
    def _lf(self, parent, text, padding=8) -> ttk.LabelFrame:
        f = ttk.LabelFrame(parent, text=text, padding=padding)
        f.pack(fill="x", padx=6, pady=3)
        return f

    def _slider(self, parent, label, from_, to, default, res=1) -> tk.DoubleVar:
        ttk.Label(parent, text=label, foreground=self.t.subtext).pack(anchor="w")
        var = tk.DoubleVar(value=default)
        row = ttk.Frame(parent)
        row.pack(fill="x")
        lbl = ttk.Label(row, text=str(int(default)), width=6, foreground=self.t.blue)
        lbl.pack(side="right")
        ttk.Scale(row, from_=from_, to=to, variable=var, orient="horizontal",
                   command=lambda v, l=lbl: l.config(text=f"{float(v):.0f}")
                   ).pack(side="left", fill="x", expand=True)
        return var

    # ══════════════════════════════════════════════════════════════════════════
    #  LOG
    # ══════════════════════════════════════════════════════════════════════════
    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.after(0, self._append_log, f"[{ts}] {msg}\n")

    def _append_log(self, line: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", line)
        self.log_box.see("end")

    # ══════════════════════════════════════════════════════════════════════════
    #  PREFERENZE
    # ══════════════════════════════════════════════════════════════════════════
    def _show_preferences(self):
        dlg = PreferencesDialog(self, self._lang, self._theme_name, self.t)
        changed = (dlg.result_lang != self._lang or
                   dlg.result_theme != self._theme_name)
        if changed:
            self.config_data["language"] = dlg.result_lang
            self.config_data["theme"]    = dlg.result_theme
            save_config(self.config_data)
            msg = {
                "Italiano": "Riavvia l'applicazione per applicare le modifiche.",
                "English":  "Please restart the application to apply changes.",
                "Español":  "Reinicia la aplicación para aplicar los cambios.",
                "Deutsch":  "Bitte starten Sie die Anwendung neu.",
            }.get(dlg.result_lang, "Please restart to apply changes.")
            messagebox.showinfo("Preferences", msg)

    def _show_help(self):
        HelpWindow(self, self.t, self.h)

    def _show_about(self):
        t = self.t
        messagebox.showinfo(
            "About",
            f"Py Laser v{APP_VERSION}\n\n"
            f"A complete laser engraving application\n"
            f"with vectorization, simulation and GCode control.\n\n"
            f"Theme: {self._theme_name}\n"
            f"Language: {self._lang}\n\n"
            f"© 2024 - Open Source"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  PORTE
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_ports(self):
        ports = LaserController.list_ports()
        self.combo_port["values"] = ports
        if ports and not self.v_port.get():
            self.v_port.set(ports[0])

    def _port_watcher(self):
        if not self.ctrl.is_connected():
            self._refresh_ports()
        self.after(4000, self._port_watcher)

    # ══════════════════════════════════════════════════════════════════════════
    #  IMMAGINE
    # ══════════════════════════════════════════════════════════════════════════
    def _open_image(self):
        path = filedialog.askopenfilename(
            title=self.s.btn_open_image,
            filetypes=[("Images","*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.gif"),
                       ("All","*.*")])
        if not path: return
        try:
            self.original_image = Image.open(path).convert("RGB")
            self.rotation = 0
            w, h = self.original_image.size
            self.v_img_info.set(f"📄 {Path(path).name}\n    {w}×{h} px")
            self._log(self.s.log_image_opened.format(path=path))
            self._show_on_canvas(self.canvas_orig, self.original_image)
            self._update_proc()
        except Exception as e:
            messagebox.showerror(self.s.error, self.s.err_image_open.format(err=e))

    def _rotate(self, deg: int):
        if self.original_image is None: return
        self.rotation = (self.rotation + deg) % 360
        self.original_image = self.original_image.rotate(-deg, expand=True)
        self.v_rotation.set(self.s.lbl_rotation.replace("0°", f"{self.rotation}°"))
        self._log(self.s.log_rotated.format(deg=deg, total=self.rotation))
        self._show_on_canvas(self.canvas_orig, self.original_image)
        self._update_proc()

    def _flip(self, direction: str):
        if self.original_image is None: return
        if direction == "h":
            self.original_image = ImageOps.mirror(self.original_image)
            self._log(self.s.log_flipped_h)
        else:
            self.original_image = ImageOps.flip(self.original_image)
            self._log(self.s.log_flipped_v)
        self._show_on_canvas(self.canvas_orig, self.original_image)
        self._update_proc()

    def _update_proc(self):
        if self.original_image is None: return
        try:
            self.binary_np = self.vec.preprocess(
                self.original_image,
                threshold=int(self.v_threshold.get()),
                blur_radius=int(self.v_blur.get()),
                invert=self.v_invert.get(),
                denoise=self.v_denoise.get())
            pil = Image.fromarray(self.binary_np)
            self._show_on_canvas(self.canvas_proc, pil)
        except Exception as e:
            self._log(self.s.log_preprocess_error.format(err=e))

    def _show_on_canvas(self, canvas: tk.Canvas, img: Image.Image):
        canvas.update_idletasks()
        cw, ch = max(canvas.winfo_width(), 160), max(canvas.winfo_height(), 140)
        thumb = img.copy()
        thumb.thumbnail((cw-4, ch-4), Image.LANCZOS)
        photo = ImageTk.PhotoImage(thumb)
        if canvas is self.canvas_orig:
            self._photo_orig = photo
        else:
            self._photo_proc = photo
        canvas.delete("all")
        canvas.create_image(cw//2, ch//2, anchor="center", image=photo)

    # ══════════════════════════════════════════════════════════════════════════
    #  GENERAZIONE GCODE
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_gcode(self):
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

        self._log(s.log_generating.format(method=method, w=w_mm, h=h_mm))
        self.v_status.set(s.status_generating)

        def _run():
            try:
                if method == s.method_contours:
                    paths = self.vec.contour_paths(self.binary_np, w_mm, h_mm, simp)
                elif method == s.method_centerline:
                    paths = self.vec.centerline_paths(self.binary_np, w_mm, h_mm)
                elif method == s.method_raster:
                    paths = self.vec.raster_paths(self.binary_np, w_mm, h_mm, gap)
                else:
                    paths = self.vec.hatch_paths(self.binary_np, w_mm, h_mm, angle, gap)

                gen  = GCodeGenerator(feed=feed, power=power, passes=passes)
                prog = gen.build(paths, offset_x=ox, offset_y=oy)
                self.gcode_program = prog

                n     = len(prog.raw_lines)
                moves = len(prog.moves)
                on_m  = sum(1 for m in prog.moves if m.laser_on)
                mn_x, mn_y, mx_x, mx_y = prog.bounds()

                info = (s.gcode_lines.format(n=n, moves=moves) + "\n" +
                        s.gcode_laser_on.format(on=on_m) +
                        s.gcode_laser_off.format(off=moves-on_m) + "\n" +
                        s.gcode_area.format(w=mx_x-mn_x, h=mx_y-mn_y) + "\n" +
                        s.gcode_feed.format(feed=feed) +
                        s.gcode_power.format(power=power) +
                        s.gcode_passes.format(passes=passes))

                self.after(0, self.v_gcode_info.set, info)
                self.after(0, self._update_model_info)
                self.after(0, self._update_work_canvas)
                self.after(0, self.v_status.set, s.status_gcode_ready)
                self._log(s.log_gcode_generated.format(lines=n))
            except Exception as e:
                self._log(s.log_gen_error.format(err=e))
                self.after(0, self.v_status.set, s.status_gen_error)

        threading.Thread(target=_run, daemon=True).start()

    def _update_work_canvas(self):
        if self.gcode_program:
            self.work_canvas.set_program(self.gcode_program.moves)
            self.work_canvas.set_model_position(
                self.v_model_x.get(), self.v_model_y.get())

    def _update_model_info(self):
        if not self.gcode_program: return
        s = self.s
        mn_x, mn_y, mx_x, mx_y = self.gcode_program.bounds()
        w, h = mx_x-mn_x, mx_y-mn_y
        ox, oy = self.v_model_x.get(), self.v_model_y.get()
        self.v_model_info.set(
            s.info_model_size.format(w=w, h=h) + "\n" +
            s.info_model_origin.format(x=ox, y=oy) + "\n" +
            s.info_model_extent_x.format(x0=ox+mn_x, x1=ox+mx_x) + "\n" +
            s.info_model_extent_y.format(y0=oy+mn_y, y1=oy+mx_y))

    # ══════════════════════════════════════════════════════════════════════════
    #  POSIZIONE MODELLO
    # ══════════════════════════════════════════════════════════════════════════
    def _on_model_moved(self, x_mm, y_mm):
        self.v_model_x.set(round(x_mm, 2))
        self.v_model_y.set(round(y_mm, 2))
        self._update_model_info()

    def _apply_work_area(self):
        w, h = self.v_work_w.get(), self.v_work_h.get()
        self.work_canvas.set_work_area(w, h)
        self.config_data["work_area_w"] = w
        self.config_data["work_area_h"] = h
        save_config(self.config_data)
        self._log(self.s.log_work_area_set.format(w=w, h=h))

    def _apply_model_pos(self):
        x, y = self.v_model_x.get(), self.v_model_y.get()
        self.work_canvas.set_model_position(x, y)
        self._update_model_info()
        self._log(self.s.log_model_position.format(x=x, y=y))

    def _quick_pos(self, where: str):
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        mn_x, mn_y, mx_x, mx_y = self.gcode_program.bounds()
        w, h = mx_x-mn_x, mx_y-mn_y
        ww, wh = self.work_canvas.work_w_mm, self.work_canvas.work_h_mm
        mg = 5.0
        positions = {
            "center": ((ww-w)/2-mn_x, (wh-h)/2-mn_y),
            "tl": (mg-mn_x, wh-h-mg-mn_y),
            "tr": (ww-w-mg-mn_x, wh-h-mg-mn_y),
            "bl": (mg-mn_x, mg-mn_y),
            "br": (ww-w-mg-mn_x, mg-mn_y),
        }
        x, y = positions[where]
        self.v_model_x.set(round(x, 2))
        self.v_model_y.set(round(y, 2))
        self.work_canvas.set_model_position(x, y)
        self._update_model_info()
        self._log(self.s.log_quick_pos.format(where=where, x=x, y=y))

    # ══════════════════════════════════════════════════════════════════════════
    #  SIMULAZIONE
    # ══════════════════════════════════════════════════════════════════════════
    def _start_sim(self):
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
                self.after(0, self.v_status.set, self.s.status_sim_completed)))

    def _stop_sim(self):
        self.work_canvas.stop_simulation()
        self._log(self.s.log_sim_stopped)
        self.v_status.set(self.s.status_ready)

    # ══════════════════════════════════════════════════════════════════════════
    #  PREVIEW / GCODE I/O
    # ══════════════════════════════════════════════════════════════════════════
    def _open_vector_preview(self):
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        VectorPreviewWindow(self, self.gcode_program.moves,
                             self.work_canvas.work_w_mm,
                             self.work_canvas.work_h_mm,
                             self.t, self.s, self._log)

    def _save_gcode(self):
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        path = filedialog.asksaveasfilename(
            title=self.s.menu_save_gcode, defaultextension=".gcode",
            filetypes=[("GCode","*.gcode *.nc *.cnc"),("All","*.*")])
        if path:
            Path(path).write_text("\n".join(self.gcode_program.translated_lines()))
            self._log(self.s.log_saved.format(path=path))

    def _load_gcode(self):
        path = filedialog.askopenfilename(
            title=self.s.menu_load_gcode,
            filetypes=[("GCode","*.gcode *.nc *.cnc"),("All","*.*")])
        if not path: return
        lines = Path(path).read_text().splitlines()
        prog           = GCodeProgram()
        prog.raw_lines = lines
        prog.moves     = GCodeParser.parse(lines)
        if prog.moves:
            mn_x, mn_y, mx_x, mx_y = prog.bounds()
            prog.width_mm  = mx_x - mn_x
            prog.height_mm = mx_y - mn_y
        self.gcode_program = prog
        self._update_work_canvas()
        self._update_model_info()
        self._log(self.s.log_loaded.format(path=path, lines=len(lines), moves=len(prog.moves)))

    def _show_gcode_text(self):
        if not self.gcode_program:
            messagebox.showinfo(self.s.info, self.s.err_no_gcode)
            return
        t = self.t
        w = tk.Toplevel(self)
        w.title(self.s.gcode_view_title)
        w.geometry("720x580")
        w.configure(bg=t.base)
        txt = scrolledtext.ScrolledText(w, bg=t.surface0, fg=t.text,
                                         font=("Consolas",9), borderwidth=0)
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert("end", "\n".join(self.gcode_program.translated_lines()))
        txt.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    #  CONNESSIONE
    # ══════════════════════════════════════════════════════════════════════════
    def _connect(self):
        sim = self.v_simulate.get()
        self.ctrl._simulating = sim
        if sim:
            self._update_conn(True)
            return
        port = self.v_port.get()
        baud = int(self.v_baud.get())
        if not port or "(none)" in port.lower() or "(nessuna)" in port.lower():
            messagebox.showwarning(self.s.warning, self.s.err_no_port)
            return
        # Salva ultima porta/baud
        self.config_data["last_port"] = port
        self.config_data["last_baud"] = baud
        save_config(self.config_data)

        def _do():
            ok = self.ctrl.connect(port, baud, self.s)
            self.after(0, self._update_conn, ok)
        threading.Thread(target=_do, daemon=True).start()

    def _disconnect(self):
        self.ctrl.disconnect(self.s)
        self.ctrl._simulating = False
        self._update_conn(False)

    def _update_conn(self, ok: bool):
        s = self.s
        if ok:
            lbl = (f"🟡  {s.simulation_mode}" if self.ctrl._simulating
                   else f"🟢  {s.btn_connect} → {self.v_port.get()}")
            self.v_conn_lbl.set(lbl)
            self.btn_conn.state(["disabled"])
            self.btn_disc.state(["!disabled"])
        else:
            self.v_conn_lbl.set(s.lbl_not_connected)
            self.btn_conn.state(["!disabled"])
            self.btn_disc.state(["disabled"])

    def _toggle_sim_mode(self):
        if self.v_simulate.get():
            self.combo_port.state(["disabled"])
        else:
            self.combo_port.state(["!disabled"])

    # ══════════════════════════════════════════════════════════════════════════
    #  JOG / HOME
    # ══════════════════════════════════════════════════════════════════════════
    def _check_conn(self) -> bool:
        if not self.ctrl.is_connected():
            messagebox.showwarning(self.s.warning, self.s.err_not_connected)
            return False
        return True

    def _jog(self, axis: str, direction: int):
        if not self._check_conn(): return
        dist = self.v_jog_dist.get() * direction
        feed = self.v_jog_feed.get()
        self.ctrl.jog(axis, dist, feed)
        self._log(self.s.log_jog.format(axis=axis, dist=dist))

    def _jog_zero(self):
        if not self._check_conn(): return
        self.ctrl.send_command("G90")
        self.ctrl.send_command("G0 X0 Y0")
        self._log(self.s.log_goto_home)

    def _set_home(self):
        if not self._check_conn(): return
        self.ctrl.set_home(self.s)

    def _goto_home(self):
        if not self._check_conn(): return
        self.ctrl.send_command("G90")
        self.ctrl.send_command("G0 X0 Y0")
        self._log(self.s.log_goto_home)

    def _cmd_send(self):
        if not self._check_conn(): return
        cmd = self.v_cmd.get().strip()
        if cmd:
            resp = self.ctrl.send_command(cmd, self.s)
            self._log(f"→ {cmd}   ← {resp}")
            self.v_cmd.set("")

    # ══════════════════════════════════════════════════════════════════════════
    #  BBOX FISICO
    # ══════════════════════════════════════════════════════════════════════════
    def _send_bbox(self):
        if not self._check_conn(): return
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return
        feed = int(self.v_bbox_feed.get())
        self._log(self.s.log_bbox_sending.format(feed=feed))
        self.work_canvas.send_bbox_to_laser(
            self.ctrl, feed=feed, s=self.s,
            done_cb=lambda: self._log(self.s.log_bbox_done))

    # ══════════════════════════════════════════════════════════════════════════
    #  INCISIONE
    # ══════════════════════════════════════════════════════════════════════════
    def _start_engraving(self):
        if not self._check_conn(): return
        if not self.gcode_program:
            messagebox.showwarning(self.s.warning, self.s.err_no_gcode)
            return

        s = self.s
        mn_x, mn_y, mx_x, mx_y = self.gcode_program.bounds()
        ox, oy = self.v_model_x.get(), self.v_model_y.get()
        note = s.dlg_start_sim_note if self.ctrl._simulating else s.dlg_start_safe_note

        ok = messagebox.askyesno(
            s.dlg_start_title,
            s.dlg_start_body.format(w=mx_x-mn_x, h=mx_y-mn_y,
                                     ox=ox, oy=oy,
                                     lines=len(self.gcode_program.raw_lines)) + note)
        if not ok: return

        self._stop_event.clear()
        self.v_progress.set(0)
        self.v_progress_lbl.set(s.lbl_waiting)
        self.v_status.set(s.status_engraving)

        lines = self.gcode_program.translated_lines()

        def _prog(cur, tot):
            pct = cur/tot*100
            self.after(0, self.v_progress.set, pct)
            self.after(0, self.v_progress_lbl.set, f"{cur}/{tot}  ({pct:.1f}%)")

        def _run():
            ok2 = self.ctrl.send_gcode(lines, progress_cb=_prog,
                                        stop_event=self._stop_event, s=self.s)
            self.after(0, self._engrave_done, ok2)

        threading.Thread(target=_run, daemon=True).start()

    def _engrave_done(self, ok: bool):
        s = self.s
        if ok:
            self.v_status.set(s.status_completed)
            self.v_progress_lbl.set(f"✅  {s.completed}!")
            messagebox.showinfo(s.dlg_completed_title, s.dlg_completed_body)
        else:
            self.v_status.set(s.status_stopped)
            self.v_progress_lbl.set(f"⚠  {s.stopped}")

    def _stop_engraving(self):
        self._stop_event.set()
        self._log(self.s.log_stop_requested)
        self.v_status.set(self.s.status_stopped)

    def _emergency_stop(self):
        self._stop_event.set()
        self.ctrl.emergency_stop(self.s)
        self.v_status.set(self.s.status_emergency)
        messagebox.showwarning(self.s.dlg_emergency_title, self.s.dlg_emergency_body)

    # ══════════════════════════════════════════════════════════════════════════
    #  CHIUSURA
    # ══════════════════════════════════════════════════════════════════════════
    def _quit(self):
        # Salva configurazione finale
        self.config_data["feed_rate"] = int(self.v_feed_rate.get())
        self.config_data["power"]     = int(self.v_power.get())
        save_config(self.config_data)

        self._stop_event.set()
        self.work_canvas.stop_simulation()
        self.ctrl.disconnect(self.s) if self.ctrl.is_connected() else None
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    missing = []
    if not PIL_AVAILABLE:   missing.append("Pillow    → pip install Pillow")
    if not NUMPY_AVAILABLE: missing.append("NumPy     → pip install numpy")
    if not CV2_AVAILABLE:   missing.append("OpenCV    → pip install opencv-python")

    if missing:
        s = get_strings()
        print("❌ " + s.err_missing_libs.format(libs="\n".join(missing)))
        for m in missing:
            print(f"   {m}")
        sys.exit(1)

    if not SERIAL_AVAILABLE:
        s = get_strings()
        print("⚠ " + s.err_pyserial_missing)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
