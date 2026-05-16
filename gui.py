# Okno aplikacji - rysuje symulację i panel sterowania

import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QDoubleSpinBox, QGroupBox,
    QGridLayout, QScrollArea
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPalette, QFont
import pyqtgraph as pg

from config import TRAIL_LENGTH, TRAIL_SEGMENTS, FPS, SIM_TIME_PER_FRAME
from physics import PhysicsEngine
from presets import get_presets


class ThreeBodyWindow(QMainWindow):
    # Główne okno programu

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Problem Trzech Ciał — Symulator 2D")
        self.setMinimumSize(1200, 800)

        self._setup_dark_theme()

        # Stan symulacji
        self.running = False
        self.engine = None
        self.trails = [[], [], []]  # ślady orbit
        self.presets = get_presets()
        self._suppress_param_signal = False  # blokada na czas programowej zmiany pól

        # Kolory ciał
        self.body_colors = [
            QColor(255, 80, 80),    # czerwony
            QColor(80, 255, 100),   # zielony
            QColor(90, 140, 255),   # niebieski
        ]
        self.trail_colors = [
            (255, 60, 60, 220),
            (60, 230, 90, 220),
            (80, 130, 255, 220),
        ]

        self._build_ui()

        # Timer do animacji
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.setInterval(int(1000 / FPS))

        # Wczytaj pierwszy preset z listy
        self._load_preset(list(self.presets.keys())[0])

    def _setup_dark_theme(self):
        # Ustawia ciemne kolory aplikacji
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(20, 20, 20))
        palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.Highlight, QColor(80, 120, 200))
        self.setPalette(palette)

    def _build_ui(self):
        # Buduje cały interfejs
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Lewa strona - wykres
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.showGrid(False, False)
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.setRange(xRange=[-3, 3], yRange=[-3, 3])
        self.plot_widget.setMouseEnabled(x=True, y=True)
        main_layout.addWidget(self.plot_widget, stretch=3)

        # Elementy graficzne
        self.trail_segments = []
        self.glow_plots = []
        self.body_plots = []

        for i in range(3):
            # Ślad podzielony na segmenty - starsze są bardziej przezroczyste
            base_r, base_g, base_b, base_a = self.trail_colors[i]
            segs = []
            for k in range(TRAIL_SEGMENTS):
                alpha = int(base_a * ((k + 1) / TRAIL_SEGMENTS) ** 2)
                pen = pg.mkPen(
                    color=(base_r, base_g, base_b, alpha),
                    width=1.5,
                    cosmetic=True
                )
                seg = self.plot_widget.plot([], [], pen=pen)
                segs.append(seg)
            self.trail_segments.append(segs)

            # Poświata wokół ciała
            glow_color = list(self.trail_colors[i])
            glow_color[3] = 80
            glow = self.plot_widget.plot(
                [], [], pen=None, symbol='o', symbolSize=20,
                symbolBrush=pg.mkBrush(*glow_color), symbolPen=None
            )
            self.glow_plots.append(glow)

            # Samo ciało
            body = self.plot_widget.plot(
                [], [], pen=None, symbol='o', symbolSize=10,
                symbolBrush=pg.mkBrush(self.body_colors[i]), symbolPen=None
            )
            self.body_plots.append(body)

        # Prawa strona - panel sterowania
        control_panel = QScrollArea()
        control_panel.setWidgetResizable(True)
        control_panel.setMaximumWidth(380)
        control_panel.setMinimumWidth(320)
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(10)

        # Tytuł
        title = QLabel("⚙ Panel Sterowania")
        title.setFont(QFont("", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(title)

        # Start / pauza / reset
        btn_group = QGroupBox("Symulacja")
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start")
        self.btn_pause = QPushButton("⏸ Pauza")
        self.btn_reset = QPushButton("↺ Reset")
        self.btn_start.clicked.connect(self._start)
        self.btn_pause.clicked.connect(self._pause)
        self.btn_reset.clicked.connect(self._reset)
        for btn in [self.btn_start, self.btn_pause, self.btn_reset]:
            btn.setMinimumHeight(35)
            btn_layout.addWidget(btn)
        btn_group.setLayout(btn_layout)
        control_layout.addWidget(btn_group)

        # Zoom
        view_group = QGroupBox("Widok")
        view_layout = QHBoxLayout()
        self.btn_zoom_in = QPushButton("🔍 +")
        self.btn_zoom_out = QPushButton("🔍 −")
        self.btn_view_reset = QPushButton("⤢ Dopasuj")
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        self.btn_view_reset.clicked.connect(self._reset_view)
        for btn in [self.btn_zoom_in, self.btn_zoom_out, self.btn_view_reset]:
            btn.setMinimumHeight(30)
            view_layout.addWidget(btn)
        view_group.setLayout(view_layout)
        control_layout.addWidget(view_group)

        # Wybór gotowego układu
        preset_group = QGroupBox("Predefiniowane układy")
        preset_layout = QVBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.presets.keys())
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        preset_group.setLayout(preset_layout)
        control_layout.addWidget(preset_group)

        # Parametry ciał - po jednej grupie na ciało
        self.param_spinboxes = []
        body_names = ["Ciało 1 (czerwone)", "Ciało 2 (zielone)", "Ciało 3 (niebieskie)"]

        for i in range(3):
            group = QGroupBox(body_names[i])
            grid = QGridLayout()
            grid.setSpacing(4)

            spinboxes = {}
            params = [
                ("Masa:", "m", 0.1, 20.0, 1.0),
                ("Pozycja X:", "x", -10.0, 10.0, 0.0),
                ("Pozycja Y:", "y", -10.0, 10.0, 0.0),
                ("Prędkość Vx:", "vx", -5.0, 5.0, 0.0),
                ("Prędkość Vy:", "vy", -5.0, 5.0, 0.0),
            ]

            for row, (label_text, key, min_val, max_val, default) in enumerate(params):
                label = QLabel(label_text)
                label.setFixedWidth(90)
                spin = QDoubleSpinBox()
                spin.setRange(min_val, max_val)
                spin.setDecimals(5)
                spin.setSingleStep(0.1)
                spin.setValue(default)
                spin.setFixedHeight(25)
                spin.valueChanged.connect(self._on_param_changed)
                grid.addWidget(label, row, 0)
                grid.addWidget(spin, row, 1)
                spinboxes[key] = spin

            group.setLayout(grid)
            control_layout.addWidget(group)
            self.param_spinboxes.append(spinboxes)

        # Przycisk do ręcznego zastosowania parametrów
        self.btn_apply = QPushButton("Zastosuj parametry ręczne")
        self.btn_apply.setMinimumHeight(35)
        self.btn_apply.clicked.connect(self._apply_manual_params)
        control_layout.addWidget(self.btn_apply)

        control_layout.addStretch()
        control_panel.setWidget(control_widget)
        main_layout.addWidget(control_panel, stretch=1)

    def _load_preset(self, name):
        # Wczytuje wybrany preset do pól i silnika
        preset = self.presets[name]
        masses = preset["masses"]
        positions = preset["positions"]
        velocities = preset["velocities"]

        # Blokujemy sygnały żeby nie wywołać niepotrzebnych aktualizacji
        self._suppress_param_signal = True
        try:
            for i in range(3):
                self.param_spinboxes[i]["m"].setValue(masses[i])
                self.param_spinboxes[i]["x"].setValue(positions[i][0])
                self.param_spinboxes[i]["y"].setValue(positions[i][1])
                self.param_spinboxes[i]["vx"].setValue(velocities[i][0])
                self.param_spinboxes[i]["vy"].setValue(velocities[i][1])
        finally:
            self._suppress_param_signal = False

        self.engine = PhysicsEngine(masses, positions, velocities)
        self._clear_trails()
        self._update_plot()
        self._reset_view()

    def _on_param_changed(self, _value=None):
        # Wywoływane gdy użytkownik zmieni wartość w polu
        if self._suppress_param_signal:
            return
        self._apply_manual_params(pause=False)

    def _on_preset_changed(self, name):
        # Wywoływane gdy użytkownik wybierze preset z listy
        self._pause()
        self._load_preset(name)

    def _apply_manual_params(self, pause=True):
        # Czyta wartości z pól i resetuje symulację
        if pause:
            self._pause()
        masses = []
        positions = []
        velocities = []
        for i in range(3):
            masses.append(self.param_spinboxes[i]["m"].value())
            positions.append([
                self.param_spinboxes[i]["x"].value(),
                self.param_spinboxes[i]["y"].value()
            ])
            velocities.append([
                self.param_spinboxes[i]["vx"].value(),
                self.param_spinboxes[i]["vy"].value()
            ])

        self.engine = PhysicsEngine(masses, positions, velocities)
        self._clear_trails()
        self._update_plot()

    def _zoom_in(self):
        self.plot_widget.getViewBox().scaleBy((0.7, 0.7))

    def _zoom_out(self):
        self.plot_widget.getViewBox().scaleBy((1.4, 1.4))

    def _reset_view(self):
        # Dopasowuje widok do wszystkich punktów (ciała + ślady)
        if self.engine is None:
            self.plot_widget.setRange(xRange=[-3, 3], yRange=[-3, 3])
            return
        all_points = [self.engine.positions]
        for tr in self.trails:
            if len(tr) > 0:
                all_points.append(np.array(tr))
        pts = np.vstack(all_points)
        xmin, ymin = pts.min(axis=0)
        xmax, ymax = pts.max(axis=0)
        dx = max(xmax - xmin, 0.5)
        dy = max(ymax - ymin, 0.5)
        pad_x = dx * 0.15
        pad_y = dy * 0.15
        self.plot_widget.setRange(
            xRange=[xmin - pad_x, xmax + pad_x],
            yRange=[ymin - pad_y, ymax + pad_y]
        )

    def _clear_trails(self):
        self.trails = [[], [], []]

    def _start(self):
        if self.engine is None:
            self._apply_manual_params()
        self.running = True
        self.timer.start()

    def _pause(self):
        self.running = False
        self.timer.stop()

    def _reset(self):
        # Resetuje do aktualnie wybranego presetu
        self._pause()
        self._load_preset(self.preset_combo.currentText())

    def _update_frame(self):
        # Wywoływane przez timer - jedna klatka animacji
        if not self.running or self.engine is None:
            return

        self.engine.advance(SIM_TIME_PER_FRAME)

        # Dodaj nową pozycję do śladu
        for i in range(3):
            self.trails[i].append(self.engine.positions[i].copy())
            if len(self.trails[i]) > TRAIL_LENGTH:
                self.trails[i] = self.trails[i][-TRAIL_LENGTH:]

        self._update_plot()

    def _update_plot(self):
        # Rysuje aktualny stan na wykresie
        if self.engine is None:
            return

        for i in range(3):
            # Ślad dzielimy na segmenty żeby zrobić efekt zanikania
            n = len(self.trails[i])
            if n > 1:
                trail_arr = np.array(self.trails[i])
                for k in range(TRAIL_SEGMENTS):
                    start = (k * n) // TRAIL_SEGMENTS
                    end = ((k + 1) * n) // TRAIL_SEGMENTS + 1  # +1 żeby segmenty się łączyły
                    end = min(end, n)
                    if end - start > 1:
                        self.trail_segments[i][k].setData(
                            trail_arr[start:end, 0], trail_arr[start:end, 1]
                        )
                    else:
                        self.trail_segments[i][k].setData([], [])
            else:
                for seg in self.trail_segments[i]:
                    seg.setData([], [])

            # Pozycja ciała i poświaty
            x, y = self.engine.positions[i]
            self.body_plots[i].setData([x], [y])
            self.glow_plots[i].setData([x], [y])
