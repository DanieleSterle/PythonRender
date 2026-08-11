# Daniele Sterle SM3201594

import numpy as np
from PIL import Image

class RenderingPipelineException(Exception):
    """Custom exception for rendering pipeline errors."""
    pass

class RenderingPipeline:
    def __init__(self, palette, vram, blitter):
        self.palette = palette
        self.vram = vram
        self.blitter = blitter

    def render_scene(self, scene_data, output_path):
        """
        Executes the complete scene composition, converts the indexed frame 
        buffer to RGB, and saves the final result as a PNG image.
        """
        try:
            # 1. Create the frame buffer (640x480)
            frame_buffer = self.blitter.create_frame_buffer()

            # 2. Draw the background tile map first
            self.blitter.draw_tile_map(
                frame_buffer, 
                scene_data["tile_map"], 
                self.vram.tiles
            )

            # 3. Draw the sprites in the order they appear in the JSON
            self.blitter.draw_sprites(
                frame_buffer, 
                scene_data["sprites"], 
                self.vram.sprites, 
                scene_data["transparent_index"]
            )

            # 4. Convert the indexed frame buffer into an RGB image using the palette
            rgb_image_data = self.__convert_to_rgb(frame_buffer)

            # 5. Save the final result as a PNG image using Pillow
            image = Image.fromarray(rgb_image_data, mode="RGB")
            image.save(output_path, format="PNG")

        except Exception as e:
            raise RenderingPipelineException(f"Failed to render scene: {e}")

    def __convert_to_rgb(self, frame_buffer):
        """Maps each pixel index in the frame buffer to its corresponding RGB triplet."""
        height, width = frame_buffer.shape
        rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

        # Map each palette index to its RGB color from the palette list
        palette_array = np.array(self.palette.palette, dtype=np.uint8)
        
        # Vectorized mapping using numpy advanced indexing
        rgb_image = palette_array[frame_buffer]

        return rgb_image