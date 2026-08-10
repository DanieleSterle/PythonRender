# Daniele Sterle SM3201594

import utils
from palette import Palette

if __name__ == "__main__":

    # Parse command-line arguments
    try:
        args = utils.get_argv()
        print("Arguments parsed successfully:", args)
        
        myP = Palette(args.palette_json)
    except Exception as e:
        print(f"An error occurred: {e}")
