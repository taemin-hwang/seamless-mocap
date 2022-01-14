#---------------------------------------------------
#        3D VIEWER FOR POSE ESTIMATION
#---------------------------------------------------

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from threading import Lock
from visualizer.utils import *
from datetime import datetime

import numpy as np
import time
import sys
import array
import math
import ctypes

M_PI = 3.1415926

SK_SPHERE_SHADER = """
# version 330 core
layout(location = 0) in vec3 in_Vertex;
layout(location = 1) in vec3 in_Normal;
out vec4 b_color;
out vec3 b_position;
out vec3 b_normal;
uniform mat4 u_mvpMatrix;
uniform vec4 u_color;
uniform vec4 u_pt;
void main() {
   b_color = u_color;
   b_position = in_Vertex;
   b_normal = in_Normal;
   gl_Position =  u_mvpMatrix * (u_pt + vec4(in_Vertex, 1));
}
"""

SK_VERTEX_SHADER = """
# version 330 core
layout(location = 0) in vec3 in_Vertex;
layout(location = 1) in vec3 in_Normal;
out vec4 b_color;
out vec3 b_position;
out vec3 b_normal;
uniform mat4 u_mvpMatrix;
uniform vec4 u_color;
void main() {
   b_color = u_color;
   b_position = in_Vertex;
   b_normal = in_Normal;
   gl_Position =  u_mvpMatrix * vec4(in_Vertex, 1);
}
"""

SK_FRAGMENT_SHADER = """
# version 330 core
in vec4 b_color;
in vec3 b_position;
in vec3 b_normal;
out vec4 out_Color;
void main() {
    vec3 lightPosition = vec3(0, 2, 1);
    float ambientStrength = 0.3;
    vec3 lightColor = vec3(0.75, 0.75, 0.9);
    vec3 ambient = ambientStrength * lightColor;
    vec3 lightDir = normalize(lightPosition - b_position);
    float diffuse = (1 - ambientStrength) * max(dot(b_normal, lightDir), 0.0);
    out_Color = vec4(b_color.rgb * (diffuse + ambient), 1);
}
"""

def generate_color_id(_idx):
    clr = np.divide(generate_color_id_u(_idx),255.0)
    clr[0], clr[2] = clr[2], clr[0]
    return clr

