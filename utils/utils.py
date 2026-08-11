# Daniele Sterle SM3201594

import argparse

def get_argv():

    parser = argparse.ArgumentParser()

    # Positional arguments (enforces strict order)
    parser.add_argument("palette_json", help="Path to palette.json")
    parser.add_argument("scene_json", help="Path to scene.json")
    parser.add_argument("tiles_bin", help="Path to tiles.bin")
    parser.add_argument("sprites_bin", help="Path to sprites.bin")
    parser.add_argument("output_png", help="Path to output.png")
    
    return parser.parse_args()