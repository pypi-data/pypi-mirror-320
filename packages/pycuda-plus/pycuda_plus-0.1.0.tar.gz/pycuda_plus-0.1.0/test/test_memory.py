import pytest
import numpy as np
from pycuda_plus.memory import allocate

def test_allocate_and_copy():
    """
    Test GPU memory allocation and data transfer to/from the GPU.
    """
    shape = (256, 256)
    dtype = np.float32
    host_array = np.random.rand(*shape).astype(dtype)

    # Allocate GPU memory and copy data to the device
    gpu_array = allocate(shape, dtype)
    gpu_array.copy_to_device(host_array)

    # Copy data back to the host
    result_array = gpu_array.copy_to_host()

    # Verify the data matches the original
    assert np.allclose(host_array, result_array), "Data mismatch after GPU transfer"

    # Free GPU memory
    gpu_array.free()

def test_memory_cleanup():
    """
    Test that GPU memory is released properly.
    """
    shape = (128, 128)
    dtype = np.float32

    # Allocate memory and check cleanup
    gpu_array = allocate(shape, dtype)
    gpu_array.free()
    # Attempting to free again should not cause an issue
    try:
        gpu_array.free()
    except Exception as e:
        pytest.fail(f"Unexpected exception during memory cleanup: {e}")