class Shader:
    def __init__(self, _vs, _fs):
        self.program_id = glCreateProgram()
        vertex_id = self.compile(GL_VERTEX_SHADER, _vs)
        fragment_id = self.compile(GL_FRAGMENT_SHADER, _fs)

        glAttachShader(self.program_id, vertex_id)
        glAttachShader(self.program_id, fragment_id)
        glBindAttribLocation( self.program_id, 0, "in_vertex")
        glBindAttribLocation( self.program_id, 1, "in_texCoord")
        glLinkProgram(self.program_id)

        if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program_id)
            glDeleteProgram(self.program_id)
            glDeleteShader(vertex_id)
            glDeleteShader(fragment_id)
            raise RuntimeError('Error linking program: %s' % (info))
        glDeleteShader(vertex_id)
        glDeleteShader(fragment_id)

    def compile(self, _type, _src):
        try:
            shader_id = glCreateShader(_type)
            if shader_id == 0:
                print("ERROR: shader type {0} does not exist".format(_type))
                exit()

            glShaderSource(shader_id, _src)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader_id)
                glDeleteShader(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def get_program_id(self):
        return self.program_id

class Simple3DObject:
    """
    Class that manages simple 3D objects to render with OpenGL
    """
    def __init__(self, _is_static):
        self.vaoID = 0
        self.drawing_type = GL_TRIANGLES
        self.is_static = _is_static
        self.elementbufferSize = 0
        self.is_init = False

        self.vertices = array.array('f')
        self.normals = array.array('f')
        self.indices = array.array('I')

    def __del__(self):
        self.is_init = False
        if self.vaoID:
            self.vaoID = 0

    def add_vert(self, i_f, limit, height):
        p1 = [i_f, height, -limit]
        p2 = [i_f, height, limit]
        p3 = [-limit, height, i_f]
        p4 = [limit, height, i_f]

        self.add_line(p1, p2)
        self.add_line(p3, p4)

    """
    Add a unique point to the list of points
    """
    def add_pt(self, _pts):
        for pt in _pts:
            self.vertices.append(pt)

    """
    Add a unique normal to the list of normals
    """
    def add_normal(self, _normals):
        for normal in _normals:
            self.normals.append(normal)

    """
    Add a set of points to the list of points and their corresponding color
    """
    def add_points(self, _pts):
        for i in range(len(_pts)):
            pt = _pts[i]
            self.add_pt(pt)
            current_size_index = int((len(self.vertices)/3))-1
            self.indices.append(current_size_index)
            self.indices.append(current_size_index+1)

    """
    Add a point and its corresponding color to the list of points
    """
    def add_point_clr(self, _pt):
        self.add_pt(_pt)
        self.add_normal([0.3,0.3,0.3])
        self.indices.append(len(self.indices))

    def add_point_clr_norm(self, _pt,  _norm):
        self.add_pt(_pt)
        self.add_normal(_norm)
        self.indices.append(len(self.indices))

    """
    Define a line from two points
    """
    def add_line(self, _p1, _p2):
        self.add_point_clr(_p1)
        self.add_point_clr(_p2)

    def add_sphere(self):
        m_radius = 0.01
        m_stack_count = 16
        m_sector_count = 16

        for i in range(m_stack_count+1):
            lat0 = M_PI * (-0.5 + (i - 1) / m_stack_count)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)

            lat1 = M_PI * (-0.5 + i / m_stack_count)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            for j in range(m_sector_count):
                lng = 2 * M_PI * (j - 1) / m_sector_count
                x = math.cos(lng)
                y = math.sin(lng)

                v = [m_radius * x * zr0, m_radius * y * zr0, m_radius * z0]
                normal = [x * zr0, y * zr0, z0]
                self.add_point_clr_norm(v, normal)

                v = [m_radius * x * zr1, m_radius * y * zr1, m_radius * z1]
                normal = [x * zr1, y * zr1, z1]
                self.add_point_clr_norm(v, normal)

                lng = 2 * M_PI * j / m_sector_count
                x = math.cos(lng)
                y = math.sin(lng)

                v= [m_radius * x * zr1, m_radius * y * zr1, m_radius * z1]
                normal = [x * zr1, y * zr1, z1]
                self.add_point_clr_norm(v, normal)

                v = [m_radius * x * zr0, m_radius * y * zr0, m_radius * z0]
                normal = [x * zr0, y * zr0, z0]
                self.add_point_clr_norm(v, normal)

    def push_to_GPU(self):
        if( self.is_init == False):
            self.vboID = glGenBuffers(3)
            self.is_init = True

        if len(self.vertices):
            glBindBuffer(GL_ARRAY_BUFFER, self.vboID[0])
            glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * self.vertices.itemsize, (GLfloat * len(self.vertices))(*self.vertices), GL_STATIC_DRAW)

        if len(self.normals):
            glBindBuffer(GL_ARRAY_BUFFER, self.vboID[1])
            glBufferData(GL_ARRAY_BUFFER, len(self.normals) * self.normals.itemsize, (GLfloat * len(self.normals))(*self.normals), GL_STATIC_DRAW)

        if len(self.indices):
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vboID[2])
            glBufferData(GL_ELEMENT_ARRAY_BUFFER,len(self.indices) * self.indices.itemsize,(GLuint * len(self.indices))(*self.indices), GL_STATIC_DRAW)

        self.elementbufferSize = len(self.indices)

    def clear(self):
        self.vertices = array.array('f')
        self.normals = array.array('f')
        self.indices = array.array('I')

    def set_drawing_type(self, _type):
        self.drawing_type = _type

    def draw(self):
        if (self.elementbufferSize > 0) and self.is_init:
            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, self.vboID[0])
            glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)

            glEnableVertexAttribArray(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vboID[1])
            glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vboID[2])
            glDrawElements(self.drawing_type, self.elementbufferSize, GL_UNSIGNED_INT, None)

            glDisableVertexAttribArray(0)
            glDisableVertexAttribArray(1)

