# Daniele Sterle SM3201594

import numpy as np

# Eccezione personalizzata per errori di disegno e trasformazione nel blitter.
class BlitterException(Exception):
    pass

class Blitter():

    # Inizializza la forma del frame buffer vuoto (altezza x larghezza) con interi a 8 bit
    def __init__(self, frame_buffer_shape = (480, 640)):
        self.frame_buffer_shape = frame_buffer_shape

    # Crea un frame buffer vuoto riempito di zeri.
    def create_frame_buffer(self):
        return np.zeros(self.frame_buffer_shape, dtype = np.uint8)

    # Disegna l'intera mappa dei tile 20x15 sul frame buffer.
    def draw_tile_map(self, frame_buffer, tile_map, tiles_vram):

        for row_idx, row in enumerate(tile_map):
            for col_idx, tile_id in enumerate(row):
                # Calcola le coordinate sullo schermo per il tile corrente
                y_start = row_idx * 32
                x_start = col_idx * 32
                
                # Ottiene i pixel del tile dalla VRAM
                tile_pixels = tiles_vram[tile_id]
                
                # Copia direttamente i pixel del tile nel frame buffer
                frame_buffer[y_start:y_start+32, x_start:x_start+32] = tile_pixels

    # Disegna tutti gli sprite sul frame buffer rispettando l'ordine di disegno, 
    # le trasformazioni, la trasparenza e il clipping dello schermo.
    def draw_sprites(self, frame_buffer, sprites_list, sprites_vram, transparent_index):

        for sprite_data in sprites_list:
            # Valida le proprietà del singolo sprite
            self.__validate_sprite(sprite_data)
            
            sprite_id = sprite_data["id"]
            x_pos = sprite_data["x"]
            y_pos = sprite_data["y"]
            flip_h = sprite_data["flip_h"]
            flip_v = sprite_data["flip_v"]
            rotation = sprite_data["rotation"]
            
            # Ottiene i pixel grezzi dello sprite (64x64) dalla VRAM
            sprite_pixels = sprites_vram[sprite_id].copy()
            
            # Applica le trasformazioni (specchiature e rotazioni)
            transformed_sprite = self.__apply_transformations(sprite_pixels, flip_h, flip_v, rotation)
            
            # Disegna (blit) sul frame buffer gestendo trasparenza e clipping
            self.__blit_sprite_to_buffer(frame_buffer, transformed_sprite, x_pos, y_pos, transparent_index)

    # Valida gli attributi del singolo sprite.
    def __validate_sprite(self, sprite):
        required_keys = {"id", "x", "y", "flip_h", "flip_v", "rotation"}
        if not all(k in sprite for k in required_keys):
            raise BlitterException("Sprite missing one or more required fields.")
        
        if sprite["rotation"] not in {0, 90, 180, 270}:
            raise BlitterException(f"Invalid rotation value: {sprite['rotation']}. Must be 0, 90, 180, or 270.")

    # Applica le specchiature orizzontali/verticali e le rotazioni con incrementi di 90 gradi.
    def __apply_transformations(self, sprite_img, flip_h, flip_v, rotation):
        # Specchiatura orizzontale
        # np.fliplr ribalta l'array orizzontalmente (da sinistra a destra) lungo l'asse 1
        if flip_h:
            sprite_img = np.fliplr(sprite_img)
            
        # Specchiatura verticale
        # np.flipud ribalta l'array verticalmente (dall'alto in basso) lungo l'asse 0
        if flip_v:
            sprite_img = np.flipud(sprite_img)
            
        # Rotazione (0, 90, 180, 270 gradi)
        if rotation == 90:
            sprite_img = np.rot90(sprite_img, k = 3)
        elif rotation == 180:
            sprite_img = np.rot90(sprite_img, k = 2)
        elif rotation == 270:
            sprite_img = np.rot90(sprite_img, k = 1)
            
        return sprite_img

    # Copia i pixel dello sprite nel frame buffer gestendo la trasparenza e il taglio (clipping) fuori dallo schermo.
    def __blit_sprite_to_buffer(self, frame_buffer, sprite_img, x, y, transparent_index):
        fh, fw = frame_buffer.shape
        sh, sw = sprite_img.shape
        
        # Calcola i confini di destinazione sullo schermo
        x1, y1 = x, y
        x2, y2 = x + sw, y + sh
        
        # Esegue il clipping se lo sprite si trova parzialmente o totalmente fuori dai bordi dello schermo
        if x1 >= fw or y1 >= fh or x2 <= 0 or y2 <= 0:
            return  # Completamente fuori dallo schermo
            
        # Calcola i margini da ritagliare sull'immagine dello sprite originale 
        # nel caso in cui esso esca dai bordi superiori o sinistri dello schermo (coordinate negative).
        sx1 = max(0, -x1)
        sy1 = max(0, -y1)
        # Calcola i margini da ritagliare se lo sprite esce dai bordi inferiori o destri dello schermo.
        sx2 = sw - max(0, x2 - fw)
        sy2 = sh - max(0, y2 - fh)
        
        # Calcola le coordinate di inizio sul frame buffer di destinazione, 
        # bloccandole a 0 se lo sprite inizia fuori dallo schermo a sinistra o in alto.
        dx1 = max(0, x1)
        dy1 = max(0, y1)
        # Calcola le coordinate di fine sul frame buffer di destinazione, 
        # bloccandole alla larghezza/altezza massima dello schermo per evitare sforamenti.
        dx2 = min(fw, x2)
        dy2 = min(fh, y2)
        
        # Estrae le porzioni (slices) corrispondenti
        target_area = frame_buffer[dy1:dy2, dx1:dx2]
        source_area = sprite_img[sy1:sy2, sx1:sx2]
        
        # Applica il filtro di trasparenza: copia sullo schermo solo i pixel visibili dello sprite.
        mask = (source_area != transparent_index)
        target_area[mask] = source_area[mask]