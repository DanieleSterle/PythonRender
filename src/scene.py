# Daniele Sterle SM3201594

import json

# Eccezione personalizzata per errori di parsing e validazione della scena.
class SceneParserException(Exception):
    pass

class SceneParser:
    # Carica i dati grezzi dal file della scena e li valida successivamente
    def __init__(self, scene_json_path):
        raw_data = self.__load(scene_json_path)
        self.scene_data = self.__validate(raw_data)

    # Carica i dati JSON grezzi dal file della scena.
    def __load(self, filepath):
        try:
            with open(filepath, "r", encoding = "utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise SceneParserException(f"Failed to read scene JSON file: {e}")

    # Valida la struttura della scena, le chiavi obbligatorie, la mappa dei tile e i vincoli degli sprite.
    def __validate(self, data):
        # Valida le chiavi principali richieste: transparent_index, tile_map, sprites
        required_keys = {"transparent_index", "tile_map", "sprites"}
        if not all(key in data for key in required_keys):
            raise SceneParserException(f"Scene JSON is missing one of the required keys: {required_keys}")

        # Valida transparent_index (deve essere un intero compreso tra 0 e 15)
        transparent_index = data["transparent_index"]
        if not isinstance(transparent_index, int) or not (0 <= transparent_index <= 15):
            raise SceneParserException("transparent_index must be an integer between 0 and 15.")

        # Valida la tile_map (deve avere esattamente 15 righe e 20 colonne)
        tile_map = data["tile_map"]
        if not isinstance(tile_map, list) or len(tile_map) != 15:
            raise SceneParserException("tile_map must be a list containing exactly 15 rows.")
        
        for row in tile_map:
            if not isinstance(row, list) or len(row) != 20:
                raise SceneParserException("Each row in tile_map must contain exactly 20 columns.")
            if not all(isinstance(t, int) and 0 <= t < 64 for t in row):
                raise SceneParserException("Tile IDs in tile_map must be integers between 0 and 63.")

        # Valida la lista degli sprite (deve essere una lista con i campi specifici)
        sprites = data["sprites"]
        if not isinstance(sprites, list):
            raise SceneParserException("sprites must be a list.")

        for sprite in sprites:
            required_sprite_keys = {"id", "x", "y", "flip_h", "flip_v", "rotation"}
            if not all(k in sprite for k in required_sprite_keys):
                raise SceneParserException(f"Sprite is missing required fields: {required_sprite_keys}")
            
            # Controlla i vincoli di rotazione (ammessi solo 0, 90, 180, 270 gradi)
            if sprite["rotation"] not in {0, 90, 180, 270}:
                raise SceneParserException("Sprite rotation must be 0, 90, 180, or 270 degrees.")

        return data