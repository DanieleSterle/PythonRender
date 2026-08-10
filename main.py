# Daniele Sterle SM3201594

import utils
from palette import Palette
from vram import VirtualVRAM

if __name__ == "__main__":

    # Parse command-line arguments
    try:
        args = utils.get_argv()
        print("Arguments parsed successfully:", args)


        # Rinominare objs
        myP = Palette(args.palette_json)
        myVRAM = VirtualVRAM(myP, args.tiles_bin, args.sprites_bin)
    except Exception as e:
        print(f"An error occurred: {e}")
