# -*- coding: utf-8 -*-
"""
Spreker Flipklok Timer - Standalone Desktop Applicatie
another #staalvaes production
"""

import tkinter as tk
from tkinter import ttk
import sys

# DPI awareness inschakelen voor haarscherpe weergave op Windows
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

class SpeakerTimerApp:
    THEMES = {
        'stage': {
            'name': 'Thema: Podium (Puur Zwart)',
            'bg': '#000000',
            'card_bg': '#070809',
            'card_border': '#18191c',
            'card_seam': '#000000',
            'fg_normal': '#00E676',
            'fg_warning': '#FFD600',
            'fg_danger': '#FF1744',
            'btn_bg': '#121417',
            'btn_fg': '#9fa4af',
            'btn_active_bg': '#1c1f24',
            'btn_active_fg': '#ffffff',
            'pill_bg': '#121417',
            'pill_fg': '#aaaaaa',
            'pill_active_bg': '#00E676',
            'pill_active_fg': '#000000',
            'bar_bg': '#0a0a0a',
            'footer_fg': '#333333',
            'muted_fg': '#555964'
        },
        'dark': {
            'name': 'Thema: Donker (Standaard)',
            'bg': '#121417',
            'card_bg': '#1e2126',
            'card_border': '#2a2e36',
            'card_seam': '#14161a',
            'fg_normal': '#00E676',
            'fg_warning': '#FFB300',
            'fg_danger': '#FF3D00',
            'btn_bg': '#1c1f24',
            'btn_fg': '#e2e5eb',
            'btn_active_bg': '#292d35',
            'btn_active_fg': '#ffffff',
            'pill_bg': '#1c1f24',
            'pill_fg': '#e2e5eb',
            'pill_active_bg': '#00E676',
            'pill_active_fg': '#05140b',
            'bar_bg': '#1a1c21',
            'footer_fg': '#5d6370',
            'muted_fg': '#8e94a0'
        },
        'bright': {
            'name': 'Thema: Bright (Licht)',
            'bg': '#eef2f7',
            'card_bg': '#ffffff',
            'card_border': '#d5dce6',
            'card_seam': '#cbd2dc',
            'fg_normal': '#0a8754',
            'fg_warning': '#d97706',
            'fg_danger': '#dc2626',
            'btn_bg': '#ffffff',
            'btn_fg': '#1f2937',
            'btn_active_bg': '#f3f4f6',
            'btn_active_fg': '#000000',
            'pill_bg': '#ffffff',
            'pill_fg': '#1f2937',
            'pill_active_bg': '#0a8754',
            'pill_active_fg': '#ffffff',
            'bar_bg': '#d8dde4',
            'footer_fg': '#9ca3af',
            'muted_fg': '#6b7280'
        }
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Spreker Flipklok Timer")
        self.root.geometry("960x650")
        self.root.minsize(580, 420)
        self.root.resizable(True, True)

        self.current_theme = 'dark'
        self.total_seconds = 300
        self.time_remaining = 300
        self.is_running = False
        self.is_paused = False
        self.timer_job = None
        self.is_fullscreen = False

        # Schaal & Afmetingen beheer
        self.card_w = 270
        self.card_h = 195
        self.font_size = 86
        self.last_root_w = 0
        self.last_root_h = 0
        self.resize_job = None

        self.setup_styles()
        self.setup_ui()
        self.apply_theme('dark')
        self.setup_bindings()

        # Eerste schaallengte direct berekenen
        self.root.after(10, self.apply_resize)

    def setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

    def setup_ui(self):
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Bovenste balk (Thema, Waarschuwing, Fullscreen)
        self.top_bar = tk.Frame(self.main_container)
        self.top_bar.pack(fill=tk.X, padx=15, pady=(12, 4))

        self.top_inner = tk.Frame(self.top_bar)
        self.top_inner.pack(anchor=tk.CENTER)

        # Thema dropdown
        self.theme_var = tk.StringVar(value="Thema: Donker (Standaard)")
        self.theme_combo = ttk.Combobox(
            self.top_inner,
            textvariable=self.theme_var,
            values=[t['name'] for t in self.THEMES.values()],
            state="readonly",
            width=24,
            font=("Segoe UI", 10)
        )
        self.theme_combo.pack(side=tk.LEFT, padx=6)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_selected)

        # Waarschuwing dropdown
        self.warning_options = [
            (120, "Waarschuwing: 2 Min (120s)"),
            (90, "Waarschuwing: 1.5 Min (90s)"),
            (60, "Waarschuwing: 1 Min (60s)"),
            (45, "Waarschuwing: 45 Sec"),
            (30, "Waarschuwing: 30 Sec"),
            (15, "Waarschuwing: 15 Sec"),
            (0, "Geen Waarschuwing")
        ]
        self.warning_var = tk.StringVar(value="Waarschuwing: 1 Min (60s)")
        self.warning_combo = ttk.Combobox(
            self.top_inner,
            textvariable=self.warning_var,
            values=[opt[1] for opt in self.warning_options],
            state="readonly",
            width=26,
            font=("Segoe UI", 10)
        )
        self.warning_combo.pack(side=tk.LEFT, padx=6)
        self.warning_combo.bind("<<ComboboxSelected>>", self.on_warning_selected)

        # Fullscreen knop
        self.fs_btn = tk.Button(
            self.top_inner,
            text="Volledig Scherm",
            command=self.toggle_fullscreen,
            font=("Segoe UI", 10, "bold"),
            padx=14, pady=4, relief=tk.FLAT, cursor="hand2"
        )
        self.fs_btn.pack(side=tk.LEFT, padx=6)

        # 2. Het Flipklok Display (dynamisch gecentreerd)
        self.clock_frame = tk.Frame(self.main_container)
        self.clock_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=(2, 2))

        self.clock_center = tk.Frame(self.clock_frame)
        self.clock_center.pack(expand=True)

        # Linker Flap: Minuten
        self.min_unit = tk.Frame(self.clock_center)
        self.min_unit.grid(row=0, column=0, padx=8, pady=4)

        # Steppers boven minuten (+5m, +1m)
        self.min_steppers_top = tk.Frame(self.min_unit)
        self.min_steppers_top.pack(pady=(0, 4))

        self.btn_min_p5 = tk.Button(self.min_steppers_top, text="+5m", font=("Segoe UI", 9, "bold"),
                                    command=lambda: self.adjust_minutes(5), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_min_p5.pack(side=tk.LEFT, padx=2)
        self.btn_min_p1 = tk.Button(self.min_steppers_top, text="+1m", font=("Segoe UI", 9, "bold"),
                                    command=lambda: self.adjust_minutes(1), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_min_p1.pack(side=tk.LEFT, padx=2)

        # Minuten Kaart
        self.min_canvas = tk.Canvas(self.min_unit, width=self.card_w, height=self.card_h, bd=0, highlightthickness=2)
        self.min_canvas.pack()

        # Steppers onder minuten (-1m, -5m)
        self.min_steppers_bot = tk.Frame(self.min_unit)
        self.min_steppers_bot.pack(pady=(4, 2))

        self.btn_min_m1 = tk.Button(self.min_steppers_bot, text="-1m", font=("Segoe UI", 9, "bold"),
                                    command=lambda: self.adjust_minutes(-1), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_min_m1.pack(side=tk.LEFT, padx=2)
        self.btn_min_m5 = tk.Button(self.min_steppers_bot, text="-5m", font=("Segoe UI", 9, "bold"),
                                    command=lambda: self.adjust_minutes(-5), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_min_m5.pack(side=tk.LEFT, padx=2)

        self.min_label = tk.Label(self.min_unit, text="MINUTEN", font=("Segoe UI", 9, "bold"))
        self.min_label.pack(pady=(1, 0))

        # Scheider (Dubbele Punt)
        self.colon_unit = tk.Frame(self.clock_center)
        self.colon_unit.grid(row=0, column=1, padx=4)
        self.colon_canvas = tk.Canvas(self.colon_unit, width=28, height=self.card_h, bd=0, highlightthickness=0)
        self.colon_canvas.pack()

        # Rechter Flap: Seconden
        self.sec_unit = tk.Frame(self.clock_center)
        self.sec_unit.grid(row=0, column=2, padx=8, pady=4)

        # Steppers boven seconden (+15s, +5s)
        self.sec_steppers_top = tk.Frame(self.sec_unit)
        self.sec_steppers_top.pack(pady=(0, 4))

        self.btn_sec_p15 = tk.Button(self.sec_steppers_top, text="+15s", font=("Segoe UI", 9, "bold"),
                                     command=lambda: self.adjust_seconds(15), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_sec_p15.pack(side=tk.LEFT, padx=2)
        self.btn_sec_p5 = tk.Button(self.sec_steppers_top, text="+5s", font=("Segoe UI", 9, "bold"),
                                    command=lambda: self.adjust_seconds(5), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_sec_p5.pack(side=tk.LEFT, padx=2)

        # Seconden Kaart
        self.sec_canvas = tk.Canvas(self.sec_unit, width=self.card_w, height=self.card_h, bd=0, highlightthickness=2)
        self.sec_canvas.pack()

        # Steppers onder seconden (-5s, -15s)
        self.sec_steppers_bot = tk.Frame(self.sec_unit)
        self.sec_steppers_bot.pack(pady=(4, 2))

        self.btn_sec_m5 = tk.Button(self.sec_steppers_bot, text="-5s", font=("Segoe UI", 9, "bold"),
                                    command=lambda: self.adjust_seconds(-5), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_sec_m5.pack(side=tk.LEFT, padx=2)
        self.btn_sec_m15 = tk.Button(self.sec_steppers_bot, text="-15s", font=("Segoe UI", 9, "bold"),
                                     command=lambda: self.adjust_seconds(-15), padx=7, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_sec_m15.pack(side=tk.LEFT, padx=2)

        self.sec_label = tk.Label(self.sec_unit, text="SECONDEN", font=("Segoe UI", 9, "bold"))
        self.sec_label.pack(pady=(1, 0))

        # 3. Presets & Directe Instelling
        self.presets_frame = tk.Frame(self.main_container)
        self.presets_frame.pack(fill=tk.X, padx=15, pady=(2, 8))

        self.presets_inner = tk.Frame(self.presets_frame)
        self.presets_inner.pack(anchor=tk.CENTER)

        self.preset_buttons = []
        preset_values = [
            (30, "30s"), (60, "1m"), (180, "3m"), (300, "5m"),
            (600, "10m"), (900, "15m"), (1200, "20m"), (1800, "30m"),
            (2700, "45m"), (3600, "60m")
        ]

        for sec, lbl in preset_values:
            btn = tk.Button(
                self.presets_inner, text=lbl,
                command=lambda s=sec: self.set_preset(s),
                font=("Segoe UI", 9, "bold"),
                padx=9, pady=3, relief=tk.FLAT, cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=3, pady=2)
            self.preset_buttons.append((sec, btn))

        # 4. Actieknoppen (Start, Pauze, Reset)
        self.action_frame = tk.Frame(self.main_container)
        self.action_frame.pack(fill=tk.X, padx=15, pady=(0, 12))

        self.action_inner = tk.Frame(self.action_frame)
        self.action_inner.pack(anchor=tk.CENTER)

        self.start_btn = tk.Button(
            self.action_inner,
            text="  ▶ Start Timer  ",
            command=self.start_timer,
            font=("Segoe UI", 11, "bold"),
            padx=18, pady=7, relief=tk.FLAT, cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=8)

        self.pause_btn = tk.Button(
            self.action_inner,
            text=" ⏸ Pauze ",
            command=self.toggle_pause,
            state=tk.DISABLED,
            font=("Segoe UI", 11, "bold"),
            padx=16, pady=7, relief=tk.FLAT, cursor="hand2"
        )
        self.pause_btn.pack(side=tk.LEFT, padx=8)

        self.reset_btn = tk.Button(
            self.action_inner,
            text=" ↺ Reset ",
            command=self.reset_timer,
            font=("Segoe UI", 11, "bold"),
            padx=16, pady=7, relief=tk.FLAT, cursor="hand2"
        )
        self.reset_btn.pack(side=tk.LEFT, padx=8)

        # Voettekst
        self.footer_label = tk.Label(
            self.main_container,
            text="another #staalvaes production",
            font=("Segoe UI", 9)
        )
        self.footer_label.pack(pady=(0, 6))

        # Aflopende voortgangsbalk onderaan
        self.progress_canvas = tk.Canvas(self.root, height=12, bd=0, highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_bindings(self):
        # Dynamisch meeschalen wanneer de gebruiker het venster sleept
        self.root.bind("<Configure>", self.on_root_configure)

        # Sneltoetsen
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())
        self.root.bind("<space>", self.on_spacebar)
        self.root.bind("<f>", lambda e: self.toggle_fullscreen())
        self.root.bind("<F>", lambda e: self.toggle_fullscreen())

    def on_root_configure(self, event):
        # Alleen reageren als het hoofdvenster van afmeting verandert door slepen
        if event.widget != self.root:
            return
        if event.width == self.last_root_w and event.height == self.last_root_h:
            return
        self.last_root_w = event.width
        self.last_root_h = event.height

        # Debounce: bereken formaat na korte pauze in het slepen
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(20, self.apply_resize)

    def apply_resize(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        # Beschikbare ruimte voor de flipklok bepalen
        pad_h = 160 if self.is_fullscreen else 250
        avail_w = max(200, w - 80)
        avail_h = max(100, h - pad_h)

        # 2 kaarten + scheider + marges
        cw = max(140, min(700, int((avail_w - 70) / 2)))
        ch = max(100, min(520, int(cw * 0.72)))

        # Beperk tot beschikbare hoogte
        if ch > avail_h:
            ch = max(100, avail_h)
            cw = int(ch / 0.72)

        self.card_w = cw
        self.card_h = ch
        self.font_size = max(36, min(240, int(ch * 0.64)))

        # Canvas widget formaten bijwerken
        self.min_canvas.configure(width=self.card_w, height=self.card_h)
        self.sec_canvas.configure(width=self.card_w, height=self.card_h)
        self.colon_canvas.configure(height=self.card_h)

        self.update_display()

    def on_spacebar(self, event):
        if isinstance(event.widget, ttk.Combobox):
            return
        if self.is_running:
            self.toggle_pause()
        else:
            self.start_timer()

    def get_selected_warning(self):
        label = self.warning_var.get()
        for s, l in self.warning_options:
            if l == label:
                return s
        return 60

    def on_warning_selected(self, event=None):
        self.update_display()

    def on_theme_selected(self, event=None):
        sel_name = self.theme_var.get()
        for key, theme in self.THEMES.items():
            if theme['name'] == sel_name:
                self.apply_theme(key)
                break

    def apply_theme(self, theme_key):
        self.current_theme = theme_key
        t = self.THEMES[theme_key]

        self.root.configure(bg=t['bg'])
        self.main_container.configure(bg=t['bg'])
        self.top_bar.configure(bg=t['bg'])
        self.top_inner.configure(bg=t['bg'])
        self.clock_frame.configure(bg=t['bg'])
        self.clock_center.configure(bg=t['bg'])
        self.min_unit.configure(bg=t['bg'])
        self.min_steppers_top.configure(bg=t['bg'])
        self.min_steppers_bot.configure(bg=t['bg'])
        self.colon_unit.configure(bg=t['bg'])
        self.sec_unit.configure(bg=t['bg'])
        self.sec_steppers_top.configure(bg=t['bg'])
        self.sec_steppers_bot.configure(bg=t['bg'])
        self.presets_frame.configure(bg=t['bg'])
        self.presets_inner.configure(bg=t['bg'])
        self.action_frame.configure(bg=t['bg'])
        self.action_inner.configure(bg=t['bg'])

        self.min_label.configure(bg=t['bg'], fg=t['muted_fg'])
        self.sec_label.configure(bg=t['bg'], fg=t['muted_fg'])
        self.footer_label.configure(bg=t['bg'], fg=t['footer_fg'])
        self.progress_canvas.configure(bg=t['bar_bg'])
        self.colon_canvas.configure(bg=t['bg'])

        # Knoppen stylen
        stepper_btns = [
            self.btn_min_p5, self.btn_min_p1, self.btn_min_m1, self.btn_min_m5,
            self.btn_sec_p15, self.btn_sec_p5, self.btn_sec_m5, self.btn_sec_m15,
            self.fs_btn, self.pause_btn, self.reset_btn
        ]
        for btn in stepper_btns:
            btn.configure(
                bg=t['btn_bg'], fg=t['btn_fg'],
                activebackground=t['btn_active_bg'], activeforeground=t['btn_active_fg']
            )

        # Start knop accentkleur
        self.start_btn.configure(
            bg=t['fg_normal'], fg="#000000" if theme_key != 'bright' else "#ffffff",
            activebackground=t['fg_normal']
        )

        self.update_preset_buttons()
        self.update_display()

    def update_preset_buttons(self):
        t = self.THEMES[self.current_theme]
        for sec, btn in self.preset_buttons:
            if sec == self.total_seconds:
                btn.configure(bg=t['pill_active_bg'], fg=t['pill_active_fg'])
            else:
                btn.configure(bg=t['pill_bg'], fg=t['pill_fg'])

    def set_preset(self, seconds):
        if self.is_running:
            self.reset_timer()
        self.total_seconds = seconds
        self.time_remaining = seconds
        self.update_preset_buttons()
        self.update_display()

    def adjust_minutes(self, delta):
        cur_m = self.time_remaining // 60
        cur_s = self.time_remaining % 60
        new_m = max(0, cur_m + delta)
        if new_m == 0 and cur_s == 0:
            new_m = 1

        new_total = (new_m * 60) + cur_s
        if not self.is_running:
            self.total_seconds = new_total
            self.time_remaining = new_total
        else:
            self.time_remaining = max(0, self.time_remaining + (delta * 60))
            self.total_seconds = max(self.total_seconds, self.time_remaining)

        self.update_preset_buttons()
        self.update_display()

    def adjust_seconds(self, delta):
        cur_m = self.time_remaining // 60
        cur_s = self.time_remaining % 60
        new_s = cur_s + delta
        new_m = cur_m

        if new_s >= 60:
            new_m += new_s // 60
            new_s = new_s % 60
        elif new_s < 0:
            if new_m > 0:
                new_m -= 1
                new_s += 60
            else:
                new_s = 0

        new_total = (new_m * 60) + new_s
        if new_total == 0:
            return

        if not self.is_running:
            self.total_seconds = new_total
            self.time_remaining = new_total
        else:
            self.time_remaining = max(0, self.time_remaining + delta)
            self.total_seconds = max(self.total_seconds, self.time_remaining)

        self.update_preset_buttons()
        self.update_display()

    def get_status_color(self):
        t = self.THEMES[self.current_theme]
        warn_sec = self.get_selected_warning()

        if self.time_remaining <= 0 and self.total_seconds > 0 and self.is_running:
            return t['fg_danger']
        elif warn_sec > 0 and self.time_remaining <= warn_sec and self.is_running:
            return t['fg_warning']
        else:
            return t['fg_normal']

    def draw_flip_card(self, canvas, text, color):
        t = self.THEMES[self.current_theme]
        w = self.card_w
        h = self.card_h

        canvas.delete("all")
        canvas.configure(bg=t['card_bg'],
                         highlightbackground=t['card_border'], highlightcolor=t['card_border'])

        # Cijferweergave
        canvas.create_text(
            w // 2, h // 2,
            text=text,
            fill=color,
            font=("Arial", self.font_size, "bold")
        )

        # De split-flap naad (horizontale scheurlijn)
        seam_y = h // 2
        canvas.create_line(0, seam_y, w, seam_y, fill=t['card_seam'], width=3)
        canvas.create_line(0, seam_y + 1, w, seam_y + 1, fill=t['card_border'], width=1)

        # Zijkant scharniertjes (hinges)
        canvas.create_rectangle(0, seam_y - 8, 5, seam_y + 8, fill=t['card_seam'], width=0)
        canvas.create_rectangle(w - 5, seam_y - 8, w, seam_y + 8, fill=t['card_seam'], width=0)

    def draw_colon(self, color):
        self.colon_canvas.delete("all")
        w = 28
        h = self.card_h
        dot_r = max(4, min(8, int(h / 32)))
        cy1 = int(h * 0.38)
        cy2 = int(h * 0.62)

        self.colon_canvas.create_oval(w // 2 - dot_r, cy1 - dot_r, w // 2 + dot_r, cy1 + dot_r, fill=color, width=0)
        self.colon_canvas.create_oval(w // 2 - dot_r, cy2 - dot_r, w // 2 + dot_r, cy2 + dot_r, fill=color, width=0)

    def update_display(self):
        m = self.time_remaining // 60
        s = self.time_remaining % 60
        color = self.get_status_color()

        self.draw_flip_card(self.min_canvas, f"{m:02d}", color)
        self.draw_flip_card(self.sec_canvas, f"{s:02d}", color)
        self.draw_colon(color)

        self.update_progress_bar(color)

    def update_progress_bar(self, color):
        self.progress_canvas.delete("all")
        width = self.root.winfo_width()
        height = 12

        if self.total_seconds > 0:
            ratio = max(0.0, min(1.0, self.time_remaining / self.total_seconds))
        else:
            ratio = 1.0

        bar_width = int(width * ratio)
        if bar_width > 0:
            self.progress_canvas.create_rectangle(
                0, 0, bar_width, height,
                fill=color, width=0
            )

    def start_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        # Als de timer afgelopen is (op 0 staat), herstarten met de ingestelde tijd
        if self.time_remaining <= 0:
            self.time_remaining = self.total_seconds if self.total_seconds > 0 else 300
            self.total_seconds = self.time_remaining

        self.is_running = True
        self.is_paused = False

        self.start_btn.pack_forget()
        self.pause_btn.configure(text=" ⏸ Pauze ", state=tk.NORMAL)
        self.update_display()
        self.timer_job = self.root.after(1000, self.run_clock)

    def run_clock(self):
        if not self.is_running or self.is_paused:
            return

        if self.time_remaining <= 1:
            self.time_remaining = 0
            self.is_running = False
            self.pause_btn.configure(state=tk.DISABLED)
            self.start_btn.pack(side=tk.LEFT, padx=8, before=self.pause_btn)
            self.update_display()
            return

        self.time_remaining -= 1
        self.update_display()
        self.timer_job = self.root.after(1000, self.run_clock)

    def toggle_pause(self):
        if not self.is_running:
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_btn.configure(text=" ⏸ Pauze ")
            self.timer_job = self.root.after(1000, self.run_clock)
        else:
            self.is_paused = True
            self.pause_btn.configure(text=" ▶ Hervatten ")
            if self.timer_job:
                self.root.after_cancel(self.timer_job)

    def reset_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        self.is_running = False
        self.is_paused = False
        self.start_btn.pack(side=tk.LEFT, padx=8, before=self.pause_btn)
        self.pause_btn.configure(text=" ⏸ Pauze ", state=tk.DISABLED)

        self.time_remaining = self.total_seconds
        self.update_display()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.fs_btn.configure(text="Venster Verlaten")
            self.footer_label.pack_forget()
            self.presets_frame.pack_forget()
        else:
            self.fs_btn.configure(text="Volledig Scherm")
            self.presets_frame.pack(fill=tk.X, padx=15, pady=(2, 8), before=self.action_frame)
            self.footer_label.pack(pady=(0, 6))

        # Forceer directe schaal-update voor fullscreen / venster
        self.root.after(30, self.apply_resize)

    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.toggle_fullscreen()

def main():
    root = tk.Tk()
    app = SpeakerTimerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
