from typing import Tuple

import cv2
import numpy as np
from app.models.resnet import model

def crop_to_multiple_of_512(image: np.ndarray) -> np.ndarray:
    height, width, _ = image.shape

    new_height = height - (height % 512)
    new_width = width - (width % 512)

    return image[:new_height, :new_width, :]


def tile_image(image: np.ndarray, tile_size: int = 512) -> np.ndarray:
    height, width, _ = image.shape

    tiles = []

    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            tile = image[y:y + tile_size, x:x + tile_size]
            tiles.append(tile)

    return np.array(tiles)

def untile_image(tiles: np.ndarray, original_height: int, original_width: int, tile_size: int = 512) -> np.ndarray:
    # Calculate how many tiles fit in each dimension
    tiles_y = original_height // tile_size
    tiles_x = original_width // tile_size

    # Create empty image to hold the result
    reconstructed = np.zeros((original_height, original_width, tiles.shape[-1]), dtype=tiles.dtype)

    # Place each tile in its correct position
    tile_idx = 0
    for y in range(0, tiles_y):
        for x in range(0, tiles_x):
            y_start = y * tile_size
            x_start = x * tile_size
            reconstructed[y_start:y_start + tile_size, x_start:x_start + tile_size] = tiles[tile_idx]
            tile_idx += 1

    return reconstructed

def analyze_image(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Crop image to multiple of 512
    image = crop_to_multiple_of_512(image)
    original_height, original_width, _ = image.shape

    # Split image into tiles
    tiles = tile_image(image)

    num_tiles = tiles.shape[0]
    print(f"Analyzing {num_tiles} tiles")

    # Normalize all tiles at once
    normalized_tiles = tiles / 255.0

    # Process all tiles in a single batch
    predictions = model.predict(normalized_tiles)

    # Get class indices for all tiles
    prediction_indices = np.argmax(predictions, axis=-1)

    # Create individual class masks for all tiles at once
    building_tiles = np.expand_dims(np.where(prediction_indices == 0, 1, 0).astype(np.uint8), axis=-1)
    vegetation_tiles = np.expand_dims(np.where(prediction_indices == 3, 1, 0).astype(np.uint8), axis=-1)

    # Reconstruct full masks from tiles
    building_mask = np.squeeze(untile_image(building_tiles, original_height, original_width, 512))
    vegetation_mask = np.squeeze(untile_image(vegetation_tiles, original_height, original_width, 512))

    return image, vegetation_mask, building_mask