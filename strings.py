#!/usr/bin/env python3
"""
strings.py
Sistema di localizzazione per Py Laser
Lingue disponibili: Italiano, English, Español, Deutsch
Per aggiungere una nuova lingua: copia un blocco esistente,
cambia il codice lingua e traduci tutti i valori.
"""

from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
#  STRUTTURA STRINGHE
#  Ogni campo corrisponde a una stringa usata nell'interfaccia.
#  Aggiungi qui nuovi campi se aggiungi nuove stringhe all'app.
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Strings:

    # ── Generale ──────────────────────────────────────────────────────────────
    app_title              : str = ""
    app_version_prefix     : str = ""
    ready                  : str = ""
    error                  : str = ""
    warning                : str = ""
    info                   : str = ""
    confirm                : str = ""
    yes                    : str = ""
    no                     : str = ""
    ok                     : str = ""
    cancel                 : str = ""
    apply                  : str = ""
    close                  : str = ""
    save                   : str = ""
    load                   : str = ""
    open                   : str = ""
    none_loaded            : str = ""
    completed              : str = ""
    stopped                : str = ""
    running                : str = ""
    simulation_mode        : str = ""

    # ── Menu File ─────────────────────────────────────────────────────────────
    menu_file              : str = ""
    menu_open_image        : str = ""
    menu_save_gcode        : str = ""
    menu_load_gcode        : str = ""
    menu_exit              : str = ""

    # ── Menu Visualizza ───────────────────────────────────────────────────────
    menu_view              : str = ""
    menu_vector_preview    : str = ""
    menu_gcode_text        : str = ""
    menu_fit_view          : str = ""

    # ── Menu Laser ────────────────────────────────────────────────────────────
    menu_laser             : str = ""
    menu_send_bbox         : str = ""
    menu_emergency_stop    : str = ""

    # ── Header / Status ───────────────────────────────────────────────────────
    status_ready           : str = ""
    status_generating      : str = ""
    status_gcode_ready     : str = ""
    status_gen_error       : str = ""
    status_engraving       : str = ""
    status_completed       : str = ""
    status_stopped         : str = ""
    status_emergency       : str = ""
    status_simulation      : str = ""
    status_sim_completed   : str = ""

    # ── Tab Immagine ──────────────────────────────────────────────────────────
    tab_image              : str = ""
    lf_import              : str = ""
    btn_open_image         : str = ""
    lbl_no_image           : str = ""
    lf_rotation            : str = ""
    btn_rot_left           : str = ""
    btn_rot_right          : str = ""
    btn_rot_180            : str = ""
    lbl_rotation           : str = ""
    lf_flip                : str = ""
    btn_flip_h             : str = ""
    btn_flip_v             : str = ""
    lf_preprocess          : str = ""
    lbl_threshold          : str = ""
    lbl_blur               : str = ""
    chk_invert             : str = ""
    chk_denoise            : str = ""
    btn_update_preview     : str = ""

    # ── Tab Vettorizza ────────────────────────────────────────────────────────
    tab_vectorize          : str = ""
    lf_method              : str = ""
    lbl_strategy           : str = ""
    method_contours        : str = ""
    method_centerline      : str = ""
    method_raster          : str = ""
    method_hatching        : str = ""
    lf_dimensions          : str = ""
    lbl_width_mm           : str = ""
    lbl_height_mm          : str = ""
    chk_keep_ratio         : str = ""
    lf_advanced            : str = ""
    lbl_simplify           : str = ""
    lbl_gap                : str = ""
    lbl_hatch_angle        : str = ""
    lbl_feed_rate          : str = ""
    lbl_power              : str = ""
    lbl_passes             : str = ""
    btn_generate_gcode     : str = ""
    lf_gcode_info          : str = ""
    lbl_no_gcode           : str = ""
    btn_save_gcode         : str = ""
    btn_gcode_text         : str = ""
    btn_vector_preview     : str = ""
    lf_simulation          : str = ""
    lbl_sim_speed          : str = ""
    btn_start_sim          : str = ""
    btn_stop_sim           : str = ""

    # ── Tab Posizione ─────────────────────────────────────────────────────────
    tab_position           : str = ""
    lf_work_area           : str = ""
    lbl_work_width         : str = ""
    lbl_work_height        : str = ""
    btn_apply_work_area    : str = ""
    lf_model_position      : str = ""
    lbl_model_x            : str = ""
    lbl_model_y            : str = ""
    btn_apply_position     : str = ""
    lf_quick_position      : str = ""
    btn_pos_center         : str = ""
    btn_pos_tl             : str = ""
    btn_pos_tr             : str = ""
    btn_pos_bl             : str = ""
    btn_pos_br             : str = ""
    lf_bbox_preview        : str = ""
    lbl_bbox_desc          : str = ""
    lbl_bbox_feed          : str = ""
    btn_send_bbox          : str = ""
    lf_model_info          : str = ""
    lbl_no_model           : str = ""

    # ── Tab Laser ─────────────────────────────────────────────────────────────
    tab_laser              : str = ""
    lf_connection          : str = ""
    lbl_port               : str = ""
    lbl_baud               : str = ""
    chk_simulation         : str = ""
    btn_connect            : str = ""
    btn_disconnect         : str = ""
    lbl_not_connected      : str = ""
    lf_home                : str = ""
    lbl_home_desc          : str = ""
    lbl_jog_step           : str = ""
    lbl_jog_feed           : str = ""
    btn_set_home           : str = ""
    btn_goto_home          : str = ""
    btn_unlock             : str = ""
    lf_manual_cmd          : str = ""
    btn_send_cmd           : str = ""
    lf_send_gcode          : str = ""
    btn_start_engraving    : str = ""
    btn_stop_engraving     : str = ""
    btn_emergency_stop     : str = ""
    lbl_waiting            : str = ""

    # ── Canvas Area di lavoro ─────────────────────────────────────────────────
    canvas_work_area_title : str = ""
    canvas_hint            : str = ""
    canvas_home_label      : str = ""
    canvas_area_label      : str = ""

    # ── Preview vettoriale ────────────────────────────────────────────────────
    preview_title          : str = ""
    preview_hint           : str = ""
    preview_stats          : str = ""
    preview_btn_fit        : str = ""
    legend_laser_on        : str = ""
    legend_rapid           : str = ""
    legend_bbox            : str = ""
    legend_origin          : str = ""

    # ── Preview immagini (bottom) ─────────────────────────────────────────────
    preview_original       : str = ""
    preview_processed      : str = ""
    lbl_log                : str = ""
    btn_clear_log          : str = ""

    # ── Messaggi di log ───────────────────────────────────────────────────────
    log_image_opened       : str = ""
    log_rotated            : str = ""
    log_flipped_h          : str = ""
    log_flipped_v          : str = ""
    log_preprocess_error   : str = ""
    log_generating         : str = ""
    log_gcode_generated    : str = ""
    log_gen_error          : str = ""
    log_saved              : str = ""
    log_loaded             : str = ""
    log_connected          : str = ""
    log_fw                 : str = ""
    log_connect_error      : str = ""
    log_disconnected       : str = ""
    log_jog                : str = ""
    log_home_set           : str = ""
    log_goto_home          : str = ""
    log_sim_started        : str = ""
    log_sim_completed      : str = ""
    log_sim_stopped        : str = ""
    log_bbox_sending       : str = ""
    log_bbox_done          : str = ""
    log_engraving_started  : str = ""
    log_engraving_done     : str = ""
    log_stop_requested     : str = ""
    log_emergency          : str = ""
    log_send_stopped       : str = ""
    log_send_error         : str = ""
    log_contours_found     : str = ""
    log_raster_info        : str = ""
    log_hatch_info         : str = ""
    log_tx_error           : str = ""
    log_alarm              : str = ""
    log_work_area_set      : str = ""
    log_model_position     : str = ""
    log_quick_pos          : str = ""
    log_test_laser         : str = ""
    log_simulation_on      : str = ""

    # ── Dialoghi di conferma ──────────────────────────────────────────────────
    dlg_start_title        : str = ""
    dlg_start_body         : str = ""
    dlg_start_sim_note     : str = ""
    dlg_start_safe_note    : str = ""
    dlg_completed_title    : str = ""
    dlg_completed_body     : str = ""
    dlg_emergency_title    : str = ""
    dlg_emergency_body     : str = ""

    # ── Errori e avvisi ───────────────────────────────────────────────────────
    err_no_image           : str = ""
    err_no_gcode           : str = ""
    err_no_model           : str = ""
    err_not_connected      : str = ""
    err_no_port            : str = ""
    err_image_open         : str = ""
    err_missing_libs       : str = ""
    err_pyserial_missing   : str = ""

    # ── Info modello (canvas) ─────────────────────────────────────────────────
    info_model_size        : str = ""
    info_model_origin      : str = ""
    info_model_extent_x    : str = ""
    info_model_extent_y    : str = ""

    # ── GCode info ────────────────────────────────────────────────────────────
    gcode_lines            : str = ""
    gcode_moves            : str = ""
    gcode_laser_on         : str = ""
    gcode_laser_off        : str = ""
    gcode_area             : str = ""
    gcode_feed             : str = ""
    gcode_power            : str = ""
    gcode_passes           : str = ""
    gcode_view_title       : str = ""

    # ── Dipendenze ────────────────────────────────────────────────────────────
    dep_missing_title      : str = ""
    dep_missing_body       : str = ""
    dep_pyserial_warn      : str = ""


