# Daniele Sterle SM3201594

import json

class SceneParserException(Exception):
    pass

class SceneParser:
    def __init__(self, scene_json_path):
        self.scene_data = self._load_and_validate(scene_json_path)

    # separare funzioni?
    def _load_and_validate(self, filepath):
        # 1. Load the JSON file
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as e:
            raise SceneParserException(f"Failed to read scene JSON file: {e}")

        # 2. Validate required top-level keys: transparent_index, tile_map, sprites
        required_keys = {"transparent_index", "tile_map", "sprites"}
        if not all(key in data for key in required_keys):
            raise SceneParserException(f"Scene JSON is missing one of the required keys: {required_keys}")

        # 3. Validate transparent_index (must be an integer between 0 and 15)
        transparent_index = data["transparent_index"]
        if not isinstance(transparent_index, int) or not (0 <= transparent_index <= 15):
            raise SceneParserException("transparent_index must be an integer between 0 and 15.")

        # 4. Validate tile_map (must be 15 rows and 20 columns)
        tile_map = data["tile_map"]
        if not isinstance(tile_map, list) or len(tile_map) != 15:
            raise SceneParserException("tile_map must be a list containing exactly 15 rows.")
        
        for row in tile_map:
            if not isinstance(row, list) or len(row) != 20:
                raise SceneParserException("Each row in tile_map must contain exactly 20 columns.")
            if not all(isinstance(t, int) and 0 <= t < 64 for t in row):
                raise SceneParserException("Tile IDs in tile_map must be integers between 0 and 63.")

        # 5. Validate sprites (must be a list with specific fields)
        sprites = data["sprites"]
        if not isinstance(sprites, list):
            raise SceneParserException("sprites must be a list.")

        for sprite in sprites:
            required_sprite_keys = {"id", "x", "y", "flip_h", "flip_v", "rotation"}
            if not all(k in sprite for k in required_sprite_keys):
                raise SceneParserException(f"Sprite is missing required fields: {required_sprite_keys}")
            
            # Check rotation constraints (only 0, 90, 180, 270)
            if sprite["rotation"] not in {0, 90, 180, 270}:
                raise SceneParserException("Sprite rotation must be 0, 90, 180, or 270 degrees.")

        return data