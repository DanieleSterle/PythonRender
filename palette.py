# Daniele Sterle SM3201594

import json

class PaletteException(Exception):
    pass

class Palette():

    def __init__(self, json_path):
        self.palette = self._load_and_validate(json_path)

    def _load_and_validate(self, palette_json):
        try:
            with open(palette_json, "r", encoding = "utf-8") as file:
                data = json.load(file)
        except Exception as e:
            raise PaletteException(f"Failed to read palette JSON file: {e}")

        # The palette must be a list containing exactly 16 colors
        if not isinstance(data, list) or len(data) != 16:
            raise PaletteException("Palette must contain exactly 16 colors.")

        validated_palette = []

        for color in data:
            # Each color must be a list or tuple of 3 integers between 0 and 255
            if not isinstance(color, (list, tuple)) or len(color) != 3:
                raise PaletteException("Each color must be an RGB triplet [R, G, B].")
            
            if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise PaletteException("RGB values must be integers between 0 and 255.")
            
            validated_palette.append(list(color))

        return validated_palette

    def get_color(self, index):
        """Resolves an index (0-15) into its corresponding RGB value."""
        if not isinstance(index, int) or not (0 <= index < len(self.palette)):
            raise PaletteException(f"Invalid palette index: {index}. Must be between 0 and 15.")
        return self.palette[index]