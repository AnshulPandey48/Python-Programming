"""
renderer.py — ModernGL+PyQt5 QOpenGLWidget draws colored spheres per planet, radius scaled, no textures.
"""
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
import os
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt

AU = 1.495978707e11

# Solar system canonical radii in meters (approx):
planetradii = {
    'sun':     6.957e8,
    'mercury': 2.44e6,
    'venus':   6.05e6,
    'earth':   6.378e6,
    'mars':    3.39e6,
    'jupiter': 6.99e7,
    'saturn':  5.82e7,
    'uranus':  2.54e7,
    'neptune': 2.46e7,
}

planetcolors = {
    'sun':     (1.0, 0.85, 0.15),  # yellow-white
    'mercury': (0.7, 0.7, 0.7),    # gray
    'venus':   (1.0, 0.9, 0.7),    # pale yellow
    'earth':   (0.2, 0.3, 1.0),    # blue
    'mars':    (1.0, 0.3, 0.1),    # orange/red
    'jupiter': (0.95, 0.8, 0.7),   # beige
    'saturn':  (0.98, 0.9, 0.6),   # light beige
    'uranus':  (0.5, 0.95, 1.0),   # cyan
    'neptune': (0.3, 0.3, 1.0),    # blue
}

def planet_color(name):
    return planetcolors.get(name.lower(), (1.0, 1.0, 1.0))

def planet_radius(name):
    r = planetradii.get(name.lower(), 3.0e6)
    # Scale up for OpenGL visibility but preserve ratios; multiply by a factor (e.g., 100)
    factor = 1e4
    return r * factor

class GLWidget(QOpenGLWidget):
    def __init__(self, bodies, parent=None):
        super().__init__(parent)
        self.bodies = bodies
        self.width = 1280
        self.height = 800
        self.ctx = None
        self.prog = None
        self.sphere_mesh = None
        self.camera_pos = Vector3([0.0, 0.0, 10*AU])
        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.view_matrix = Matrix44.look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
        self.proj_matrix = Matrix44.perspective_projection(60.0, self.width/self.height, 0.1*AU, 100*AU)
        self.setFocusPolicy(Qt.ClickFocus)

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self._setup_shaders()
        self.sphere_mesh = self._load_sphere_mesh()
        self.ctx.enable(moderngl.DEPTH_TEST)

    def resizeGL(self, w, h):
        self.width = w
        self.height = h
        self.proj_matrix = Matrix44.perspective_projection(60.0, w/max(h,1), 0.1*AU, 100*AU)

    def paintGL(self):
        self.ctx.clear(0.01, 0.01, 0.01)
        for body in self.bodies:
            model = Matrix44.from_scale([planet_radius(body.name)]*3) @ Matrix44.from_translation(body.position)
            self.prog['model'].write(model.astype('f4').tobytes())
            self.prog['view'].write(self.view_matrix.astype('f4').tobytes())
            self.prog['proj'].write(self.proj_matrix.astype('f4').tobytes())
            self.prog['color'].value = planet_color(body.name)
            self.sphere_mesh.render()

    def _setup_shaders(self):
        vertex_src = """
        #version 330
        in vec3 in_position;
        in vec3 in_normal;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 proj;
        out vec3 v_normal;
        out vec3 v_pos;
        void main() {
            v_normal = mat3(model) * in_normal;
            v_pos = vec3(model * vec4(in_position, 1.0));
            gl_Position = proj * view * model * vec4(in_position, 1.0);
        }
        """
        fragment_src = """
        #version 330
        uniform vec3 color;
        in vec3 v_normal;
        in vec3 v_pos;
        out vec4 frag_color;
        void main() {
            vec3 norm = normalize(v_normal);
            vec3 lightdir = normalize(-v_pos); // sun at origin emits outward
            float diff = max(dot(norm, lightdir), 0.0);
            float spec = pow(max(dot(reflect(-lightdir, norm), normalize(-v_pos)), 0.0), 24.0);
            vec3 c = (0.2 + 0.8*diff)*color + 0.2*spec*vec3(1,1,0.85);
            frag_color = vec4(c, 1.0);
        }
        """
        self.prog = self.ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)

    def _load_sphere_mesh(self, subdivisions=48):
        lat = subdivisions
        lon = 2*subdivisions
        vertices = []
        for i in range(lat + 1):
            theta = np.pi * i / lat
            for j in range(lon + 1):
                phi = 2 * np.pi * j / lon
                x = np.sin(theta) * np.cos(phi)
                y = np.cos(theta)
                z = np.sin(theta) * np.sin(phi)
                vertices.extend([x, y, z, x, y, z])
        vertices = np.array(vertices, dtype=np.float32)
        indices = []
        for i in range(lat):
            for j in range(lon):
                idx = i * (lon + 1) + j
                indices.extend([idx, idx + lon + 1, idx + 1, idx + 1, idx + lon + 1, idx + lon + 2])
        indices = np.array(indices, dtype=np.uint32)
        vbo = self.ctx.buffer(vertices.tobytes())
        ibo = self.ctx.buffer(indices.tobytes())
        vao = self.ctx.vertex_array(self.prog,
            [(vbo, "3f 3f", "in_position", "in_normal")],
            index_buffer=ibo)
        return vao

    def set_focus(self, position):
        self.camera_pos = Vector3([0.0, 0.0, 3*AU])  # Only 3 AU out, not 10
        self.camera_front = Vector3([0.0, 0.0, -1.0])
