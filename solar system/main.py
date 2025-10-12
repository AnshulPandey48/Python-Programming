"""
main.py — PyQt5 window with QOpenGLWidget, controls, physics loop.
"""
import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets
from pyrr import Matrix44
from physics import Body, kepler_to_cartesian, velocity_verlet_step, system_energy, AU, G
from renderer import GLWidget

class SimState:
    def __init__(self, timescale=1.0, dt=3600.0, paused=False):
        self.timescale = timescale
        self.dt = dt
        self.paused = paused
        self.focus_idx = 0

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-body Solar System")
        self.resize(1280, 850)
        self.sim = SimState()
        self.bodies = self._init_bodies()
        self.gl_widget = GLWidget(self.bodies, self)
        self.energy_label = QtWidgets.QLabel(self)
        self.pause_btn = QtWidgets.QPushButton("Pause", self)
        self.timescale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.focus_combo = QtWidgets.QComboBox(self)
        self._setup_ui()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._on_timer)
        self.timer.start(16)  # ~60 FPS

    def _init_bodies(self):
        sun = Body(1.989e30, np.zeros(3), np.zeros(3), "sun")
        params = [
            ("mercury", 3.301e23, 0.387, 0.205, 7.0, 48.3, 29.1, 174.8),
            ("venus",   4.867e24, 0.723, 0.007, 3.39, 76.7, 54.9, 50.1),
            ("earth",   5.972e24, 1.000, 0.017, 0.0, -11.3, 114.2, 358.6),
            ("mars",    6.417e23, 1.524, 0.093, 1.85, 49.6, 286.5, 19.4)
        ]
        bodies = [sun]
        mu = G * sun.mass
        for name, mass, a_AU, e, i_deg, omega_deg, w_deg, M_deg in params:
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
        # Controls at the top
        self.energy_label.setText("Energy: ")
        layout.addWidget(self.energy_label)
        self.pause_btn.clicked.connect(self._pause)
        layout.addWidget(self.pause_btn)
        layout.addWidget(QtWidgets.QLabel("Timescale:"))
        self.timescale_slider.setRange(1, 50)
        self.timescale_slider.setValue(1)
        self.timescale_slider.valueChanged.connect(self._change_timescale)
        layout.addWidget(self.timescale_slider)
        layout.addWidget(QtWidgets.QLabel("Focus body:"))
        self.focus_combo.addItems([b.name.capitalize() for b in self.bodies])
        self.focus_combo.currentIndexChanged.connect(self._focus_body)
        layout.addWidget(self.focus_combo)
        # 3D OpenGL
        layout.addWidget(self.gl_widget, stretch=10)
        self.setLayout(layout)

    def _pause(self):
        self.sim.paused = not self.sim.paused
        self.pause_btn.setText("Resume" if self.sim.paused else "Pause")

    def _change_timescale(self, val):
        self.sim.timescale = float(val)

    def _focus_body(self, idx):
        self.sim.focus_idx = idx

    def _on_timer(self):
        if not self.sim.paused:
            for _ in range(int(self.sim.timescale)):
                velocity_verlet_step(self.bodies, self.sim.dt)
        k, u, e = system_energy(self.bodies)
        self.energy_label.setText(f"Energy: T={k:.2e} U={u:.2e} E={e:.2e}")
        focus_body = self.bodies[self.sim.focus_idx]
        self.gl_widget.set_focus(focus_body.position)
        self.gl_widget.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