class Skeleton:
    def __init__(self, _body_format = 25): # body_format = 18 / 25 / 34
        self.clr = [0,0,0,1]
        self.kps = []
        self.joints = Simple3DObject(False)
        self.Z = 1
        self.body_format = _body_format

    def set_skeleton(self, person_id, skeletons):
        self.joints.set_drawing_type(GL_LINES)
        self.clr = generate_color_id(person_id)
        self.Z = 0.6

        # Draw skeletons
        if len(skeletons) > 0:
            # POSE_18 -> 18 keypoints
            if self.body_format == 18:
                # Bones
                # Definition of SKELETON_BONES in cv_viewer.utils.py, which slightly differs from BODY_BONES
                for bone in SKELETON_BONES:
                    kp_1 = skeletons[bone[0].value]
                    kp_2 = skeletons[bone[1].value]
                    if math.isfinite(kp_1[0]) and math.isfinite(kp_2[0]):
                        self.joints.add_line(kp_1, kp_2)

                for part in range(len(BODY_PARTS)-1):    # -1 to avoid LAST
                    kp = skeletons[part]
                    norm = np.linalg.norm(kp)
                    if math.isfinite(norm):
                        self.kps.append(kp)

                # Create backbone (not defined in BODY_BONES)
                spine = (skeletons[BODY_PARTS.LEFT_HIP.value] + skeletons[BODY_PARTS.RIGHT_HIP.value]) / 2
                neck = skeletons[BODY_PARTS.NECK.value]
                self.joints.add_line(spine, neck)

                # Spine base joint
                if math.isfinite(np.linalg.norm(spine)):
                    self.kps.append(spine)

            # POSE_25 -> 25 keypoints
            elif self.body_format == 25:
                for bone in BODY_BONES_POSE_25:
                    kp_1 = skeletons[bone[0].value]
                    kp_2 = skeletons[bone[1].value]
                    np_kp_1 = np.array(kp_1[:3])
                    np_kp_1_c = np_kp_1.copy()
                    np_kp_1_c[0] = np_kp_1[1]
                    np_kp_1_c[1] = np_kp_1[2]
                    np_kp_1_c[2] = np_kp_1[0]
                    np_kp_1_c[:2] = np_kp_1_c[:2]/2
                    np_kp_1_c[1] = np_kp_1_c[1]-0.3
                    np_kp_1_c[2] = np_kp_1_c[2]-2.5

                    np_kp_2 = np.array(kp_2[:3])
                    np_kp_2_c = np_kp_2.copy()
                    np_kp_2_c[0] = np_kp_2[1]
                    np_kp_2_c[1] = np_kp_2[2]
                    np_kp_2_c[2] = np_kp_2[0]
                    np_kp_2_c[:2] = np_kp_2_c[:2]/2
                    np_kp_2_c[1] = np_kp_2_c[1]-0.3
                    np_kp_2_c[2] = np_kp_2_c[2]-2.5
                    if math.isfinite(np_kp_1_c[0]) and math.isfinite(np_kp_2_c[0]):
                        self.joints.add_line(np_kp_1_c.tolist(), np_kp_2_c.tolist())

                for part in range(len(BODY_PARTS_POSE_25)-1):
                    kp = skeletons[part]
                    np_kp = np.array(kp[:3])
                    np_kp_c = np_kp_2.copy()
                    np_kp_c[0] = np_kp[1]
                    np_kp_c[1] = np_kp[2]
                    np_kp_c[2] = np_kp[0]
                    np_kp_c[:2] = np_kp_c[:2]/2
                    np_kp_c[1] = np_kp_c[1]-0.3
                    np_kp_c[2] = np_kp_c[2]-2.5
                    norm = np.linalg.norm(np_kp_c.tolist())
                    if math.isfinite(norm):
                        self.kps.append(np_kp_c.tolist())

            # POSE_34 -> 34 keypoints
            elif self.body_format == 34:
                for bone in BODY_BONES_POSE_34:
                    kp_1 = skeletons[bone[0].value]
                    kp_2 = skeletons[bone[1].value]
                    if math.isfinite(kp_1[0]) and math.isfinite(kp_2[0]):
                        self.joints.add_line(kp_1, kp_2)

                for part in range(len(BODY_PARTS_POSE_34)-1):
                    kp = skeletons[part]
                    norm = np.linalg.norm(kp)
                    if math.isfinite(norm):
                        self.kps.append(kp)

    def push_to_GPU(self):
        self.joints.push_to_GPU()

    def draw(self, shader_sk_clr, sphere, shader_mvp, projection):
        glUniform4f(shader_sk_clr, self.clr[0],self.clr[1],self.clr[2],self.clr[3])
        line_w = (20. / self.Z)
        glLineWidth(line_w)
        self.joints.draw()

    def drawKPS(self, shader_clr, sphere, shader_pt):
        glUniform4f(shader_clr, self.clr[0],self.clr[1],self.clr[2],self.clr[3])
        for k in self.kps:
            glUniform4f(shader_pt, k[0],k[1],k[2], 1)
            sphere.draw()
            sphere.draw()

