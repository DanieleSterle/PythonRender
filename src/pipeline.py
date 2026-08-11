# Daniele Sterle SM3201594

import numpy as np
from PIL import Image

# Eccezione personalizzata per errori nella pipeline di rendering.
class RenderingPipelineException(Exception):
    pass

class RenderingPipeline:
    def __init__(self, palette, vram, blitter):
        self.palette = palette
        self.vram = vram
        self.blitter = blitter

    # Esegue la composizione completa della scena, converte il frame buffer 
    # indicizzato in RGB e salva il risultato finale come immagine PNG.
    def render_scene(self, scene_data, output_path):

        try:
            # Crea il frame buffer vuoto (risoluzione predefinita 640x480)
            frame_buffer = self.blitter.create_frame_buffer()

            # Disegna per prima la mappa dei tile di sfondo sul frame buffer
            self.blitter.draw_tile_map(
                frame_buffer, 
                scene_data["tile_map"], 
                self.vram.tiles
            )

            # Disegna gli sprite nell'ordine in cui compaiono nel file JSON
            self.blitter.draw_sprites(
                frame_buffer, 
                scene_data["sprites"], 
                self.vram.sprites, 
                scene_data["transparent_index"]
            )

            # Converte il frame buffer indicizzato in un'immagine RGB usando la palette
            rgb_image_data = self.__convert_to_rgb(frame_buffer)

            # Salva il risultato finale su file come immagine PNG tramite la libreria Pillow
            image = Image.fromarray(rgb_image_data, mode = "RGB")
            image.save(output_path, format = "PNG")

        except Exception as e:
            raise RenderingPipelineException(f"Failed to render scene: {e}")

    # Mappa ogni indice di pixel nel frame buffer alla corrispondente tripla RGB.
    def __convert_to_rgb(self, frame_buffer):
        height, width = frame_buffer.shape
        rgb_image = np.zeros((height, width, 3), dtype = np.uint8)

        # Estrae l'array dei colori della palette e lo converte in array NumPy uint8
        palette_array = np.array(self.palette.palette, dtype = np.uint8)
        
        # Converte ogni numero del frame buffer nel colore RGB corrispondente usando la palette
        rgb_image = palette_array[frame_buffer]

        return rgb_image