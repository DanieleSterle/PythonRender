# Daniele Sterle SM3201594

import sys
import utils.utils as utl
from src.palette import Palette, PaletteException
from src.vram import VirtualVRAM, VirtualVRAMException
from src.scene import SceneParser, SceneParserException
from src.blitter import Blitter, BlitterException
from src.pipeline import RenderingPipeline, RenderingPipelineException

# Funzione principale che gestisce l'esecuzione del programma da riga di comando.
# Legge gli argomenti, inizializza le componenti del renderer e avvia il rendering.
def main():
    
    try:
        # Ottiene gli argomenti passati da riga di comando tramite l'utility dedicata
        args = utl.get_argv()

        # Caricamento e validazione dei componenti principali di input
        palette = Palette(args.palette_json)
        vram = VirtualVRAM(args.tiles_bin, args.sprites_bin)
        scene_parser = SceneParser(args.scene_json)
        
        # Inizializzazione del blitter e della pipeline di rendering
        blitter = Blitter()
        pipeline = RenderingPipeline(palette, vram, blitter)

        # Esecuzione della pipeline di composizione e salvataggio dell'immagine finale
        pipeline.render_scene(scene_parser.scene_data, args.output_png)

    except (PaletteException, VirtualVRAMException, SceneParserException, BlitterException, RenderingPipelineException) as e:
        # Gestione delle eccezioni specifiche del programma
        print(f"Render Error: {e}", file = sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Gestione di qualsiasi altro errore imprevisto
        print(f"An unexpected error occurred: {e}", file = sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()