IMAGE_FRAGMENT_SHADER = """
# version 330 core
in vec2 UV;
out vec4 color;
uniform sampler2D texImage;
void main() {
    vec2 scaler =vec2(UV.x,1.f - UV.y);
    vec3 rgbcolor = vec3(texture(texImage, scaler).zyx);
    vec3 color_rgb = pow(rgbcolor, vec3(1.65f));
    color = vec4(color_rgb,1.f);
}
"""

IMAGE_VERTEX_SHADER = """
# version 330
layout(location = 0) in vec3 vert;
out vec2 UV;
void main() {
    UV = (vert.xy+vec2(1.f,1.f))*.5f;
    gl_Position = vec4(vert, 1.f);
}
"""

class ImageHandler:
    """
    Class that manages the image stream to render with OpenGL
    """
    def __init__(self):
        self.tex_id = 0
        self.image_tex = 0
        self.quad_vb = 0
        self.is_called = 0

    def close(self):
        if self.image_tex:
            self.image_tex = 0

    def initialize(self, _res):
        self.shader_image = Shader(IMAGE_VERTEX_SHADER, IMAGE_FRAGMENT_SHADER)
        self.tex_id = glGetUniformLocation( self.shader_image.get_program_id(), "texImage")

        g_quad_vertex_buffer_data = np.array([-1, -1, 0,
                                                1, -1, 0,
                                                -1, 1, 0,
                                                -1, 1, 0,
                                                1, -1, 0,
                                                1, 1, 0], np.float32)

        self.quad_vb = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.quad_vb)
        glBufferData(GL_ARRAY_BUFFER, g_quad_vertex_buffer_data.nbytes,
                     g_quad_vertex_buffer_data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Create and populate the texture
        glEnable(GL_TEXTURE_2D)

        # Generate a texture name
        self.image_tex = glGenTextures(1)

        # Select the created texture
        glBindTexture(GL_TEXTURE_2D, self.image_tex)

        # Set the texture minification and magnification filters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Fill the texture with an image
        # None means reserve texture memory, but texels are undefined
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, _res.width, _res.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        # Unbind the texture
        glBindTexture(GL_TEXTURE_2D, 0)

    def push_new_image(self, _zed_mat):
        glBindTexture(GL_TEXTURE_2D, self.image_tex)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, _zed_mat.get_width(), _zed_mat.get_height(), GL_RGBA, GL_UNSIGNED_BYTE,  ctypes.c_void_p(_zed_mat.get_pointer()))
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw(self):
        glUseProgram(self.shader_image.get_program_id())
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.image_tex)
        glUniform1i(self.tex_id, 0)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.quad_vb)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glDisableVertexAttribArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

