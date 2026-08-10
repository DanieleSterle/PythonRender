# Daniele Sterle SM3201594

import json
import numpy as np

class BlitterException(Exception):
    pass

class Blitter():

    def __init__(self, frame_buffer_shape=(480, 640)):
        # Initialize an empty frame buffer (height x width) with uint8
        self.frame_buffer_shape = frame_buffer_shape

    def create_frame_buffer(self):
        """Creates a blank frame buffer filled with zeros."""
        return np.zeros(self.frame_buffer_shape, dtype=np.uint8)

    def draw_tile_map(self, frame_buffer, tile_map, tiles_vram):
        """
        Draws the entire 20x15 tile map onto the frame buffer.
        Each tile is 32x32 pixels.
        """
        for row_idx, row in enumerate(tile_map):
            for col_idx, tile_id in enumerate(row):
                # Calculate screen coordinates for the tile
                y_start = row_idx * 32
                x_start = col_idx * 32
                
                # Get the tile pixels from VRAM
                tile_pixels = tiles_vram[tile_id]
                
                # Copy tile pixels directly into the frame buffer
                frame_buffer[y_start:y_start+32, x_start:x_start+32] = tile_pixels

    def draw_sprites(self, frame_buffer, sprites_list, sprites_vram, transparent_index):
        """
        Draws all sprites onto the frame buffer respecting order, 
        transformations, transparency, and screen clipping.
        """
        for sprite_data in sprites_list:
            # 1. Validate sprite properties
            self._validate_sprite(sprite_data)
            
            sprite_id = sprite_data["id"]
            x_pos = sprite_data["x"]
            y_pos = sprite_data["y"]
            flip_h = sprite_data["flip_h"]
            flip_v = sprite_data["flip_v"]
            rotation = sprite_data["rotation"]
            
            # Get raw sprite pixels (64x64) from VRAM
            sprite_pixels = sprites_vram[sprite_id].copy()
            
            # 2. Apply transformations (flips and rotations)
            transformed_sprite = self._apply_transformations(sprite_pixels, flip_h, flip_v, rotation)
            
            # 3. Blit onto frame buffer with transparency and clipping
            self._blit_sprite_to_buffer(frame_buffer, transformed_sprite, x_pos, y_pos, transparent_index)

    def _validate_sprite(self, sprite):
        """Validates individual sprite attributes."""
        required_keys = {"id", "x", "y", "flip_h", "flip_v", "rotation"}
        if not all(k in sprite for k in required_keys):
            raise BlitterException("Sprite missing one or more required fields.")
        
        if sprite["rotation"] not in {0, 90, 180, 270}:
            raise BlitterException(f"Invalid rotation value: {sprite['rotation']}. Must be 0, 90, 180, or 270.")

    def _apply_transformations(self, sprite_img, flip_h, flip_v, rotation):
        """Applies horizontal/vertical flips and 90-degree increments of rotation."""
        # Horizontal flip
        if flip_h:
            sprite_img = np.fliplr(sprite_img)
            
        # Vertical flip
        if flip_v:
            sprite_img = np.flipud(sprite_img)
            
        # Rotation (0, 90, 180, 270 degrees)
        if rotation == 90:
            sprite_img = np.rot90(sprite_img, k=3)  # Counter-clockwise 90 is clockwise 270, or k=1 depending on convention
        elif rotation == 180:
            sprite_img = np.rot90(sprite_img, k=2)
        elif rotation == 270:
            sprite_img = np.rot90(sprite_img, k=1)
            
        return sprite_img

    def _blit_sprite_to_buffer(self, frame_buffer, sprite_img, x, y, transparent_index):
        """Copies sprite pixels to frame buffer handling transparency and out-of-bounds clipping."""
        fh, fw = frame_buffer.shape
        sh, sw = sprite_img.shape
        
        # Calculate destination bounds on screen
        x1, y1 = x, y
        x2, y2 = x + sw, y + sh
        
        # Clip if sprite is partially or fully outside the screen bounds
        if x1 >= fw or y1 >= fh or x2 <= 0 or y2 <= 0:
            return  # Completely outside
            
        # Source sprite clip offsets
        sx1 = max(0, -x1)
        sy1 = max(0, -y1)
        sx2 = sw - max(0, x2 - fw)
        sy2 = sh - max(0, y2 - fh)
        
        # Destination frame buffer clip offsets
        dx1 = max(0, x1)
        dy1 = max(0, y1)
        dx2 = min(fw, x2)
        dy2 = min(fh, y2)
        
        # Extract slices
        target_area = frame_buffer[dy1:dy2, dx1:dx2]
        source_area = sprite_img[sy1:sy2, sx1:sx2]
        
        # Apply transparency: only copy pixels that do NOT match the transparent index
        mask = (source_area != transparent_index)
        target_area[mask] = source_area[mask]