# ══════════════════════════════════════════════════════════════════════════════
#  ITALIANO  (it)
# ══════════════════════════════════════════════════════════════════════════════
IT = Strings(
    # Generale
    app_title              = "Py Laser",
    app_version_prefix     = "v",
    ready                  = "Pronto",
    error                  = "Errore",
    warning                = "Attenzione",
    info                   = "Informazioni",
    confirm                = "Conferma",
    yes                    = "Sì",
    no                     = "No",
    ok                     = "OK",
    cancel                 = "Annulla",
    apply                  = "Applica",
    close                  = "Chiudi",
    save                   = "Salva",
    load                   = "Carica",
    open                   = "Apri",
    none_loaded            = "Nessun elemento caricato",
    completed              = "Completato",
    stopped                = "Interrotto",
    running                = "In esecuzione",
    simulation_mode        = "Simulazione",

    # Menu File
    menu_file              = "File",
    menu_open_image        = "Apri immagine…",
    menu_save_gcode        = "Salva GCode…",
    menu_load_gcode        = "Carica GCode…",
    menu_exit              = "Esci",

    # Menu Visualizza
    menu_view              = "Visualizza",
    menu_vector_preview    = "Anteprima vettoriale",
    menu_gcode_text        = "Visualizza GCode testo",
    menu_fit_view          = "Adatta vista",

    # Menu Laser
    menu_laser             = "Laser",
    menu_send_bbox         = "Invia contorno (bbox)",
    menu_emergency_stop    = "Emergency Stop",

    # Status
    status_ready           = "Pronto",
    status_generating      = "Generazione GCode…",
    status_gcode_ready     = "GCode pronto",
    status_gen_error       = "Errore generazione",
    status_engraving       = "Incisione in corso…",
    status_completed       = "Completato",
    status_stopped         = "Stop…",
    status_emergency       = "EMERGENCY STOP",
    status_simulation      = "Simulazione in corso…",
    status_sim_completed   = "Simulazione completata",

    # Tab Immagine
    tab_image              = "  🖼 Immagine  ",
    lf_import              = "📂 Importa immagine",
    btn_open_image         = "Apri immagine…",
    lbl_no_image           = "Nessuna immagine caricata",
    lf_rotation            = "🔄 Rotazione",
    btn_rot_left           = "↺ 90° SX",
    btn_rot_right          = "↻ 90° DX",
    btn_rot_180            = "↕ 180°",
    lbl_rotation           = "Rotazione: 0°",
    lf_flip                = "↔ Specchia",
    btn_flip_h             = "↔ Orizzontale",
    btn_flip_v             = "↕ Verticale",
    lf_preprocess          = "⚙ Pre-elaborazione",
    lbl_threshold          = "Soglia (threshold)",
    lbl_blur               = "Sfocatura (blur)",
    chk_invert             = "Inverti colori",
    chk_denoise            = "Riduci rumore",
    btn_update_preview     = "↻ Aggiorna",

    # Tab Vettorizza
    tab_vectorize          = "  ✏ Vettorizza  ",
    lf_method              = "🔧 Metodo",
    lbl_strategy           = "Strategia:",
    method_contours        = "Contorni",
    method_centerline      = "Centerline",
    method_raster          = "Raster",
    method_hatching        = "Hatching",
    lf_dimensions          = "📐 Dimensioni",
    lbl_width_mm           = "Larghezza (mm):",
    lbl_height_mm          = "Altezza (mm):",
    chk_keep_ratio         = "Mantieni proporzioni",
    lf_advanced            = "🔩 Opzioni avanzate",
    lbl_simplify           = "Semplificazione",
    lbl_gap                = "Gap linee (×0.1 mm)",
    lbl_hatch_angle        = "Angolo hatch (°)",
    lbl_feed_rate          = "Velocità (mm/min)",
    lbl_power              = "Potenza S (0-255)",
    lbl_passes             = "Passate",
    btn_generate_gcode     = "🚀  Genera GCode",
    lf_gcode_info          = "📊 GCode",
    lbl_no_gcode           = "—",
    btn_save_gcode         = "💾 Salva GCode",
    btn_gcode_text         = "📋 Testo GCode",
    btn_vector_preview     = "🔍 Preview vett.",
    lf_simulation          = "🎬 Simulazione",
    lbl_sim_speed          = "Velocità sim (×)",
    btn_start_sim          = "▶ Avvia sim.",
    btn_stop_sim           = "⏹ Stop sim.",

    # Tab Posizione
    tab_position           = "  📍 Posizione  ",
    lf_work_area           = "📏 Area di lavoro macchina (mm)",
    lbl_work_width         = "Larghezza:",
    lbl_work_height        = "Altezza:",
    btn_apply_work_area    = "Applica dimensioni",
    lf_model_position      = "📍 Posizione modello (mm)",
    lbl_model_x            = "X origine:",
    lbl_model_y            = "Y origine:",
    btn_apply_position     = "Applica posizione",
    lf_quick_position      = "⊞ Posizionamento rapido",
    btn_pos_center         = "Centro",
    btn_pos_tl             = "↖ In alto SX",
    btn_pos_tr             = "↗ In alto DX",
    btn_pos_bl             = "↙ In basso SX",
    btn_pos_br             = "↘ In basso DX",
    lf_bbox_preview        = "📦 Anteprima contorno fisico",
    lbl_bbox_desc          = "Muove il laser lungo il perimetro\ndel modello a laser SPENTO.",
    lbl_bbox_feed          = "Velocità anteprima (mm/min)",
    btn_send_bbox          = "📦 Invia contorno al laser",
    lf_model_info          = "ℹ Informazioni modello",
    lbl_no_model           = "Nessun modello caricato",

    # Tab Laser
    tab_laser              = "  🔥 Laser  ",
    lf_connection          = "🔌 Connessione COM",
    lbl_port               = "Porta:",
    lbl_baud               = "Baud:",
    chk_simulation         = "Modalità simulazione (offline)",
    btn_connect            = "Connetti",
    btn_disconnect         = "Disconnetti",
    lbl_not_connected      = "⚫  Non connesso",
    lf_home                = "🏠 Impostazione Home manuale",
    lbl_home_desc          = "Usa il JOG per posizionare il laser,\npoi premi 'Imposta Home qui'.",
    lbl_jog_step           = "Passo (mm):",
    lbl_jog_feed           = "F:",
    btn_set_home           = "🏠 Imposta Home qui  (G92 X0 Y0)",
    btn_goto_home          = "⏮ Vai all'Home  (G0 X0 Y0)",
    btn_unlock             = "🔓 Unlock Alarm ($X)",
    lf_manual_cmd          = "💻 Comando manuale",
    btn_send_cmd           = "Invia",
    lf_send_gcode          = "📤 Invio GCode",
    btn_start_engraving    = "▶ Avvia incisione",
    btn_stop_engraving     = "⏹ Stop",
    btn_emergency_stop     = "🚨 EMERGENCY STOP",
    lbl_waiting            = "In attesa…",

    # Canvas
    canvas_work_area_title = "🗺 Area di Lavoro  (drag=sposta modello | rotella=zoom | destro=pan)",
    canvas_hint            = "Area: {w}×{h} mm",
    canvas_home_label      = "HOME",
    canvas_area_label      = "Area: {w}×{h} mm",

    # Preview vettoriale
    preview_title          = "Anteprima Vettoriale",
    preview_hint           = "🔍 Zoom: rotella  |  🖱 Pan: tasto destro  |  🔵=laser ON  ⚫=laser OFF  ──=rapido",
    preview_stats          = "Movimenti totali: {total}  |  Laser ON: {on}  |  Laser OFF (rapidi): {off}",
    preview_btn_fit        = "⊡ Fit",
    legend_laser_on        = "━━ Incisione (laser ON)",
    legend_rapid           = "╌╌ Movimento rapido (laser OFF)",
    legend_bbox            = "□  Bounding box",
    legend_origin          = "⊕  Origine / Home",

    # Preview immagini
    preview_original       = "Originale",
    preview_processed      = "Elaborata (B/N)",
    lbl_log                = "📝 Log",
    btn_clear_log          = "Pulisci",

    # Log
    log_image_opened       = "🖼 Aperta: {path}",
    log_rotated            = "🔄 Ruotato {deg:+d}° → totale {total}°",
    log_flipped_h          = "↔ Specchiato orizzontalmente",
    log_flipped_v          = "↕ Specchiato verticalmente",
    log_preprocess_error   = "❌ Preprocess: {err}",
    log_generating         = "🔧 Genera GCode: {method} | {w}×{h} mm",
    log_gcode_generated    = "✅ GCode generato: {lines} righe",
    log_gen_error          = "❌ Errore generazione: {err}",
    log_saved              = "💾 Salvato: {path}",
    log_loaded             = "📂 Caricato: {path}  ({lines} righe, {moves} movimenti)",
    log_connected          = "✅ Connesso {port}@{baud}",
    log_fw                 = "   FW: {fw}",
    log_connect_error      = "❌ Connessione fallita: {err}",
    log_disconnected       = "🔌 Disconnesso",
    log_jog                = "🕹 JOG {axis}{dist:+.1f} mm",
    log_home_set           = "🏠 Home impostato qui (G92 X0 Y0)",
    log_goto_home          = "🏠 Vai a Home",
    log_sim_started        = "🎬 Simulazione avviata (×{speed})",
    log_sim_completed      = "✅ Simulazione completata",
    log_sim_stopped        = "⏹ Simulazione fermata",
    log_bbox_sending       = "📦 Invio contorno fisico (F{feed}, laser OFF)…",
    log_bbox_done          = "✅ Contorno completato",
    log_engraving_started  = "▶ Incisione avviata",
    log_engraving_done     = "✅ Fine. Errori: {errors}",
    log_stop_requested     = "⛔ Stop richiesto",
    log_emergency          = "🚨 EMERGENCY STOP",
    log_send_stopped       = "⛔ Stop",
    log_send_error         = "⚠ Errore riga {line}: {cmd!r} → {resp}",
    log_contours_found     = "   Contorni: {n}",
    log_raster_info        = "   Raster: {rows} righe, {segs} segmenti accesi",
    log_hatch_info         = "   Hatching {angle}°: {n} istruzioni",
    log_tx_error           = "⚠ TX: {err}",
    log_alarm              = "🚨 ALARM: {resp}",
    log_work_area_set      = "📏 Area di lavoro: {w}×{h} mm",
    log_model_position     = "📍 Posizione modello: X={x:.2f}  Y={y:.2f}",
    log_quick_pos          = "📍 Posizione rapida '{where}': X={x:.2f}  Y={y:.2f}",
    log_test_laser         = "💡 Test laser 0.5 s",
    log_simulation_on      = "🟡 Simulazione attiva",

    # Dialoghi
    dlg_start_title        = "Conferma incisione",
    dlg_start_body         = (
        "Avviare l'incisione?\n\n"
        "  Area: {w:.1f}×{h:.1f} mm\n"
        "  Posizione: X={ox:.1f}  Y={oy:.1f}\n"
        "  Righe GCode: {lines}"
    ),
    dlg_start_sim_note     = "\n⚠ SIMULAZIONE — nessun laser reale",
    dlg_start_safe_note    = "\n⚠ Assicurati che il percorso sia libero!",
    dlg_completed_title    = "Completato",
    dlg_completed_body     = "Incisione completata con successo!",
    dlg_emergency_title    = "EMERGENCY STOP",
    dlg_emergency_body     = "Soft reset inviato!\nEsegui 'Unlock' prima di riprendere.",

    # Errori
    err_no_image           = "Carica prima un'immagine",
    err_no_gcode           = "Genera prima il GCode",
    err_no_model           = "Nessun modello caricato",
    err_not_connected      = "Connettiti prima all'incisore",
    err_no_port            = "Seleziona una porta COM valida",
    err_image_open         = "Impossibile aprire l'immagine:\n{err}",
    err_missing_libs       = "Librerie mancanti:\n{libs}",
    err_pyserial_missing   = "⚠ pyserial non trovato → solo modalità simulazione",

    # Info modello
    info_model_size        = "Dimensioni modello: {w:.2f} × {h:.2f} mm",
    info_model_origin      = "Posizione origine:  X={x:.2f}  Y={y:.2f}",
    info_model_extent_x    = "Estensione X: {x0:.2f} → {x1:.2f} mm",
    info_model_extent_y    = "Estensione Y: {y0:.2f} → {y1:.2f} mm",

    # GCode info
    gcode_lines            = "✅  {n} righe | {moves} movimenti",
    gcode_laser_on         = "    Laser ON: {on}",
    gcode_laser_off        = " | OFF: {off}",
    gcode_area             = "    Area: {w:.1f}×{h:.1f} mm",
    gcode_feed             = "    Feed:{feed}",
    gcode_power            = " | S:{power}",
    gcode_passes           = " | ×{passes}",
    gcode_view_title       = "GCode",

    # Dipendenze
    dep_missing_title      = "Librerie mancanti",
    dep_missing_body       = "pip install {lib}",
    dep_pyserial_warn      = "pyserial non installato → solo simulazione",
)


