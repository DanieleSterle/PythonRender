# Daniele Sterle SM3201594

import argparse

# Configura e richiede gli argomenti da riga di comando nell'ordine specificato.
def get_argv():

    parser = argparse.ArgumentParser(description = "Retro 2D Renderer Command Line Interface")

    # Argomenti posizionali (forzano l'ordine richiesto)
    parser.add_argument("palette_json", help = "Percorso del file JSON della palette")
    parser.add_argument("scene_json", help = "Percorso del file JSON della scena")
    parser.add_argument("tiles_bin", help = "Percorso del file binario del tile sheet")
    parser.add_argument("sprites_bin", help = "Percorso del file binario dello sprite sheet")
    parser.add_argument("output_png", help = "Percorso del file PNG di output")
    
    # Restituisce l'oggetto Namespace contenente tutti i percorsi analizzati
    return parser.parse_args()