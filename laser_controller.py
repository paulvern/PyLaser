#!/usr/bin/env python3
"""
laser_controller.py
Modulo di comunicazione seriale per PyLaser

Gestisce:
- Connessione/disconnessione
- Invio comandi GCode
- Rilevamento automatico controller
- Modalità simulazione
"""

import time
import threading
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass
from enum import Enum, auto

# ══════════════════════════════════════════════════════════════════════════════
#  DIPENDENZE
# ══════════════════════════════════════════════════════════════════════════════
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
#  ENUMERAZIONI E COSTANTI
# ══════════════════════════════════════════════════════════════════════════════
class ControllerType(Enum):
    """Tipi di controller supportati."""
    UNKNOWN = auto()
    GRBL = auto()
    GRBL_LPC = auto()
    MARLIN = auto()
    SMOOTHIE = auto()


@dataclass
class ControllerInfo:
    """Informazioni sul controller rilevato."""
    type: ControllerType = ControllerType.UNKNOWN
    version: str = ""
    firmware: str = ""
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


# Pattern per riconoscimento controller
CONTROLLER_PATTERNS = {
    ControllerType.GRBL: ["grbl", "gnea"],
    ControllerType.GRBL_LPC: ["grbl-lpc", "lpc"],
    ControllerType.MARLIN: ["marlin"],
    ControllerType.SMOOTHIE: ["smoothie"],
}


