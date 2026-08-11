# Test suite for the retro 2D renderer project

## What's covered (10 tests)

| # | Test | Class | Checks |
|---|------|-------|--------|
| 1 | `test_palette_loads_and_resolves_colors` | `Palette` | Loads a valid 16-color JSON and resolves indices to RGB tuples |
| 2 | `test_palette_wrong_length_raises` | `Palette` | Rejects a palette that doesn't have exactly 16 colors |
| 3 | `test_palette_out_of_range_component_raises` | `Palette` | Rejects an RGB component outside 0–255 |
| 4 | `test_vram_tile_extraction_correct_region_and_values` | `VirtualVRAM` | Nibble-unpacking is correct and tile IDs map to the right 32×32 region |
| 5 | `test_vram_wrong_sized_binary_raises` | `VirtualVRAM` | A binary file that isn't exactly 32768 bytes raises an error |
| 6 | `test_scene_parser_reads_tile_map_and_sprites` | `SceneParser` | `tile_map` is 15×20, `transparent_index` and `sprites` are parsed correctly |
| 7 | `test_scene_parser_rejects_invalid_rotation` | `SceneParser` | A rotation value other than 0/90/180/270 raises an error |
| 8 | `test_blitter_respects_transparency` | `Blitter` | Pixels equal to the transparent index don't overwrite the frame buffer |
| 9 | `test_blitter_transform_flip_and_rotation` | `Blitter` | `flip_v` and 90° rotation actually change pixel orientation as expected |
| 10 | `test_full_pipeline_renders_expected_png` | `RenderingPipeline` | End-to-end: 640×480 PNG is produced, background tile color is correct, off-screen sprite doesn't crash |

## Important: adapt the "ADAPTER" section

The assignment specifies the **class names** (`Palette`, `VirtualVRAM`,
`SceneParser`, `Blitter`, `RenderingPipeline`) but not their exact method
signatures. I picked a reasonable interface (documented in the comment block
at the top of `test_renderer.py`) and wrote the tests against it. Before
running, either:

- name your methods to match the assumed API (`get_color`, `get_tile`,
  `get_sprite`, `transform_sprite`, `blit`, `render`, `to_rgb`, `save`, and
  the attributes `.colors`, `.tile_map`, `.transparent_index`, `.sprites`), or
- edit the small number of call sites in each test to match your actual
  method/attribute names.

The fixtures (fake palette/scene/binary sheets) are generated on the fly in
`tmp_path`, so no external asset files are needed to run the suite.

## Running

```bash
pip install pytest pillow numpy
# put test_renderer.py in the same folder as your main.py (or adjust the import)
pytest test_renderer.py -v
```
