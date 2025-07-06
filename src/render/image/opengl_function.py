import OpenGL.GL as GL
from PIL import Image
import numpy as np


def compile_shader(shader_src: str, shader_type) -> int:
    """
    Compile a single shader (vertex or fragment).
    :param shader_src: GLSL shader source code.
    :param shader_type: GL.GL_VERTEX_SHADER or GL.GL_FRAGMENT_SHADER.
    :return: Shader ID.
    """
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, shader_src)
    GL.glCompileShader(shader)

    status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not status:
        msg = GL.glGetShaderInfoLog(shader)
        raise RuntimeError(f"Shader compilation failed: {msg}")

    return shader


def create_program(vertex_src: str, fragment_src: str) -> int:
    """
    Create and link a shader program from vertex and fragment shaders.
    :param vertex_src: Vertex shader GLSL source.
    :param fragment_src: Fragment shader GLSL source.
    :return: Program ID.
    """
    vertex_shader = compile_shader(vertex_src, GL.GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_src, GL.GL_FRAGMENT_SHADER)

    program = GL.glCreateProgram()
    GL.glAttachShader(program, vertex_shader)
    GL.glAttachShader(program, fragment_shader)
    GL.glLinkProgram(program)

    status = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not status:
        msg = GL.glGetProgramInfoLog(program)
        raise RuntimeError(f"Program linking failed: {msg}")

    return program


def create_vao(v_pos: np.ndarray, uv_coord: np.ndarray) -> int:
    """
    Create a Vertex Array Object (VAO) with position and UV buffers.
    :param v_pos: Vertex positions as numpy float32 array.
    :param uv_coord: UV coordinates as numpy float32 array.
    :return: VAO ID.
    """
    vao = GL.glGenVertexArrays(1)
    vbo = GL.glGenBuffers(1)
    uvbo = GL.glGenBuffers(1)

    GL.glBindVertexArray(vao)

    # Upload vertex positions
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, v_pos.nbytes, v_pos, GL.GL_DYNAMIC_DRAW)
    GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 0, None)
    GL.glEnableVertexAttribArray(0)

    # Upload UV coordinates
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, uvbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, uv_coord.nbytes, uv_coord, GL.GL_STATIC_DRAW)
    GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, 0, None)
    GL.glEnableVertexAttribArray(1)

    # Cleanup
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    GL.glBindVertexArray(0)

    return vao


def create_texture(imagePath: str) -> int:
    """
    Load an image file into an OpenGL texture.
    :param imagePath: Path to image file.
    :return: Texture ID.
    """
    image = Image.open(imagePath)
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image_data = image.tobytes()
    width, height = image.size

    GL.glEnable(GL.GL_TEXTURE_2D)
    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,
        0,
        GL.GL_RGBA,
        width,
        height,
        0,
        GL.GL_RGBA,
        GL.GL_UNSIGNED_BYTE,
        image_data,
    )

    GL.glTexParameteri(
        GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_NEAREST
    )
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    return texture


def create_canvas_framebuffer(width: int, height: int) -> tuple[int, int]:
    """
    Create a framebuffer object (FBO) with attached texture.
    :param width: Framebuffer width.
    :param height: Framebuffer height.
    :return: Tuple of (FBO ID, texture ID).
    """
    old_fbo = GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING)

    fbo = GL.glGenFramebuffers(1)
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)

    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,
        0,
        GL.GL_RGBA,
        width,
        height,
        0,
        GL.GL_RGBA,
        GL.GL_UNSIGNED_BYTE,
        None,
    )
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

    GL.glFramebufferTexture2D(
        GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, texture, 0
    )

    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, old_fbo)
    return fbo, texture
