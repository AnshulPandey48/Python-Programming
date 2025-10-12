"""
main.py — launcher, UI, physics + renderer sync
Uses PyQt5 (or DearPyGui — user may choose) for UI controls
"""
import sys
import numpy as np
from physics import Body, kepler_to_cartesian, velocity_verlet_step, system_energy, AU, G
from renderer import Renderer
from PyQt5 import QtWidgets, QtCore

class SimState:
    def __init__(self, timescale=1.0, dt=3600.0, paused=False):
        self.timescale = timescale  # simulation speed factor
        self.dt = dt                # simulation timestep in seconds
        self.paused = paused
        self.focus_idx = 0          # body to focus camera

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-body Solar System")
        self.resize(1280, 800)
        self.sim = SimState()
        self.bodies = self._init_bodies()
        self.renderer = Renderer(width=1280, height=800)
        self._setup_ui()
        self.energy_label = QtWidgets.QLabel(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._on_timer)
        self.timer.start(16)  # ~60 FPS

    def _init_bodies(self):
        # Hardcoded sample orbital configs for Sun + 4 inner planets
        sun = Body(1.9885e30, np.zeros(3), np.zeros(3), "sun")
        planet_params = [  # (name, mass, a_AU, e, i_deg, omega_deg, w_deg, M_deg)
            ("mercury", 3.3011e23, 0.387, 0.2056, 7.0, 48.3, 29.1, 174.8),
            ("venus", 4.8675e24, 0.723, 0.0068, 3.39, 76.7, 54.9, 50.1),
            ("earth", 5.9723e24, 1.000, 0.0167, 0.0, -11.3, 114.2, 358.6),
            ("mars", 6.4171e23, 1.524, 0.0934, 1.85, 49.6, 286.5, 19.4)
        ]
        bodies = [sun]
        mu = G * sun.mass
        for name, mass, a_AU, e, i_deg, omega_deg, w_deg, M_deg in planet_params:
            a = a_AU * AU
            i = np.radians(i_deg)
            omega = np.radians(omega_deg)
            w = np.radians(w_deg)
            M = np.radians(M_deg)
            pos, vel = kepler_to_cartesian(a, e, i, omega, w, M, mu)
            bodies.append(Body(mass, pos, vel, name))
        return bodies

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.pause_btn = QtWidgets.QPushButton("Pause", self)
        self.pause_btn.clicked.connect(self._on_pause)
        self.timescale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.timescale_slider.setRange(1,100)
        self.timescale_slider.setValue(1)
        self.timescale_slider.valueChanged.connect(self._on_timescale)
        self.focus_combo = QtWidgets.QComboBox(self)
        names = [b.name.capitalize() for b in self.bodies]
        self.focus_combo.addItems(names)
        self.focus_combo.currentIndexChanged.connect(self._on_focus)
        layout.addWidget(self.pause_btn)
        layout.addWidget(QtWidgets.QLabel("Timescale:"))
        layout.addWidget(self.timescale_slider)
        layout.addWidget(QtWidgets.QLabel("Focus body:"))
        layout.addWidget(self.focus_combo)
        layout.addWidget(self.energy_label)
        self.setLayout(layout)

    def _on_pause(self):
        self.sim.paused = not self.sim.paused
        self.pause_btn.setText("Resume" if self.sim.paused else "Pause")

    def _on_timescale(self, val):
        self.sim.timescale = float(val)

    def _on_focus(self, idx):
        self.sim.focus_idx = idx

    def _on_timer(self):
        # Physics step (fixed dt)
        if not self.sim.paused:
            for _ in range(int(self.sim.timescale)):
                velocity_verlet_step(self.bodies, self.sim.dt)
        # Diagnostics
        k, u, e = system_energy(self.bodies)
        self.energy_label.setText(
            f"Energy: T={k:.2e} U={u:.2e} E={e:.2e}"
        )
        # Renderer: Update camera to focus body
        focus_body = self.bodies[self.sim.focus_idx]
        self.renderer.camera_pos = focus_body.position + np.array([0,0,10*AU])
        self.renderer.view_matrix = self.renderer.view_matrix = Matrix44.look_at(
            self.renderer.camera_pos,
            focus_body.position,
            self.renderer.camera_up
        )
        # Draw frame
        self.renderer.render_planets(self.bodies)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
