# Daniele Sterle SM3201594

import json

class PaletteException(Exception):
    pass

class Palette():

    def __init__(self, json_path):
        raw_data = self.__load(json_path)
        self.palette = self.__validate(raw_data)

    def __load(self, palette_json):
        """Loads the raw JSON data from the palette file."""
        try:
            with open(palette_json, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise PaletteException(f"Failed to read palette JSON file: {e}")

    def __validate(self, data):
        """Validates the palette data structure and its color constraints."""
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