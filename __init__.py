# Interactive Heatmap v24.35
# Copyright (c) 2026 Jerry Shen
# License: MIT

import datetime
import time
import json
import os
import math
import traceback
import re
import aqt
from datetime import timedelta, date
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo

ADDON_NAME = "Interactive Heatmap"
VERSION = "1.2.4"

def _is_dark_mode():
    """Check if Anki is in dark mode."""
    try:
        from aqt.theme import theme_manager
        return theme_manager.night_mode
    except:
        return False

def _get_whats_new_html(dark=False):
    """Generate What's New HTML with theme-appropriate colors."""
    if dark:
        text = "#e0e0e0"
        subtext = "#9a9a9a"
        accent = "#b388ff"
    else:
        text = "#2d3436"
        subtext = "#636e72"
        accent = "#8e44ad"

    return f"""
<p style="font-family: -apple-system, sans-serif; font-size: 22px; font-weight: 700; color: {text}; text-align: center; margin: 0 0 4px 0;">Interactive Heatmap</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {accent}; font-weight: 600; text-align: center; margin: 0 0 28px 0;">VERSION {VERSION}</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Revamped Settings Menu</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 20px 0;">Settings menu revamped to allow clearer navigation with tabs for adjusting specific settings.</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Modern Browse Menu</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 20px 0;">Browse menu modernization added with autoformatting for cloze cards in the viewer for quick view of cards and tag coloring. You can turn this feature off in settings</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Customizable Thresholds for Heatmap Coloring</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 20px 0;">Color heatmap using your own personal threshold ranges for desired retention and review speed.</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Customizable Average Period</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 20px 0;">Choose how your daily average is calculated: past week, month, year, or all time. Find it in Settings.</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Deck Cards Colors</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 24px 0;">Customize the colors of New, Learning, and Due pills in your deck list. Find it in Settings under Colors.</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Exam Updates</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 24px 0;">Add multiple exams on the same day.</p>

<p style="font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; color: {text}; margin: 0 0 4px 0;">Other</p>
<p style="font-family: -apple-system, sans-serif; font-size: 12px; color: {subtext}; margin: 0 0 24px 0;">Minor bug fixes.</p>

<p style="font-family: -apple-system, sans-serif; font-size: 11px; color: {subtext}; text-align: center; margin: 0;">Thank you for using Interactive Heatmap!</p>
"""

class WhatsNewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark = _is_dark_mode()
        self.setWindowTitle(f"What's New")
        self.setFixedSize(480, 620)
        self.setup_ui()

    def setup_ui(self):
        if self.dark:
            bg_color = "#2d2d2d"
            btn_area_bg = "#252525"
            border_color = "#404040"
        else:
            bg_color = "#ffffff"
            btn_area_bg = "#f8f9fa"
            border_color = "#e9ecef"

        self.setStyleSheet(f"QDialog {{ background: {bg_color}; }}")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Content area
        content = QWidget()
        content.setStyleSheet(f"background: {bg_color};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 12)

        label = QLabel(_get_whats_new_html(self.dark))
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(label)
        content_layout.addStretch()

        content.setLayout(content_layout)
        layout.addWidget(content)

        # Button area
        btn_container = QWidget()
        btn_container.setFixedHeight(60)
        btn_container.setStyleSheet(f"background: {btn_area_bg};")
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 12, 20, 12)

        btn_layout.addStretch()
        ok_btn = QPushButton("Got it")
        ok_btn.setFixedSize(90, 34)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #8e44ad;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background: #9b59b6; }
            QPushButton:pressed { background: #7d3c98; }
        """)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        btn_container.setLayout(btn_layout)
        layout.addWidget(btn_container)

        self.setLayout(layout)

def check_whats_new():
    """Show What's New dialog if version has changed or on first install."""
    cfg = get_config()
    last_version = cfg.get("last_seen_version", "")

    if last_version != VERSION:
        cfg["last_seen_version"] = VERSION
        write_config(cfg)
        mw.progress.timer(500, lambda: WhatsNewDialog(mw).exec(), False)

gui_hooks.profile_did_open.append(check_whats_new)

_ONE_YEAR_AGO = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")

DEFAULT_CONFIG = {
    "base_color": "#8e44ad",
    "forecast_color": "#bdc3c7",
    "today_color": "#2ecc71",
    "empty_color": "#ebedf0",
    "empty_color_night": "#282c34",
    "graph_reviews_color": "#3498db",
    "graph_time_color": "#e67e22",
    "graph_retention_color": "#f1c40f",
    "graph_forecast_color": "#95a5a6",
    "start_date": _ONE_YEAR_AGO,
    "days_future": 21,
    "cell_size": 10,
    "cell_gap": 2,
    "border_radius": 2,
    "display_mode": "volume",
    "show_graph": True,
    "monochrome_text": False,
    "enable_shadows": True,
    "enable_glass": True,
    "modern_deck_theme": True,
    "enable_deck_glass": True,
    "show_deck_ratio": True,
    "replace_stats": True,
    "glass_opacity": 0.4,
    "active_graphs_v14": ["reviews", "time_card", "retention", "forecast"],
    "refresh_interval": 60,
    "daily_notes": {},
    "exam_days": {},
    "tag_colors": {},
    "retention_min": 75,
    "retention_max": 95,
    "speed_min": 3.0,
    "speed_max": 15.0,
    "avg_period": "year",  # Options: "week", "month", "year", "all"
    "pill_new_color": "#4a90e2",
    "pill_learn_color": "#e74c3c",
    "pill_due_color": "#f1c40f"
}

refresh_timer = None

def get_config():
    conf = DEFAULT_CONFIG.copy()
    mgr_conf = mw.addonManager.getConfig(__name__)
    if mgr_conf: conf.update(mgr_conf)
    return conf

def write_config(conf):
    mw.addonManager.writeConfig(__name__, conf)

class HeatmapSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interactive Heatmap Settings")
        self.setMinimumWidth(420)
        self.cfg = get_config()
        self.color_btns = {}
        self.color_inputs = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()
        tabs.addTab(self.create_general_tab(), "General")
        tabs.addTab(self.create_appearance_tab(), "Appearance")
        tabs.addTab(self.create_colors_tab(), "Colors")
        tabs.addTab(self.create_graphs_tab(), "Graphs")
        layout.addWidget(tabs)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        heatmap_group = QGroupBox("Heatmap Settings")
        hm_layout = QVBoxLayout()

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Default Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Activity Volume", "volume")
        self.mode_combo.addItem("Retention Rate", "retention")
        self.mode_combo.addItem("Review Speed", "score")
        current_mode = self.cfg.get('display_mode', 'volume')
        idx = 0
        if current_mode == 'retention': idx = 1
        elif current_mode == 'score': idx = 2
        self.mode_combo.setCurrentIndex(idx)
        combo_layout.addWidget(self.mode_combo)
        combo_layout.addStretch()
        hm_layout.addLayout(combo_layout)

        avg_layout = QHBoxLayout()
        avg_layout.addWidget(QLabel("Average Period:"))
        self.avg_combo = QComboBox()
        self.avg_combo.addItem("Past Week", "week")
        self.avg_combo.addItem("Past Month", "month")
        self.avg_combo.addItem("Past Year", "year")
        self.avg_combo.addItem("All Time", "all")
        current_avg = self.cfg.get('avg_period', 'year')
        avg_idx = {"week": 0, "month": 1, "year": 2, "all": 3}.get(current_avg, 2)
        self.avg_combo.setCurrentIndex(avg_idx)
        avg_layout.addWidget(self.avg_combo)
        avg_layout.addStretch()
        hm_layout.addLayout(avg_layout)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.date_input = QLineEdit()
        self.date_input.setText(self.cfg.get('start_date', _ONE_YEAR_AGO))
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.date_input.setFixedWidth(100)
        date_layout.addWidget(self.date_input)
        date_layout.addStretch()
        hm_layout.addLayout(date_layout)

        heatmap_group.setLayout(hm_layout)
        layout.addWidget(heatmap_group)

        threshold_group = QGroupBox("Thresholds")
        th_layout = QVBoxLayout()

        ret_layout = QHBoxLayout()
        ret_layout.addWidget(QLabel("Retention Range (%):"))
        self.ret_min_input = QSpinBox()
        self.ret_min_input.setRange(0, 100)
        self.ret_min_input.setValue(int(self.cfg.get('retention_min', 75)))
        ret_layout.addWidget(self.ret_min_input)
        ret_layout.addWidget(QLabel("-"))
        self.ret_max_input = QSpinBox()
        self.ret_max_input.setRange(0, 100)
        self.ret_max_input.setValue(int(self.cfg.get('retention_max', 95)))
        ret_layout.addWidget(self.ret_max_input)
        ret_layout.addStretch()
        th_layout.addLayout(ret_layout)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed Range (sec):"))
        self.speed_min_input = QDoubleSpinBox()
        self.speed_min_input.setRange(0.1, 60.0)
        self.speed_min_input.setSingleStep(0.5)
        self.speed_min_input.setValue(float(self.cfg.get('speed_min', 3.0)))
        speed_layout.addWidget(self.speed_min_input)
        speed_layout.addWidget(QLabel("-"))
        self.speed_max_input = QDoubleSpinBox()
        self.speed_max_input.setRange(0.1, 60.0)
        self.speed_max_input.setSingleStep(0.5)
        self.speed_max_input.setValue(float(self.cfg.get('speed_max', 15.0)))
        speed_layout.addWidget(self.speed_max_input)
        speed_layout.addStretch()
        th_layout.addLayout(speed_layout)

        threshold_group.setLayout(th_layout)
        layout.addWidget(threshold_group)

        other_group = QGroupBox("Other")
        other_layout = QVBoxLayout()

        self.chk_browser_theme = QCheckBox("Enable Card Browser Theme")
        self.chk_browser_theme.setToolTip("Apply modern theme styling to the card browser window.")
        self.chk_browser_theme.setChecked(self.cfg.get("enable_browser_theme", True))
        other_layout.addWidget(self.chk_browser_theme)

        other_group.setLayout(other_layout)
        layout.addWidget(other_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        heatmap_group = QGroupBox("Heatmap")
        hm_layout = QVBoxLayout()

        self.chk_glass = QCheckBox("Enable Glass Effect")
        self.chk_glass.setChecked(self.cfg.get("enable_glass", True))
        hm_layout.addWidget(self.chk_glass)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Glass Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        current_opacity = int(self.cfg.get('glass_opacity', 0.4) * 100)
        self.opacity_slider.setValue(current_opacity)
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        self.opacity_label = QLabel(f"{current_opacity}%")
        self.opacity_label.setFixedWidth(35)
        slider_layout.addWidget(self.opacity_slider)
        slider_layout.addWidget(self.opacity_label)
        hm_layout.addLayout(slider_layout)

        self.chk_replace = QCheckBox("Hide Anki default stats")
        self.chk_replace.setToolTip("Hides the default 'Studied X cards in Y minutes' message.")
        self.chk_replace.setChecked(self.cfg.get("replace_stats", True))
        hm_layout.addWidget(self.chk_replace)

        heatmap_group.setLayout(hm_layout)
        layout.addWidget(heatmap_group)

        deck_group = QGroupBox("Deck Browser")
        deck_layout = QVBoxLayout()

        self.chk_modern = QCheckBox("Enable Modern Deck Theme")
        self.chk_modern.setChecked(self.cfg.get("modern_deck_theme", True))
        deck_layout.addWidget(self.chk_modern)

        sub_layout = QVBoxLayout()
        sub_layout.setContentsMargins(20, 0, 0, 0)

        self.chk_deck_glass = QCheckBox("Liquid Glass Background")
        self.chk_deck_glass.setChecked(self.cfg.get("enable_deck_glass", True))
        sub_layout.addWidget(self.chk_deck_glass)

        self.chk_ratio = QCheckBox("Activity Ratio Ring")
        self.chk_ratio.setChecked(self.cfg.get("show_deck_ratio", True))
        sub_layout.addWidget(self.chk_ratio)

        deck_layout.addLayout(sub_layout)

        self.chk_modern.toggled.connect(self.chk_deck_glass.setEnabled)
        self.chk_modern.toggled.connect(self.chk_ratio.setEnabled)
        self.chk_deck_glass.setEnabled(self.chk_modern.isChecked())
        self.chk_ratio.setEnabled(self.chk_modern.isChecked())

        deck_group.setLayout(deck_layout)
        layout.addWidget(deck_group)

        text_group = QGroupBox("Text")
        text_layout = QVBoxLayout()

        self.chk_monochrome = QCheckBox("High Contrast Text (Disable Colors)")
        self.chk_monochrome.setChecked(self.cfg.get("monochrome_text", False))
        text_layout.addWidget(self.chk_monochrome)

        self.chk_shadows = QCheckBox("Enable Text Shadows")
        self.chk_shadows.setChecked(self.cfg.get("enable_shadows", True))
        text_layout.addWidget(self.chk_shadows)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_colors_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout()

        # Card Counts (New/Learning/Due)
        pill_colors = QGroupBox("Card Counts")
        pc_layout = QGridLayout()

        pill_color_defs = [
            ("pill_new_color", "New:", "#4a90e2"),
            ("pill_learn_color", "Learning:", "#e74c3c"),
            ("pill_due_color", "Due:", "#f1c40f"),
        ]

        for row, (key, label, default) in enumerate(pill_color_defs):
            pc_layout.addWidget(QLabel(label), row, 0)

            color_input = QLineEdit()
            color_input.setText(self.cfg.get(key, default))
            color_input.setFixedWidth(80)
            self.color_inputs[key] = color_input
            pc_layout.addWidget(color_input, row, 1)

            color_btn = QPushButton()
            color_btn.setFixedSize(24, 24)
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setStyleSheet(f"background-color: {self.cfg.get(key, default)}; border: 1px solid #bdc3c7; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, k=key: self.pick_graph_color(k))
            self.color_btns[key] = color_btn
            pc_layout.addWidget(color_btn, row, 2)

        pill_colors.setLayout(pc_layout)
        layout.addWidget(pill_colors)

        # Heatmap Colors
        heatmap_colors = QGroupBox("Heatmap")
        hc_layout = QGridLayout()

        color_defs = [
            ("base_color", "Volume Color:", "#8e44ad"),
            ("today_color", "Today Cell Border:", "#2ecc71"),
            ("forecast_color", "Forecast Color:", "#bdc3c7"),
            ("empty_color", "Empty Cell (Light):", "#ebedf0"),
            ("empty_color_night", "Empty Cell (Dark):", "#282c34"),
        ]

        for row, (key, label, default) in enumerate(color_defs):
            hc_layout.addWidget(QLabel(label), row, 0)

            color_input = QLineEdit()
            color_input.setText(self.cfg.get(key, default))
            color_input.setFixedWidth(80)
            color_input.setPlaceholderText("#RRGGBB")
            color_input.textChanged.connect(lambda t, k=key: self.on_color_hex_changed(k, t))
            self.color_inputs[key] = color_input
            hc_layout.addWidget(color_input, row, 1)

            color_btn = QPushButton()
            color_btn.setFixedSize(24, 24)
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setStyleSheet(f"background-color: {self.cfg.get(key, default)}; border: 1px solid #bdc3c7; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, k=key: self.pick_graph_color(k))
            self.color_btns[key] = color_btn
            hc_layout.addWidget(color_btn, row, 2)

        heatmap_colors.setLayout(hc_layout)
        layout.addWidget(heatmap_colors)

        # Graph Colors
        graph_colors = QGroupBox("Graph Lines")
        gc_layout = QGridLayout()

        graph_color_defs = [
            ("graph_reviews_color", "Reviews:", "#3498db"),
            ("graph_time_color", "Time/Card:", "#e67e22"),
            ("graph_retention_color", "Retention:", "#f1c40f"),
            ("graph_forecast_color", "Forecast:", "#95a5a6"),
        ]

        for row, (key, label, default) in enumerate(graph_color_defs):
            gc_layout.addWidget(QLabel(label), row, 0)

            color_input = QLineEdit()
            color_input.setText(self.cfg.get(key, default))
            color_input.setFixedWidth(80)
            color_input.setPlaceholderText("#RRGGBB")
            color_input.textChanged.connect(lambda t, k=key: self.on_color_hex_changed(k, t))
            self.color_inputs[key] = color_input
            gc_layout.addWidget(color_input, row, 1)

            color_btn = QPushButton()
            color_btn.setFixedSize(24, 24)
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setStyleSheet(f"background-color: {self.cfg.get(key, default)}; border: 1px solid #bdc3c7; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, k=key: self.pick_graph_color(k))
            self.color_btns[key] = color_btn
            gc_layout.addWidget(color_btn, row, 2)

        graph_colors.setLayout(gc_layout)
        layout.addWidget(graph_colors)

        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll

    def create_graphs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        gb = QGroupBox("Graph Panel")
        gl = QVBoxLayout()

        self.chk_show_graph = QCheckBox("Show Bottom Graph Panel")
        self.chk_show_graph.setChecked(self.cfg.get("show_graph", True))
        gl.addWidget(self.chk_show_graph)

        gl.addWidget(QLabel("Active Metrics:"))

        metrics_layout = QVBoxLayout()
        metrics_layout.setContentsMargins(20, 0, 0, 0)

        self.chk_rev = QCheckBox("Review Count")
        self.chk_time = QCheckBox("Time/Card")
        self.chk_ret = QCheckBox("Retention %")
        self.chk_fut = QCheckBox("Forecast")

        active = self.cfg.get("active_graphs_v14", [])
        self.chk_rev.setChecked("reviews" in active)
        self.chk_time.setChecked("time_card" in active)
        self.chk_ret.setChecked("retention" in active)
        self.chk_fut.setChecked("forecast" in active)

        metrics_layout.addWidget(self.chk_rev)
        metrics_layout.addWidget(self.chk_time)
        metrics_layout.addWidget(self.chk_ret)
        metrics_layout.addWidget(self.chk_fut)

        gl.addLayout(metrics_layout)
        gb.setLayout(gl)
        layout.addWidget(gb)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def update_opacity_label(self, value):
        self.opacity_label.setText(f"{value}%")

    def on_color_hex_changed(self, key, text):
        if QColor.isValidColor(text) and key in self.color_btns:
            self.color_btns[key].setStyleSheet(f"background-color: {text}; border: 1px solid #bdc3c7; border-radius: 4px;")

    def pick_graph_color(self, key):
        current = self.color_inputs[key].text()
        c = QColorDialog.getColor(QColor(current), self)
        if c.isValid():
            self.color_inputs[key].setText(c.name())
            self.color_btns[key].setStyleSheet(f"background-color: {c.name()}; border: 1px solid #bdc3c7; border-radius: 4px;")

    def save(self):
        ag = []
        if self.chk_rev.isChecked(): ag.append("reviews")
        if self.chk_time.isChecked(): ag.append("time_card")
        if self.chk_ret.isChecked(): ag.append("retention")
        if self.chk_fut.isChecked(): ag.append("forecast")

        self.cfg['active_graphs_v14'] = ag
        self.cfg['show_graph'] = self.chk_show_graph.isChecked()
        self.cfg['monochrome_text'] = self.chk_monochrome.isChecked()
        self.cfg['enable_shadows'] = self.chk_shadows.isChecked()
        self.cfg['enable_glass'] = self.chk_glass.isChecked()
        self.cfg['enable_browser_theme'] = self.chk_browser_theme.isChecked()

        self.cfg['modern_deck_theme'] = self.chk_modern.isChecked()
        self.cfg['enable_deck_glass'] = self.chk_deck_glass.isChecked()
        self.cfg['show_deck_ratio'] = self.chk_ratio.isChecked()
        self.cfg['replace_stats'] = self.chk_replace.isChecked()

        self.cfg['display_mode'] = self.mode_combo.currentData()
        self.cfg['avg_period'] = self.avg_combo.currentData()
        self.cfg['glass_opacity'] = self.opacity_slider.value() / 100.0

        new_date = self.date_input.text().strip()
        try:
            datetime.datetime.strptime(new_date, "%Y-%m-%d")
            self.cfg['start_date'] = new_date
        except: pass

        self.cfg['retention_min'] = self.ret_min_input.value()
        self.cfg['retention_max'] = self.ret_max_input.value()
        self.cfg['speed_min'] = self.speed_min_input.value()
        self.cfg['speed_max'] = self.speed_max_input.value()

        for key, inp in self.color_inputs.items():
            color = inp.text().strip()
            if QColor.isValidColor(color):
                self.cfg[key] = color

        write_config(self.cfg)
        self.accept()
        mw.reset()

class HeatmapNoteDialog(QDialog):
    def __init__(self, date_str, current_note="", exam_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Note for {date_str}")
        self.setMinimumWidth(380)
        self.date_str = date_str
        self.note_text = current_note

        # Convert old single-exam format to list format
        if exam_data is None:
            self.exams = []
        elif isinstance(exam_data, list):
            self.exams = exam_data.copy()
        else:
            # Old format: single dict
            self.exams = [exam_data]

        self.exam_widgets = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Exams section
        exam_group = QGroupBox("Exams / Deadlines")
        exam_group_layout = QVBoxLayout()
        exam_group_layout.setContentsMargins(10, 10, 10, 10)

        # Container for exam rows
        self.exams_container = QWidget()
        self.exams_layout = QVBoxLayout()
        self.exams_layout.setContentsMargins(0, 0, 0, 0)
        self.exams_layout.setSpacing(8)
        self.exams_container.setLayout(self.exams_layout)
        exam_group_layout.addWidget(self.exams_container)

        # Add existing exams
        for exam in self.exams:
            self.add_exam_row(exam.get("label", "Exam"), exam.get("color", "#e74c3c"))

        # Add exam button
        add_btn = QPushButton("+ Add Exam")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(lambda: self.add_exam_row("", "#e74c3c"))
        exam_group_layout.addWidget(add_btn)

        exam_group.setLayout(exam_group_layout)
        layout.addWidget(exam_group)

        # Notes section
        lbl = QLabel("Daily Note:")
        layout.addWidget(lbl)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.note_text)
        self.text_edit.setFixedHeight(80)
        layout.addWidget(self.text_edit)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def add_exam_row(self, label="", color="#e74c3c"):
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        lbl_input = QLineEdit()
        lbl_input.setPlaceholderText("Label (e.g. Biology)")
        lbl_input.setText(label)
        row_layout.addWidget(lbl_input)

        hex_input = QLineEdit()
        hex_input.setPlaceholderText("#RRGGBB")
        hex_input.setFixedWidth(70)
        hex_input.setText(color)
        row_layout.addWidget(hex_input)

        color_btn = QPushButton()
        color_btn.setFixedSize(24, 24)
        color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #bdc3c7; border-radius: 4px;")

        def on_hex_change(text, btn=color_btn):
            if QColor.isValidColor(text):
                btn.setStyleSheet(f"background-color: {text}; border: 1px solid #bdc3c7; border-radius: 4px;")
        hex_input.textChanged.connect(on_hex_change)

        def pick_color(checked, inp=hex_input, btn=color_btn):
            c = QColorDialog.getColor(QColor(inp.text()), self)
            if c.isValid():
                inp.setText(c.name())
                btn.setStyleSheet(f"background-color: {c.name()}; border: 1px solid #bdc3c7; border-radius: 4px;")
        color_btn.clicked.connect(pick_color)
        row_layout.addWidget(color_btn)

        del_btn = QPushButton("x")
        del_btn.setFixedSize(24, 24)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("color: #e74c3c; font-weight: bold;")
        row_layout.addWidget(del_btn)

        row.setLayout(row_layout)

        widget_data = {"row": row, "label": lbl_input, "hex": hex_input, "color_btn": color_btn}
        self.exam_widgets.append(widget_data)
        self.exams_layout.addWidget(row)

        def remove_row(checked, wd=widget_data):
            self.exam_widgets.remove(wd)
            wd["row"].deleteLater()
        del_btn.clicked.connect(remove_row)

    def get_text(self):
        return self.text_edit.toPlainText().strip()

    def get_exam_result(self):
        result = []
        for wd in self.exam_widgets:
            label = wd["label"].text().strip()
            color = wd["hex"].text().strip()
            if label:  # Only include if label is not empty
                if not QColor.isValidColor(color):
                    color = "#e74c3c"
                result.append({"label": label, "color": color})
        return result if result else None

class FastEngine:
    def __init__(self):
        self.col = mw.col
        self.cfg = get_config()
        self.rollover = self.col.conf.get('rollover', 4)
    
    def get_start_date(self):
        try:
            config_start = datetime.datetime.strptime(self.cfg['start_date'], "%Y-%m-%d").date()
        except:
            config_start = date.today() - timedelta(days=365)

        first_rev_ts = self.col.db.scalar("SELECT min(id) FROM revlog")
        if first_rev_ts:
            first_rev_date = datetime.datetime.fromtimestamp(first_rev_ts / 1000).date()
        else:
            first_rev_date = date.today()

        effective_start = max(config_start, first_rev_date)
        offset = (effective_start.weekday() + 1) % 7
        return effective_start - timedelta(days=offset)

    def get_data(self):
        rollover_ms = self.rollover * 3600 * 1000
        now_ts = time.time()
        anki_today_dt = datetime.datetime.fromtimestamp(now_ts - (self.rollover * 3600))
        today_str = anki_today_dt.strftime("%Y-%m-%d")
        today_date = anki_today_dt.date()
        start_date = self.get_start_date()
        cutoff_ts = int(time.mktime(start_date.timetuple()) * 1000)

        data = self.col.db.all(f"SELECT id, cid, ease, time, type FROM revlog WHERE id > {cutoff_ts} AND type < 4 ORDER BY id")

        history = {}
        time_history = {}
        retention = {}
        today_revs = 0
        today_time_ms = 0
        today_pass = 0
        today_revs_retention = 0
        today_pass_retention = 0
        seen_cards = set()

        for (ts, cid, ease, t_taken, rev_type) in data:
            row_dt = datetime.datetime.fromtimestamp((ts - rollover_ms) / 1000)
            d_str = row_dt.strftime("%Y-%m-%d")
            history[d_str] = history.get(d_str, 0) + 1
            time_history[d_str] = time_history.get(d_str, 0) + t_taken
            is_first_review = cid not in seen_cards
            seen_cards.add(cid)
            # Only count retention for reviews, relearns, filtered, and learning cards that aren't first-time
            if rev_type > 0 or not is_first_review:
                if d_str not in retention: retention[d_str] = [0, 0]
                retention[d_str][1] += 1
                if ease > 1: retention[d_str][0] += 1
            if d_str == today_str:
                today_revs += 1
                today_time_ms += t_taken
                if ease > 1: today_pass += 1
                # Include reviews, relearns, filtered, and learning cards that aren't first-time
                if rev_type > 0 or not is_first_review:
                    today_revs_retention += 1
                    if ease > 1: today_pass_retention += 1

        try:
            today_int = self.col.sched.today
            day_cutoff = self.col.sched.day_cutoff 
            now_int = int(time.time())
        except:
            today_int = 0
            day_cutoff = int(time.time()) + 86400
            now_int = int(time.time())

        deck_stats = {} 
        def add_stat(did, key, val):
            d_str = str(did)
            if d_str not in deck_stats: deck_stats[d_str] = {'n':0, 'l':0, 'd':0, 'done':0}
            deck_stats[d_str][key] = val

        rows = self.col.db.all("SELECT did, count() FROM cards WHERE queue=0 GROUP BY did")
        for did, cnt in rows: add_stat(did, 'n', cnt)
        rows = self.col.db.all(f"SELECT did, count() FROM cards WHERE queue IN (1,3) AND due <= {now_int} GROUP BY did")
        for did, cnt in rows: add_stat(did, 'l', cnt)
        rows = self.col.db.all(f"SELECT did, count() FROM cards WHERE queue=2 AND due <= {today_int} GROUP BY did")
        for did, cnt in rows: add_stat(did, 'd', cnt)

        today_start_ts = int(day_cutoff - 86400) * 1000
        done_rows = self.col.db.all(f"""
            SELECT c.did, count(DISTINCT c.id) 
            FROM revlog r 
            JOIN cards c ON r.cid = c.id 
            WHERE r.id > {today_start_ts} 
            AND (
                (c.queue IN (2, 3) AND c.due > {today_int})
                OR
                (c.queue IN (0, 1) AND c.due > {day_cutoff})
                OR
                (c.queue < 0)
            )
            GROUP BY c.did
        """)
        for did, cnt in done_rows: add_stat(did, 'done', cnt)

        all_decks = self.col.decks.all_names_and_ids()
        id_to_name = { (d.id if hasattr(d,'id') else d['id']): (d.name if hasattr(d,'name') else d['name']) for d in all_decks }
        name_to_id = { name: did for did, name in id_to_name.items() }
        
        snapshot = list(deck_stats.items()) 
        for did_str, stats in snapshot:
            try: did_int = int(did_str)
            except: continue
            if did_int in id_to_name:
                parts = id_to_name[did_int].split("::")
                current = ""
                for i in range(len(parts) - 1):
                    if i > 0: current += "::"
                    current += parts[i]
                    if current in name_to_id:
                        pid = str(name_to_id[current])
                        if pid not in deck_stats: deck_stats[pid] = {'n':0, 'l':0, 'd':0, 'done':0}
                        deck_stats[pid]['n'] += stats['n']
                        deck_stats[pid]['l'] += stats['l']
                        deck_stats[pid]['d'] += stats['d']
                        deck_stats[pid]['done'] += stats['done']

        forecast = {}
        cards = self.col.db.list(f"SELECT due FROM cards WHERE queue IN (2,3) AND due >= {self.col.sched.today}")
        base_dt = datetime.datetime.strptime(today_str, "%Y-%m-%d").date()
        for due_val in cards:
            try:
                days_diff = due_val - self.col.sched.today
                f_date = base_dt + timedelta(days=days_diff)
                f_str = f_date.strftime("%Y-%m-%d")
                forecast[f_str] = forecast.get(f_str, 0) + 1
            except: pass

        today_rate = int((today_pass_retention/today_revs_retention)*100) if today_revs_retention > 0 else 0
        avg_time = round((today_time_ms/today_revs)/1000, 1) if today_revs > 0 else 0
        total_mins = int(round((today_time_ms/1000)/60))

        # Calculate daily average based on selected period
        avg_period = self.cfg.get("avg_period", "year")
        if avg_period == "week":
            period_start = today_date - timedelta(days=7)
        elif avg_period == "month":
            period_start = today_date - timedelta(days=30)
        elif avg_period == "year":
            period_start = today_date - timedelta(days=365)
        else:  # "all"
            period_start = start_date

        period_revs = sum(v for k, v in history.items()
                         if datetime.datetime.strptime(k, "%Y-%m-%d").date() >= period_start)
        period_days = max(1, (today_date - period_start).days + 1)
        daily_avg = int(period_revs / period_days)
        
        cards_due = 0
        try:
             rev = self.col.db.scalar(f"SELECT count() FROM cards WHERE queue = 2 AND due <= {today_int}")
             lrn = self.col.db.scalar(f"SELECT count() FROM cards WHERE queue IN (1, 3) AND due <= {now_int}")
             cards_due = rev + lrn
        except: pass

        streak = 0
        dates = sorted(history.keys())
        ords = [datetime.datetime.strptime(d, "%Y-%m-%d").toordinal() for d in dates]
        today_ord = today_date.toordinal()
        if ords and (today_ord - ords[-1]) <= 1:
            streak = 1
            for i in range(len(ords)-1, 0, -1):
                if ords[i] == ords[i-1] + 1: streak += 1
                elif ords[i] == ords[i-1]: continue
                else: break

        return history, time_history, retention, forecast, today_revs, today_rate, avg_time, total_mins, cards_due, daily_avg, streak, today_str, start_date, deck_stats, avg_period

    def get_graph_points(self, history, time_hist, retention, forecast, today_str):
        days = 30
        w, h = 530, 60
        today = datetime.datetime.strptime(today_str, "%Y-%m-%d").date()
        active = self.cfg.get("active_graphs_v14", ["reviews", "time_card", "retention", "forecast"])
        
        raw_rev, raw_time, raw_ret, raw_fut = [], [], [], []
        meta_data = []
        
        for i in range(days-1, -1, -1):
            d = today - timedelta(days=i)
            d_s = d.strftime("%Y-%m-%d")
            
            r = history.get(d_s, 0)
            t = time_hist.get(d_s, 0)
            s = round((t/r)/1000, 1) if r > 0 else 0
            
            ret_data = retention.get(d_s, [0, 0])
            ret_pct = int((ret_data[0] / ret_data[1]) * 100) if ret_data[1] > 0 else 0
            
            f_d = today + timedelta(days=(days-i)) 
            f_s = f_d.strftime("%Y-%m-%d")
            f = forecast.get(f_s, 0)
            
            raw_rev.append(r)
            raw_time.append(s)
            raw_ret.append(ret_pct)
            raw_fut.append(f)
            
            meta_data.append({ 
                "label": d.strftime("%b %d").upper(), 
                "rev": r, 
                "time": s, 
                "ret": ret_pct,
                "fut": f
            })
            
        def get_path(arr, invert=False, fill=False, is_retention=False, line_color=None):
            if not arr: return ""
            clean_arr = [x if x is not None else 0 for x in arr]
            mx = max(clean_arr) if max(clean_arr) > 0 else 1
            min_v = 0
            if is_retention:
                valid = [v for v in clean_arr if v > 0]
                true_min = min(valid) if valid else 0
                min_v = max(0, true_min - 5)
                mx = 100
                if min_v >= mx: min_v = 0
            pts = []
            step = w / (len(clean_arr) - 1) if len(clean_arr) > 1 else w
            padding = 5
            draw_h = h - (2 * padding)
            for i, val in enumerate(clean_arr):
                x = i * step
                v_clamped = val
                if is_retention:
                    if v_clamped < min_v: v_clamped = min_v
                    if v_clamped > mx: v_clamped = mx
                rng = mx - min_v
                if rng <= 0: rng = 1
                ratio = (v_clamped - min_v) / rng
                if invert: y = padding + (ratio * draw_h)
                else: y = (h - padding) - (ratio * draw_h)
                pts.append(f"{x:.1f},{y:.1f}")
            d = f"M {pts[0]}"
            for i in range(len(pts)-1):
                p0 = pts[max(0, i - 1)]
                p1 = pts[i]
                p2 = pts[i + 1]
                p3 = pts[min(len(pts) - 1, i + 2)]
                def pc(s): return [float(v) for v in s.split(',')]
                c0, c1, c2, c3 = pc(p0), pc(p1), pc(p2), pc(p3)
                tension = 0.2
                cp1x = c1[0] + (c2[0] - c0[0]) * tension
                cp1y = c1[1] + (c2[1] - c0[1]) * tension
                cp2x = c2[0] - (c3[0] - c1[0]) * tension
                cp2y = c2[1] - (c3[1] - c1[1]) * tension
                d += f" C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {c2[0]:.1f},{c2[1]:.1f}"
            if fill:
                d_fill = d + f" L {w},{h} L 0,{h} Z"
                stroke_c = line_color or self.cfg['base_color']
                return f'<path d="{d_fill}" fill="url(#grad)" stroke="none" /> <path d="{d}" fill="none" stroke="{stroke_c}" stroke-width="2" />'
            color = line_color or "#95a5a6"
            return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" />'

        svg_layers = ""
        legend_items = []
        if "reviews" in active:
            rev_color = self.cfg.get('graph_reviews_color', '#3498db')
            d_rev = get_path(raw_rev, False, True, line_color=rev_color)
            svg_layers += d_rev
            legend_items.append(f'<span style="color:{rev_color}">■ REVIEWS</span>')
        if "forecast" in active:
            fut_color = self.cfg.get('graph_forecast_color', '#95a5a6')
            d_fut = get_path(raw_fut, False, False, line_color=fut_color)
            svg_layers += d_fut
            legend_items.append(f'<span style="color:{fut_color}">■ FORECAST</span>')
        if "time_card" in active:
            time_color = self.cfg.get('graph_time_color', '#e67e22')
            d_time = get_path(raw_time, True, False, line_color=time_color)
            svg_layers += d_time
            legend_items.append(f'<span style="color:{time_color}">■ TIME/CARD</span>')
        if "retention" in active:
            ret_color = self.cfg.get('graph_retention_color', '#f1c40f')
            d_ret = get_path(raw_ret, False, False, is_retention=True, line_color=ret_color)
            svg_layers += d_ret
            legend_items.append(f'<span style="color:{ret_color}">■ RETENTION</span>')
            
        return svg_layers, meta_data, " &nbsp;&nbsp; ".join(legend_items)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def interpolate_color(color_start, color_end, ratio):
    ratio = max(0, min(1, ratio))
    r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
    g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
    b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"

def blend_colors(c1_hex, c2_hex, ratio):
    r1, g1, b1 = hex_to_rgb(c1_hex)
    r2, g2, b2 = hex_to_rgb(c2_hex)
    r = r1 + (r2 - r1) * ratio
    g = g1 + (g2 - g1) * ratio
    b = b1 + (b2 - b1) * ratio
    return rgb_to_hex((r, g, b))

c_bad = (255, 85, 85)    # Red
c_mid = (255, 204, 0)    # Bright Yellow
c_good = (0, 204, 51)    # Green

def get_speed_color(seconds, cfg=None):
    if cfg is None: cfg = get_config()
    best_sec = float(cfg.get('speed_min', 3.0))
    worst_sec = float(cfg.get('speed_max', 15.0))
    if seconds <= best_sec: return rgb_to_hex(c_good)
    if seconds >= worst_sec: return rgb_to_hex(c_bad)
    ratio = (worst_sec - seconds) / (worst_sec - best_sec)
    if ratio < 0.5:
        local_ratio = ratio * 2
        return interpolate_color(c_bad, c_mid, local_ratio)
    else:
        local_ratio = (ratio - 0.5) * 2
        return interpolate_color(c_mid, c_good, local_ratio)

def get_retention_color(percentage, cfg=None):
    if cfg is None: cfg = get_config()
    min_threshold = float(cfg.get('retention_min', 75)) / 100.0
    max_threshold = float(cfg.get('retention_max', 95)) / 100.0
    if percentage <= min_threshold: ratio = 0.0
    elif percentage >= max_threshold: ratio = 1.0
    else: ratio = (percentage - min_threshold) / (max_threshold - min_threshold)
    if ratio < 0.5:
        local_ratio = ratio * 2
        return interpolate_color(c_bad, c_mid, local_ratio)
    else:
        local_ratio = (ratio - 0.5) * 2
        return interpolate_color(c_mid, c_good, local_ratio)

def setup_timer():
    global refresh_timer
    cfg = get_config()
    if refresh_timer: 
        try: refresh_timer.stop()
        except: pass
        refresh_timer = None
    interval = cfg.get('refresh_interval', 60) * 1000
    refresh_timer = QTimer()
    refresh_timer.timeout.connect(on_refresh_timer)
    refresh_timer.start(interval)

def on_refresh_timer():
    if mw.state == "deckBrowser":
        try:
            html_body = get_html_body_content()
            safe_html = json.dumps(html_body)
            js = f"var root = document.getElementById('heatmap-root'); if(root) {{ root.outerHTML = {safe_html}; if(window.initHeatmap) window.initHeatmap(); }}"
            mw.deckBrowser.web.eval(js)
        except: pass

def get_html_body_content():
    cfg = get_config()
    eng = FastEngine()
    
    active_graphs = cfg.get("active_graphs_v14", [])
    show_graph = cfg.get("show_graph", True)
    
    try: opacity = float(cfg.get("glass_opacity", 0.4))
    except: opacity = 0.4
        
    monochrome = cfg.get("monochrome_text", False)
    enable_shadows = cfg.get("enable_shadows", True)
    
    modern_theme = cfg.get("modern_deck_theme", True)
    enable_glass_bg = cfg.get("enable_deck_glass", True)
    show_ratio = cfg.get("show_deck_ratio", True)

    # Pill colors
    pill_new = cfg.get("pill_new_color", "#4a90e2")
    pill_learn = cfg.get("pill_learn_color", "#e74c3c")
    pill_due = cfg.get("pill_due_color", "#f1c40f")

    enable_glass = cfg.get("enable_glass", True)

    notes = cfg.get('daily_notes', {})
    base_c = cfg.get('base_color', "#8e44ad") 
    
    # Normalize exam data to list format per day
    raw_exams = cfg.get("exam_days", {})
    exam_days = {}
    if isinstance(raw_exams, list):
        # Very old format: list of date strings
        for ex_date in raw_exams:
            exam_days[ex_date] = [{"label": "Exam", "color": "#e74c3c"}]
    else:
        for ex_date, ex_data in raw_exams.items():
            if isinstance(ex_data, list):
                exam_days[ex_date] = ex_data
            else:
                # Old format: single dict per day
                exam_days[ex_date] = [ex_data]

    hist, time_hist, retention, forecast, today_revs, today_rate, avg_time, total_mins, cards_due, daily_avg, streak, today_str, start_dt, deck_stats, avg_period = eng.get_data()
    
    deck_stats_json = json.dumps(deck_stats)
    
    svg_paths, meta_data, legend_html = eng.get_graph_points(hist, time_hist, retention, forecast, today_str)

    target_cells = 259
    target_end_dt = start_dt + timedelta(days=target_cells - 1)
    min_end_dt = datetime.datetime.strptime(today_str, "%Y-%m-%d").date() + timedelta(days=cfg['days_future'])
    end_dt = max(target_end_dt, min_end_dt)

    cell_w = cfg['cell_size'] + cfg['cell_gap']
    total_days = (end_dt - start_dt).days + 1
    num_weeks = (total_days // 7)
    total_width_px = num_weeks * cell_w
    
    month_html = ""
    temp_curr = start_dt
    col_idx = 0
    last_label_end_pos = -50 
    
    while temp_curr <= end_dt:
        m_label = ""
        for d in range(7):
            check_day = temp_curr + timedelta(days=d)
            if check_day.day == 1:
                m_label = check_day.strftime("%b").upper()
                break
        
        if not m_label and col_idx == 0:
            m_label = temp_curr.strftime("%b").upper()
            
        if m_label:
            left_pos = col_idx * cell_w
            if left_pos > last_label_end_pos + 10: 
                month_html += f'<div style="position:absolute; left:{left_pos}px;">{m_label}</div>'
                last_label_end_pos = left_pos + 25 
        
        temp_curr += timedelta(days=7)
        col_idx += 1

    curr = start_dt
    cells_html = "" 
    max_rev = max(hist.values()) if hist else 1
    max_score = 1
    for d_key, r_data in retention.items():
        if r_data[0] > max_score: max_score = r_data[0]

    curr_mode = cfg.get('display_mode', 'volume')
    is_ret_mode = (curr_mode == 'retention')
    is_score_mode = (curr_mode == 'score')

    while curr <= end_dt:
        d_s = curr.strftime("%Y-%m-%d")
        d_nice = curr.strftime("%b %d").upper()
        count = hist.get(d_s, 0)
        is_today = (d_s == today_str)
        is_fut = (curr > datetime.datetime.strptime(today_str, "%Y-%m-%d").date())
        exam_list = exam_days.get(d_s, [])
        is_exam = len(exam_list) > 0

        bg_hex = cfg['empty_color']

        alpha = 0.2 if enable_glass else 0.4

        border = "1px solid transparent"
        outline = "none"
        inner_content = ""

        t_val = time_hist.get(d_s, 0)
        spd = round((t_val/count)/1000, 1) if count > 0 else 0
        ret_data = retention.get(d_s, [0, 0])
        correct_count = ret_data[0]
        ret_pct = int((ret_data[0]/ret_data[1])*100) if ret_data[1] > 0 else 0
        f_val = forecast.get(d_s, 0)

        if count > 0: daily_score = (t_val / count) / 1000
        else: daily_score = 0

        info_str = f'{d_nice} &#10; {count} REV'
        if count > 0:
            info_str += f' | {spd} S/C'
            info_str += f' | {ret_pct}% RET'
        if f_val > 0:
            info_str += f' | {f_val} FUT'

        day_note = notes.get(d_s, "").strip()
        if day_note:
            safe_note = day_note.replace('"', "'")
            info_str += f' &#10;&#10; {safe_note}'

        is_future_exam = is_exam and (is_fut or is_today)

        if is_future_exam:
            # Use first exam's color for cell background
            ex_color = exam_list[0].get("color", "#e74c3c")
            for ex in exam_list:
                info_str += f" &#10; ⚠ {ex.get('label', 'Exam').upper()}"
            bg_hex = ex_color
            alpha = 1.0
            inner_content = "<div style='display:flex;justify-content:center;align-items:center;height:100%;font-size:8px;color:#fff;font-weight:bold;'>!</div>"
        elif is_exam:
            for ex in exam_list:
                info_str += f" &#10; ⚠ {ex.get('label', 'Exam').upper()}"

        rev_c = cfg.get('graph_reviews_color', '#3498db')
        time_c = cfg.get('graph_time_color', '#e67e22')
        ret_c = cfg.get('graph_retention_color', '#f1c40f')
        fut_c = cfg.get('graph_forecast_color', '#95a5a6')
        legend_info = f"{d_nice} &nbsp;&nbsp; <span style='color:{rev_c}'>{count} REV</span>"
        if count > 0:
            legend_info += f" &nbsp;&nbsp; <span style='color:{time_c}'>{spd} S/C</span>"
            legend_info += f" &nbsp;&nbsp; <span style='color:{ret_c}'>{ret_pct}% RET</span>"
        if f_val > 0:
            legend_info += f" &nbsp;&nbsp; <span style='color:{fut_c}'>{f_val} FUT</span>"
        for ex in exam_list:
            ex_label = ex.get("label", "Exam")
            ex_color = ex.get("color", "#e74c3c")
            legend_info += f" &nbsp;&nbsp; <span style='color:{ex_color}'>⚠ {ex_label.upper()}</span>"

        safe_legend = legend_info.replace("'", "&#39;")
        safe_tooltip = info_str.replace('"', '&quot;')

        if not is_future_exam:
            if count > 0:
                if is_ret_mode:
                    rate = (correct_count / ret_data[1]) if ret_data[1] > 0 else 0
                    bg_hex = get_retention_color(rate)
                    alpha = 1.0 
                elif is_score_mode:
                    real_sec = (t_val / count) / 1000
                    bg_hex = get_speed_color(real_sec)
                    alpha = 1.0 
                else:
                    bg_hex = base_c
                    ratio = count / max_rev
                    alpha = ratio ** 0.7
                    alpha = max(0.05, alpha)
            elif is_fut and f_val > 0:
                 bg_hex = cfg['forecast_color']
                 alpha = 0.5
        
        try:
            h_clean = bg_hex.lstrip('#')
            r, g, b = tuple(int(h_clean[i:i+2], 16) for i in (0, 2, 4))
            rgba_bg = f"rgba({r},{g},{b},{alpha:.2f})"
        except: rgba_bg = bg_hex

        if is_today:
            today_c = cfg.get('today_color', '#2ecc71')
            outline = f"2px solid {today_c}"
            if count == 0 and f_val == 0 and not is_exam: rgba_bg = "transparent"
            
        click_cmd = f"heatmap:note:{d_s}"
        cells_html += f'<div class="cell tooltip-target" style="background:{rgba_bg}; opacity:1.0; border:{border}; outline:{outline}; outline-offset:-1px;" onclick="pycmd(\'{click_cmd}\')" data-tooltip="{safe_tooltip}" data-legend="{safe_legend}">{inner_content}</div>'
        curr += timedelta(days=1)

    if total_mins >= 60:
        display_time = f"{total_mins/60:.1f}"
        time_unit = "h"
    else:
        display_time = str(total_mins)
        time_unit = "m"

    workload = today_revs + cards_due
    ratio = today_revs / max(1, workload)
    
    if monochrome:
        c_today = "var(--txt)"
        c_time = "var(--txt)"
        c_qual = "var(--txt)"
        base_text_color = "var(--txt)"
    else:
        c_today = "#2ecc71" if ratio >= 0.8 else ("#f1c40f" if ratio >= 0.5 else "#e74c3c")
        c_time = get_speed_color(avg_time)
        c_qual = get_retention_color(today_rate / 100.0)
        base_text_color = base_c

    meta_json = json.dumps(meta_data)

    vol_class = "active" if curr_mode == "volume" else ""
    ret_class = "active" if curr_mode == "retention" else ""
    scr_class = "active" if curr_mode == "score" else ""
    graph_display_style = "display: block;" if show_graph else "display: none;"

    mono_js = "true" if monochrome else "false"
    
    if enable_glass:
        base_glass = f"""
            background: linear-gradient(135deg, rgba(255,255,255,{opacity}) 0%, rgba(255,255,255,{max(0, opacity-0.2)}) 100%);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.05);
        """
        night_glass = f"""
            background: linear-gradient(135deg, rgba(30,30,30,{opacity}) 0%, rgba(10,10,10,{max(0, opacity-0.2)}) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4), inset 0 0 0 1px rgba(255,255,255,0.02);
        """
    else:
        base_glass = f"""
            background: rgba(255,255,255,{opacity});
            border: 1px solid var(--border); box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        """
        night_glass = f"""
            background: rgba(30,30,30,{opacity});
            border: 1px solid var(--border); box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        """

    deck_css = ""
    if modern_theme:
        if enable_glass_bg:
            cont_bg_light = base_glass
            cont_bg_dark = night_glass
        else:
            cont_bg_light = "background: transparent; border: none; box-shadow: none;"
            cont_bg_dark = "background: transparent; border: none; box-shadow: none;"

        deck_css = f"""
        .glass-deck-container {{
            {cont_bg_light}
            border-radius: 16px !important;
            margin: 30px auto !important;
            padding: 15px !important;
            width: 540px !important; min-width: 540px !important; max-width: 540px !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }}
        .night_mode .glass-deck-container {{
            {cont_bg_dark}
        }}
        .glass-deck-container table {{
            background: transparent !important;
            border: none !important;
            border-collapse: separate !important; 
            border-spacing: 0 1px !important;
            width: 100% !important;
            table-layout: fixed !important;
        }}
        .glass-deck-container tr {{
            background: transparent !important;
        }}
        .glass-deck-container th {{
            padding: 0px 5px 8px 5px !important;
            border: none !important;
            border-bottom: 1px solid rgba(140, 140, 140, 0.15) !important;
            font-weight: 700 !important;
            font-size: 10px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.5;
            vertical-align: bottom !important;
        }}
        .glass-deck-container td {{
            padding: 5px 5px !important;
            border: none !important;
            vertical-align: middle !important;
        }}
        .glass-deck-container th:first-child,
        .glass-deck-container td:first-child {{
            text-align: left !important;
            width: auto !important;
            padding-left: 10px !important;
        }}
        .glass-deck-container th:nth-child(2), .glass-deck-container td:nth-child(2),
        .glass-deck-container th:nth-child(3), .glass-deck-container td:nth-child(3),
        .glass-deck-container th:nth-child(4), .glass-deck-container td:nth-child(4) {{
            text-align: center !important;
            width: 60px !important;
        }}
        .glass-deck-container th:nth-child(5),
        .glass-deck-container td:nth-child(5) {{
            text-align: center !important;
            width: 45px !important;
        }}
        .glass-deck-container th:last-child,
        .glass-deck-container td:last-child {{
            width: 40px !important;
            text-align: center !important;
        }}
        .stat-badge {{
            display: inline-block;
            padding: 3px 0px;
            width: 42px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            transition: all 0.2s ease;
        }}
        .badge-dim {{ color: currentColor; opacity: 0.15; font-weight: 400; }}
        .badge-new {{ color: {pill_new}; background: {pill_new}20; border: 1px solid {pill_new}50; }}
        .badge-lrn {{ color: {pill_learn}; background: {pill_learn}20; border: 1px solid {pill_learn}50; }}
        .badge-due {{ color: {pill_due}; background: {pill_due}20; border: 1px solid {pill_due}50; }}
        .activity-ring-svg {{
            width: 24px;
            height: 24px;
            transform: rotate(-90deg);
            display: block; 
            margin: 0 auto;
        }}
        .ring-bg {{ fill: none; stroke: currentColor; opacity: 0.1; }}
        .ring-seg {{ fill: none; stroke-linecap: round; transition: stroke-dasharray 0.5s ease; }}
        .ring-checkmark {{ fill: none; stroke: #2ecc71; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }}
        .glass-deck-container a {{
            font-family: system-ui, -apple-system, sans-serif !important;
            color: var(--link) !important;
            text-decoration: none !important;
            font-weight: 500 !important; 
            font-size: 14px !important;
            letter-spacing: -0.2px !important;
        }}
        body .deck-browser tr:hover td {{
            background-color: rgba(255, 255, 255, 0.3) !important;
        }}
        .night_mode body .deck-browser tr:hover td {{
            background-color: rgba(255, 255, 255, 0.05) !important;
        }}
        """

    if monochrome or not enable_shadows:
        shadow_style = "none"
        night_shadow_style = "none"
    else:
        shadow_style = "0 4px 10px rgba(0,0,0,0.1)"
        night_shadow_style = "0 2px 5px rgba(0,0,0,0.5)"

    style = f"""
    <style>
        :root {{ --bg-empty: {cfg["empty_color"]}; --txt: #24292e; --sub: #95a5a6; --border: #dfe6e9; }}
        .night_mode {{ --bg-empty: {cfg["empty_color_night"]}; --txt: #ecf0f1; --sub: #7f8c8d; --border: #34495e; }}
        
        #heatmap-root {{ width: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; cursor: default; }}
        #heatmap-root, .leaderboard-wrapper, .ankileaderboard {{ display: block !important; }}
        
        .hud {{
            padding: 15px;
            width: 540px !important; min-width: 540px !important; max-width: 540px !important;
            margin: 10px auto;
            border-radius: 16px;
            {base_glass}
        }}
        
        .night_mode .hud {{
            {night_glass}
        }}
        
        {deck_css}
        
        .top {{ display: flex; justify-content: flex-end; margin-bottom: 5px; }}
        .sets {{ cursor: pointer; color: var(--sub); font-size: 14px; opacity: 0.5; transition: 0.2s; }}
        .sets:hover {{ opacity: 1; transform: rotate(90deg); }}
        
        .mid {{ display: flex; align-items: center; margin-bottom: 25px; height: 50px; }}
        .stat-group {{ display: flex; flex-direction: column; align-items: center; min-width: 35px; }}
        
        .stat-val {{ 
            font-size: 22px; 
            font-weight: 400; 
            color: var(--txt); 
            line-height: 1.1; 
            letter-spacing: -0.5px;
            text-shadow: {shadow_style};
        }}
        
        .night_mode .stat-val {{ text-shadow: {night_shadow_style}; }}
        
        .stat-lbl {{ font-size: 8px; font-weight: 700; color: var(--sub); margin-top: 2px; letter-spacing: 0.5px; text-shadow: none; opacity: 0.8; }}
        .divider {{ width: 1px; height: 25px; background: var(--border); margin: 0 10px; opacity: 0.5; }}
        .spacer {{ flex-grow: 1; }}

        .toggle-wrapper {{ display: flex; align-items: center; margin-bottom: 2px; width: 100%; }}
        .mode-toggle {{ display: flex; background: rgba(0,0,0,0.1); border-radius: 12px; padding: 2px; height: 18px; flex-shrink: 0; border: 1px solid rgba(255,255,255,0.1); }}
        .toggle-opt {{ font-size: 9px; padding: 0 12px; border-radius: 10px; cursor: pointer; line-height: 18px; color: var(--sub); font-weight: 700; }}
        .toggle-opt:hover {{ color: var(--txt); }}
        .toggle-opt.active {{ background: {cfg['base_color']}; color: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.2); }}
        .h-divider {{ border-bottom: 1px solid var(--border); flex-grow: 1; margin-left: 15px; height: 0px; opacity: 0.5; }}
        
        .graph-container {{ margin-bottom: 15px; display: flex; gap: 5px; }}
        .day-labels {{ display: grid; grid-template-rows: repeat(7, {cfg['cell_size']}px); gap: {cfg['cell_gap']}px; padding-top: 21px; }}
        .day-labels div {{ font-size: 9px; line-height: {cfg['cell_size']}px; color: var(--sub); width: 12px; text-align: center; font-weight: 600; text-shadow: none; }}
        
        .scroll-wrapper {{ overflow: hidden; flex-grow: 1; position: relative; }}
        .scroll {{ overflow-x: auto; padding: 4px; }}
        .scroll::-webkit-scrollbar {{ height: 0px; }}
        .grid {{ display: grid; grid-auto-flow: column; }}
        
        .cell {{ width: {cfg['cell_size']}px; height: {cfg['cell_size']}px; border-radius: {cfg['border_radius']}px; box-sizing: border-box; }}
        .cell:hover {{ transform: scale(1.2); transition: 0.1s; z-index: 10; }}
        
        #heatmap-tooltip {{
            position: fixed; 
            top: 0; left: 0;
            background: rgba(0,0,0,0.92);
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 500;
            line-height: 1.4;
            max-width: 320px;        
            white-space: pre-wrap;   
            word-wrap: break-word;   
            z-index: 9999;
            pointer-events: none; 
            display: none;        
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            text-shadow: none;
        }}

        .spark-wrapper {{ width: 100%; }}
        .spark-header {{ display: flex; justify-content: center; height: 14px; font-size: 9px; font-weight: 700; color: var(--sub); letter-spacing: 0.5px; margin-bottom: 2px; text-shadow: {shadow_style}; }}
        .night_mode .spark-header {{ text-shadow: {night_shadow_style}; }}
        
        .svg-container {{ position: relative; width: 100%; height: 60px; }}
        .graph-labels {{ display: flex; justify-content: space-between; font-size: 8px; color: var(--sub); font-weight: 700; margin-top: 4px; padding: 0 2px; opacity: 0.6; text-shadow: none; }}
    </style>
    """
    
    return f"""
    <div id="heatmap-root">
        <div id="heatmap-tooltip"></div>
        {style}
        <div class="hud">
            <div class="top">
                <div class="sets" onclick="pycmd('heatmap:settings')">⚙</div>
            </div>
            <div class="mid">
                <div class="stat-group"><div class="stat-val" style="color:{base_text_color}">{cards_due}</div><div class="stat-lbl">DUE</div></div>
                <div class="divider"></div>
                <div class="stat-group"><div class="stat-val" style="color:{c_today}">{today_revs}</div><div class="stat-lbl">DONE</div></div>
                <div class="divider"></div>
                <div class="stat-group"><div class="stat-val" style="color:{c_time}">{avg_time}<span style="font-size:10px">s</span></div><div class="stat-lbl">SPEED</div></div>
                <div class="divider"></div>
                <div class="stat-group"><div class="stat-val">{display_time}<span style="font-size:10px">{time_unit}</span></div><div class="stat-lbl">TIME</div></div>
                <div class="divider"></div>
                <div class="stat-group"><div class="stat-val" style="color:{c_qual}">{today_rate}<span style="font-size:10px">%</span></div><div class="stat-lbl">QUAL</div></div>
                <div class="spacer"></div>
                <div class="stat-group"><div class="stat-val">{daily_avg}</div><div class="stat-lbl">AVG</div></div>
                <div class="divider"></div>
                <div class="stat-group"><div class="stat-val">{streak}</div><div class="stat-lbl">STREAK</div></div>
            </div>

            <div class="toggle-wrapper">
                <div class="mode-toggle">
                    <div class="toggle-opt {vol_class}" onclick="pycmd('heatmap:setmode:volume')">VOLUME</div>
                    <div class="toggle-opt {ret_class}" onclick="pycmd('heatmap:setmode:retention')">RETENTION</div>
                    <div class="toggle-opt {scr_class}" onclick="pycmd('heatmap:setmode:score')">SPEED</div>
                </div>
                <div class="h-divider"></div>
            </div>
            
            <div class="graph-container">
                <div class="day-labels"><div>S</div><div>M</div><div>T</div><div>W</div><div>T</div><div>F</div><div>S</div></div>
                <div class="scroll-wrapper">
                    <div class="scroll" id="heatmap-scroll">
                        <div style="width: {total_width_px}px; position:relative; height:15px; margin-bottom:2px; font-size:9px; font-weight:700; color:#95a5a6; display:flex;">
                            {month_html}
                        </div>
                        <div class="grid" style="width: max-content; grid-template-rows:repeat(7,{cfg["cell_size"]}px); gap:{cfg["cell_gap"]}px">
                            {cells_html}
                        </div>
                    </div>
                </div>
            </div>

            <div class="spark-wrapper" style="{graph_display_style}">
                <div id="heatmap-legend" class="spark-header">{legend_html}</div>
                <div class="svg-container" id="heatmap-graph-container">
                    <svg width="100%" height="100%" preserveAspectRatio="none" viewBox="0 0 530 60">
                        <defs>
                            <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color:{cfg['base_color']};stop-opacity:0.3" />
                                <stop offset="100%" style="stop-color:{cfg['base_color']};stop-opacity:0" />
                            </linearGradient>
                        </defs>
                        {svg_paths}
                    </svg>
                    <div id="heatmap-touch" style="position:absolute; top:0; left:0; width:100%; height:100%; cursor:crosshair;"></div>
                </div>
                <div class="graph-labels"><div>30 DAYS AGO</div><div>TODAY</div></div>
            </div>
        </div>

        <script>
            (function() {{
                window.initHeatmap = function() {{
                    const meta = {meta_json};
                    const fullDeckStats = {deck_stats_json}; 
                    
                    const touch = document.getElementById('heatmap-touch');
                    const legend = document.getElementById('heatmap-legend');
                    const scrollBox = document.getElementById('heatmap-scroll');
                    const tooltip = document.getElementById('heatmap-tooltip');
                    const baseColor = "{cfg['base_color']}";
                    const revColor = "{cfg.get('graph_reviews_color', '#3498db')}";
                    const timeColor = "{cfg.get('graph_time_color', '#e67e22')}";
                    const retColor = "{cfg.get('graph_retention_color', '#f1c40f')}";
                    const futColor = "{cfg.get('graph_forecast_color', '#95a5a6')}";
                    const defaultHTML = legend ? legend.innerHTML : "";
                    const isMono = {mono_js};

                    const modernTheme = {str(modern_theme).lower()};
                    const showRatio = {str(show_ratio).lower()};

                    function showTooltip(evt, el) {{
                        const text = el.getAttribute('data-tooltip');
                        if(!text || !tooltip) return;
                        tooltip.innerHTML = text;
                        tooltip.style.display = 'block';
                        
                        let x = evt.clientX - (tooltip.offsetWidth / 2);
                        if (x < 10) x = 10;
                        tooltip.style.left = x + 'px';
                        tooltip.style.top = (evt.clientY - tooltip.offsetHeight - 15) + 'px';
                    }}

                    if (scrollBox) {{
                        scrollBox.onmouseover = function(e) {{
                            const cell = e.target.closest('.cell');
                            if (cell) {{
                                showTooltip(e, cell);
                                const lg = cell.getAttribute('data-legend');
                                if (lg && legend) legend.innerHTML = lg;
                            }}
                        }};
                        scrollBox.onmouseout = function() {{
                            if(tooltip) tooltip.style.display = 'none';
                            if(legend) legend.innerHTML = defaultHTML;
                        }};
                    }}

                    if (touch && legend) {{
                        touch.onmousemove = function(e) {{
                            const rect = touch.getBoundingClientRect();
                            const x = e.clientX - rect.left;
                            const idx = Math.floor((x / rect.width) * meta.length);
                            if (idx >= 0 && idx < meta.length) {{
                                const d = meta[idx];
                                
                                const c_rev = isMono ? "var(--txt)" : revColor;
                                const c_time = isMono ? "var(--txt)" : timeColor;
                                const c_ret  = isMono ? "var(--txt)" : retColor;
                                const c_fut  = isMono ? "var(--txt)" : futColor;

                                let html = `<span>${{d.label}}</span> &nbsp;&nbsp; <span style="color:${{c_rev}}">${{d.rev}} REV</span>`;
                                
                                if (d.time > 0) html += ` &nbsp;&nbsp; <span style="color:${{c_time}}">${{d.time}} S/C</span>`;
                                if (d.rev > 0)  html += ` &nbsp;&nbsp; <span style="color:${{c_ret}}">${{d.ret}}% RET</span>`;
                                if (d.fut > 0)  html += ` &nbsp;&nbsp; <span style="color:${{c_fut}}">${{d.fut}} FUT</span>`;
                                
                                legend.innerHTML = html;
                            }}
                        }};
                        touch.onmouseleave = function() {{ legend.innerHTML = defaultHTML; }};
                    }}

                    function applyDeckGlass() {{
                        if (!modernTheme) return;
                        const tables = document.getElementsByTagName('table');
                        if (tables.length === 0) return;
                        const table = tables[0];
                        if (table.parentElement.classList.contains('glass-deck-container')) return;
                        const wrapper = document.createElement('div');
                        wrapper.className = 'glass-deck-container';
                        table.parentNode.insertBefore(wrapper, table);
                        wrapper.appendChild(table);
                        enhanceDeckRows(table);
                    }}
                    
                    function enhanceDeckRows(table) {{
                        const rows = table.getElementsByTagName('tr');
                        if (showRatio) {{
                            const headerRow = rows[0];
                            if (headerRow) {{
                                if (!headerRow.querySelector('.heatmap-ratio-header')) {{
                                    const th = document.createElement('th');
                                    th.innerText = 'RATIO'; 
                                    th.className = 'heatmap-ratio-header';
                                    headerRow.insertBefore(th, headerRow.lastElementChild);
                                }}
                            }}
                        }}
                        for (let i = 1; i < rows.length; i++) {{
                            const row = rows[i];
                            const cells = row.getElementsByTagName('td');
                            if (cells.length < 5) continue;
                            
                            const wrap = (cell, type) => {{
                                const raw = cell.innerText.replace(/[^0-9]/g, '');
                                const val = parseInt(raw, 10) || 0;
                                if (cell.querySelector('.stat-badge')) return val; 
                                const span = document.createElement('span');
                                span.innerText = val;
                                span.className = 'stat-badge ' + (val > 0 ? type : 'badge-dim');
                                cell.innerHTML = '';
                                cell.appendChild(span);
                                return val;
                            }};
                            
                            wrap(cells[1], 'badge-new');
                            wrap(cells[2], 'badge-lrn');
                            wrap(cells[3], 'badge-due');
                            
                            if (!showRatio) continue;

                            const did = row.id.replace('deck-', '');
                            const stats = fullDeckStats[did];
                            if (!stats) continue;

                            const n = stats.n || 0;
                            const l = stats.l || 0;
                            const d = stats.d || 0;
                            const done = stats.done || 0;
                            const total = n + l + d + done;
                            
                            let ringTd = row.querySelector('.heatmap-ring-cell');
                            if (!ringTd) {{
                                ringTd = document.createElement('td');
                                ringTd.className = 'heatmap-ring-cell';
                                row.insertBefore(ringTd, row.lastElementChild);
                            }}
                            
                            if (total > 0) {{
                                const n_pct = (n / total) * 100;
                                const l_pct = (l / total) * 100;
                                const d_pct = (d / total) * 100;
                                const done_pct = (done / total) * 100;

                                const off_n = done_pct;
                                const off_l = done_pct + n_pct;
                                const off_d = done_pct + n_pct + l_pct;

                                let paths = '';
                                paths += `<path class="ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-width="4" />`;
                                if (done > 0) paths += `<path class="ring-seg" stroke="#2ecc71" stroke-dasharray="${{done_pct}}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-width="4" />`;
                                if (n > 0) paths += `<path class="ring-seg" stroke="{pill_new}" stroke-dasharray="${{n_pct}}, 100" stroke-dashoffset="-${{off_n}}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-width="4" />`;
                                if (l > 0) paths += `<path class="ring-seg" stroke="{pill_learn}" stroke-dasharray="${{l_pct}}, 100" stroke-dashoffset="-${{off_l}}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-width="4" />`;
                                if (d > 0) paths += `<path class="ring-seg" stroke="{pill_due}" stroke-dasharray="${{d_pct}}, 100" stroke-dashoffset="-${{off_d}}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-width="4" />`;

                                // Add checkmark when all reviews are complete
                                if (done === total) {{
                                    paths += `<path class="ring-checkmark" d="M12 18.5 l 4 4 l 8.5 -8.5" transform="rotate(90 18 18)" />`;
                                }}

                                ringTd.innerHTML = `<svg class="activity-ring-svg" viewBox="0 0 36 36">${{paths}}</svg>`;
                            }} else {{
                                ringTd.innerHTML = '<svg class="activity-ring-svg" viewBox="0 0 36 36"><path class="ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-width="4" /></svg>';
                            }}
                        }}
                    }}

                    function cleanStats() {{
                        const ov = document.getElementById('overview');
                        if(!ov) return;
                        ov.childNodes.forEach(n => {{
                            if(n.textContent && n.textContent.includes('Studied') && n.textContent.includes('cards')) {{
                                if(n.nodeType === 3) n.textContent = '';
                                else n.style.display = 'none';
                            }}
                        }});
                    }}
                    cleanStats();
                    applyDeckGlass();
                    setTimeout(() => {{ if(scrollBox) scrollBox.scrollLeft = scrollBox.scrollWidth; }}, 50);
                }};
                window.initHeatmap();
            }})();
        </script>
    </div>
    """

def render(deck_browser, content):
    cfg = get_config()
    setup_timer()

    hide_studied_css = ""
    if cfg.get('replace_stats', True):
        hide_studied_css = "<style>#studiedToday { display: none !important; }</style>"

    try:
        heatmap_html = get_html_body_content()
        existing = content.stats or ""

        content.stats = hide_studied_css + heatmap_html + existing
            
    except Exception as e:
        import traceback
        error_msg = f"<div style='color:red; padding:10px;'>HEATMAP ERROR: {str(e)}<br>{traceback.format_exc()}</div>"
        content.stats += error_msg

def on_msg(h, m, c):
    if m == "heatmap:settings": HeatmapSettingsDialog(mw).exec(); return True, None
    if m.startswith("heatmap:setmode:"):
        new_mode = m.split(":")[2]
        cfg = get_config()
        cfg['display_mode'] = new_mode
        write_config(cfg)
        mw.reset()
        return True, None

    if m.startswith("heatmap:note:"):
        date_str = m.split(":")[2]
        cfg = get_config()
        notes = cfg.get('daily_notes', {})
        raw_exams = cfg.get("exam_days", {})
        if isinstance(raw_exams, list):
            exams = {d: {"label": "Exam", "color": "#e74c3c"} for d in raw_exams}
        else:
            exams = raw_exams
            
        exam_data = exams.get(date_str)
        current_note = notes.get(date_str, "")
        
        dlg = HeatmapNoteDialog(date_str, current_note, exam_data, mw)
        
        if dlg.exec():
            new_text = dlg.get_text()
            new_exam_data = dlg.get_exam_result()
            
            if new_text: notes[date_str] = new_text
            elif date_str in notes: del notes[date_str]
            cfg['daily_notes'] = notes
            
            if new_exam_data: exams[date_str] = new_exam_data
            elif date_str in exams: del exams[date_str]
            cfg['exam_days'] = exams
            
            write_config(cfg)
            mw.reset()
        return True, None
    return h

gui_hooks.webview_did_receive_js_message.append(on_msg)
try: gui_hooks.deck_browser_will_render_content.remove(render)
except: pass
gui_hooks.deck_browser_will_render_content.append(render)

from aqt import mw, gui_hooks
from aqt.qt import *
from anki.cards import Card
import re

class ModernBrowserDelegate(QStyledItemDelegate):
    def __init__(self, browser, theme_color="#8e44ad"):
        super().__init__(browser)
        self.browser = browser
        self.theme_color = theme_color
        
        # Suspended icon SVG (pause icon in gold)
        self.suspended_icon_data = QByteArray.fromBase64(
            b"PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZjM5YzEyIiBzdHJva2Utd2lkdGg9IjIuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48bGluZSB4MT0iMTAiIHkxPSI0IiB4Mj0iMTAiIHkyPSIyMCI+PC9saW5lPjxsaW5lIHgxPSIxNCIgeTE9IjQiIHgyPSIxNCIgeTI9IjIwIj48L2xpbmU+PC9zdmc+"
        )
        
        # Cloze colors optimized for both dark and suspended (yellow-brown) backgrounds
        self.cloze_colors = [
            "#3b82f6",  # Bright blue - works on both
            "#10b981",  # Emerald - works on both
            "#FFB8FA",  # Amber - slightly darker, contrasts yellow
            "#8b5cf6",  # Purple - balanced brightness
            "#ec4899",  # Hot pink - pops on both
            "#14b8a6",  # Teal - good contrast
            "#f97316",  # Orange - distinct from amber
            "#06b6d4",  # Cyan - bright and clear
        ]
        
        # Cache for card IDs
        self._card_cache = {}
    
    def _get_card_id_from_index(self, index):
        try:
            model = index.model()
            if hasattr(model, 'get_card_id'):
                return model.get_card_id(index)
            elif hasattr(model, 'getCardId'):
                return model.getCardId(index)
            
            row = index.row()
            if hasattr(self.browser.table, 'get_card_id'):
                return self.browser.table.get_card_id(row)
            
            source_model = model
            while hasattr(source_model, 'sourceModel'):
                source_model = source_model.sourceModel()
            
            if hasattr(source_model, '_items') and row < len(source_model._items):
                return source_model._items[row]
                
        except:
            pass
        
        return None
    
    def _is_card_suspended(self, card_id):
        if card_id is None:
            return False
        
        if card_id in self._card_cache:
            return self._card_cache[card_id]
        
        try:
            card = mw.col.get_card(card_id)
            is_suspended = (card.queue == -1)
            self._card_cache[card_id] = is_suspended
            return is_suspended
        except:
            return False
    
    def paint(self, painter, option, index):
        """Custom paint with modern dark styling"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get card state
        card_id = self._get_card_id_from_index(index)
        is_suspended = self._is_card_suspended(card_id)
        is_selected = option.state & QStyle.StateFlag.State_Selected
        
        # Modern dark mode colors
        if is_selected:
            bg_color = QColor(self.theme_color)
        elif is_suspended:
            bg_color = QColor("#3a2f1a")  # Dark brown/gold tint
        else:
            # Subtle alternating rows
            if index.row() % 2 == 0:
                bg_color = QColor("#1e1e1e")
            else:
                bg_color = QColor("#252525")
        
        # Paint background with rounded corners for modern look
        rect = QRectF(option.rect)
        rect.adjust(2, 1, -2, -1)
        painter.fillRect(rect, bg_color)
        
        # Draw suspended icon
        icon_offset = 0
        if is_suspended and index.column() == 0:
            icon_size = 14
            icon_x = rect.x() + 8
            icon_y = rect.y() + (rect.height() - icon_size) / 2
            
            icon_img = QImage()
            icon_img.loadFromData(self.suspended_icon_data)
            painter.drawImage(QRect(int(icon_x), int(icon_y), icon_size, icon_size), icon_img)
            icon_offset = 24
        
        # Process text with cloze styling
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            text = str(text)
            text = self._clean_text(text)
            
            # Determine text color
            if is_selected:
                text_color = QColor("#ffffff")
            elif is_suspended:
                text_color = QColor("#d4af37")  # Gold for suspended
            else:
                text_color = QColor("#e0e0e0")  # Light gray for normal
            
            text_x = rect.x() + icon_offset + 12
            text_width = rect.width() - icon_offset - 24
            text_y = rect.y() + (rect.height() - option.fontMetrics.height()) / 2

            if "{{c" in text:
                self._paint_text_with_clozes(painter, text, text_x, text_y, text_width, 
                                            option, text_color, is_selected, is_suspended)
            else:
                painter.setPen(text_color)
                painter.setFont(option.font)
                plain_text = re.sub(r'<[^>]+>', '', text)
                elided_text = option.fontMetrics.elidedText(
                    plain_text, 
                    Qt.TextElideMode.ElideRight, 
                    int(text_width)
                )
                # Center text vertically properly
                text_rect = QRectF(text_x, rect.y(), text_width, rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)
        
        painter.restore()
    
    def _clean_text(self, text):
        """Clean HTML and formatting from text"""
        text = text.replace("&nbsp;", " ")
        text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'<div[^>]*>', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<p[^>]*>', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '', text, flags=re.IGNORECASE)
        text = ' '.join(text.split())
        return text
    
    def _paint_text_with_clozes(self, painter, text, x, y, max_width, option, base_color, is_selected, is_suspended):
        """Paint text with minimal styled clozes"""
        # Parse clozes and regular text
        parts = []
        last_end = 0
        
        for match in re.finditer(r'\{\{c(\d+)::(.*?)(?:::.*?)?\}\}', text):
            # Add text before cloze
            if match.start() > last_end:
                before_text = text[last_end:match.start()]
                before_text = re.sub(r'<[^>]+>', '', before_text)
                parts.append(('text', before_text))
            
            # Add cloze
            cloze_num = int(match.group(1))
            cloze_content = match.group(2)
            cloze_content = re.sub(r'<[^>]+>', '', cloze_content)
            parts.append(('cloze', cloze_content, cloze_num))
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            after_text = text[last_end:]
            after_text = re.sub(r'<[^>]+>', '', after_text)
            parts.append(('text', after_text))
        
        # Draw parts
        current_x = x
        font = option.font
        metrics = QFontMetrics(font)
        line_height = metrics.height()
        baseline_y = y + metrics.ascent()
        
        for part in parts:
            if current_x >= x + max_width:
                break
            
            if part[0] == 'text':
                # Regular text
                painter.setFont(font)
                painter.setPen(base_color)
                
                text_content = part[1]
                text_width = metrics.horizontalAdvance(text_content)
                
                if current_x + text_width > x + max_width:
                    # Truncate
                    available = x + max_width - current_x
                    text_content = metrics.elidedText(text_content, Qt.TextElideMode.ElideRight, int(available))
                    text_width = available
                
                painter.drawText(QPointF(current_x, baseline_y), text_content)
                current_x += text_width
                
            elif part[0] == 'cloze':
                # Minimal cloze styling - just colored text with subtle background
                cloze_text = part[1]
                cloze_num = part[2]
                
                painter.setFont(font)
                
                # Choose color based on cloze number
                color_idx = (cloze_num - 1) % len(self.cloze_colors)
                cloze_color = QColor(self.cloze_colors[color_idx])
                
                # Measure text
                text_width = metrics.horizontalAdvance(cloze_text)
                
                if current_x + text_width > x + max_width:
                    # Truncate if needed
                    available = x + max_width - current_x
                    cloze_text = metrics.elidedText(cloze_text, Qt.TextElideMode.ElideRight, int(available))
                    text_width = available
                
                # Draw very subtle background highlight with slight padding
                padding = 4
                bg_rect = QRectF(current_x - padding, y - 1, text_width + padding * 2, line_height + 2)
                
                # Adjust background based on selection state
                if is_selected:
                    # On selected background, use darker tinted background
                    bg_color = QColor(cloze_color)
                    bg_color.setAlpha(50)  # More visible on selection
                else:
                    bg_color = QColor(cloze_color)
                    bg_color.setAlpha(30)  # Very subtle
                
                painter.setBrush(bg_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(bg_rect, 3, 3)
                
                # Draw colored text - MUCH brighter on selected rows
                if is_selected:
                    # Use white with subtle tint for selected rows
                    text_color = QColor("#ffffff")
                else:
                    # Use bright color for unselected
                    text_color = cloze_color.lighter(120)
                
                painter.setPen(text_color)
                painter.drawText(QPointF(current_x, baseline_y), cloze_text)
                
                current_x += text_width + 4  # Small spacing after cloze
        
        # Add ellipsis if text was cut off
        if parts and last_end > 0 and current_x >= x + max_width - 20:
            painter.setFont(font)
            painter.setPen(base_color)
            painter.drawText(QPointF(x + max_width - 20, baseline_y), "...")


class BrowserEnhancer:
    """Main enhancer class"""
    
    def __init__(self):
        self.installed_browsers = set()
        gui_hooks.browser_will_show.append(self.on_browser_will_show)
    
    def on_browser_will_show(self, browser):
        self.install_enhancements(browser)
    
    def install_enhancements(self, browser):
        if id(browser) in self.installed_browsers:
            return

        try:
            config = mw.addonManager.getConfig(__name__)
            if not config.get('enable_browser_theme', True):
                return
        except:
            pass

        self.installed_browsers.add(id(browser))
        theme_color = self._get_theme_color()

        self._apply_styles(browser, theme_color)
        self._install_table_delegate(browser, theme_color)
    
    def _get_theme_color(self):
        try:
            config = mw.addonManager.getConfig(__name__)
            return config.get('base_color', '#8e44ad')
        except:
            return '#8e44ad'
    
    def _apply_styles(self, browser, theme_color):
        """Apply modern dark mode styles"""
        
        stylesheet = f"""
        /* ===== MAIN BROWSER WINDOW ===== */
        QMainWindow {{
            background-color: #1a1a1a;
        }}
        
        /* ===== SIDEBAR TREE VIEW ===== */
        QTreeView {{
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: none;
            outline: none;
            padding: 8px 4px;
            indentation: 20px;
        }}
        
        QTreeView::item {{
            padding: 6px 8px;
            border: none;
            border-radius: 6px;
            margin: 2px 4px;
        }}
        
        QTreeView::item:hover {{
            background-color: #2d2d2d;
        }}
        
        QTreeView::item:selected {{
            background-color: {theme_color};
            color: white;
        }}
        
        /* ===== SIDEBAR TREE VIEW ===== */
        QTreeView {{
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: none;
            outline: none;
            word-wrap: break-word;
        }}
        
        QTreeView::item {{
            padding: 6px 4px;
            border: none;
            min-height: 24px;
        }}
        
        QTreeView::item:hover {{
            background-color: #2d2d2d;
        }}
        
        QTreeView::item:selected {{
            background-color: {theme_color};
            color: white;
        }}
        
        /* ===== CARD TABLE ===== */
        QTableView {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
            background-color: #1a1a1a;
            color: #e0e0e0;
            selection-background-color: {theme_color};
            gridline-color: transparent;
            border: none;
            outline: none;
            show-decoration-selected: 0;
        }}
        
        QTableView::item {{
            padding: 10px 12px;
            border: none;
        }}
        
        QTableView::item:selected {{
            background-color: {theme_color};
            color: white;
        }}
        
        /* ===== TABLE HEADERS ===== */
        QHeaderView {{
            background-color: #1e1e1e;
            border: none;
        }}
        
        QHeaderView::section {{
            background-color: #1e1e1e;
            border: none;
            border-bottom: 2px solid {theme_color};
            padding: 10px 12px;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #999999;
        }}
        
        QHeaderView::section:hover {{
            background-color: #252525;
            color: {theme_color};
        }}
        
        /* ===== SCROLLBARS ===== */
        QScrollBar:vertical {{
            background-color: #1a1a1a;
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #404040;
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #505050;
        }}
        
        QScrollBar:horizontal {{
            background-color: #1a1a1a;
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: #404040;
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: #505050;
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
        }}
        """
        
        browser.setStyleSheet(stylesheet)
        
        # Fix tree view - minimal indentation for narrow sidebars
        try:
            sidebar = None
            if hasattr(browser, 'sidebarTree'):
                sidebar = browser.sidebarTree
            elif hasattr(browser, 'sidebar') and hasattr(browser.sidebar, 'tree'):
                sidebar = browser.sidebar.tree
            
            if sidebar:
                # Smaller indentation for better space usage
                sidebar.setRootIsDecorated(True)
                sidebar.setIndentation(12)  # Reduced from 20
                sidebar.setWordWrap(True)  # Allow text wrapping for long names
                sidebar.setTextElideMode(Qt.TextElideMode.ElideMiddle)  # Show start and end of long names
                
                # Try to remove any custom item delegate that might be adding the box
                try:
                    sidebar.setItemDelegate(QStyledItemDelegate(sidebar))
                except:
                    pass
                
                # Only set colors, nothing about branches/items
                sidebar.setStyleSheet(f"""
                    QTreeView {{
                        background-color: #1e1e1e;
                        color: #e0e0e0;
                        font-size: 12px;
                    }}
                    QTreeView::item {{
                        padding: 5px 2px;
                        margin: 0px;
                        border: none;
                        border-radius: 0px;
                    }}
                    QTreeView::item:selected {{
                        background-color: {theme_color};
                        border-radius: 4px;
                    }}
                    QTreeView::item:hover {{
                        background-color: #2d2d2d;
                        border-radius: 4px;
                    }}
                """)
        except:
            pass
    
    def _install_table_delegate(self, browser, theme_color):
        """Install the custom delegate"""
        
        table_view = None
        try:
            if hasattr(browser, 'table') and hasattr(browser.table, '_view'):
                table_view = browser.table._view
            elif hasattr(browser, 'form') and hasattr(browser.form, 'tableView'):
                table_view = browser.form.tableView
        except:
            pass
        
        if not table_view:
            return
        
        current_delegate = table_view.itemDelegate()
        if isinstance(current_delegate, ModernBrowserDelegate):
            return
        
        delegate = ModernBrowserDelegate(browser, theme_color)
        table_view.setItemDelegate(delegate)
        
        # Configure table
        table_view.setWordWrap(False)
        table_view.setAlternatingRowColors(False)
        table_view.setTextElideMode(Qt.TextElideMode.ElideRight)
        table_view.setShowGrid(False)
        
        # Set row height for better spacing
        if hasattr(table_view, 'verticalHeader'):
            v_header = table_view.verticalHeader()
            v_header.setDefaultSectionSize(38)  # Taller for cloze buttons
            v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Connect to changes
        try:
            model = table_view.model()
            if model:
                def refresh_view():
                    if hasattr(delegate, '_card_cache'):
                        delegate._card_cache.clear()
                    table_view.viewport().update()
                
                model.layoutChanged.connect(refresh_view)
                model.modelReset.connect(refresh_view)
                model.dataChanged.connect(refresh_view)
        except:
            pass
        
        # Hook state changes
        try:
            from aqt import gui_hooks
            
            # Use a wrapper that checks if objects still exist
            def on_state_change(new_state, old_state):
                try:
                    if hasattr(delegate, '_card_cache'):
                        delegate._card_cache.clear()
                    # Try to update viewport, will fail silently if deleted
                    if table_view is not None:
                        table_view.viewport().update()
                except RuntimeError:
                    # Object has been deleted, ignore
                    pass
                except:
                    # Any other error, ignore
                    pass
            
            gui_hooks.state_did_change.append(on_state_change)
        except:
            pass


enhancer = BrowserEnhancer()

class EditorEnhancer:
    def __init__(self):
        gui_hooks.editor_did_init.append(self.on_editor_init)

    def on_editor_init(self, editor):
        cfg = get_config()
        base_color = cfg.get('base_color', "#8e44ad")
        cloze_color = "#f1c40f"
        # 3. Dynamic Cloze indicators
        
        css = f"""
        :root {{
            --accent: {base_color};
            --cloze-accent: {cloze_color};
            --radius: 12px;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif !important;
            padding: 24px !important;
            background-color: transparent !important;
        }}

        /* --- MODERN TOOLBAR --- */
        .editor-toolbar {{
            border: none !important;
            background: transparent !important;
            padding: 0 5px !important;
            margin-bottom: 12px !important;
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }}

        /* Flat, Modern Buttons */
        button.anki-editor-button {{
            background: transparent !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 6px !important;
            margin: 0 !important;
            box-shadow: none !important;
            opacity: 0.7;
            transition: all 0.15s ease;
            cursor: pointer;
        }}

        button.anki-editor-button:hover {{
            background: rgba(0,0,0,0.06) !important;
            opacity: 1;
            transform: translateY(-1px);
        }}
        
        .night_mode button.anki-editor-button:hover {{
            background: rgba(255,255,255,0.15) !important;
        }}

        /* Active/Pressed State */
        button.anki-editor-button:active {{
            transform: scale(0.96);
            background: rgba(0,0,0,0.1) !important;
        }}

        /* --- FLOATING FIELDS --- */
        .field {{
            background: #ffffff;
            border: 1px solid #e1e4e8;
            border-radius: var(--radius);
            padding: 16px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            transition: border 0.2s ease, box-shadow 0.2s ease;
            position: relative; /* For badges */
        }}

        .night_mode .field {{
            background: #202225;
            border: 1px solid #2f3136;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}

        .field:focus-within {{
            border-color: var(--accent) !important;
            box-shadow: 0 4px 12px rgba(142, 68, 173, 0.15) !important;
        }}

        /* --- CLOZE DETECTION STYLES --- */
        /* When JS detects {{c1::, we add this class */
        .field.has-cloze {{
            border-left: 3px solid var(--cloze-accent) !important;
        }}
        
        /* Optional: A small "CLOZE" badge in the corner */
        .field.has-cloze::after {{
            content: "CLOZE";
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 9px;
            font-weight: 800;
            color: var(--cloze-accent);
            opacity: 0.6;
            pointer-events: none;
            letter-spacing: 1px;
        }}

        /* --- FIELD LABELS --- */
        .fname {{
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600 !important;
            color: #95a5a6 !important;
            margin-bottom: 8px;
            display: block;
        }}

        /* --- TAGS --- */
        .tag-editor-area {{
            background: transparent !important;
            border: none !important;
            padding-top: 10px !important;
        }}
        
        #tags-container {{
            background: #f1f3f5;
            border-radius: 8px;
            padding: 8px 12px !important;
            font-weight: 500;
        }}
        
        .night_mode #tags-container {{
            background: #2f3136;
        }}
        """
        
        # JAVASCRIPT: Detects Cloze Syntax as you type
        # It adds the '.has-cloze' class to the field container
        js = """
        <script>
        (function() {
            function checkCloze(field) {
                // Look for standard Anki {{c...}} syntax
                if (field.innerHTML.includes('{{c')) {
                    field.parentElement.classList.add('has-cloze');
                } else {
                    field.parentElement.classList.remove('has-cloze');
                }
            }

            // Monitor all fields for input
            document.body.addEventListener('input', function(e) {
                if (e.target.classList.contains('rich-text-editable')) {
                    checkCloze(e.target);
                }
            });

            // Initial check on load (wait slightly for Anki to populate)
            setTimeout(() => {
                document.querySelectorAll('.rich-text-editable').forEach(checkCloze);
            }, 300);
        })();
        </script>
        """
        
        safe_css = css.replace('\n', ' ')
        
        # Combine CSS and JS injection
        injection = f"""
        var style = document.createElement('style');
        style.innerHTML = `{safe_css}`;
        document.head.appendChild(style);
        document.body.insertAdjacentHTML('beforeend', `{js}`);
        """
        
        editor.web.eval(injection)

EditorEnhancer()


# ===== TAG COLOR MANAGER =====
# Allows right-click coloring of tags in the browser sidebar

TAG_COLOR_PRESETS = [
    ("#e74c3c", "Red"),
    ("#e67e22", "Orange"),
    ("#f1c40f", "Yellow"),
    ("#2ecc71", "Green"),
    ("#1abc9c", "Teal"),
    ("#3498db", "Blue"),
    ("#9b59b6", "Purple"),
    ("#e91e63", "Pink"),
    ("#795548", "Brown"),
    ("#607d8b", "Gray"),
]


def _color_icon(color):
    """Create a small color swatch icon"""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(QColor("#555555"))
    painter.drawRoundedRect(2, 2, 12, 12, 3, 3)
    painter.end()
    return QIcon(pixmap)


def _on_browser_sidebar_context_menu(sidebar, menu, item, index):
    """Add tag color options to the sidebar context menu"""
    try:
        from aqt.browser.sidebar import SidebarItemType

        # Only add menu for tags
        if item.item_type != SidebarItemType.TAG:
            return

        tag_name = item.full_name

        # Add separator before our options
        menu.addSeparator()

        # Add color submenu
        color_menu = menu.addMenu("Set Tag Color")

        # Add preset colors
        for color, name in TAG_COLOR_PRESETS:
            action = color_menu.addAction(_color_icon(color), name)
            action.triggered.connect(
                lambda checked, c=color, t=tag_name, s=sidebar: _set_tag_color(t, c, s)
            )

        # Add custom color option
        color_menu.addSeparator()
        custom_action = color_menu.addAction("Custom Color...")
        custom_action.triggered.connect(
            lambda checked, t=tag_name, s=sidebar: _pick_custom_color(t, s)
        )

        # Add clear color option if tag has a color
        cfg = get_config()
        tag_colors = cfg.get("tag_colors", {})
        if tag_name in tag_colors:
            clear_action = menu.addAction("Clear Tag Color")
            clear_action.triggered.connect(
                lambda checked, t=tag_name, s=sidebar: _clear_tag_color(t, s)
            )

    except (ImportError, AttributeError):
        pass


def _set_tag_color(tag_name, color, sidebar):
    """Set color for a tag"""
    cfg = get_config()
    tag_colors = cfg.get("tag_colors", {})
    tag_colors[tag_name] = color
    cfg["tag_colors"] = tag_colors
    write_config(cfg)
    sidebar.viewport().update()


def _pick_custom_color(tag_name, sidebar):
    """Open color picker for custom color"""
    cfg = get_config()
    tag_colors = cfg.get("tag_colors", {})
    current = tag_colors.get(tag_name, "#8e44ad")

    color = QColorDialog.getColor(QColor(current), sidebar, f"Color for tag: {tag_name}")
    if color.isValid():
        _set_tag_color(tag_name, color.name(), sidebar)


def _clear_tag_color(tag_name, sidebar):
    """Remove color from a tag"""
    cfg = get_config()
    tag_colors = cfg.get("tag_colors", {})
    if tag_name in tag_colors:
        del tag_colors[tag_name]
        cfg["tag_colors"] = tag_colors
        write_config(cfg)
        sidebar.viewport().update()


class TagColorDelegate(QStyledItemDelegate):
    """Custom delegate that renders tags with their assigned colors (text and icon)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._icon_cache = {}  # Cache colorized icons

    def _colorize_icon(self, icon, color):
        """Create a colorized version of the icon"""
        cache_key = (id(icon), color.name())
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Get the icon as a pixmap
        sizes = icon.availableSizes()
        size = sizes[0] if sizes else QSize(16, 16)
        pixmap = icon.pixmap(size)

        # Create a colored version
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)

        # Draw original pixmap
        painter.drawPixmap(0, 0, pixmap)

        # Apply color overlay using CompositionMode_SourceIn
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)

        painter.end()

        colored_icon = QIcon(colored_pixmap)
        self._icon_cache[cache_key] = colored_icon
        return colored_icon

    def initStyleOption(self, option, index):
        """Modify the style option to change text and icon color for colored tags"""
        super().initStyleOption(option, index)

        try:
            from aqt.browser.sidebar import SidebarItemType
            model = index.model()
            item = model.item_for_index(index)

            if item and item.item_type == SidebarItemType.TAG:
                tag_name = item.full_name
                cfg = get_config()
                tag_colors = cfg.get("tag_colors", {})

                if tag_name in tag_colors:
                    color = QColor(tag_colors[tag_name])

                    # Set the text color in the palette
                    option.palette.setColor(option.palette.ColorRole.Text, color)
                    option.palette.setColor(option.palette.ColorRole.HighlightedText, color.lighter(150))

                    # Colorize the icon
                    if not option.icon.isNull():
                        option.icon = self._colorize_icon(option.icon, color)

        except (ImportError, AttributeError):
            pass


class TagColorManager:
    """Manages custom colors for tags in the browser sidebar"""

    def __init__(self):
        self.installed_browsers = set()
        # Hook into browser show to install delegate
        gui_hooks.browser_will_show.append(self.on_browser_show)
        # Hook into sidebar context menu to add our options
        gui_hooks.browser_sidebar_will_show_context_menu.append(_on_browser_sidebar_context_menu)

    def on_browser_show(self, browser):
        if id(browser) in self.installed_browsers:
            return
        self.installed_browsers.add(id(browser))

        # Get the sidebar tree widget and install delegate
        sidebar = self._get_sidebar(browser)
        if sidebar:
            self._install_tag_delegate(sidebar)

    def _get_sidebar(self, browser):
        """Get the sidebar tree widget from browser"""
        try:
            if hasattr(browser, 'sidebarTree'):
                return browser.sidebarTree
            elif hasattr(browser, 'sidebar') and hasattr(browser.sidebar, 'tree'):
                return browser.sidebar.tree
        except:
            pass
        return None

    def _install_tag_delegate(self, sidebar):
        """Install a custom delegate that colors tag text"""
        delegate = TagColorDelegate(sidebar)
        sidebar.setItemDelegate(delegate)


# Initialize tag color manager
tag_color_manager = TagColorManager()