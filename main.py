# Daniele Sterle SM3201594

import sys
import utils.utils as utl
from src.palette import Palette, PaletteException
from src.vram import VirtualVRAM, VirtualVRAMException
from src.scene import SceneParser, SceneParserException
from src.blitter import Blitter, BlitterException
from src.pipeline import RenderingPipeline, RenderingPipelineException

# TODO: + test, cambiare struttura prog, refactor

def main():

    try:
        args = utl.get_argv()

        # 1. Load and validate components
        palette = Palette(args.palette_json)
        vram = VirtualVRAM(args.tiles_bin, args.sprites_bin)
        scene_parser = SceneParser(args.scene_json)
        
        # 2. Initialize blitter and pipeline
        blitter = Blitter()
        pipeline = RenderingPipeline(palette, vram, blitter)

        # 3. Execute the rendering pipeline
        pipeline.render_scene(scene_parser.scene_data, args.output_png)

    except (PaletteException, VirtualVRAMException, SceneParserException, BlitterException, RenderingPipelineException) as e:
        print(f"Render Error: {e}", file = sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file = sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()