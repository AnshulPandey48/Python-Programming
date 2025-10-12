"""
physics.py — all physics simulation code for planetary N-body system
Includes:
- Physical units
- Keplerian → Cartesian conversion
- N-body gravitational forces
- Velocity-Verlet integration
- System energy diagnostics
"""
import numpy as np
from typing import Tuple

G = 6.67430e-11           # Gravitational constant (m^3/kg/s^2)
AU = 1.495978707e11        # Astronomical Unit (meters)
DAY = 86400                # Seconds in one day

class Body:
    def __init__(self, mass: float, position: np.ndarray, velocity: np.ndarray, name: str = "body"):
        self.mass = mass
        self.position = position  # shape (3,)
        self.velocity = velocity  # shape (3,)
        self.name = name


def kepler_to_cartesian(a: float, e: float, i: float, omega: float, w: float, M: float, mu: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Converts Keplerian elements to Cartesian position and velocity.
    Args:
        a: semi-major axis (meters)
        e: eccentricity
        i: inclination (radians)
        omega: longitude of ascending node Ω (radians)
        w: argument of periapsis ω (radians)
        M: mean anomaly M (radians)
        mu: standard gravitational parameter (GM_sun; m^3/s^2)
    Returns:
        position: (3,) ndarray (meters)
        velocity: (3,) ndarray (meters/second)
    """
    # Solve Kepler's Equation for E (eccentric anomaly)
    def kepler_eq(E):
        return E - e * np.sin(E) - M
    E = M
    for _ in range(10):
        E -= kepler_eq(E) / (1 - e * np.cos(E))
    # True anomaly
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E/2), np.sqrt(1 - e) * np.cos(E/2))
    r = a * (1 - e * np.cos(E))
    # Position in orbital plane
    x_op = r * np.cos(nu)
    y_op = r * np.sin(nu)
    # Velocity magnitude
    v_r = (mu/a)**0.5 * e * np.sin(nu) / (1 - e * np.cos(E))
    v_t = (mu*a)**0.5 * (1 + e * np.cos(nu)) / r
    vx_op = v_r * np.cos(nu) - v_t * np.sin(nu)
    vy_op = v_r * np.sin(nu) + v_t * np.cos(nu)
    # Rotate to 3D ecliptic coordinates
    cos_o, sin_o = np.cos(omega), np.sin(omega)
    cos_i, sin_i = np.cos(i), np.sin(i)
    cos_w, sin_w = np.cos(w), np.sin(w)
    # Rotation matrix: Rz(Ω) Rx(i) Rz(ω)
    R = np.array([
        [cos_o*cos_w - sin_o*sin_w*cos_i, -cos_o*sin_w - sin_o*cos_w*cos_i,    sin_o*sin_i],
        [sin_o*cos_w + cos_o*sin_w*cos_i, -sin_o*sin_w + cos_o*cos_w*cos_i,  -cos_o*sin_i],
        [sin_w*sin_i,                     cos_w*sin_i,                       cos_i        ]
    ])
    position = R @ np.array([x_op, y_op, 0])
    velocity = R @ np.array([vx_op, vy_op, 0])
    return position, velocity


def compute_accelerations(bodies: list, softening: float = 1e7) -> np.ndarray:
    """
    Computes N-body gravitational accelerations for each body.
    Args:
        bodies: list of Body objects
        softening: softening length epsilon (meters) to avoid singularities
    Returns:
        (N, 3) ndarray accelerations in m/s^2
    """
    N = len(bodies)
    positions = np.array([b.position for b in bodies])
    masses = np.array([b.mass for b in bodies])
    acc = np.zeros((N, 3))
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            r = positions[j] - positions[i]
            dist3 = (np.linalg.norm(r)**2 + softening**2) ** (1.5)
            acc[i] += G * masses[j] * r / dist3
    return acc


def velocity_verlet_step(bodies: list, dt: float, softening: float = 1e7):
    """
    Advances the system by one Velocity-Verlet step
    Args:
        bodies: list of Body objects
        dt: timestep (seconds)
        softening: softening length (meters)
    """
    positions = np.array([b.position for b in bodies])
    velocities = np.array([b.velocity for b in bodies])
    masses = np.array([b.mass for b in bodies])
    acc = compute_accelerations(bodies, softening)
    next_positions = positions + velocities * dt + 0.5 * acc * dt**2
    # Temporarily update positions for new acceleration
    for idx, b in enumerate(bodies):
        b.position = next_positions[idx]
    acc_next = compute_accelerations(bodies, softening)
    next_velocities = velocities + 0.5 * (acc + acc_next) * dt
    for idx, b in enumerate(bodies):
        b.velocity = next_velocities[idx]


def system_energy(bodies: list, softening: float = 1e7) -> Tuple[float, float, float]:
    """
    Computes kinetic, potential, and total energy of the system
    Args:
        bodies: list of Body objects
        softening: epsilon (meters)
    Returns:
        kinetic, potential, total energy (Joules)
    """
    N = len(bodies)
    positions = np.array([b.position for b in bodies])
    masses = np.array([b.mass for b in bodies])
    velocities = np.array([b.velocity for b in bodies])
    kinetic = 0.5 * np.sum(masses * np.sum(velocities**2, axis=1))
    potential = 0
    for i in range(N):
        for j in range(i + 1, N):
            r = positions[j] - positions[i]
            dist = np.sqrt(np.sum(r**2) + softening**2)
            potential -= G * masses[i] * masses[j] / dist
    total = kinetic + potential
    return kinetic, potential, total

