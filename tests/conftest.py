# conftest.py
# Shared fixtures for the renderer test suite (test_renderer.py + test_renderer_extended.py)

import json
import numpy as np
import pytest

BASE_PALETTE = [
    [0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255],
    [255, 255, 255], [255, 255, 0], [255, 128, 0], [128, 128, 128],
    [0, 255, 255], [255, 0, 255], [128, 0, 0], [0, 128, 0],
    [0, 0, 128], [128, 128, 0], [128, 0, 128], [0, 128, 128],
]


def pack_nibbles(indices_flat):
    """Pack a flat list of 4-bit indices (high nibble first) into bytes."""
    assert len(indices_flat) % 2 == 0
    out = bytearray()
    for i in range(0, len(indices_flat), 2):
        hi = indices_flat[i] & 0x0F
        lo = indices_flat[i + 1] & 0x0F
        out.append((hi << 4) | lo)
    return bytes(out)


def make_sheet_bytes(fill_fn):
    """
    Build a 256x256 packed-nibble sheet (32768 bytes) where fill_fn(row, col)
    returns the 4-bit palette index for that pixel.
    """
    flat = []
    for row in range(256):
        for col in range(256):
            flat.append(fill_fn(row, col) & 0x0F)
    return pack_nibbles(flat)


@pytest.fixture
def palette_path(tmp_path):
    p = tmp_path / "palette.json"
    p.write_text(json.dumps(BASE_PALETTE))
    return p


@pytest.fixture
def tiles_bin_path(tmp_path):
    """
    8x8 grid of 32x32 tiles. Tile id 0 -> index 1, tile id 1 -> index 2,
    everything else -> index 0.
    """
    def fill(row, col):
        tile_row, tile_col = row // 32, col // 32
        tile_id = tile_row * 8 + tile_col
        if tile_id == 0:
            return 1
        if tile_id == 1:
            return 2
        return 0

    path = tmp_path / "tiles.bin"
    path.write_bytes(make_sheet_bytes(fill))
    return path


@pytest.fixture
def sprites_bin_path(tmp_path):
    """
    4x4 grid of 64x64 sprites.
    Sprite 0: top row = index 5, rest = index 0 (transparent).
    Sprite 1: filled entirely with index 3.
    """
    def fill(row, col):
        sprite_row, sprite_col = row // 64, col // 64
        sprite_id = sprite_row * 4 + sprite_col
        local_row = row % 64
        if sprite_id == 0:
            return 5 if local_row == 0 else 0
        if sprite_id == 1:
            return 3
        return 0

    path = tmp_path / "sprites.bin"
    path.write_bytes(make_sheet_bytes(fill))
    return path


@pytest.fixture
def distinct_tiles_bin_path(tmp_path):
    """
    8x8 grid of 32x32 tiles where every tile id is filled with (tile_id % 16),
    so any tile id's resulting region can be checked against a known value.
    """
    def fill(row, col):
        tile_row, tile_col = row // 32, col // 32
        tile_id = tile_row * 8 + tile_col
        return tile_id % 16

    path = tmp_path / "tiles_distinct.bin"
    path.write_bytes(make_sheet_bytes(fill))
    return path


@pytest.fixture
def distinct_sprites_bin_path(tmp_path):
    """
    4x4 grid of 64x64 sprites where every sprite id is filled with sprite_id
    itself (0-15, always a valid nibble).
    """
    def fill(row, col):
        sprite_row, sprite_col = row // 64, col // 64
        sprite_id = sprite_row * 4 + sprite_col
        return sprite_id

    path = tmp_path / "sprites_distinct.bin"
    path.write_bytes(make_sheet_bytes(fill))
    return path


@pytest.fixture
def scene_path(tmp_path):
    tile_map = [[0 if (r + c) % 2 == 0 else 1 for c in range(20)] for r in range(15)]
    scene = {
        "transparent_index": 0,
        "tile_map": tile_map,
        "sprites": [
            {"id": 0, "x": 32, "y": 32, "flip_h": False, "flip_v": False, "rotation": 0},
            {"id": 1, "x": 620, "y": 460, "flip_h": False, "flip_v": False, "rotation": 0},
        ],
    }
    p = tmp_path / "scene.json"
    p.write_text(json.dumps(scene))
    return p


def make_scene_dict(transparent_index=0, tile_map=None, sprites=None):
    """Helper to build a minimal, valid scene dict for tests that need one inline."""
    if tile_map is None:
        tile_map = [[0] * 20 for _ in range(15)]
    if sprites is None:
        sprites = []
    return {
        "transparent_index": transparent_index,
        "tile_map": tile_map,
        "sprites": sprites,
    }