# ══════════════════════════════════════════════════════════════════════════════
#  ENGLISH  (en)
# ══════════════════════════════════════════════════════════════════════════════
EN = Strings(
    # General
    app_title              = "Py Laser",
    app_version_prefix     = "v",
    ready                  = "Ready",
    error                  = "Error",
    warning                = "Warning",
    info                   = "Information",
    confirm                = "Confirm",
    yes                    = "Yes",
    no                     = "No",
    ok                     = "OK",
    cancel                 = "Cancel",
    apply                  = "Apply",
    close                  = "Close",
    save                   = "Save",
    load                   = "Load",
    open                   = "Open",
    none_loaded            = "Nothing loaded",
    completed              = "Completed",
    stopped                = "Stopped",
    running                = "Running",
    simulation_mode        = "Simulation",

    # Menu File
    menu_file              = "File",
    menu_open_image        = "Open image…",
    menu_save_gcode        = "Save GCode…",
    menu_load_gcode        = "Load GCode…",
    menu_exit              = "Exit",

    # Menu View
    menu_view              = "View",
    menu_vector_preview    = "Vector preview",
    menu_gcode_text        = "Show GCode text",
    menu_fit_view          = "Fit view",

    # Menu Laser
    menu_laser             = "Laser",
    menu_send_bbox         = "Send outline (bbox)",
    menu_emergency_stop    = "Emergency Stop",

    # Status
    status_ready           = "Ready",
    status_generating      = "Generating GCode…",
    status_gcode_ready     = "GCode ready",
    status_gen_error       = "Generation error",
    status_engraving       = "Engraving…",
    status_completed       = "Completed",
    status_stopped         = "Stopping…",
    status_emergency       = "EMERGENCY STOP",
    status_simulation      = "Simulation running…",
    status_sim_completed   = "Simulation completed",

    # Tab Image
    tab_image              = "  🖼 Image  ",
    lf_import              = "📂 Import image",
    btn_open_image         = "Open image…",
    lbl_no_image           = "No image loaded",
    lf_rotation            = "🔄 Rotation",
    btn_rot_left           = "↺ 90° Left",
    btn_rot_right          = "↻ 90° Right",
    btn_rot_180            = "↕ 180°",
    lbl_rotation           = "Rotation: 0°",
    lf_flip                = "↔ Mirror",
    btn_flip_h             = "↔ Horizontal",
    btn_flip_v             = "↕ Vertical",
    lf_preprocess          = "⚙ Pre-processing",
    lbl_threshold          = "Threshold",
    lbl_blur               = "Blur",
    chk_invert             = "Invert colors",
    chk_denoise            = "Reduce noise",
    btn_update_preview     = "↻ Update",

    # Tab Vectorize
    tab_vectorize          = "  ✏ Vectorize  ",
    lf_method              = "🔧 Method",
    lbl_strategy           = "Strategy:",
    method_contours        = "Contours",
    method_centerline      = "Centerline",
    method_raster          = "Raster",
    method_hatching        = "Hatching",
    lf_dimensions          = "📐 Dimensions",
    lbl_width_mm           = "Width (mm):",
    lbl_height_mm          = "Height (mm):",
    chk_keep_ratio         = "Keep aspect ratio",
    lf_advanced            = "🔩 Advanced options",
    lbl_simplify           = "Simplification",
    lbl_gap                = "Line gap (×0.1 mm)",
    lbl_hatch_angle        = "Hatch angle (°)",
    lbl_feed_rate          = "Feed rate (mm/min)",
    lbl_power              = "Power S (0-255)",
    lbl_passes             = "Passes",
    btn_generate_gcode     = "🚀  Generate GCode",
    lf_gcode_info          = "📊 GCode",
    lbl_no_gcode           = "—",
    btn_save_gcode         = "💾 Save GCode",
    btn_gcode_text         = "📋 GCode text",
    btn_vector_preview     = "🔍 Vec. preview",
    lf_simulation          = "🎬 Simulation",
    lbl_sim_speed          = "Sim speed (×)",
    btn_start_sim          = "▶ Start sim.",
    btn_stop_sim           = "⏹ Stop sim.",

    # Tab Position
    tab_position           = "  📍 Position  ",
    lf_work_area           = "📏 Machine work area (mm)",
    lbl_work_width         = "Width:",
    lbl_work_height        = "Height:",
    btn_apply_work_area    = "Apply dimensions",
    lf_model_position      = "📍 Model position (mm)",
    lbl_model_x            = "X origin:",
    lbl_model_y            = "Y origin:",
    btn_apply_position     = "Apply position",
    lf_quick_position      = "⊞ Quick positioning",
    btn_pos_center         = "Center",
    btn_pos_tl             = "↖ Top Left",
    btn_pos_tr             = "↗ Top Right",
    btn_pos_bl             = "↙ Bottom Left",
    btn_pos_br             = "↘ Bottom Right",
    lf_bbox_preview        = "📦 Physical outline preview",
    lbl_bbox_desc          = "Moves the laser along the model\nperimeter with laser OFF.",
    lbl_bbox_feed          = "Preview speed (mm/min)",
    btn_send_bbox          = "📦 Send outline to laser",
    lf_model_info          = "ℹ Model information",
    lbl_no_model           = "No model loaded",

    # Tab Laser
    tab_laser              = "  🔥 Laser  ",
    lf_connection          = "🔌 COM Connection",
    lbl_port               = "Port:",
    lbl_baud               = "Baud:",
    chk_simulation         = "Simulation mode (offline)",
    btn_connect            = "Connect",
    btn_disconnect         = "Disconnect",
    lbl_not_connected      = "⚫  Not connected",
    lf_home                = "🏠 Manual Home setting",
    lbl_home_desc          = "Use JOG to position the laser,\nthen press 'Set Home here'.",
    lbl_jog_step           = "Step (mm):",
    lbl_jog_feed           = "F:",
    btn_set_home           = "🏠 Set Home here  (G92 X0 Y0)",
    btn_goto_home          = "⏮ Go to Home  (G0 X0 Y0)",
    btn_unlock             = "🔓 Unlock Alarm ($X)",
    lf_manual_cmd          = "💻 Manual command",
    btn_send_cmd           = "Send",
    lf_send_gcode          = "📤 Send GCode",
    btn_start_engraving    = "▶ Start engraving",
    btn_stop_engraving     = "⏹ Stop",
    btn_emergency_stop     = "🚨 EMERGENCY STOP",
    lbl_waiting            = "Waiting…",

    # Canvas
    canvas_work_area_title = "🗺 Work Area  (drag=move model | wheel=zoom | right=pan)",
    canvas_hint            = "Area: {w}×{h} mm",
    canvas_home_label      = "HOME",
    canvas_area_label      = "Area: {w}×{h} mm",

    # Vector preview
    preview_title          = "Vector Preview",
    preview_hint           = "🔍 Zoom: wheel  |  🖱 Pan: right click  |  🔵=laser ON  ⚫=laser OFF  ──=rapid",
    preview_stats          = "Total moves: {total}  |  Laser ON: {on}  |  Laser OFF (rapid): {off}",
    preview_btn_fit        = "⊡ Fit",
    legend_laser_on        = "━━ Engraving (laser ON)",
    legend_rapid           = "╌╌ Rapid move (laser OFF)",
    legend_bbox            = "□  Bounding box",
    legend_origin          = "⊕  Origin / Home",

    # Image previews
    preview_original       = "Original",
    preview_processed      = "Processed (B/W)",
    lbl_log                = "📝 Log",
    btn_clear_log          = "Clear",

    # Log messages
    log_image_opened       = "🖼 Opened: {path}",
    log_rotated            = "🔄 Rotated {deg:+d}° → total {total}°",
    log_flipped_h          = "↔ Mirrored horizontally",
    log_flipped_v          = "↕ Mirrored vertically",
    log_preprocess_error   = "❌ Preprocess: {err}",
    log_generating         = "🔧 Generate GCode: {method} | {w}×{h} mm",
    log_gcode_generated    = "✅ GCode generated: {lines} lines",
    log_gen_error          = "❌ Generation error: {err}",
    log_saved              = "💾 Saved: {path}",
    log_loaded             = "📂 Loaded: {path}  ({lines} lines, {moves} moves)",
    log_connected          = "✅ Connected {port}@{baud}",
    log_fw                 = "   FW: {fw}",
    log_connect_error      = "❌ Connection failed: {err}",
    log_disconnected       = "🔌 Disconnected",
    log_jog                = "🕹 JOG {axis}{dist:+.1f} mm",
    log_home_set           = "🏠 Home set here (G92 X0 Y0)",
    log_goto_home          = "🏠 Go to Home",
    log_sim_started        = "🎬 Simulation started (×{speed})",
    log_sim_completed      = "✅ Simulation completed",
    log_sim_stopped        = "⏹ Simulation stopped",
    log_bbox_sending       = "📦 Sending physical outline (F{feed}, laser OFF)…",
    log_bbox_done          = "✅ Outline completed",
    log_engraving_started  = "▶ Engraving started",
    log_engraving_done     = "✅ Done. Errors: {errors}",
    log_stop_requested     = "⛔ Stop requested",
    log_emergency          = "🚨 EMERGENCY STOP",
    log_send_stopped       = "⛔ Stopped",
    log_send_error         = "⚠ Error line {line}: {cmd!r} → {resp}",
    log_contours_found     = "   Contours: {n}",
    log_raster_info        = "   Raster: {rows} rows, {segs} active segments",
    log_hatch_info         = "   Hatching {angle}°: {n} instructions",
    log_tx_error           = "⚠ TX: {err}",
    log_alarm              = "🚨 ALARM: {resp}",
    log_work_area_set      = "📏 Work area: {w}×{h} mm",
    log_model_position     = "📍 Model position: X={x:.2f}  Y={y:.2f}",
    log_quick_pos          = "📍 Quick position '{where}': X={x:.2f}  Y={y:.2f}",
    log_test_laser         = "💡 Laser test 0.5 s",
    log_simulation_on      = "🟡 Simulation active",

    # Dialogs
    dlg_start_title        = "Confirm engraving",
    dlg_start_body         = (
        "Start engraving?\n\n"
        "  Area: {w:.1f}×{h:.1f} mm\n"
        "  Position: X={ox:.1f}  Y={oy:.1f}\n"
        "  GCode lines: {lines}"
    ),
    dlg_start_sim_note     = "\n⚠ SIMULATION — no real laser",
    dlg_start_safe_note    = "\n⚠ Make sure the path is clear!",
    dlg_completed_title    = "Completed",
    dlg_completed_body     = "Engraving completed successfully!",
    dlg_emergency_title    = "EMERGENCY STOP",
    dlg_emergency_body     = "Soft reset sent!\nRun 'Unlock' before resuming.",

    # Errors
    err_no_image           = "Please load an image first",
    err_no_gcode           = "Please generate GCode first",
    err_no_model           = "No model loaded",
    err_not_connected      = "Please connect to the engraver first",
    err_no_port            = "Please select a valid COM port",
    err_image_open         = "Cannot open image:\n{err}",
    err_missing_libs       = "Missing libraries:\n{libs}",
    err_pyserial_missing   = "⚠ pyserial not found → simulation mode only",

    # Model info
    info_model_size        = "Model size: {w:.2f} × {h:.2f} mm",
    info_model_origin      = "Origin position:  X={x:.2f}  Y={y:.2f}",
    info_model_extent_x    = "X extent: {x0:.2f} → {x1:.2f} mm",
    info_model_extent_y    = "Y extent: {y0:.2f} → {y1:.2f} mm",

    # GCode info
    gcode_lines            = "✅  {n} lines | {moves} moves",
    gcode_laser_on         = "    Laser ON: {on}",
    gcode_laser_off        = " | OFF: {off}",
    gcode_area             = "    Area: {w:.1f}×{h:.1f} mm",
    gcode_feed             = "    Feed:{feed}",
    gcode_power            = " | S:{power}",
    gcode_passes           = " | ×{passes}",
    gcode_view_title       = "GCode",

    # Dependencies
    dep_missing_title      = "Missing libraries",
    dep_missing_body       = "pip install {lib}",
    dep_pyserial_warn      = "pyserial not installed → simulation only",
)