# ══════════════════════════════════════════════════════════════════════════════
#  CONTROLLER LASER
# ══════════════════════════════════════════════════════════════════════════════
class LaserController:
    """
    Gestisce la comunicazione con il controller laser via seriale.
    
    Supporta:
    - Connessione manuale e auto-detect
    - Invio comandi singoli e batch
    - Modalità simulazione
    - Emergency stop
    """
    
    def __init__(self, log_cb: Optional[Callable] = None):
        """
        Inizializza il controller.
        
        Args:
            log_cb: Callback per logging
        """
        self.log = log_cb or print
        self.ser: Optional[serial.Serial] = None
        self._simulating = False
        self._controller_info = ControllerInfo()
        self._lock = threading.Lock()
    
    # ══════════════════════════════════════════════════════════════════════════
    #  GESTIONE PORTE
    # ══════════════════════════════════════════════════════════════════════════
    @staticmethod
    def list_ports() -> List[str]:
        """Elenca le porte seriali disponibili."""
        if not SERIAL_AVAILABLE:
            return ["(simulated)"]
        
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports or ["(none)"]
    
    @staticmethod
    def get_port_info(port: str) -> dict:
        """Ottiene informazioni dettagliate su una porta."""
        if not SERIAL_AVAILABLE:
            return {}
        
        for p in serial.tools.list_ports.comports():
            if p.device == port:
                return {
                    'device': p.device,
                    'description': p.description,
                    'hwid': p.hwid,
                    'vid': p.vid,
                    'pid': p.pid,
                    'manufacturer': p.manufacturer,
                    'product': p.product,
                    'serial_number': p.serial_number,
                }
        return {}
    
    # ══════════════════════════════════════════════════════════════════════════
    #  CONNESSIONE
    # ══════════════════════════════════════════════════════════════════════════
    def connect(self, port: str, baud: int, strings=None) -> bool:
        """
        Connette al controller.
        
        Args:
            port: Porta seriale
            baud: Baud rate
            strings: Oggetto stringhe per localizzazione
        
        Returns:
            True se connesso con successo
        """
        if self._simulating:
            if strings:
                self.log(strings.log_simulation_on)
            else:
                self.log("🟡 Modalità simulazione attiva")
            return True
        
        if not SERIAL_AVAILABLE:
            self.log("❌ pyserial non disponibile")
            return False
        
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=5,
                write_timeout=5
            )
            
            # Attendi inizializzazione controller
            time.sleep(2)
            self.ser.reset_input_buffer()
            
            # Leggi messaggio di benvenuto
            greeting = self.ser.read_all().decode(errors="ignore").strip()
            
            if strings:
                self.log(strings.log_connected.format(port=port, baud=baud))
            else:
                self.log(f"✅ Connesso a {port}@{baud}")
            
            if greeting:
                if strings:
                    self.log(strings.log_fw.format(fw=greeting[:80]))
                else:
                    self.log(f"   FW: {greeting[:80]}")
                
                # Rileva tipo controller
                self._detect_controller(greeting)
            
            return True
            
        except Exception as e:
            if strings:
                self.log(strings.log_connect_error.format(err=e))
            else:
                self.log(f"❌ Connessione fallita: {e}")
            self.ser = None
            return False
    
    def disconnect(self, strings=None):
        """Disconnette dal controller."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
        self.ser = None
        self._controller_info = ControllerInfo()
        
        if strings:
            self.log(strings.log_disconnected)
        else:
            self.log("🔌 Disconnesso")
    
    def is_connected(self) -> bool:
        """Verifica se connesso."""
        return self._simulating or (self.ser is not None and self.ser.is_open)
    
    def _detect_controller(self, greeting: str):
        """Rileva il tipo di controller dal messaggio di benvenuto."""
        greeting_lower = greeting.lower()
        
        for ctrl_type, patterns in CONTROLLER_PATTERNS.items():
            for pattern in patterns:
                if pattern in greeting_lower:
                    self._controller_info.type = ctrl_type
                    self._controller_info.firmware = greeting
                    
                    # Estrai versione se presente
                    import re
                    version_match = re.search(r'(\d+\.\d+[a-z]?)', greeting)
                    if version_match:
                        self._controller_info.version = version_match.group(1)
                    
                    self.log(f"   Controller: {ctrl_type.name} v{self._controller_info.version}")
                    return
        
        self._controller_info.type = ControllerType.UNKNOWN
    
    @property
    def controller_info(self) -> ControllerInfo:
        """Restituisce le informazioni sul controller."""
        return self._controller_info
    
    # ══════════════════════════════════════════════════════════════════════════
    #  INVIO COMANDI
    # ══════════════════════════════════════════════════════════════════════════
    def send_command(self, cmd: str, strings=None) -> str:
        """
        Invia un singolo comando GCode.
        
        Args:
            cmd: Comando da inviare
            strings: Oggetto stringhe per localizzazione
        
        Returns:
            Risposta del controller
        """
        cmd = cmd.strip()
        if not cmd or cmd.startswith(";"):
            return "ok"
        
        if self._simulating:
            time.sleep(0.001)
            return "ok"
        
        with self._lock:
            try:
                self.ser.write((cmd + "\n").encode())
                
                # Leggi risposta
                resp = self.ser.readline().decode(errors="ignore").strip()
                
                # Salta risposte intermedie
                while resp and not any(resp.startswith(k) for k in ("ok", "error", "ALARM")):
                    resp = self.ser.readline().decode(errors="ignore").strip()
                
                return resp
                
            except Exception as e:
                if strings:
                    self.log(strings.log_tx_error.format(err=e))
                return "error"
    
    def send_gcode(self, lines: List[str], 
                   progress_cb: Optional[Callable] = None,
                   stop_event: Optional[threading.Event] = None,
                   strings=None) -> bool:
        """
        Invia un programma GCode completo.
        
        Args:
            lines: Lista di righe GCode
            progress_cb: Callback per progresso (current, total)
            stop_event: Event per interrompere l'invio
            strings: Oggetto stringhe
        
        Returns:
            True se completato senza errori
        """
        stop = stop_event or threading.Event()
        total = len(lines)
        errors = 0
        
        for i, line in enumerate(lines):
            if stop.is_set():
                self.send_command("M5")
                if strings:
                    self.log(strings.log_send_stopped)
                return False
            
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                if progress_cb:
                    progress_cb(i + 1, total)
                continue
            
            resp = self.send_command(stripped, strings)
            
            if "error" in resp.lower():
                errors += 1
            elif "alarm" in resp.lower():
                if strings:
                    self.log(strings.log_alarm.format(resp=resp))
                self.send_command("M5")
                return False
            
            if progress_cb:
                progress_cb(i + 1, total)
        
        if strings:
            self.log(strings.log_engraving_done.format(errors=errors))
        
        return errors == 0
    
    # ══════════════════════════════════════════════════════════════════════════
    #  COMANDI SPECIALI
    # ══════════════════════════════════════════════════════════════════════════
    def emergency_stop(self, strings=None):
        """Invia emergency stop (soft reset)."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b"\x18")  # Ctrl-X
            except:
                pass
        
        if strings:
            self.log(strings.log_emergency)
        else:
            self.log("🚨 EMERGENCY STOP")
    
    def home(self):
        """Esegue homing automatico."""
        self.send_command("$H")
    
    def unlock(self):
        """Sblocca allarme."""
        self.send_command("$X")
    
    def get_status(self) -> str:
        """Richiede lo stato del controller."""
        return self.send_command("?")
    
    def set_home(self, strings=None):
        """Imposta la posizione corrente come home."""
        self.send_command("G92 X0 Y0")
        if strings:
            self.log(strings.log_home_set)
        else:
            self.log("🏠 Home impostato qui")
    
    def jog(self, axis: str, distance: float, feed: int):
        """
        Esegue movimento JOG.
        
        Args:
            axis: 'X' o 'Y'
            distance: Distanza in mm (con segno)
            feed: Velocità mm/min
        """
        self.send_command("G91")  # Relativo
        self.send_command(f"G0 {axis}{distance:.3f} F{feed}")
        self.send_command("G90")  # Assoluto
    
    def go_to(self, x: float, y: float, feed: int = 1000):
        """Vai a una posizione specifica."""
        self.send_command("G90")
        self.send_command(f"G0 X{x:.3f} Y{y:.3f} F{feed}")
    
    def laser_test(self, power: int = 10, duration: float = 0.5):
        """
        Test breve del laser.
        
        Args:
            power: Potenza (0-255)
            duration: Durata in secondi
        """
        self.send_command(f"M3 S{power}")
        time.sleep(duration)
        self.send_command("M5")
    
    # ══════════════════════════════════════════════════════════════════════════
    #  SIMULAZIONE
    # ══════════════════════════════════════════════════════════════════════════
    def set_simulation(self, enabled: bool):
        """Abilita/disabilita modalità simulazione."""
        self._simulating = enabled
    
    @property
    def is_simulating(self) -> bool:
        """Verifica se in modalità simulazione."""
        return self._simulating


