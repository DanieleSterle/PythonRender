# Daniele Sterle SM3201594

import sys
import utils
from palette import Palette, PaletteException
from vram import VirtualVRAM, VirtualVRAMException
from scene import SceneParser, SceneParserException
from blitter import Blitter, BlitterException
from pipeline import RenderingPipeline, RenderingPipelineException

def main():

    try:
        args = utils.get_argv()

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