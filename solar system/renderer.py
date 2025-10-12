"""
renderer.py — OpenGL scene, planetary models, camera, lighting, trail, UI controls
Uses moderngl, pyrr for math, Pillow for textures
"""
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
from PIL import Image
import os

class Renderer:
    
    def __init__(self, width=1280, height=800):
        # Initialize ModernGL context
        self.ctx = moderngl.create_standalone_context()
        self.width = width
        self.height = height
        self._setup_shaders()
        self.camera_pos = Vector3([0.0, 0.0, 10*AU])
        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.view_matrix = Matrix44.look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
        self.proj_matrix = Matrix44.perspective_projection(60.0, width/height, 0.1*AU, 100*AU)
        self.planet_mesh = self._load_sphere_mesh()
        self.textures = {}
        self.trails = []
        self._load_textures()
        self._init_buffers()
        self.light_pos = Vector3([0, 0, 0])  # Sun at origin

    def _setup_shaders(self):
        # Simple vertex/fragment shader (Phong Illumination)
        vertex_src = """
        #version 330
        in vec3 in_position;
        in vec3 in_normal;
        in vec2 in_texcoord;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 proj;
        uniform float AU; // Declare AU used for scaling

        out vec3 frag_normal;
        out vec3 frag_pos;
        out vec2 frag_texcoord;
        void main() {
            frag_normal = mat3(model) * in_normal;
            frag_pos = vec3(model * vec4(in_position, 1.0));
            frag_texcoord = in_texcoord;
            gl_Position = proj * view * model * vec4(in_position, 1.0);
        }
        """
        fragment_src = """
        #version 330
        uniform sampler2D tex;
        uniform vec3 light_pos;
        in vec3 frag_normal;
        in vec3 frag_pos;
        in vec2 frag_texcoord;
        out vec4 frag_color;
        void main() {
            vec3 normal = normalize(frag_normal);
            vec3 lightdir = normalize(light_pos - frag_pos);
            float diff = max(dot(normal, lightdir), 0.0);
            float spec = pow(max(dot(reflect(-lightdir, normal), normalize(-frag_pos)), 0.0), 32.0);
            float glow = max(0.0, 1.0 - length(frag_pos)/AU);
            vec3 texcolor = texture(tex, frag_texcoord).rgb;
            frag_color = vec4((0.2 + 0.7*diff)*texcolor + 0.3*spec*vec3(1.0,1.0,0.8) + glow*vec3(1.0,0.8,0.5), 1.0);
        }
        """
        self.prog = self.ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)
    
    def _load_sphere_mesh(self, subdivisions=48):
        # Procedural sphere mesh (vertex pos, normals, texcoords)
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
                u = j / lon
                v = i / lat
                vertices.extend([x, y, z, x, y, z, u, v])
        vertices = np.array(vertices, dtype=np.float32)
        # Indices
        indices = []
        for i in range(lat):
            for j in range(lon):
                idx = i * (lon + 1) + j
                indices.extend([idx, idx + lon + 1, idx + 1, idx + 1, idx + lon + 1, idx + lon + 2])
        indices = np.array(indices, dtype=np.uint32)
        vbo = self.ctx.buffer(vertices.tobytes())
        ibo = self.ctx.buffer(indices.tobytes())
        vao = self.ctx.vertex_array(self.prog,
            [(vbo, "3f 3f 2f", "in_position", "in_normal", "in_texcoord")],
            index_buffer=ibo)
        return vao

    def _load_textures(self):
        asset_dir = os.path.join(os.path.dirname(__file__), "assets")
        for fname in os.listdir(asset_dir):
            if fname.endswith(".jpg") or fname.endswith(".png"):
                path = os.path.join(asset_dir, fname)
                img = Image.open(path)
                img = img.resize((2048,2048)).convert('RGB')
                tex = self.ctx.texture(img.size, 3, img.tobytes())
                tex.build_mipmaps()
                self.textures[fname.split(".")[0]] = tex

    def _init_buffers(self):
        self.trail_buffer = []  # List of trails per planet, add positions

    def render_planets(self, bodies: list):
        self.ctx.clear(0.01, 0.01, 0.01)
        for body in bodies:
            model = Matrix44.from_translation(body.position)
            self.prog['model'].write(model.astype('f4').tobytes())
            self.prog['view'].write(self.view_matrix.astype('f4').tobytes())
            self.prog['proj'].write(self.proj_matrix.astype('f4').tobytes())
            self.prog['light_pos'].value = tuple(self.light_pos)
            tex = self.textures.get(body.name.lower(), None)
            if tex:
                tex.use()
            self.planet_mesh.render()
            # Update and draw trail (simplified)
            trail = self._update_trail(body)
            self._render_trail(trail)

    def _update_trail(self, body):
        # Store last N positions
        trail_len = 500
        if not hasattr(body, 'trail'): body.trail = []
        body.trail.append(body.position.copy())
        if len(body.trail) > trail_len:
            body.trail = body.trail[-trail_len:]
        return np.array(body.trail)

    def _render_trail(self, trail):
        # Render trail as a polyline (override for OpenGL line calls)
        pass  # Implement with glLine if needed; skipped for brevity

    def handle_camera_drag(self, dx, dy):
        # Map 2D mouse drag to camera translation along view direction
        # dx, dy: pixel deltas
        move_speed = 0.1 * AU * (abs(dy)/50)
        self.camera_pos += self.camera_front * move_speed * np.sign(dy)
        self.view_matrix = Matrix44.look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

