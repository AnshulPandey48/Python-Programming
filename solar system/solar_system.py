"""
solar_system_vpython.py

Interactive 3D Solar System n-body simulator (VPython visualization)

Dependencies:
    pip install numpy scipy vpython

Run:
    python solar_system_vpython.py

Notes:
 - Units: SI (meters, kilograms, seconds).
 - Physics: Newtonian N-body gravity. Integration: Velocity-Verlet (good energy behavior).
 - Visualization: VPython (mouse: rotate/zoom/pan; GUI controls provided).
 - This is an educational sim — long-term integration requires more advanced integrators or smaller timesteps.

Author: Mentor-style teaching version (detailed comments included)
"""

from vpython import sphere, vector, color, rate, scene, local_light, slider, button, checkbox, wtext
import numpy as np
from math import sin, cos, sqrt, pi, atan2
from scipy.optimize import newton

# -----------------------------
# ---------- Constants ----------
# -----------------------------
G = 6.67430e-11           # gravitational constant (m^3 kg^-1 s^-2)
AU = 1.495978707e11       # astronomical unit (m)
DAY = 86400.0             # seconds in a day
YEAR = 365.25 * DAY       # seconds in a year

# Visual scale factors (to make planets visible; not used in physics)
VISUAL_DISTANCE_SCALE = 0.5 / AU   # compress distances for display (dimensionless)
VISUAL_SIZE_SCALE = 3e-5           # scale planet radii for visibility

# Softening length to avoid singular accelerations when bodies get very close (m)
# Very small; increases numerical stability but slightly changes true gravity at tiny radii.
SOFTENING = 1e7  # 10,000 km

# -----------------------------
# ---------- Masses -----------
# -----------------------------
# Real masses (kg) for Sun + 8 planets
masses = {
    "Sun": 1.98847e30,
    "Mercury": 3.3011e23,
    "Venus":   4.8675e24,
    "Earth":   5.97237e24,
    "Mars":    6.4171e23,
    "Jupiter": 1.8982e27,
    "Saturn":  5.6834e26,
    "Uranus":  8.6810e25,
    "Neptune": 1.02413e26
}

# Approx physical radii (m) for visual scaling only
radii = {
    "Sun": 6.9634e8,
    "Mercury": 2.4397e6,
    "Venus": 6.0518e6,
    "Earth": 6.371e6,
    "Mars": 3.3895e6,
    "Jupiter": 6.9911e7,
    "Saturn": 5.8232e7,
    "Uranus": 2.5362e7,
    "Neptune": 2.4622e7
}

# Colors for visualization (vpython color objects or rgb-like)
colors = {
    "Sun": color.yellow,
    "Mercury": color.gray(0.6),
    "Venus": color.orange,
    "Earth": color.blue,
    "Mars": color.red,
    "Jupiter": color.orange,
    "Saturn": color.white,
    "Uranus": color.cyan,
    "Neptune": color.blue
}

# -----------------------------
# ----- Orbital elements ------
# -----------------------------
# J2000-like osculating elements for each planet:
# a (AU), e, i (deg), Omega (deg, longitude of ascending node),
# omega (deg, argument of perihelion), M (deg, mean anomaly)
# These values are approximate and good for visualization/short-term integration.
planet_elements = {
    "Mercury": {"a":0.38709927, "e":0.20563593, "i":7.00498, "Omega":48.33077, "omega":29.12703, "M":174.79253},
    "Venus":   {"a":0.72333566, "e":0.00677672, "i":3.39468, "Omega":76.67984, "omega":54.92262, "M":50.37663},
    "Earth":   {"a":1.00000011, "e":0.01671022, "i":0.00005, "Omega":-11.26064, "omega":102.94719, "M":100.46435},
    "Mars":    {"a":1.52371034, "e":0.09339410, "i":1.84969, "Omega":49.55954, "omega":-73.50317, "M":19.39020},
    "Jupiter": {"a":5.20288700, "e":0.04838624, "i":1.30440, "Omega":100.47391, "omega":-85.74543, "M":19.66796},
    "Saturn":  {"a":9.53667594, "e":0.05386179, "i":2.48599, "Omega":113.66242, "omega":-21.06355, "M":-42.64463},
    "Uranus":  {"a":19.18916464, "e":0.04725744, "i":0.77264, "Omega":74.01693, "omega":96.93735, "M":142.28383},
    "Neptune": {"a":30.06992276, "e":0.00859048, "i":1.77004, "Omega":131.78423, "omega":-86.81946, "M":-100.08479}
}
# Note: elements are osculating at some epoch (J2000-ish). Good for short simulations. For long accurate ephemerides use JPL Horizons.

