# Python Render

A Python-based 2D renderer for retro scenes, using NumPy for efficient pixel and array processing.

This is the second of two projects for the Programmazione Avanzata e Parallela course (Artificial Intelligence & Data Analytics B.Sc.) at Università di Trieste for the 2025/2026 academic year.

## Description

### Architecture

The renderer's architecture is divided into the following sections:

- A 16-color RGB palette.
- A 256x256 tile sheet containing 32x32 pixel tiles.
- A 256x256 sprite sheet containing 64x64 pixel sprites.
- A 640x480 frame buffer.
- A transparent color index specifically for sprites.
- Sprite transformations: horizontal and vertical flips, plus 0, 90, 180, or 270-degree rotations.

### Pipeline

The composition follows this sequence:

- The entire background is drawn first using the tile map.
- Transformations are applied to the sprites.
- Sprites are drawn onto the frame buffer in the exact order in which they are listed in the scene.

## Implementation Notes

### Program Structure and Classes

The script is organized into classes to separate responsibilities. The following steps are performed in order, with each step corresponding to a class:

- **Palette:** Loads and validates the palette JSON file.
- **VirtualVRAM:** Loads and decodes the tile and sprite sheets.
- **SceneParser:** Loads and validates the scene JSON file.
- **Blitter:** Initializes the frame buffer, draws the tiles, applies transformations, and draws the sprites.
- **RenderingPipeline:** Assembles the final image. See [Pipeline](#pipeline) for more details.

### Extracting the Nibbles

The tile and sprite sheets use packed nibbles, meaning each byte stores two 4-bit pixels to save space. To decode this binary data, the following steps were taken:

- The raw byte data is loaded into a flat `uint8` NumPy array.
- The high nibbles (the first pixel) are extracted by shifting the bits 4 positions to the right (`>> 4`).
- The low nibbles (the second pixel) are isolated using a bitwise AND mask (`& 0x0F`) to clear the upper bits.
- The extracted nibbles are interleaved into a new array: high nibbles at even indices and low nibbles at odd indices. The result is then reshaped into a 2D matrix.

### Sprite Clipping

To accurately draw sprites that might fall partially or completely outside the screen bounds, the clipping process works as follows:

- The initial screen coordinates are calculated, immediately discarding the sprite if it is completely off-screen.
- If the sprite is partially visible, its internal source coordinates are cropped to remove portions extending beyond the top/left (`< 0`) or bottom/right screen edges.
- The destination coordinates on the frame buffer are clamped to strict screen boundaries (`0` to `width`/`height`) to prevent out-of-bounds errors.
- Matching slices are extracted from both the cropped sprite and the frame buffer.
- A boolean mask is applied to these slices to copy only visible pixels, filtering out the transparent index.

## Project Structure

```text
PythonRender/
├── example/                 # Example assets and configuration files
│   ├── palette.json         # 16-color RGB palette configuration
│   ├── reference.png        # Reference image for the expected output
│   ├── scene.json           # Scene configuration (tile map and sprites)
│   ├── sprites.bin          # Binary sprite sheet data
│   ├── sprites.png          # Visual representation of the sprites
│   ├── tiles.bin            # Binary tile sheet data
│   └── tiles.png            # Visual representation of the tiles
├── src/                     # Core source code for the renderer
│   ├── blitter.py           # Handles drawing, clipping, and transformations
│   ├── palette.py           # Loads and decodes the color palette
│   ├── pipeline.py          # Assembles the rendering pipeline and final image
│   ├── scene.py             # Parses the scene JSON configuration
│   └── vram.py              # Decodes and manages the tile and sprite sheets
├── tests/                   # Unit tests
├── utils/                   # Helper modules
│   └── utils.py             # General utility functions
├── .gitignore               # Specifies intentionally untracked files
├── main.py                  # Main CLI entry point
├── project_python.pdf       # Original project specifications
└── README.md                # Project documentation
```

## Documentation

To better understand all the project’s specifications and details, check the official documentation:
[Project Documentation (PDF)](project_python.pdf)

## License

This project is licensed under the MIT License.

