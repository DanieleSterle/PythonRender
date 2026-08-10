# Daniele Sterle SM3201594

import numpy as np

class VirtualVRAMException(Exception):
    pass

class VirtualVRAM():
    def __init__(self, tiles_path, sprites_path):
        self.tiles = self._load_and_decode_sheet(tiles_path, 256, 32, 8, 8)
        self.sprites = self._load_and_decode_sheet(sprites_path, 256, 64, 4, 4)

    # separare funzioni?
    def _load_and_decode_sheet(self, filepath, sheet_size, item_size, grid_rows, grid_cols):
        
        try:
            with open(filepath, "rb") as file:
                raw_data = file.read()
        except Exception as e:
            raise VirtualVRAMException(f"Failed to read binary file {filepath}: {e}")

        expected_bytes = (sheet_size * sheet_size) // 2  # 32768 bytes

        if len(raw_data) != expected_bytes:
            raise VirtualVRAMException(f"Invalid file size for {filepath}. Expected {expected_bytes} bytes.")

        # Convert raw bytes to a numpy array of uint8
        byte_array = np.frombuffer(raw_data, dtype = np.uint8)

        # Unpack nibbles: each byte contains 2 pixels (high nibble and low nibble)
        # Notation: 0000 actual_bit (eg. 0000 0100) 
        # NOTE: byte_array remains unshifted
        # NOTE: with >> the 4 initially left-most bit get dropped
        # NOTE: working on the whole array
        high_nibble = byte_array >> 4

        # 0x0F is a mask: 0000 1111
        # with & (bit-wise and) and a mask i can extract the bits I want
        # NOTE: working on the whole array
        low_nibble = byte_array & 0x0F

        # Interleave high and low nibbles to restore the full pixel array
        # idea: re-ordering array
        pixels = np.empty(sheet_size * sheet_size, dtype = np.uint8)
        # start = 0, end = None (end of list), step = 2
        pixels[0::2] = high_nibble
        # start = 1, end = None (end of list), step = 2
        pixels[1::2] = low_nibble

        # Reshape into a 2D sheet (sheet_size x sheet_size)
        sheet_2d = pixels.reshape((sheet_size, sheet_size))

        # Split the sheet into individual items arranged in a grid
        items = []
        for r in range(grid_rows):
            for c in range(grid_cols):
                # calculate y coordinates (start,end)
                y1 = r * item_size
                y2 = y1 + item_size

                # calculate x coordinates (start,end)
                x1 = c * item_size
                x2 = x1 + item_size

                # extract the item (tile / sheet)
                item = sheet_2d[y1:y2, x1:x2]
                items.append(item)

        # return all item
        return np.array(items, dtype = np.uint8)