# ══════════════════════════════════════════════════════════════════════════════
#  ESPAÑOL  (es)
# ══════════════════════════════════════════════════════════════════════════════
ES = Strings(
    # General
    app_title              = "Py Laser",
    app_version_prefix     = "v",
    ready                  = "Listo",
    error                  = "Error",
    warning                = "Atención",
    info                   = "Información",
    confirm                = "Confirmar",
    yes                    = "Sí",
    no                     = "No",
    ok                     = "OK",
    cancel                 = "Cancelar",
    apply                  = "Aplicar",
    close                  = "Cerrar",
    save                   = "Guardar",
    load                   = "Cargar",
    open                   = "Abrir",
    none_loaded            = "Nada cargado",
    completed              = "Completado",
    stopped                = "Detenido",
    running                = "En ejecución",
    simulation_mode        = "Simulación",

    # Menú Archivo
    menu_file              = "Archivo",
    menu_open_image        = "Abrir imagen…",
    menu_save_gcode        = "Guardar GCode…",
    menu_load_gcode        = "Cargar GCode…",
    menu_exit              = "Salir",

    # Menú Ver
    menu_view              = "Ver",
    menu_vector_preview    = "Vista previa vectorial",
    menu_gcode_text        = "Ver GCode texto",
    menu_fit_view          = "Ajustar vista",

    # Menú Laser
    menu_laser             = "Láser",
    menu_send_bbox         = "Enviar contorno (bbox)",
    menu_emergency_stop    = "Parada de emergencia",

    # Estado
    status_ready           = "Listo",
    status_generating      = "Generando GCode…",
    status_gcode_ready     = "GCode listo",
    status_gen_error       = "Error de generación",
    status_engraving       = "Grabando…",
    status_completed       = "Completado",
    status_stopped         = "Deteniendo…",
    status_emergency       = "PARADA DE EMERGENCIA",
    status_simulation      = "Simulación en curso…",
    status_sim_completed   = "Simulación completada",

    # Pestaña Imagen
    tab_image              = "  🖼 Imagen  ",
    lf_import              = "📂 Importar imagen",
    btn_open_image         = "Abrir imagen…",
    lbl_no_image           = "Ninguna imagen cargada",
    lf_rotation            = "🔄 Rotación",
    btn_rot_left           = "↺ 90° IZQ",
    btn_rot_right          = "↻ 90° DER",
    btn_rot_180            = "↕ 180°",
    lbl_rotation           = "Rotación: 0°",
    lf_flip                = "↔ Espejo",
    btn_flip_h             = "↔ Horizontal",
    btn_flip_v             = "↕ Vertical",
    lf_preprocess          = "⚙ Pre-procesado",
    lbl_threshold          = "Umbral (threshold)",
    lbl_blur               = "Desenfoque (blur)",
    chk_invert             = "Invertir colores",
    chk_denoise            = "Reducir ruido",
    btn_update_preview     = "↻ Actualizar",

    # Pestaña Vectorizar
    tab_vectorize          = "  ✏ Vectorizar  ",
    lf_method              = "🔧 Método",
    lbl_strategy           = "Estrategia:",
    method_contours        = "Contornos",
    method_centerline      = "Línea central",
    method_raster          = "Raster",
    method_hatching        = "Tramado",
    lf_dimensions          = "📐 Dimensiones",
    lbl_width_mm           = "Ancho (mm):",
    lbl_height_mm          = "Alto (mm):",
    chk_keep_ratio         = "Mantener proporciones",
    lf_advanced            = "🔩 Opciones avanzadas",
    lbl_simplify           = "Simplificación",
    lbl_gap                = "Separación líneas (×0.1 mm)",
    lbl_hatch_angle        = "Ángulo tramado (°)",
    lbl_feed_rate          = "Velocidad (mm/min)",
    lbl_power              = "Potencia S (0-255)",
    lbl_passes             = "Pasadas",
    btn_generate_gcode     = "🚀  Generar GCode",
    lf_gcode_info          = "📊 GCode",
    lbl_no_gcode           = "—",
    btn_save_gcode         = "💾 Guardar GCode",
    btn_gcode_text         = "📋 Texto GCode",
    btn_vector_preview     = "🔍 Vista vector.",
    lf_simulation          = "🎬 Simulación",
    lbl_sim_speed          = "Velocidad sim (×)",
    btn_start_sim          = "▶ Iniciar sim.",
    btn_stop_sim           = "⏹ Parar sim.",

    # Pestaña Posición
    tab_position           = "  📍 Posición  ",
    lf_work_area           = "📏 Área de trabajo máquina (mm)",
    lbl_work_width         = "Ancho:",
    lbl_work_height        = "Alto:",
    btn_apply_work_area    = "Aplicar dimensiones",
    lf_model_position      = "📍 Posición del modelo (mm)",
    lbl_model_x            = "Origen X:",
    lbl_model_y            = "Origen Y:",
    btn_apply_position     = "Aplicar posición",
    lf_quick_position      = "⊞ Posicionamiento rápido",
    btn_pos_center         = "Centro",
    btn_pos_tl             = "↖ Arriba IZQ",
    btn_pos_tr             = "↗ Arriba DER",
    btn_pos_bl             = "↙ Abajo IZQ",
    btn_pos_br             = "↘ Abajo DER",
    lf_bbox_preview        = "📦 Vista previa contorno físico",
    lbl_bbox_desc          = "Mueve el láser a lo largo del perímetro\ndel modelo con láser APAGADO.",
    lbl_bbox_feed          = "Velocidad vista previa (mm/min)",
    btn_send_bbox          = "📦 Enviar contorno al láser",
    lf_model_info          = "ℹ Información del modelo",
    lbl_no_model           = "Ningún modelo cargado",

    # Pestaña Láser
    tab_laser              = "  🔥 Láser  ",
    lf_connection          = "🔌 Conexión COM",
    lbl_port               = "Puerto:",
    lbl_baud               = "Baud:",
    chk_simulation         = "Modo simulación (sin conexión)",
    btn_connect            = "Conectar",
    btn_disconnect         = "Desconectar",
    lbl_not_connected      = "⚫  No conectado",
    lf_home                = "🏠 Configuración Home manual",
    lbl_home_desc          = "Usa el JOG para posicionar el láser,\nluego pulsa 'Establecer Home aquí'.",
    lbl_jog_step           = "Paso (mm):",
    lbl_jog_feed           = "F:",
    btn_set_home           = "🏠 Establecer Home aquí  (G92 X0 Y0)",
    btn_goto_home          = "⏮ Ir al Home  (G0 X0 Y0)",
    btn_unlock             = "🔓 Desbloquear Alarm ($X)",
    lf_manual_cmd          = "💻 Comando manual",
    btn_send_cmd           = "Enviar",
    lf_send_gcode          = "📤 Envío GCode",
    btn_start_engraving    = "▶ Iniciar grabado",
    btn_stop_engraving     = "⏹ Parar",
    btn_emergency_stop     = "🚨 PARADA DE EMERGENCIA",
    lbl_waiting            = "Esperando…",

    # Canvas
    canvas_work_area_title = "🗺 Área de Trabajo  (arrastrar=mover modelo | rueda=zoom | derecho=pan)",
    canvas_hint            = "Área: {w}×{h} mm",
    canvas_home_label      = "HOME",
    canvas_area_label      = "Área: {w}×{h} mm",

    # Vista previa vectorial
    preview_title          = "Vista Previa Vectorial",
    preview_hint           = "🔍 Zoom: rueda  |  🖱 Pan: clic derecho  |  🔵=láser ON  ⚫=láser OFF  ──=rápido",
    preview_stats          = "Movimientos totales: {total}  |  Láser ON: {on}  |  Láser OFF (rápidos): {off}",
    preview_btn_fit        = "⊡ Ajustar",
    legend_laser_on        = "━━ Grabado (láser ON)",
    legend_rapid           = "╌╌ Movimiento rápido (láser OFF)",
    legend_bbox            = "□  Bounding box",
    legend_origin          = "⊕  Origen / Home",

    # Vista previa imágenes
    preview_original       = "Original",
    preview_processed      = "Procesada (B/N)",
    lbl_log                = "📝 Registro",
    btn_clear_log          = "Limpiar",

    # Mensajes de registro
    log_image_opened       = "🖼 Abierta: {path}",
    log_rotated            = "🔄 Rotado {deg:+d}° → total {total}°",
    log_flipped_h          = "↔ Espejado horizontalmente",
    log_flipped_v          = "↕ Espejado verticalmente",
    log_preprocess_error   = "❌ Pre-proceso: {err}",
    log_generating         = "🔧 Generando GCode: {method} | {w}×{h} mm",
    log_gcode_generated    = "✅ GCode generado: {lines} líneas",
    log_gen_error          = "❌ Error de generación: {err}",
    log_saved              = "💾 Guardado: {path}",
    log_loaded             = "📂 Cargado: {path}  ({lines} líneas, {moves} movimientos)",
    log_connected          = "✅ Conectado {port}@{baud}",
    log_fw                 = "   FW: {fw}",
    log_connect_error      = "❌ Conexión fallida: {err}",
    log_disconnected       = "🔌 Desconectado",
    log_jog                = "🕹 JOG {axis}{dist:+.1f} mm",
    log_home_set           = "🏠 Home establecido aquí (G92 X0 Y0)",
    log_goto_home          = "🏠 Ir al Home",
    log_sim_started        = "🎬 Simulación iniciada (×{speed})",
    log_sim_completed      = "✅ Simulación completada",
    log_sim_stopped        = "⏹ Simulación detenida",
    log_bbox_sending       = "📦 Enviando contorno físico (F{feed}, láser OFF)…",
    log_bbox_done          = "✅ Contorno completado",
    log_engraving_started  = "▶ Grabado iniciado",
    log_engraving_done     = "✅ Fin. Errores: {errors}",
    log_stop_requested     = "⛔ Parada solicitada",
    log_emergency          = "🚨 PARADA DE EMERGENCIA",
    log_send_stopped       = "⛔ Detenido",
    log_send_error         = "⚠ Error línea {line}: {cmd!r} → {resp}",
    log_contours_found     = "   Contornos: {n}",
    log_raster_info        = "   Raster: {rows} filas, {segs} segmentos activos",
    log_hatch_info         = "   Tramado {angle}°: {n} instrucciones",
    log_tx_error           = "⚠ TX: {err}",
    log_alarm              = "🚨 ALARMA: {resp}",
    log_work_area_set      = "📏 Área de trabajo: {w}×{h} mm",
    log_model_position     = "📍 Posición modelo: X={x:.2f}  Y={y:.2f}",
    log_quick_pos          = "📍 Posición rápida '{where}': X={x:.2f}  Y={y:.2f}",
    log_test_laser         = "💡 Prueba láser 0.5 s",
    log_simulation_on      = "🟡 Simulación activa",

    # Diálogos
    dlg_start_title        = "Confirmar grabado",
    dlg_start_body         = (
        "¿Iniciar el grabado?\n\n"
        "  Área: {w:.1f}×{h:.1f} mm\n"
        "  Posición: X={ox:.1f}  Y={oy:.1f}\n"
        "  Líneas GCode: {lines}"
    ),
    dlg_start_sim_note     = "\n⚠ SIMULACIÓN — sin láser real",
    dlg_start_safe_note    = "\n⚠ ¡Asegúrate de que el recorrido esté libre!",
    dlg_completed_title    = "Completado",
    dlg_completed_body     = "¡Grabado completado con éxito!",
    dlg_emergency_title    = "PARADA DE EMERGENCIA",
    dlg_emergency_body     = "¡Reset enviado!\nEjecuta 'Desbloquear' antes de continuar.",

    # Errores
    err_no_image           = "Carga primero una imagen",
    err_no_gcode           = "Genera primero el GCode",
    err_no_model           = "Ningún modelo cargado",
    err_not_connected      = "Conéctate primero al grabador",
    err_no_port            = "Selecciona un puerto COM válido",
    err_image_open         = "No se puede abrir la imagen:\n{err}",
    err_missing_libs       = "Librerías faltantes:\n{libs}",
    err_pyserial_missing   = "⚠ pyserial no encontrado → solo modo simulación",

    # Info modelo
    info_model_size        = "Tamaño del modelo: {w:.2f} × {h:.2f} mm",
    info_model_origin      = "Posición origen:  X={x:.2f}  Y={y:.2f}",
    info_model_extent_x    = "Extensión X: {x0:.2f} → {x1:.2f} mm",
    info_model_extent_y    = "Extensión Y: {y0:.2f} → {y1:.2f} mm",

    # Info GCode
    gcode_lines            = "✅  {n} líneas | {moves} movimientos",
    gcode_laser_on         = "    Láser ON: {on}",
    gcode_laser_off        = " | OFF: {off}",
    gcode_area             = "    Área: {w:.1f}×{h:.1f} mm",
    gcode_feed             = "    Feed:{feed}",
    gcode_power            = " | S:{power}",
    gcode_passes           = " | ×{passes}",
    gcode_view_title       = "GCode",

    # Dependencias
    dep_missing_title      = "Librerías faltantes",
    dep_missing_body       = "pip install {lib}",
    dep_pyserial_warn      = "pyserial no instalado → solo simulación",
)


