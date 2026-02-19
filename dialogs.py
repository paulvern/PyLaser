#!/usr/bin/env python3
"""
dialogs.py
Finestre di dialogo per PyLaser

Include:
- PreferencesDialog: Impostazioni lingua e tema
- HelpWindow: Finestra help
- MaterialPresetDialog: Gestione preset materiali (NUOVO)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

# ══════════════════════════════════════════════════════════════════════════════
#  PRESET MATERIALI
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class MaterialPreset:
    """Preset parametri per un materiale."""
    name: str
    feed_rate: int = 1000
    power: int = 200
    passes: int = 1
    resolution: float = 0.1
    method: str = "Contours"
    notes: str = ""


class MaterialPresetManager:
    """Gestisce il salvataggio e caricamento dei preset materiali."""
    
    DEFAULT_FILE = Path(__file__).parent / ".material_presets.json"
    
    # Preset predefiniti
    DEFAULT_PRESETS = [
        MaterialPreset("Compensato 3mm", 800, 255, 2, 0.1, "Contours", "Taglio"),
        MaterialPreset("Compensato 3mm Incisione", 1500, 180, 1, 0.1, "Contours", ""),
        MaterialPreset("MDF 3mm", 600, 255, 2, 0.1, "Contours", ""),
        MaterialPreset("Cartone", 2000, 150, 1, 0.1, "Raster", ""),
        MaterialPreset("Pelle", 1200, 200, 1, 0.15, "Contours", ""),
        MaterialPreset("Acrilico 3mm", 400, 255, 3, 0.1, "Contours", "Attenzione fumi"),
        MaterialPreset("Legno duro", 500, 255, 3, 0.1, "Contours", ""),
        MaterialPreset("Foto su legno", 1000, 180, 1, 0.08, "Raster", "Grayscale"),
    ]
    
    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or self.DEFAULT_FILE
        self.presets: Dict[str, MaterialPreset] = {}
        self.load()
    
    def load(self):
        """Carica i preset dal file."""
        self.presets = {}
        
        # Carica preset predefiniti
        for p in self.DEFAULT_PRESETS:
            self.presets[p.name] = p
        
        # Carica preset utente
        try:
            if self.filepath.exists():
                data = json.loads(self.filepath.read_text())
                for name, values in data.items():
                    self.presets[name] = MaterialPreset(**values)
        except Exception as e:
            print(f"Errore caricamento preset: {e}")
    
    def save(self):
        """Salva i preset su file."""
        try:
            data = {name: asdict(preset) for name, preset in self.presets.items()}
            self.filepath.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Errore salvataggio preset: {e}")
    
    def get(self, name: str) -> Optional[MaterialPreset]:
        """Ottiene un preset per nome."""
        return self.presets.get(name)
    
    def add(self, preset: MaterialPreset):
        """Aggiunge o aggiorna un preset."""
        self.presets[preset.name] = preset
        self.save()
    
    def remove(self, name: str):
        """Rimuove un preset."""
        if name in self.presets:
            del self.presets[name]
            self.save()
    
    def list_names(self) -> List[str]:
        """Restituisce la lista dei nomi preset."""
        return sorted(self.presets.keys())


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG PRESET MATERIALI
# ══════════════════════════════════════════════════════════════════════════════
class MaterialPresetDialog(tk.Toplevel):
    """Dialog per gestione preset materiali."""
    
    def __init__(self, parent, preset_manager: MaterialPresetManager,
                 theme, strings=None, on_apply=None):
        super().__init__(parent)
        
        self.manager = preset_manager
        self.theme = theme
        self.s = strings
        self.on_apply = on_apply
        self.selected_preset = None
        
        t = theme
        self.title("📦 Material Presets" if not strings else "📦 Preset Materiali")
        self.geometry("500x450")
        self.configure(bg=t.base)
        self.resizable(False, False)
        
        # Frame principale
        main = tk.Frame(self, bg=t.base)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Lista preset
        list_frame = tk.LabelFrame(main, text="Preset disponibili",
                                   bg=t.base, fg=t.blue,
                                   font=("Segoe UI", 10, "bold"))
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.listbox = tk.Listbox(list_frame, bg=t.surface0, fg=t.text,
                                  font=("Consolas", 10),
                                  selectbackground=t.blue,
                                  selectforeground=t.base,
                                  height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        self._refresh_list()
        
        # Dettagli preset
        detail_frame = tk.LabelFrame(main, text="Dettagli",
                                     bg=t.base, fg=t.blue,
                                     font=("Segoe UI", 10, "bold"))
        detail_frame.pack(fill="x", pady=(0, 10))
        
        self.detail_text = tk.Text(detail_frame, bg=t.surface0, fg=t.text,
                                   font=("Consolas", 9), height=5,
                                   state="disabled")
        self.detail_text.pack(fill="x", padx=5, pady=5)
        
        # Pulsanti
        btn_frame = tk.Frame(main, bg=t.base)
        btn_frame.pack(fill="x")
        
        tk.Button(btn_frame, text="✅ Applica",
                 bg=t.green, fg=t.base,
                 font=("Segoe UI", 9, "bold"),
                 command=self._apply).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="➕ Nuovo",
                 bg=t.blue, fg=t.base,
                 font=("Segoe UI", 9),
                 command=self._new).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="✏ Modifica",
                 bg=t.surface0, fg=t.text,
                 font=("Segoe UI", 9),
                 command=self._edit).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="🗑 Elimina",
                 bg=t.red, fg=t.base,
                 font=("Segoe UI", 9),
                 command=self._delete).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="✖ Chiudi",
                 bg=t.surface0, fg=t.text,
                 font=("Segoe UI", 9),
                 command=self.destroy).pack(side="right", padx=2)
    
    def _refresh_list(self):
        """Aggiorna la lista preset."""
        self.listbox.delete(0, "end")
        for name in self.manager.list_names():
            self.listbox.insert("end", name)
    
    def _on_select(self, event):
        """Gestisce selezione preset."""
        sel = self.listbox.curselection()
        if not sel:
            return
        
        name = self.listbox.get(sel[0])
        preset = self.manager.get(name)
        
        if preset:
            self.selected_preset = preset
            self._show_details(preset)
    
    def _show_details(self, preset: MaterialPreset):
        """Mostra i dettagli del preset."""
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        
        details = f"""Nome: {preset.name}
