# Daniele Sterle SM3201594

import json

# Eccezione personalizzata per errori di caricamento e validazione della palette.
class PaletteException(Exception):
    pass

class Palette():

    # Carica i dati grezzi dal file JSON e li valida successivamente.
    def __init__(self, json_path):
        raw_data = self.__load(json_path)
        self.palette = self.__validate(raw_data)

    # Carica i dati JSON grezzi dal file della palette.
    def __load(self, palette_json):
        try:
            with open(palette_json, "r", encoding = "utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise PaletteException(f"Failed to read palette JSON file: {e}")

    # Valida la struttura dei dati della palette e i vincoli dei colori.
    def __validate(self, data):
        # La palette deve essere una lista contenente esattamente 16 colori
        if not isinstance(data, list) or len(data) != 16:
            raise PaletteException("Palette must contain exactly 16 colors.")

        validated_palette = []

        for color in data:
            # Ogni colore deve essere una lista o tupla di 3 interi compresi tra 0 e 255
            if not isinstance(color, (list, tuple)) or len(color) != 3:
                raise PaletteException("Each color must be an RGB triplet [R, G, B].")
            
            if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise PaletteException("RGB values must be integers between 0 and 255.")
            
            validated_palette.append(list(color))

        return validated_palette