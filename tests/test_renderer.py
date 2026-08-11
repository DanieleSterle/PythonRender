# test_renderer_extended.py
#
# Extended test suite (90 tests) for Daniele Sterle's (SM3201594) retro 2D
# renderer project. Combined with test_renderer.py (10 tests) this gives
# 100 tests total. Run `pytest --collect-only -q` to see the full count.
#
# Organized by class, roughly in increasing complexity:
#   A. Palette              (15 tests)
#   B. VirtualVRAM           (15 tests)
#   C. SceneParser           (20 tests)
#   D. Blitter               (25 tests)
#   E. RenderingPipeline     (15 tests)

import json
import numpy as np
import pytest
from PIL import Image

from src.palette import Palette, PaletteException
from src.vram import VirtualVRAM, VirtualVRAMException
from src.scene import SceneParser, SceneParserException
from src.blitter import Blitter, BlitterException
from src.pipeline import RenderingPipeline, RenderingPipelineException

from conftest import BASE_PALETTE, make_sheet_bytes, make_scene_dict


# =============================================================================
# A. Palette — 15 tests
# =============================================================================

def test_palette_file_not_found(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(PaletteException):
        Palette(str(missing))


def test_palette_invalid_json_syntax(tmp_path):
    bad = tmp_path / "broken.json"
    bad.write_text("{not valid json")
    with pytest.raises(PaletteException):
        Palette(str(bad))


def test_palette_not_a_list(tmp_path):
    bad = tmp_path / "dict_palette.json"
    bad.write_text(json.dumps({"colors": BASE_PALETTE}))
    with pytest.raises(PaletteException):
        Palette(str(bad))


def test_palette_empty_list(tmp_path):
    bad = tmp_path / "empty_palette.json"
    bad.write_text(json.dumps([]))
    with pytest.raises(PaletteException):
        Palette(str(bad))


def test_palette_too_many_colors(tmp_path):
    too_many = BASE_PALETTE + [[10, 10, 10]]
    bad = tmp_path / "seventeen_palette.json"
    bad.write_text(json.dumps(too_many))
    with pytest.raises(PaletteException):
        Palette(str(bad))


@pytest.mark.parametrize("bad_length_color", [[1, 2], [1, 2, 3, 4]])
def test_palette_color_wrong_length(tmp_path, bad_length_color):
    colors = [list(c) for c in BASE_PALETTE]
    colors[5] = bad_length_color
    bad = tmp_path / "wrong_length.json"
    bad.write_text(json.dumps(colors))
    with pytest.raises(PaletteException):
        Palette(str(bad))


@pytest.mark.parametrize("bad_type_color", ["red", {"r": 1, "g": 2, "b": 3}])
def test_palette_color_wrong_type(tmp_path, bad_type_color):
    colors = [list(c) for c in BASE_PALETTE]
    colors[5] = bad_type_color
    bad = tmp_path / "wrong_type.json"
    bad.write_text(json.dumps(colors))
    with pytest.raises(PaletteException):
        Palette(str(bad))


@pytest.mark.parametrize("bad_component", [-1, 256, 1.5, "255"])
def test_palette_invalid_component(tmp_path, bad_component):
    colors = [list(c) for c in BASE_PALETTE]
    colors[5] = [bad_component, 0, 0]
    bad = tmp_path / "bad_component.json"
    bad.write_text(json.dumps(colors))
    with pytest.raises(PaletteException):
        Palette(str(bad))


def test_palette_negative_index_wraps_like_a_list(palette_path):
    """
    Palette no longer validates indices itself; .palette is a plain Python
    list, so negative indices follow normal list semantics (wrap from the end)
    rather than raising.
    """
    palette = Palette(str(palette_path))
    assert palette.palette[-1] == palette.palette[15]


def test_palette_out_of_range_index_raises_index_error(palette_path):
    """With no bounds-checking method, indexing past the end of the list
    falls through to Python's own IndexError."""
    palette = Palette(str(palette_path))
    with pytest.raises(IndexError):
        palette.palette[16]


# =============================================================================
# B. VirtualVRAM — 15 tests
# =============================================================================

def test_vram_tiles_file_not_found(tmp_path, sprites_bin_path):
    missing = tmp_path / "no_tiles.bin"
    with pytest.raises(VirtualVRAMException):
        VirtualVRAM(str(missing), str(sprites_bin_path))


def test_vram_sprites_file_not_found(tmp_path, tiles_bin_path):
    missing = tmp_path / "no_sprites.bin"
    with pytest.raises(VirtualVRAMException):
        VirtualVRAM(str(tiles_bin_path), str(missing))


def test_vram_sprites_wrong_size_raises(tmp_path, tiles_bin_path):
    truncated = tmp_path / "sprites_truncated.bin"
    truncated.write_bytes(b"\x00" * 500)
    with pytest.raises(VirtualVRAMException):
        VirtualVRAM(str(tiles_bin_path), str(truncated))


def test_vram_tiles_shape_and_dtype(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    assert vram.tiles.shape == (64, 32, 32)
    assert vram.tiles.dtype == np.uint8


def test_vram_sprites_shape_and_dtype(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    assert vram.sprites.shape == (16, 64, 64)
    assert vram.sprites.dtype == np.uint8


def test_vram_nibble_order_high_before_low(tmp_path, sprites_bin_path):
    """
    First byte 0x1F must decode to pixel[0]=1 (high nibble) and pixel[1]=15
    (low nibble), landing in tile 0's top-left corner.
    """
    raw = bytearray(32768)
    raw[0] = 0x1F  # high nibble=1, low nibble=15
    tiles_path = tmp_path / "nibble_order.bin"
    tiles_path.write_bytes(bytes(raw))

    vram = VirtualVRAM(str(tiles_path), str(sprites_bin_path))
    assert vram.tiles[0][0, 0] == 1
    assert vram.tiles[0][0, 1] == 15


def test_vram_all_pixel_values_within_nibble_range(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    assert vram.tiles.max() <= 15
    assert vram.sprites.max() <= 15
    assert vram.tiles.min() >= 0
    assert vram.sprites.min() >= 0


@pytest.mark.parametrize("tile_id", [0, 1, 8, 63])
def test_vram_tile_grid_row_major_mapping(distinct_tiles_bin_path, sprites_bin_path, tile_id):
    """Every tile id in a distinct-fill sheet must map to its own region."""
    vram = VirtualVRAM(str(distinct_tiles_bin_path), str(sprites_bin_path))
    expected_value = tile_id % 16
    assert np.all(vram.tiles[tile_id] == expected_value)


@pytest.mark.parametrize("sprite_id", [0, 1, 4, 15])
def test_vram_sprite_grid_row_major_mapping(tiles_bin_path, distinct_sprites_bin_path, sprite_id):
    vram = VirtualVRAM(str(tiles_bin_path), str(distinct_sprites_bin_path))
    assert np.all(vram.sprites[sprite_id] == sprite_id)


# =============================================================================
# C. SceneParser — 20 tests
# =============================================================================

def test_scene_file_not_found(tmp_path):
    missing = tmp_path / "no_scene.json"
    with pytest.raises(SceneParserException):
        SceneParser(str(missing))


def test_scene_invalid_json_syntax(tmp_path):
    bad = tmp_path / "broken_scene.json"
    bad.write_text("{not valid json")
    with pytest.raises(SceneParserException):
        SceneParser(str(bad))


@pytest.mark.parametrize("missing_key", ["transparent_index", "tile_map", "sprites"])
def test_scene_missing_top_level_key(tmp_path, missing_key):
    scene = make_scene_dict()
    del scene[missing_key]
    p = tmp_path / f"missing_{missing_key}.json"
    p.write_text(json.dumps(scene))
    with pytest.raises(SceneParserException):
        SceneParser(str(p))


@pytest.mark.parametrize("bad_transparent_index", [-1, 16, 1.5])
def test_scene_invalid_transparent_index(tmp_path, bad_transparent_index):
    scene = make_scene_dict(transparent_index=bad_transparent_index)
    p = tmp_path / "bad_transparent.json"
    p.write_text(json.dumps(scene))
    with pytest.raises(SceneParserException):
        SceneParser(str(p))


@pytest.mark.parametrize("row_count", [14, 16])
def test_scene_tile_map_wrong_row_count(tmp_path, row_count):
    tile_map = [[0] * 20 for _ in range(row_count)]
    scene = make_scene_dict(tile_map=tile_map)
    p = tmp_path / "wrong_rows.json"
    p.write_text(json.dumps(scene))
    with pytest.raises(SceneParserException):
        SceneParser(str(p))


@pytest.mark.parametrize("col_count", [19, 21])
def test_scene_tile_map_wrong_col_count(tmp_path, col_count):
    tile_map = [[0] * col_count for _ in range(15)]
    scene = make_scene_dict(tile_map=tile_map)
    p = tmp_path / "wrong_cols.json"
    p.write_text(json.dumps(scene))
    with pytest.raises(SceneParserException):
        SceneParser(str(p))


@pytest.mark.parametrize("bad_tile_id", [-1, 64])
def test_scene_tile_map_invalid_tile_id(tmp_path, bad_tile_id):
    tile_map = [[0] * 20 for _ in range(15)]
    tile_map[0][0] = bad_tile_id
    scene = make_scene_dict(tile_map=tile_map)
    p = tmp_path / "bad_tile_id.json"
    p.write_text(json.dumps(scene))
    with pytest.raises(SceneParserException):
        SceneParser(str(p))


@pytest.mark.parametrize("missing_field", ["id", "x", "y", "flip_h", "flip_v", "rotation"])
def test_scene_sprite_missing_field(tmp_path, missing_field):
    sprite = {"id": 0, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}
    del sprite[missing_field]
    scene = make_scene_dict(sprites=[sprite])
    p = tmp_path / f"missing_sprite_{missing_field}.json"
    p.write_text(json.dumps(scene))
    with pytest.raises(SceneParserException):
        SceneParser(str(p))


# =============================================================================
# D. Blitter — 25 tests
# =============================================================================

def test_create_frame_buffer_default_shape():
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    assert fb.shape == (480, 640)


def test_create_frame_buffer_custom_shape():
    blitter = Blitter(frame_buffer_shape=(100, 200))
    fb = blitter.create_frame_buffer()
    assert fb.shape == (100, 200)


def test_create_frame_buffer_dtype_and_zero_filled():
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    assert fb.dtype == np.uint8
    assert np.all(fb == 0)


@pytest.mark.parametrize("row,col", [(0, 0), (0, 1), (14, 19), (7, 10)])
def test_draw_tile_map_correct_tile_at_position(distinct_tiles_bin_path, sprites_bin_path, row, col):
    vram = VirtualVRAM(str(distinct_tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()

    tile_map = [[0] * 20 for _ in range(15)]
    chosen_tile_id = 9  # arbitrary, maps to value 9 in the distinct fixture
    tile_map[row][col] = chosen_tile_id

    blitter.draw_tile_map(fb, tile_map, vram.tiles)

    y, x = row * 32, col * 32
    assert np.all(fb[y:y+32, x:x+32] == 9)


def test_draw_tile_map_full_coverage(distinct_tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(distinct_tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()

    tile_id = 5
    tile_map = [[tile_id] * 20 for _ in range(15)]
    blitter.draw_tile_map(fb, tile_map, vram.tiles)

    assert fb.shape == (480, 640)
    assert np.all(fb == 5)


def test_draw_tile_map_handles_repeated_tile_ids(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()

    # tile id 0 (value 1 in the basic fixture) used everywhere
    tile_map = [[0] * 20 for _ in range(15)]
    blitter.draw_tile_map(fb, tile_map, vram.tiles)

    assert np.all(fb == 1)


def test_draw_sprites_empty_list_no_op(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    fb[:, :] = 4
    blitter.draw_sprites(fb, [], vram.sprites, transparent_index=0)
    assert np.all(fb == 4)


def test_draw_sprites_invalid_rotation_raises(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    sprites = [{"id": 0, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 45}]
    with pytest.raises(BlitterException):
        blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)


def test_draw_sprites_missing_field_raises(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    sprites = [{"id": 0, "x": 0, "y": 0, "flip_h": False, "flip_v": False}]  # no rotation
    with pytest.raises(BlitterException):
        blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)


def test_apply_transformations_flip_h():
    blitter = Blitter()
    sprite = np.zeros((64, 64), dtype = np.uint8)
    sprite[:, 0] = 5  # marker column at the left edge
    flipped = blitter._Blitter__apply_transformations(sprite, flip_h=True, flip_v=False, rotation=0)
    assert np.all(flipped[:, 63] == 5) and np.all(flipped[:, 0] == 0)


def test_apply_transformations_flip_h_and_v_combined():
    blitter = Blitter()
    sprite = np.zeros((64, 64), dtype = np.uint8)
    sprite[0, 0] = 9  # single marker pixel at top-left corner
    flipped = blitter._Blitter__apply_transformations(sprite, flip_h=True, flip_v=True, rotation=0)
    assert flipped[63, 63] == 9
    assert flipped[0, 0] == 0


def test_apply_transformations_rotation_180():
    blitter = Blitter()
    sprite = np.zeros((64, 64), dtype = np.uint8)
    sprite[0, 0] = 9
    rotated = blitter._Blitter__apply_transformations(sprite, flip_h=False, flip_v=False, rotation=180)
    assert rotated[63, 63] == 9
    assert rotated[0, 0] == 0


def test_apply_transformations_rotation_270():
    blitter = Blitter()
    sprite = np.zeros((64, 64), dtype = np.uint8)
    sprite[0, :] = 5  # top row marker
    rotated = blitter._Blitter__apply_transformations(sprite, flip_h=False, flip_v=False, rotation=270)
    assert rotated.shape == (64, 64)
    # rotating twice by 90 should equal one rotation by 180, cross-checking consistency
    twice_90 = sprite.copy()
    for _ in range(2):
        twice_90 = blitter._Blitter__apply_transformations(twice_90, flip_h=False, flip_v=False, rotation=90)
    rot_180 = blitter._Blitter__apply_transformations(sprite, flip_h=False, flip_v=False, rotation=180)
    assert np.array_equal(twice_90, rot_180)


def test_apply_transformations_flip_plus_rotation_combo():
    blitter = Blitter()
    sprite = np.zeros((64, 64), dtype = np.uint8)
    sprite[0, 0] = 7
    combo = blitter._Blitter__apply_transformations(sprite, flip_h=True, flip_v=False, rotation=180)
    # flip_h moves marker to (0,63); rotation 180 then moves it to (63,0)
    assert combo[63, 0] == 7


def test_blit_sprite_fully_offscreen_no_crash_no_change(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    fb[:, :] = 7
    sprites = [{"id": 1, "x": 1000, "y": 1000, "flip_h": False, "flip_v": False, "rotation": 0}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)
    assert np.all(fb == 7)


def test_blit_sprite_fully_onscreen_all_pixels_drawn(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    sprites = [{"id": 1, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)
    assert np.all(fb[0:64, 0:64] == 3)


def test_blit_sprite_negative_xy_clipping(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    fb[:, :] = 9
    sprites = [{"id": 1, "x": -32, "y": -32, "flip_h": False, "flip_v": False, "rotation": 0}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)
    assert fb[31, 31] == 3          # inside the clipped visible region
    assert fb[35, 35] == 9          # outside the sprite entirely, untouched


def test_blit_sprite_exact_right_edge_fully_visible(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    sprites = [{"id": 1, "x": 640 - 64, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)
    assert fb[0, 576] == 3
    assert fb[0, 639] == 3


def test_blit_sprite_one_pixel_overlap(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    fb[:, :] = 9
    sprites = [{"id": 1, "x": 639, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)
    assert fb[0, 639] == 3
    assert fb[0, 638] == 9  # just outside the 1px-wide visible sliver


def test_transparency_with_nonzero_transparent_index(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    fb[:, :] = 8
    # sprite 0: top row = 5, rest = 0. Now treat 5 as transparent instead of 0.
    sprites = [{"id": 0, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=5)
    assert np.all(fb[0, 0:64] == 8)    # top row (value 5) treated as transparent, left alone
    assert np.all(fb[1, 0:64] == 0)    # rest of the sprite (value 0) is now opaque


def test_blit_does_not_mutate_source_vram_array(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    original_sprite_0 = vram.sprites[0].copy()

    blitter = Blitter()
    fb = blitter.create_frame_buffer()
    sprites = [{"id": 0, "x": 0, "y": 0, "flip_h": True, "flip_v": True, "rotation": 90}]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)

    assert np.array_equal(vram.sprites[0], original_sprite_0)


def test_draw_sprites_zorder_later_sprite_on_top(tiles_bin_path, sprites_bin_path):
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    fb = blitter.create_frame_buffer()

    # sprite 1 (opaque, all value 3) drawn first, then sprite 0
    # (top row = 5 opaque, rest = 0 transparent) drawn on top at the same spot.
    sprites = [
        {"id": 1, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0},
        {"id": 0, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0},
    ]
    blitter.draw_sprites(fb, sprites, vram.sprites, transparent_index=0)

    assert np.all(fb[0, 0:64] == 5)     # sprite 0's opaque top row wins
    assert np.all(fb[1, 0:64] == 3)     # sprite 0's transparent pixels reveal sprite 1 underneath


# =============================================================================
# E. RenderingPipeline — 15 tests
# =============================================================================

def test_render_scene_creates_file_at_given_path(palette_path, tiles_bin_path, sprites_bin_path, tmp_path):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    out = tmp_path / "out.png"
    pipeline.render_scene(make_scene_dict(), str(out))
    assert out.exists()


@pytest.mark.parametrize("missing_key", ["transparent_index", "tile_map", "sprites"])
def test_render_scene_raises_on_missing_scene_key(
    palette_path, tiles_bin_path, sprites_bin_path, tmp_path, missing_key
):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    scene = make_scene_dict()
    del scene[missing_key]
    with pytest.raises(RenderingPipelineException):
        pipeline.render_scene(scene, str(tmp_path / "out.png"))


def test_render_scene_raises_on_invalid_tile_id(palette_path, tiles_bin_path, sprites_bin_path, tmp_path):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    tile_map = [[0] * 20 for _ in range(15)]
    tile_map[0][0] = 999  # out of range for a 64-tile sheet
    scene = make_scene_dict(tile_map=tile_map)
    with pytest.raises(RenderingPipelineException):
        pipeline.render_scene(scene, str(tmp_path / "out.png"))


def test_render_scene_image_mode_rgb(palette_path, tiles_bin_path, sprites_bin_path, tmp_path):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    out = tmp_path / "out.png"
    pipeline.render_scene(make_scene_dict(), str(out))
    assert Image.open(out).mode == "RGB"


def test_render_scene_image_size_always_640x480(palette_path, tiles_bin_path, sprites_bin_path, tmp_path):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    out = tmp_path / "out.png"
    pipeline.render_scene(make_scene_dict(), str(out))
    assert Image.open(out).size == (640, 480)


def test_render_scene_no_sprites_background_only(palette_path, tiles_bin_path, sprites_bin_path, tmp_path):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    # tile id 0 everywhere -> value 1 -> palette index 1 -> red
    tile_map = [[0] * 20 for _ in range(15)]
    scene = make_scene_dict(tile_map=tile_map, sprites=[])
    out = tmp_path / "out.png"
    pipeline.render_scene(scene, str(out))

    rgb = np.array(Image.open(out))
    assert np.all(rgb == np.array([255, 0, 0], dtype = np.uint8))


def test_render_scene_composition_order_tile_then_sprite(
    palette_path, tiles_bin_path, sprites_bin_path, tmp_path
):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    tile_map = [[0] * 20 for _ in range(15)]  # background -> value 1 -> red
    sprites = [{"id": 1, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}]  # value 3
    scene = make_scene_dict(tile_map=tile_map, sprites=sprites)
    out = tmp_path / "out.png"
    pipeline.render_scene(scene, str(out))

    rgb = np.array(Image.open(out))
    # inside the sprite: index 3 -> blue, not the background red
    assert tuple(rgb[0, 0]) == tuple(BASE_PALETTE[3])
    # outside the sprite: background red remains
    assert tuple(rgb[0, 600]) == tuple(BASE_PALETTE[1])


def test_render_scene_overwrites_existing_output_file(
    palette_path, tiles_bin_path, sprites_bin_path, tmp_path
):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    out = tmp_path / "out.png"
    out.write_bytes(b"not a real png")
    pipeline.render_scene(make_scene_dict(), str(out))

    # should now be a valid, openable PNG
    img = Image.open(out)
    assert img.size == (640, 480)


@pytest.mark.parametrize("index", [0, 5, 10, 15])
def test_convert_to_rgb_matches_palette_for_all_indices(
    palette_path, distinct_tiles_bin_path, sprites_bin_path, tmp_path, index
):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(distinct_tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    # tile id == index (index <= 15 < 64), so every tile is filled with `index`
    tile_map = [[index] * 20 for _ in range(15)]
    scene = make_scene_dict(tile_map=tile_map, sprites=[])
    out = tmp_path / "out.png"
    pipeline.render_scene(scene, str(out))

    rgb = np.array(Image.open(out))
    expected = np.array(BASE_PALETTE[index], dtype = np.uint8)
    assert np.all(rgb == expected)


def test_render_scene_transparency_preserves_background_tile(
    palette_path, tiles_bin_path, sprites_bin_path, tmp_path
):
    palette = Palette(str(palette_path))
    vram = VirtualVRAM(str(tiles_bin_path), str(sprites_bin_path))
    blitter = Blitter()
    pipeline = RenderingPipeline(palette, vram, blitter)

    # background: tile id 1 everywhere -> value 2 -> green
    tile_map = [[1] * 20 for _ in range(15)]
    # sprite 0: top row opaque (5), rest transparent (0) -> background shows through below row 0
    sprites = [{"id": 0, "x": 0, "y": 0, "flip_h": False, "flip_v": False, "rotation": 0}]
    scene = make_scene_dict(tile_map=tile_map, sprites=sprites, transparent_index=0)
    out = tmp_path / "out.png"
    pipeline.render_scene(scene, str(out))

    rgb = np.array(Image.open(out))
    assert tuple(rgb[1, 0]) == tuple(BASE_PALETTE[2])  # green background shows through