# ══════════════════════════════════════════════════════════════════════════════
#  FUNZIONI DI UTILITÀ
# ══════════════════════════════════════════════════════════════════════════════
def find_laser_ports() -> List[Tuple[str, str]]:
    """
    Cerca porte che potrebbero essere controller laser.
    
    Returns:
        Lista di tuple (porta, descrizione)
    """
    if not SERIAL_AVAILABLE:
        return []
    
    laser_keywords = ['ch340', 'cp210', 'arduino', 'serial', 'usb']
    results = []
    
    for port in serial.tools.list_ports.comports():
        desc_lower = (port.description or "").lower()
        if any(kw in desc_lower for kw in laser_keywords):
            results.append((port.device, port.description))
        elif port.vid and port.pid:
            # Alcuni VID/PID comuni per controller
            results.append((port.device, port.description))
    
    return results


def check_serial_available() -> bool:
    """Verifica se pyserial è disponibile."""
    return SERIAL_AVAILABLE


# ══════════════════════════════════════════════════════════════════════════════
#  TEST
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== Test Laser Controller Module ===\n")
    
    print(f"pyserial disponibile: {SERIAL_AVAILABLE}\n")
    
    print("Porte disponibili:")
    for port in LaserController.list_ports():
        print(f"  - {port}")
        info = LaserController.get_port_info(port)
        if info:
            print(f"    {info.get('description', 'N/A')}")
    
    print("\nPossibili porte laser:")
    for port, desc in find_laser_ports():
        print(f"  - {port}: {desc}")
    
    # Test simulazione
    print("\nTest modalità simulazione:")
    ctrl = LaserController()
    ctrl.set_simulation(True)
    
    if ctrl.connect("SIM", 115200):
        resp = ctrl.send_command("G0 X10 Y10")
        print(f"  Risposta: {resp}")
        ctrl.disconnect()
    
    print("\n=== Test completati ===")