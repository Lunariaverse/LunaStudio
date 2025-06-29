from .opengl_function import create_vao, create_program, create_texture
import OpenGL.GL as GL
import numpy as np


class Image:
    """
    Simple textured quad renderer using OpenGL.
    Loads an image as a texture and draws it fullscreen.
    """

    def __init__(self, imagePath: str):
        """
        Initialize the OpenGL program, VAO and texture.
        :param imagePath: Path to the image file to load.
        """
        # Vertex shader: passes through position and texture coordinates
        vertex_shader = """
        #version 330 core
        layout(location = 0) in vec2 a_position;
        layout(location = 1) in vec2 a_texCoord;
        out vec2 v_texCoord;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
            v_texCoord = a_texCoord;
        }
        """

        # Fragment shader: samples from texture
        frag_shader = """
        #version 330 core
        in vec2 v_texCoord;
        uniform sampler2D tex;
        uniform float opacity;  // unused for now
        void main() {
            gl_FragColor = texture(tex, v_texCoord);
        }
        """

        # Compile shader program and create texture
        self.program = create_program(vertex_shader, frag_shader)
        self.texture = create_texture(imagePath)

        # Vertex positions (two triangles forming a rectangle)
        vertices = np.array(
            [
                -1,
                1,  # top-left
                -1,
                -1,  # bottom-left
                1,
                -1,  # bottom-right
                -1,
                1,  # top-left
                1,
                -1,  # bottom-right
                1,
                1,  # top-right
            ],
            dtype=np.float32,
        )

        # Texture coordinates (matching the vertices)
        uvs = np.array(
            [
                0,
                1,  # top-left
                0,
                0,  # bottom-left
                1,
                0,  # bottom-right
                0,
                1,  # top-left
                1,
                0,  # bottom-right
                1,
                1,  # top-right
            ],
            dtype=np.float32,
        )

        # Create vertex array object
        self.vao = create_vao(vertices, uvs)

    def Draw(self) -> None:
        """
        Draw the textured quad to the screen.
        """
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.program)

        # Bind texture unit 0
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        # Draw 6 vertices as 2 triangles
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        # Unbind
        GL.glBindVertexArray(0)