# ══════════════════════════════════════════════════════════════════════════════
#  DEUTSCH  (de)
# ══════════════════════════════════════════════════════════════════════════════
DE = Strings(
    # Allgemein
    app_title              = "Py Laser",
    app_version_prefix     = "v",
    ready                  = "Bereit",
    error                  = "Fehler",
    warning                = "Warnung",
    info                   = "Information",
    confirm                = "Bestätigen",
    yes                    = "Ja",
    no                     = "Nein",
    ok                     = "OK",
    cancel                 = "Abbrechen",
    apply                  = "Anwenden",
    close                  = "Schließen",
    save                   = "Speichern",
    load                   = "Laden",
    open                   = "Öffnen",
    none_loaded            = "Nichts geladen",
    completed              = "Abgeschlossen",
    stopped                = "Gestoppt",
    running                = "Läuft",
    simulation_mode        = "Simulation",

    # Menü Datei
    menu_file              = "Datei",
    menu_open_image        = "Bild öffnen…",
    menu_save_gcode        = "GCode speichern…",
    menu_load_gcode        = "GCode laden…",
    menu_exit              = "Beenden",

    # Menü Ansicht
    menu_view              = "Ansicht",
    menu_vector_preview    = "Vektorvorschau",
    menu_gcode_text        = "GCode-Text anzeigen",
    menu_fit_view          = "Ansicht anpassen",

    # Menü Laser
    menu_laser             = "Laser",
    menu_send_bbox         = "Umriss senden (bbox)",
    menu_emergency_stop    = "Notaus",

    # Status
    status_ready           = "Bereit",
    status_generating      = "GCode wird generiert…",
    status_gcode_ready     = "GCode bereit",
    status_gen_error       = "Generierungsfehler",
    status_engraving       = "Gravur läuft…",
    status_completed       = "Abgeschlossen",
    status_stopped         = "Wird gestoppt…",
    status_emergency       = "NOTAUS",
    status_simulation      = "Simulation läuft…",
    status_sim_completed   = "Simulation abgeschlossen",

    # Reiter Bild
    tab_image              = "  🖼 Bild  ",
    lf_import              = "📂 Bild importieren",
    btn_open_image         = "Bild öffnen…",
    lbl_no_image           = "Kein Bild geladen",
    lf_rotation            = "🔄 Rotation",
    btn_rot_left           = "↺ 90° Links",
    btn_rot_right          = "↻ 90° Rechts",
    btn_rot_180            = "↕ 180°",
    lbl_rotation           = "Rotation: 0°",
    lf_flip                = "↔ Spiegeln",
    btn_flip_h             = "↔ Horizontal",
    btn_flip_v             = "↕ Vertikal",
    lf_preprocess          = "⚙ Vorverarbeitung",
    lbl_threshold          = "Schwellenwert (threshold)",
    lbl_blur               = "Unschärfe (blur)",
    chk_invert             = "Farben invertieren",
    chk_denoise            = "Rauschen reduzieren",
    btn_update_preview     = "↻ Aktualisieren",

    # Reiter Vektorisieren
    tab_vectorize          = "  ✏ Vektorisieren  ",
    lf_method              = "🔧 Methode",
    lbl_strategy           = "Strategie:",
    method_contours        = "Konturen",
    method_centerline      = "Mittellinie",
    method_raster          = "Raster",
    method_hatching        = "Schraffur",
    lf_dimensions          = "📐 Abmessungen",
    lbl_width_mm           = "Breite (mm):",
    lbl_height_mm          = "Höhe (mm):",
    chk_keep_ratio         = "Seitenverhältnis beibehalten",
    lf_advanced            = "🔩 Erweiterte Optionen",
    lbl_simplify           = "Vereinfachung",
    lbl_gap                = "Linienabstand (×0.1 mm)",
    lbl_hatch_angle        = "Schraffurwinkel (°)",
    lbl_feed_rate          = "Vorschub (mm/min)",
    lbl_power              = "Leistung S (0-255)",
    lbl_passes             = "Durchgänge",
    btn_generate_gcode     = "🚀  GCode generieren",
    lf_gcode_info          = "📊 GCode",
    lbl_no_gcode           = "—",
    btn_save_gcode         = "💾 GCode speichern",
    btn_gcode_text         = "📋 GCode-Text",
    btn_vector_preview     = "🔍 Vektorvorschau",
    lf_simulation          = "🎬 Simulation",
    lbl_sim_speed          = "Simulationsgeschw. (×)",
    btn_start_sim          = "▶ Sim. starten",
    btn_stop_sim           = "⏹ Sim. stoppen",

    # Reiter Position
    tab_position           = "  📍 Position  ",
    lf_work_area           = "📏 Maschinenarbeitsbereich (mm)",
    lbl_work_width         = "Breite:",
    lbl_work_height        = "Höhe:",
    btn_apply_work_area    = "Abmessungen anwenden",
    lf_model_position      = "📍 Modellposition (mm)",
    lbl_model_x            = "X-Ursprung:",
    lbl_model_y            = "Y-Ursprung:",
    btn_apply_position     = "Position anwenden",
    lf_quick_position      = "⊞ Schnellpositionierung",
    btn_pos_center         = "Mitte",
    btn_pos_tl             = "↖ Oben Links",
    btn_pos_tr             = "↗ Oben Rechts",
    btn_pos_bl             = "↙ Unten Links",
    btn_pos_br             = "↘ Unten Rechts",
    lf_bbox_preview        = "📦 Physische Umrissvorschau",
    lbl_bbox_desc          = "Bewegt den Laser entlang des Modellumfangs\nmit ausgeschaltetem Laser.",
    lbl_bbox_feed          = "Vorschaugeschwindigkeit (mm/min)",
    btn_send_bbox          = "📦 Umriss an Laser senden",
    lf_model_info          = "ℹ Modellinformationen",
    lbl_no_model           = "Kein Modell geladen",

    # Reiter Laser
    tab_laser              = "  🔥 Laser  ",
    lf_connection          = "🔌 COM-Verbindung",
    lbl_port               = "Port:",
    lbl_baud               = "Baud:",
    chk_simulation         = "Simulationsmodus (offline)",
    btn_connect            = "Verbinden",
    btn_disconnect         = "Trennen",
    lbl_not_connected      = "⚫  Nicht verbunden",
    lf_home                = "🏠 Manuelle Home-Einstellung",
    lbl_home_desc          = "Verwende JOG zum Positionieren des Lasers,\ndann 'Home hier setzen' drücken.",
    lbl_jog_step           = "Schritt (mm):",
    lbl_jog_feed           = "F:",
    btn_set_home           = "🏠 Home hier setzen  (G92 X0 Y0)",
    btn_goto_home          = "⏮ Zu Home fahren  (G0 X0 Y0)",
    btn_unlock             = "🔓 Alarm entsperren ($X)",
    lf_manual_cmd          = "💻 Manueller Befehl",
    btn_send_cmd           = "Senden",
    lf_send_gcode          = "📤 GCode senden",
    btn_start_engraving    = "▶ Gravur starten",
    btn_stop_engraving     = "⏹ Stop",
    btn_emergency_stop     = "🚨 NOTAUS",
    lbl_waiting            = "Warte…",

    # Canvas
    canvas_work_area_title = "🗺 Arbeitsbereich  (ziehen=Modell bewegen | Rad=Zoom | rechts=Pan)",
    canvas_hint            = "Bereich: {w}×{h} mm",
    canvas_home_label      = "HOME",
    canvas_area_label      = "Bereich: {w}×{h} mm",

    # Vektorvorschau
    preview_title          = "Vektorvorschau",
    preview_hint           = "🔍 Zoom: Rad  |  🖱 Pan: Rechtsklick  |  🔵=Laser AN  ⚫=Laser AUS  ──=Eilgang",
    preview_stats          = "Gesamtbewegungen: {total}  |  Laser AN: {on}  |  Laser AUS (Eilgang): {off}",
    preview_btn_fit        = "⊡ Anpassen",
    legend_laser_on        = "━━ Gravur (Laser AN)",
    legend_rapid           = "╌╌ Eilgang (Laser AUS)",
    legend_bbox            = "□  Begrenzungsrahmen",
    legend_origin          = "⊕  Ursprung / Home",

    # Bildvorschau
    preview_original       = "Original",
    preview_processed      = "Verarbeitet (S/W)",
    lbl_log                = "📝 Protokoll",
    btn_clear_log          = "Leeren",

    # Protokollmeldungen
    log_image_opened       = "🖼 Geöffnet: {path}",
    log_rotated            = "🔄 Gedreht {deg:+d}° → gesamt {total}°",
    log_flipped_h          = "↔ Horizontal gespiegelt",
    log_flipped_v          = "↕ Vertikal gespiegelt",
    log_preprocess_error   = "❌ Vorverarbeitung: {err}",
    log_generating         = "🔧 GCode generieren: {method} | {w}×{h} mm",
    log_gcode_generated    = "✅ GCode generiert: {lines} Zeilen",
    log_gen_error          = "❌ Generierungsfehler: {err}",
    log_saved              = "💾 Gespeichert: {path}",
    log_loaded             = "📂 Geladen: {path}  ({lines} Zeilen, {moves} Bewegungen)",
    log_connected          = "✅ Verbunden {port}@{baud}",
    log_fw                 = "   FW: {fw}",
    log_connect_error      = "❌ Verbindung fehlgeschlagen: {err}",
    log_disconnected       = "🔌 Getrennt",
    log_jog                = "🕹 JOG {axis}{dist:+.1f} mm",
    log_home_set           = "🏠 Home hier gesetzt (G92 X0 Y0)",
    log_goto_home          = "🏠 Zu Home fahren",
    log_sim_started        = "🎬 Simulation gestartet (×{speed})",
    log_sim_completed      = "✅ Simulation abgeschlossen",
    log_sim_stopped        = "⏹ Simulation gestoppt",
    log_bbox_sending       = "📦 Physischen Umriss senden (F{feed}, Laser AUS)…",
    log_bbox_done          = "✅ Umriss abgeschlossen",
    log_engraving_started  = "▶ Gravur gestartet",
    log_engraving_done     = "✅ Fertig. Fehler: {errors}",
    log_stop_requested     = "⛔ Stop angefordert",
    log_emergency          = "🚨 NOTAUS",
    log_send_stopped       = "⛔ Gestoppt",
    log_send_error         = "⚠ Fehler Zeile {line}: {cmd!r} → {resp}",
    log_contours_found     = "   Konturen: {n}",
    log_raster_info        = "   Raster: {rows} Zeilen, {segs} aktive Segmente",
    log_hatch_info         = "   Schraffur {angle}°: {n} Anweisungen",
    log_tx_error           = "⚠ TX: {err}",
    log_alarm              = "🚨 ALARM: {resp}",
    log_work_area_set      = "📏 Arbeitsbereich: {w}×{h} mm",
    log_model_position     = "📍 Modellposition: X={x:.2f}  Y={y:.2f}",
    log_quick_pos          = "📍 Schnellposition '{where}': X={x:.2f}  Y={y:.2f}",
    log_test_laser         = "💡 Lasertest 0,5 s",
    log_simulation_on      = "🟡 Simulation aktiv",

    # Dialoge
    dlg_start_title        = "Gravur bestätigen",
    dlg_start_body         = (
        "Gravur starten?\n\n"
        "  Bereich: {w:.1f}×{h:.1f} mm\n"
        "  Position: X={ox:.1f}  Y={oy:.1f}\n"
        "  GCode-Zeilen: {lines}"
    ),
    dlg_start_sim_note     = "\n⚠ SIMULATION — kein echter Laser",
    dlg_start_safe_note    = "\n⚠ Stelle sicher, dass der Weg frei ist!",
    dlg_completed_title    = "Abgeschlossen",
    dlg_completed_body     = "Gravur erfolgreich abgeschlossen!",
    dlg_emergency_title    = "NOTAUS",
    dlg_emergency_body     = "Soft-Reset gesendet!\nFühre 'Entsperren' vor dem Fortfahren aus.",

    # Fehler
    err_no_image           = "Bitte zuerst ein Bild laden",
    err_no_gcode           = "Bitte zuerst GCode generieren",
    err_no_model           = "Kein Modell geladen",
    err_not_connected      = "Bitte zuerst mit dem Graveur verbinden",
    err_no_port            = "Bitte einen gültigen COM-Port auswählen",
    err_image_open         = "Bild kann nicht geöffnet werden:\n{err}",
    err_missing_libs       = "Fehlende Bibliotheken:\n{libs}",
    err_pyserial_missing   = "⚠ pyserial nicht gefunden → nur Simulationsmodus",

    # Modellinformationen
    info_model_size        = "Modellgröße: {w:.2f} × {h:.2f} mm",
    info_model_origin      = "Ursprungsposition:  X={x:.2f}  Y={y:.2f}",
    info_model_extent_x    = "X-Bereich: {x0:.2f} → {x1:.2f} mm",
    info_model_extent_y    = "Y-Bereich: {y0:.2f} → {y1:.2f} mm",

    # GCode-Info
    gcode_lines            = "✅  {n} Zeilen | {moves} Bewegungen",
    gcode_laser_on         = "    Laser AN: {on}",
    gcode_laser_off        = " | AUS: {off}",
    gcode_area             = "    Bereich: {w:.1f}×{h:.1f} mm",
    gcode_feed             = "    Vorschub:{feed}",
    gcode_power            = " | S:{power}",
    gcode_passes           = " | ×{passes}",
    gcode_view_title       = "GCode",

    # Abhängigkeiten
    dep_missing_title      = "Fehlende Bibliotheken",
    dep_missing_body       = "pip install {lib}",
    dep_pyserial_warn      = "pyserial nicht installiert → nur Simulation",
)


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTRO LINGUE DISPONIBILI
#  Per aggiungere una nuova lingua:
#  1. Crea un nuovo blocco Strings (es. FR = Strings(...))
#  2. Aggiungi la voce qui sotto nel dizionario LANGUAGES
# ══════════════════════════════════════════════════════════════════════════════
LANGUAGES: dict[str, Strings] = {
    "Italiano" : IT,
    "English"  : EN,
    "Español"  : ES,
    "Deutsch"  : DE,
    # "Français" : FR,   # ← esempio per aggiungere il francese
    # "中文"      : ZH,   # ← esempio per aggiungere il cinese
}

DEFAULT_LANGUAGE = "Italiano"


def get_strings(language: str = DEFAULT_LANGUAGE) -> Strings:
    """
    Restituisce l'oggetto Strings per la lingua richiesta.
    Se la lingua non esiste, ritorna la lingua di default.
    """
    return LANGUAGES.get(language, LANGUAGES[DEFAULT_LANGUAGE])


def available_languages() -> list[str]:
    """Restituisce la lista dei nomi delle lingue disponibili."""
    return list(LANGUAGES.keys())