# -----------------------------
# ---- Kepler -> Cartesian ----
# -----------------------------
# We'll convert orbital elements to state vectors (r, v) in heliocentric ecliptic frame.
# The steps:
#  1. Solve Kepler's equation: M = E - e*sin E  -> find E (eccentric anomaly)
#  2. Compute true anomaly nu from E
#  3. Compute position in orbital plane: (x_orb, y_orb) with radius r = a*(1 - e cos E)
#  4. Compute velocity in orbital plane using standard orbital mechanics relations
#  5. Rotate from orbital plane to ecliptic coordinates using:
#     r_ecl = R_z(Omega) * R_x(i) * R_z(omega) * r_orb
#  Note: mu = G*(M_sun + m_planet), but since planet mass << sun, mu ≈ G*M_sun works fine.

def deg2rad(x): return x * pi / 180.0

def solve_kepler(M, e):
    """Solve M = E - e sin E for E using Newton's method.
    Input M in radians."""
    # initial guess: E0 = M for small e; else pi
    if e < 0.8:
        E0 = M
    else:
        E0 = pi
    f = lambda E: E - e*np.sin(E) - M
    fp = lambda E: 1 - e*np.cos(E)
    E = newton(func=f, x0=E0, fprime=fp, tol=1e-12, maxiter=200)
    return E

def elements_to_state(a_AU, e, i_deg, Omega_deg, omega_deg, M_deg, central_mass):
    """Convert orbital elements to heliocentric Cartesian r (m) and v (m/s).
    central_mass is the mass of the Sun (kg) used in mu = G*central_mass.
    Returns r (3,), v (3,) as numpy arrays.
    """
    a = a_AU * AU
    i = deg2rad(i_deg)
    Omega = deg2rad(Omega_deg)
    omega = deg2rad(omega_deg)
    M = deg2rad(M_deg) % (2*pi)
    mu = G * central_mass

    # 1) Solve Kepler
    E = solve_kepler(M, e)

    # 2) True anomaly nu
    cos_nu = (np.cos(E) - e) / (1 - e*np.cos(E))
    sin_nu = (np.sqrt(1 - e*e) * np.sin(E)) / (1 - e*np.cos(E))
    nu = atan2(sin_nu, cos_nu)

    # 3) Distance r (radius)
    r_orb = a * (1 - e * np.cos(E))

    # Position in orbital plane
    x_orb = r_orb * np.cos(nu)
    y_orb = r_orb * np.sin(nu)

    # 4) Velocity in orbital plane
    # Specific angular momentum: h = sqrt(mu * a * (1 - e^2))
    h = sqrt(mu * a * (1 - e*e))
    # vx_orb = -mu/h * sin(nu)
    # vy_orb =  mu/h * (e + cos(nu))
    vx_orb = - (mu / h) * np.sin(nu)
    vy_orb =   (mu / h) * (e + np.cos(nu))

    # 5) rotate from orbital plane to ecliptic coordinates
    # Rotation matrix R = Rz(Omega) * Rx(i) * Rz(omega)
    cosO, sinO = cos(Omega), sin(Omega)
    cosi, sini = cos(i), sin(i)
    cosw, sinw = cos(omega), sin(omega)

    # Rotation matrix components (3x3)
    R11 = cosO * cosw - sinO * sinw * cosi
    R12 = -cosO * sinw - sinO * cosw * cosi
    R13 = sinO * sini

    R21 = sinO * cosw + cosO * sinw * cosi
    R22 = -sinO * sinw + cosO * cosw * cosi
    R23 = -cosO * sini

    R31 = sinw * sini
    R32 = cosw * sini
    R33 = cosi

    r_vec = np.array([R11 * x_orb + R12 * y_orb,
                      R21 * x_orb + R22 * y_orb,
                      R31 * x_orb + R32 * y_orb])

    v_vec = np.array([R11 * vx_orb + R12 * vy_orb,
                      R21 * vx_orb + R22 * vy_orb,
                      R31 * vx_orb + R32 * vy_orb])

    return r_vec, v_vec

