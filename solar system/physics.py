"""
physics.py — N-body planetary physics and utility functions (unchanged).
"""
import numpy as np
from typing import List, Tuple

G = 6.67430e-11
AU = 1.495978707e11

class Body:
    def __init__(self, mass, position, velocity, name="body", radius=1):
        self.mass = float(mass)
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.name = name
        self.radius = float(radius)  # in meters

def kepler_to_cartesian(a, e, i, omega, w, M, mu):
    # ... (as given previously, unchanged)
    def solve_kepler(E0, e, M, tol=1e-10):
        E = E0
        for _ in range(32):
            f = E - e * np.sin(E) - M
            df = 1 - e * np.cos(E)
            E -= f / df
            if abs(f) < tol: break
        return E
    E = solve_kepler(M, e, M)
    nu = 2 * np.arctan2(np.sqrt(1+e)*np.sin(E/2), np.sqrt(1-e)*np.cos(E/2))
    r = a * (1 - e * np.cos(E))
    x_op, y_op = r * np.cos(nu), r * np.sin(nu)
    cos_o, sin_o = np.cos(omega), np.sin(omega)
    cos_i, sin_i = np.cos(i), np.sin(i)
    cos_w, sin_w = np.cos(w), np.sin(w)
    R = np.array([
        [cos_o*cos_w - sin_o*sin_w*cos_i, -cos_o*sin_w - sin_o*cos_w*cos_i, sin_o*sin_i],
        [sin_o*cos_w + cos_o*sin_w*cos_i, -sin_o*sin_w + cos_o*cos_w*cos_i, -cos_o*sin_i],
        [sin_w*sin_i,  cos_w*sin_i, cos_i]
    ])
    pos = R @ np.array([x_op, y_op, 0.0])
    n = np.sqrt(mu / a**3)
    rdot = n * a * e * np.sin(E) / (1 - e*np.cos(E))
    rfdot = n * a * np.sqrt(1-e**2) / r
    vx_op = rdot * np.cos(nu) - rfdot * np.sin(nu)
    vy_op = rdot * np.sin(nu) + rfdot * np.cos(nu)
    vel = R @ np.array([vx_op, vy_op, 0.0])
    return pos, vel

def compute_accelerations(bodies, eps=1e7):
    # ... as previously
    N = len(bodies)
    acc = np.zeros((N,3))
    pos = np.array([b.position for b in bodies])
    mass = np.array([b.mass for b in bodies])
    for i in range(N):
        for j in range(N):
            if i == j: continue
            r = pos[j] - pos[i]
            dist3 = (np.dot(r,r) + eps**2) ** 1.5
            acc[i] += G * mass[j] * r / dist3
    return acc

def velocity_verlet_step(bodies, dt, eps=1e7):
    N = len(bodies)
    positions = np.array([b.position for b in bodies])
    velocities = np.array([b.velocity for b in bodies])
    acc = compute_accelerations(bodies, eps)
    positions_new = positions + velocities * dt + 0.5 * acc * dt**2
    for i, b in enumerate(bodies):
        b.position = positions_new[i]
    acc_new = compute_accelerations(bodies, eps)
    velocities_new = velocities + 0.5 * (acc + acc_new) * dt
    for i, b in enumerate(bodies):
        b.velocity = velocities_new[i]

def system_energy(bodies, eps=1e7):
    N = len(bodies)
    kinetic = sum(0.5 * b.mass * np.dot(b.velocity, b.velocity) for b in bodies)
    potential = 0.0
    for i in range(N):
        for j in range(i+1,N):
            r = bodies[j].position - bodies[i].position
            dist = np.sqrt(np.dot(r,r) + eps**2)
            potential -= G * bodies[i].mass * bodies[j].mass / dist
    total = kinetic + potential
    return kinetic, potential, total