Velocità: {preset.feed_rate} mm/min
Potenza: {preset.power}
Passate: {preset.passes}
Risoluzione: {preset.resolution} mm
Metodo: {preset.method}
Note: {preset.notes}"""
        
        self.detail_text.insert("1.0", details)
        self.detail_text.config(state="disabled")
    
    def _apply(self):
        """Applica il preset selezionato."""
        if self.selected_preset and self.on_apply:
            self.on_apply(self.selected_preset)
            self.destroy()
    
    def _new(self):
        """Crea nuovo preset."""
        EditPresetDialog(self, self.manager, self.theme,
                        on_save=self._refresh_list)
    
    def _edit(self):
        """Modifica preset selezionato."""
        if self.selected_preset:
            EditPresetDialog(self, self.manager, self.theme,
                            preset=self.selected_preset,
                            on_save=self._refresh_list)
    
    def _delete(self):
        """Elimina preset selezionato."""
        if self.selected_preset:
            if messagebox.askyesno("Conferma",
                                   f"Eliminare '{self.selected_preset.name}'?"):
                self.manager.remove(self.selected_preset.name)
                self.selected_preset = None
                self._refresh_list()


class EditPresetDialog(tk.Toplevel):
    """Dialog per creare/modificare un preset."""
    
    def __init__(self, parent, manager: MaterialPresetManager, theme,
                 preset: Optional[MaterialPreset] = None, on_save=None):
        super().__init__(parent)
        
        self.manager = manager
        self.theme = theme
        self.on_save = on_save
        self.editing = preset is not None
        
        t = theme
        self.title("Modifica Preset" if self.editing else "Nuovo Preset")
        self.geometry("350x350")
        self.configure(bg=t.base)
        self.resizable(False, False)
        self.grab_set()
        
        # Campi
        fields = [
            ("Nome:", "name", preset.name if preset else ""),
            ("Velocità (mm/min):", "feed", preset.feed_rate if preset else 1000),
            ("Potenza (0-255):", "power", preset.power if preset else 200),
            ("Passate:", "passes", preset.passes if preset else 1),
            ("Risoluzione (mm):", "resolution", preset.resolution if preset else 0.1),
            ("Note:", "notes", preset.notes if preset else ""),
        ]
        
        self.vars = {}
        for i, (label, key, default) in enumerate(fields):
            tk.Label(self, text=label, bg=t.base, fg=t.text).grid(
                row=i, column=0, sticky="w", padx=10, pady=5)
            
            if isinstance(default, (int, float)):
                var = tk.DoubleVar(value=default) if isinstance(default, float) else tk.IntVar(value=default)
            else:
                var = tk.StringVar(value=default)
            
            self.vars[key] = var
            tk.Entry(self, textvariable=var, bg=t.surface0, fg=t.text).grid(
                row=i, column=1, sticky="ew", padx=10, pady=5)
        
        # Metodo
        tk.Label(self, text="Metodo:", bg=t.base, fg=t.text).grid(
            row=len(fields), column=0, sticky="w", padx=10, pady=5)
        
        self.vars["method"] = tk.StringVar(value=preset.method if preset else "Contours")
        ttk.Combobox(self, textvariable=self.vars["method"],
                    values=["Contours", "Centerline", "Raster", "Hatching"],
                    state="readonly").grid(row=len(fields), column=1, sticky="ew", padx=10, pady=5)
        
        # Pulsanti
        btn_frame = tk.Frame(self, bg=t.base)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Salva", bg=t.green, fg=t.base,
                 command=self._save).pack(side="left", padx=5)
        tk.Button(btn_frame, text="✖ Annulla", bg=t.surface0, fg=t.text,
                 command=self.destroy).pack(side="left", padx=5)
        
        self.columnconfigure(1, weight=1)
    
    def _save(self):
        """Salva il preset."""
        try:
            preset = MaterialPreset(
                name=self.vars["name"].get(),
                feed_rate=int(self.vars["feed"].get()),
                power=int(self.vars["power"].get()),
                passes=int(self.vars["passes"].get()),
                resolution=float(self.vars["resolution"].get()),
                method=self.vars["method"].get(),
                notes=self.vars["notes"].get()
            )
            
            self.manager.add(preset)
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Dati non validi: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  PREFERENCES DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class PreferencesDialog(tk.Toplevel):
    """Dialog per preferenze lingua e tema."""
    
    def __init__(self, parent, current_lang: str, current_theme: str,
                 theme, available_languages, available_themes):
        super().__init__(parent)
        
        t = self.theme = theme
        self.result_lang = current_lang
        self.result_theme = current_theme
        
        self.title("⚙ Preferences / Preferenze")
        self.resizable(False, False)
        self.configure(bg=t.base)
        self.grab_set()
        
        # Lingua
        lf1 = tk.LabelFrame(self, text="🌐 Language / Lingua",
                           bg=t.base, fg=t.blue,
                           font=("Segoe UI", 10, "bold"))
        lf1.pack(fill="x", padx=16, pady=(16, 8))
        
        self.lang_var = tk.StringVar(value=current_lang)
        for lang in available_languages:
            tk.Radiobutton(lf1, text=lang, variable=self.lang_var, value=lang,
                          bg=t.base, fg=t.text, selectcolor=t.surface0,
                          activebackground=t.base, activeforeground=t.blue,
                          font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=2)
        
        # Tema
        lf2 = tk.LabelFrame(self, text="🎨 Theme / Tema",
                           bg=t.base, fg=t.blue,
                           font=("Segoe UI", 10, "bold"))
        lf2.pack(fill="x", padx=16, pady=8)
        
        self.theme_var = tk.StringVar(value=current_theme)
        for theme_name in available_themes:
            tk.Radiobutton(lf2, text=theme_name, variable=self.theme_var, value=theme_name,
                          bg=t.base, fg=t.text, selectcolor=t.surface0,
                          activebackground=t.base, activeforeground=t.blue,
                          font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=2)
        
        # Nota riavvio
        tk.Label(self,
                text="⚠ Changes require restart / Le modifiche richiedono riavvio",
                bg=t.base, fg=t.yellow,
                font=("Segoe UI", 8)).pack(pady=(8, 4))
        
        # Pulsanti
        btn_frm = tk.Frame(self, bg=t.base)
        btn_frm.pack(pady=(8, 16))
        
        tk.Button(btn_frm, text="✔  OK", bg=t.green, fg=t.base,
                 font=("Segoe UI", 9, "bold"), relief="flat",
                 padx=20, pady=6, command=self._ok).pack(side="left", padx=6)
        
        tk.Button(btn_frm, text="✘  Cancel", bg=t.surface0, fg=t.text,
                 font=("Segoe UI", 9), relief="flat",
                 padx=16, pady=6, command=self.destroy).pack(side="left", padx=6)
        
        self.transient(parent)
        self.wait_window()
    
    def _ok(self):
        self.result_lang = self.lang_var.get()
        self.result_theme = self.theme_var.get()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  HELP WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class HelpWindow(tk.Toplevel):
    """Finestra help."""
    
    def __init__(self, parent, theme, help_content, app_version: str = ""):
        super().__init__(parent)
        
        t = self.theme = theme
        h = self.help = help_content
        
        self.title(h.title_main)
        self.geometry("900x700")
        self.minsize(700, 500)
        self.configure(bg=t.base)
        
        # Pannello principale
        main_paned = tk.PanedWindow(self, orient="horizontal",
                                   bg=t.base, sashwidth=4)
        main_paned.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Sidebar
        sidebar = tk.Frame(main_paned, bg=t.mantle)
        main_paned.add(sidebar, minsize=200)
        
        tk.Label(sidebar, text="📚 " + h.title_main,
                bg=t.mantle, fg=t.blue,
                font=("Segoe UI", 11, "bold")).pack(padx=8, pady=(12, 8))
        
        # Sezioni
        self.sections = [
            (h.title_getting_started, h.getting_started),
            (h.title_image, h.image_section),
            (h.title_vectorize, h.vectorize_section),
            (h.title_position, h.position_section),
            (h.title_laser, h.laser_section),
            (h.title_simulation, h.simulation_section),
            (h.title_shortcuts, h.shortcuts_section),
            (h.title_gcode, h.gcode_section),
            (h.title_troubleshooting, h.troubleshooting),
            (h.title_safety, h.safety_section),
        ]
        
        for title, content in self.sections:
            btn = tk.Button(sidebar, text=title,
                           bg=t.surface0, fg=t.text,
                           activebackground=t.blue, activeforeground=t.base,
                           relief="flat", anchor="w",
                           padx=12, pady=6, font=("Segoe UI", 9),
                           command=lambda c=content, ti=title: self._show_section(ti, c))
            btn.pack(fill="x", padx=4, pady=1)
        
        # Contenuto
        content_frame = tk.Frame(main_paned, bg=t.base)
        main_paned.add(content_frame, minsize=450)
        
        self.content_title = tk.Label(content_frame,
                                      text=h.title_getting_started,
                                      bg=t.base, fg=t.blue,
                                      font=("Segoe UI", 12, "bold"))
        self.content_title.pack(anchor="w", padx=8, pady=(8, 4))
        
        self.content_text = scrolledtext.ScrolledText(content_frame,
                                                      bg=t.surface0, fg=t.text,
                                                      font=("Consolas", 9),
                                                      wrap="word", borderwidth=0,
                                                      insertbackground=t.text,
                                                      selectbackground=t.blue,
                                                      selectforeground=t.base)
        self.content_text.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Mostra prima sezione
        self._show_section(h.title_getting_started, h.getting_started)
        
        # Footer
        footer = tk.Frame(self, bg=t.mantle)
        footer.pack(fill="x")
        
        tk.Label(footer, text=f"PyLaser {app_version}",
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