# -----------------------------
# ---- Build body objects -----
# -----------------------------
class Body:
    def __init__(self, name, mass, r, v, radius, color):
        self.name = name
        self.m = mass
        self.r = np.array(r, dtype=float)
        self.v = np.array(v, dtype=float)
        self.radius = radius
        # Visual sphere in VPython: scale positions & sizes for display
        pos_vis = vector(*(self.r * VISUAL_DISTANCE_SCALE))
        self.sphere = sphere(pos=pos_vis,
                             radius = radius * VISUAL_SIZE_SCALE,
                             color = color,
                             make_trail=True,
                             retain=600)  # retain last N trail points
        # shininess controls how bright/specular the object looks
        self.sphere.shininess = 0.6 if name != "Sun" else 1.0

    def update_visual(self):
        self.sphere.pos = vector(*(self.r * VISUAL_DISTANCE_SCALE))

# Create bodies list: Sun first at origin
bodies = []
# Sun: place at origin initially
sun = Body("Sun", masses["Sun"], r=[0.0,0.0,0.0], v=[0.0,0.0,0.0], radius=radii["Sun"], color=colors["Sun"])
bodies.append(sun)

# Planets: compute initial state from orbital elements
for pname, el in planet_elements.items():
    r0, v0 = elements_to_state(el["a"], el["e"], el["i"], el["Omega"], el["omega"], el["M"], masses["Sun"])
    b = Body(pname, masses[pname], r=r0, v=v0, radius=radii[pname], color=colors.get(pname, color.white))
    bodies.append(b)

# Shift into barycenter frame for more accuracy (total momentum = 0)
total_mom = np.zeros(3)
total_mass = 0.0
for b in bodies:
    total_mom += b.m * b.v
    total_mass += b.m
# give Sun a compensating velocity so system momentum is zero
bodies[0].v = - total_mom / bodies[0].m

# -----------------------------
# ---- Physics functions ------
# -----------------------------
def compute_accelerations(bodies):
    """Compute accelerations on each body from pairwise Newtonian gravity.
    Uses softening to avoid singularities.
    Returns list of numpy arrays (accelerations)."""
    N = len(bodies)
    accs = [np.zeros(3) for _ in range(N)]
    for i in range(N):
        ri = bodies[i].r
        for j in range(N):
            if i == j: continue
            rj = bodies[j].r
            rij = rj - ri
            dist2 = np.dot(rij, rij) + SOFTENING**2
            inv_dist3 = 1.0 / (dist2 * sqrt(dist2))
            accs[i] += G * bodies[j].m * rij * inv_dist3
    return accs

# -----------------------------
# ---- Integration (VV) -------
# -----------------------------
def velocity_verlet_step(bodies, dt, accs):
    """Perform one velocity-verlet update for all bodies given current accelerations accs.
    Returns new accelerations."""
    # 1) update positions: r += v*dt + 0.5*a*dt^2
    for i, b in enumerate(bodies):
        b.r = b.r + b.v * dt + 0.5 * accs[i] * dt * dt

    # 2) compute new accelerations at new positions
    new_accs = compute_accelerations(bodies)

    # 3) update velocities: v += 0.5*(a + a_new)*dt
    for i, b in enumerate(bodies):
        b.v = b.v + 0.5 * (accs[i] + new_accs[i]) * dt

    return new_accs

