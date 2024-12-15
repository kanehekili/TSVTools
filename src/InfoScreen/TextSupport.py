from PIL import Image, ImageDraw, ImageFont
from ctypes import c_float
import OpenGL

class Laufband():
    def __init__(self,glObject,shader):
        self.openGL = glObject
        self.shader=shader

    #def create_text_texture(self,text, font_path="arial.ttf", font_size=32):
    def create_text_texture(self,text, font, font_size=32):        
        # Create an image with Pillow
        image = self._create_text_image(text, font,font_size)
        
        # Pass the image to make_texture
        texture_id = self.openGL.make_texture(img=image)
        
        return texture_id


    #def _create_text_image(self,text, font_path="arial.ttf", font_size=32, text_color=(255, 255, 255)):
    def _create_text_image(self,text, font, font_size=32,text_color=(255, 255, 255)):  
        #font=ImageFont.truetype("arial.ttf", font_size, encoding='unic')      
        #font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(text)
        self.text_width = bbox[2] - bbox[0]  # Width of the text
        self.text_height = bbox[3] - bbox[1]  # Height of the text
        image = Image.new("RGBA", (self.text_width, self.text_height), (255, 0, 0, 1))  # Red background
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=font, fill=text_color)
        return image

    
    ##render section
    
    #way to render that stuff existing_object == self.openGL
    def render_text_at_bottom(self,texture_id, screen_width, screen_height, texture_width, texture_height):
        #makes screen yellow for testing
        #self.openGL.ClearColor(1.0, 1.0, 0.0, 1.0)  # Set background to yellow for testing
        #self.openGL.Clear(self.openGL.COLOR_BUFFER_BIT)
        # Step 1: Set up orthographic projection (2D rendering)
        projection_matrix = self.create_ortho_projection(0, screen_width, screen_height, 0, -1, 1)

        # Activate the text shader
        self.shader.use()
        
        # Pass the projection matrix to your shader
        projection_matrix_ctypes = (c_float * len(projection_matrix))(*projection_matrix)
        self.openGL.UniformMatrix4fv(self.shader.projection_location, 1, 0, projection_matrix_ctypes)

        error = self.openGL.GetError()
        if error != self.openGL.NO_ERROR:
            print(f"OpenGL Error1: {error}")         
        
        # Bind the texture
        self.openGL.ActiveTexture(self.openGL.TEXTURE0)  # Activate texture unit 0
        self.openGL.BindTexture(self.openGL.TEXTURE_2D, texture_id)
        self.openGL.Uniform1i(self.shader.tex_location, 0)  # Set the texture sampler
        
        error = self.openGL.GetError()
        if error != self.openGL.NO_ERROR:
            print(f"OpenGL Error2: {error}")
        
        # Step 2: Bind the texture
        self.openGL.set_texture(tex=texture_id)
        #def set_texture(self, target=TEXTURE_2D, tex=0, tmu=0):
        
        # Step 3: Render the quad at the bottom of the screen
        x = (screen_width - texture_width) / 2  # Center horizontally
        y = screen_height - texture_height  # Position at the bottom
        
        self._render_quad(x, y, texture_width, texture_height)
        error = self.openGL.GetError()
        if error != self.openGL.NO_ERROR:
            print(f"OpenGL Error3: {error}")   

    def _render_quad(self,x, y, width, height):
        vertices = [
            x, y, 0.0,        # Bottom-left corner
            x + width, y, 0.0,  # Bottom-right corner
            x, y + height, 0.0,  # Top-left corner
            x + width, y + height, 0.0  # Top-right corner
        ]

        print(f"Rendering quad at ({x}, {y}) with width {width} and height {height}")

        
        tex_coords = [
            0.0, 1.0,  # Bottom-left corner
            1.0, 1.0,  # Bottom-right corner
            0.0, 0.0,  # Top-left corner
            1.0, 0.0   # Top-right corner
        ]
        
        # Convert to ctypes arrays
        vertex_data = (c_float * len(vertices))(*vertices)
        tex_coord_data = (c_float * len(tex_coords))(*tex_coords)
        
        # Enable vertex and texture coordinate arrays
        self.openGL.EnableVertexAttribArray(0)
        self.openGL.VertexAttribPointer(0, 3, self.openGL.FLOAT, False, 0, vertex_data)
        
        self.openGL.EnableVertexAttribArray(1)
        self.openGL.VertexAttribPointer(1, 2, self.openGL.FLOAT, False, 0, tex_coord_data)
        
        # Draw the quad
        self.openGL.DrawArrays(self.openGL.TRIANGLE_STRIP, 0, 4)
        
        # Disable vertex and texture coordinate arrays
        self.openGL.DisableVertexAttribArray(0)
        self.openGL.DisableVertexAttribArray(1)
    

    def create_ortho_projection(self,left, right, bottom, top, near, far):
        # Manually create a 4x4 orthographic projection matrix
        ortho_matrix = [
            [2.0 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2.0 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2.0 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ]
        # Flatten the matrix into a single list (OpenGL expects matrices as a flat array)
        return [item for sublist in ortho_matrix for item in sublist]
    '''
    def _setup_ortho_viewport(self, screen_width, screen_height):
        # Set up orthographic projection (no perspective)
        self.openGL.Viewport(0, 0, screen_width, screen_height)
        self.openGL.MatrixMode(self.openGL.PROJECTION)
        self.openGL.LoadIdentity()
        # Define an orthographic projection with screen dimensions
        self.openGL.Ortho(0, screen_width, screen_height, 0, -1, 1)
        self.openGL.MatrixMode(self.openGL.MODELVIEW)
        self.openGL.LoadIdentity()
    '''
    
    def render_text_image(self, texture_id, screen_width, screen_height, texture_width, texture_height):
        self._setup_ortho_viewport(screen_width, screen_height)
        
        # Bind the texture
        self.openGL.set_texture(tex=texture_id)
        
        # Render the quad
        x = (screen_width - texture_width) / 2  # Center horizontally
        y = screen_height - texture_height  # Position at the bottom
        
        print(f"Texture Width: {texture_width}, Height: {texture_height}")
        print(f"Texture ID: {texture_id}")
        
        self._render_quad(x, y, texture_width, texture_height)
    
    
'''
def bind_texture(existing_object, texture_id):
    existing_object.ActiveTexture(existing_object.TEXTURE0)
    existing_object.BindTexture(existing_object.TEXTURE_2D, texture_id)  
'''
      