class Viewer3d:
    """
    Class that manages input events, window and OpenGL rendering pipeline
    """
    def __init__(self):
        self.available = False
        self.bodies = []
        self.mutex = Lock()
        # Create the rendering camera
        self.projection = array.array('f')
        self.basic_sphere = Simple3DObject(True)
        # Show tracked objects only
        self.body_format = 25

    def init(self):
        glutInit()
        wnd_w = glutGet(GLUT_SCREEN_WIDTH)
        wnd_h = glutGet(GLUT_SCREEN_HEIGHT)
        width = (int)(wnd_w*0.7)
        height = (int)(wnd_h*0.7)

        glutInitWindowSize(width, height)
        glutInitWindowPosition((int)(wnd_w*0.05), (int)(wnd_h*0.05)) # The window opens at the upper left corner of the screen
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_SRGB)
        glutCreateWindow("ZED Body Tracking")
        glViewport(0, 0, width, height)

        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE,
                      GLUT_ACTION_CONTINUE_EXECUTION)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glDisable(GL_DEPTH_TEST)

        glEnable(GL_FRAMEBUFFER_SRGB)

        # Compile and create the shader for 3D objects
        self.shader_sk_image = Shader(SK_VERTEX_SHADER, SK_FRAGMENT_SHADER)
        self.shader_sk_MVP = glGetUniformLocation(self.shader_sk_image.get_program_id(), "u_mvpMatrix")
        self.shader_sk_clr = glGetUniformLocation(self.shader_sk_image.get_program_id(), "u_color")

        self.shader_sphere_image = Shader(SK_SPHERE_SHADER, SK_FRAGMENT_SHADER)
        self.shader_sphere_MVP = glGetUniformLocation(self.shader_sphere_image.get_program_id(), "u_mvpMatrix")
        self.shader_sphere_clr = glGetUniformLocation(self.shader_sphere_image.get_program_id(), "u_color")
        self.shader_sphere_pt = glGetUniformLocation(self.shader_sphere_image.get_program_id(), "u_pt")

        self.set_render_camera_projection(0.1, 200)

        self.floor_plane_set = False

        self.basic_sphere.add_sphere()
        self.basic_sphere.set_drawing_type(GL_QUADS)
        self.basic_sphere.push_to_GPU()

        # Register the drawing function with GLUT
        glutDisplayFunc(self.draw_callback)
        # Register the function called when nothing happens
        glutIdleFunc(self.idle)

        glutKeyboardFunc(self.keyPressedCallback)
        # Register the closing function
        glutCloseFunc(self.close_func)

        self.available = True
        self.body_format = 25

    def set_floor_plane_equation(self, _eq):
        self.floor_plane_set = True
        self.floor_plane_eq = _eq

    def set_render_camera_projection(self, _znear, _zfar):
        # Just slightly move up the ZED camera FOV to make a small black border

        # fov_y :  0.9466695954842801
        # fov_x :  1.4751958758738115
        # image_size.width :  1920
        # image_size.height:  1080
        # cx :  939.536376953125
        # cy :  546.5872802734375
        # _znear :  0.1
        # _zfar :  200
        # self.Z:  0.6196141839027405

        v_fov = 53.7725
        h_fov = 84.0623
        cx = 939.536376953125
        cy = 546.5872802734375
        width = 1920
        height = 1080

        fov_y = (v_fov + 0.5) * M_PI / 180
        fov_x = (h_fov + 0.5) * M_PI / 180

        self.projection.append( 1 / math.tan(fov_x * 0.5) )  # Horizontal FoV.
        self.projection.append( 0)
        # Horizontal offset.
        self.projection.append( 2 * ((width - cx) / width) - 1)
        self.projection.append( 0)

        self.projection.append( 0)
        self.projection.append( 1 / math.tan(fov_y * 0.5))  # Vertical FoV.
        # Vertical offset.
        self.projection.append(-(2 * ((height - cy) / height) - 1))
        self.projection.append( 0)

        self.projection.append( 0)
        self.projection.append( 0)
        # Near and far planes.
        self.projection.append( -(_zfar + _znear) / (_zfar - _znear))
        # Near and far planes.
        self.projection.append( -(2 * _zfar * _znear) / (_zfar - _znear))

        self.projection.append( 0)
        self.projection.append( 0)
        self.projection.append( -1)
        self.projection.append( 0)

    def is_available(self):
        if self.available:
            glutMainLoopEvent()
        return self.available

    # Modified function
    def render_3d(self, _skeleton_3d):
        self.mutex.acquire()
        now = datetime.now()

        # Clear objects
        self.bodies.clear()
        # Only show tracked objects
        for person in _skeleton_3d:
            person_id = person['id']
            skeleton = person['keypoints3d']
            current_sk = Skeleton(25)
            current_sk.set_skeleton(person_id, skeleton)
            self.bodies.append(current_sk)
        later = datetime.now()
        print(later-now)

        self.mutex.release()

    def idle(self):
        if self.available:
            glutPostRedisplay()

    def exit(self):
        if self.available:
            self.available = False

    def close_func(self):
        if self.available:
            self.available = False

    def keyPressedCallback(self, key, x, y):
        if ord(key) == 113 or ord(key) == 27:
            self.close_func()

    def draw_callback(self):
        if self.available:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.mutex.acquire()
            self.update()
            self.draw()
            self.mutex.release()

            glutSwapBuffers()
            glutPostRedisplay()

    def update(self):
        for body in self.bodies:
            body.push_to_GPU()

    def draw(self):
        glUseProgram(self.shader_sk_image.get_program_id())
        glUniformMatrix4fv(self.shader_sk_MVP, 1, GL_TRUE,  (GLfloat * len(self.projection))(*self.projection))
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        for body in self.bodies:
            body.draw(self.shader_sphere_clr, self.basic_sphere, self.shader_sphere_MVP, self.projection)
        glUseProgram(0)

        glUseProgram(self.shader_sphere_image.get_program_id())
        glUniformMatrix4fv(self.shader_sphere_MVP, 1, GL_TRUE,  (GLfloat * len(self.projection))(*self.projection))
        for body in self.bodies:
            body.drawKPS(self.shader_sphere_clr, self.basic_sphere, self.shader_sphere_pt)

        glUseProgram(0)