# Energy diagnostic (optional): compute total energy (kinetic + potential)
def total_energy(bodies):
    K = 0.0
    U = 0.0
    for i, bi in enumerate(bodies):
        K += 0.5 * bi.m * np.dot(bi.v, bi.v)
        for j in range(i+1, len(bodies)):
            bj = bodies[j]
            r = np.linalg.norm(bi.r - bj.r) + 1e-12
            U -= G * bi.m * bj.m / r
    return K + U

# -----------------------------
# ---- VPython UI elements ----
# -----------------------------
scene.title = "3D Realistic Solar System — mouse to rotate/zoom/pan\n"
scene.background = color.black
scene.width = 1100
scene.height = 700
scene.forward = vector(-0.5, -0.3, -1)  # initial camera direction

# Add a local light (sunlight)
local_light(pos=vector(0,0,0), color=color.white)

# UI widgets
running = True
time_scale = 1.0   # how many simulated seconds per real second of wall-clock
dt_default = 60.0 * 60.0 * 4.0   # 4 hours per physics step (seconds)
dt = dt_default

def toggle_run(b):
    global running
    running = not running
    b.text = "Pause" if running else "Play"

button(bind=toggle_run, text="Pause")
wtext(text="   ")
wtext(text="Time scale: ")
# slider to change time scale
def on_time_scale(s):
    global time_scale
    time_scale = s.value

slider_time = slider(min=0.01, max=200.0, value=1.0, length=200, bind=on_time_scale, right=15)

wtext(text="   ")
# focus dropdown - simple button cycle to focus camera on each planet
focus_idx = 0
def focus_next():
    global focus_idx
    focus_idx = (focus_idx + 1) % len(bodies)
    scene.center = vector(*(bodies[focus_idx].r * VISUAL_DISTANCE_SCALE))
    label_text.text = f"Camera focus: {bodies[focus_idx].name}"

def on_focus(b):
    focus_next()

button(bind=on_focus, text="Focus Next")
wtext(text="   ")
label_text = wtext(text=f"Camera focus: {bodies[0].name}")
wtext(text="   ")

# checkbox to toggle trails
def on_trails(c):
    for b in bodies:
        b.sphere.make_trail = c.checked

checkbox(bind=on_trails, text="Trails", checked=True)

# -----------------------------
# ---- Simulation main loop ---
# -----------------------------
# Precompute initial accelerations
accs = compute_accelerations(bodies)

# Diagnostics
initial_energy = total_energy(bodies)
print("Initial total energy (J):", initial_energy)

# Main loop
# We'll aim to run the physics at an internal rate and update visuals at reasonable fps.
visual_fps = 60  # frame updates per second (wall clock)
while True:
    rate(visual_fps)   # yield to VPython and limit loop speed

    # if paused, skip physics integration but keep allowing camera moves
    if not running:
        continue

    # Determine how many simulated seconds to advance this iteration based on time_scale.
    # We step physics in fixed dt increments. We'll advance Nsub steps proportional to time_scale.
    # time_scale means "simulated seconds per real second".
    simulated_seconds_this_frame = time_scale / visual_fps
    # number of dt steps to take this frame
    nsteps = max(1, int(simulated_seconds_this_frame / dt))
    # ensure at least one step but don't take too many in one frame
    nsteps = min(nsteps, 50)

    for _ in range(nsteps):
        accs = velocity_verlet_step(bodies, dt, accs)

    # update visuals (move spheres)
    for b in bodies:
        b.update_visual()

    # Optionally: show energy drift occasionally (not printed every frame)
    # current_energy = total_energy(bodies)
    # print('E drift', (current_energy - initial_energy) / initial_energy)

# End of script
