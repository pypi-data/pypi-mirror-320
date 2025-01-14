
from sardine._sardine.region.host import shm as bytes

import numpy as np

def open(name: str, dtype = float, read_only: bool = False) -> np.ndarray:
    """
    @brief Opens a shared memory region.

    @param name The name of the shared memory region.
    @param dtype The data type of the shared memory region.
    @param read_only Whether to open the region in read-only mode.
    @return An ndarray representing the shared memory region.
    """
    memory_v = bytes.open(name, read_only)

    return np.frombuffer(memory_v, dtype=dtype)

def create(name: str, size: int, dtype = float, read_only: bool = False) -> np.ndarray:
    """
    @brief Creates a shared memory region.

    @param name The name of the shared memory region.
    @param size The size of the shared memory region.
    @param dtype The data type of the shared memory region.
    @param read_only Whether to open the region in read-only mode.
    @return An ndarray representing the shared memory region.
    """
    size_in_bytes = size * np.dtype(dtype).itemsize

    memory_v = bytes.create(name, size_in_bytes, read_only)

    return np.frombuffer(memory_v, dtype=dtype)

def open_or_create(name: str, size: int, dtype = float, read_only: bool = False) -> np.ndarray:
    """
    @brief Opens or creates a shared memory region.

    @param name The name of the shared memory region.
    @param size The size of the shared memory region.
    @param dtype The data type of the shared memory region.
    @param read_only Whether to open the region in read-only mode.
    @return An ndarray representing the shared memory region.
    """
    size_in_bytes = size * np.dtype(dtype).itemsize

    memory_v = bytes.open_or_create(name, size_in_bytes, read_only)

    return np.frombuffer(memory_v, dtype=dtype)
