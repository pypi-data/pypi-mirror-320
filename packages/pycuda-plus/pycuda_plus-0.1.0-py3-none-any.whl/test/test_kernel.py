import numpy as np
import pycuda.driver as cuda
from pycuda_plus.memory import allocate
from pycuda_plus.kernel import compile_kernel
from pycuda_plus.profiler import Profiler
from pycuda_plus.utils import generate_random_array, compare_arrays, print_array_summary
import pytest

# Initialize CUDA driver
cuda.init()

def test_compile_and_execute_kernel():
    # Step 1: Generate random data on the host
    shape = (256, 256)
    dtype = np.float32
    host_array = generate_random_array(shape, dtype, min_val=0.0, max_val=10.0)

    # Print summary of the host array
    print_array_summary(host_array, name="Host Array")

    # Step 2: Allocate GPU memory and copy data to the GPU
    gpu_array = allocate(shape, dtype)
    gpu_array.copy_to_device(host_array)

    # Debugging: Confirm the data is copied to GPU
    print("Data copied to GPU:")
    print("First 10 elements on host (before copy):", host_array.flat[:10])

    # Step 3: Define a simple CUDA kernel for scaling
    kernel_code = """
    __global__ void scale_array(float *array, float scale_factor, int size) {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        if (idx < size) {
            array[idx] *= scale_factor;  // Perform the scaling operation
        }
    }
    """

    # Step 4: Compile the kernel
    kernel_manager = compile_kernel(kernel_code)
    scale_array_kernel = kernel_manager.get_function("scale_array")

    # Step 5: Launch the kernel with adjusted grid and block size
    block_size = (16, 16, 1)  # Threads per block
    grid_size = (int(np.ceil(shape[0] * shape[1] / block_size[0])), 1, 1)  # Grid size based on total size

    scale_factor = np.float32(2.0)

    # Debugging before kernel execution
    print("Block size:", block_size)
    print("Grid size:", grid_size)

    # Run the kernel and profile its execution
    execution_time = Profiler.time_kernel(
        scale_array_kernel,
        grid_size,
        block_size,
        gpu_array.gpu_buffer,  # Pass the GPU memory buffer
        scale_factor,
        np.int32(gpu_array.size)  # Total number of elements
    )

    print(f"Kernel execution time: {execution_time:.4f} ms")

    # Step 6: Synchronize to ensure kernel execution completes
    cuda.Context.synchronize()

    # Debugging after kernel execution
    result_array = gpu_array.copy_to_host()
    print("GPU array (first 10 elements after scaling):", result_array.flat[:10])

    # Step 7: Copy the data back to the host
    print("Result array:")
    print_array_summary(result_array, name="Result Array")

    # Step 8: Verify the result
    expected_array = host_array * scale_factor

    # Debugging: Print out first few elements
    print("Host Array (first 10 elements):", host_array.flat[:10])
    print("Expected Array (first 10 elements):", expected_array.flat[:10])
    print("Result Array (first 10 elements):", result_array.flat[:10])

    # Check if the result matches the expected output (with tolerance)
    try:
        assert compare_arrays(expected_array, result_array, atol=1e-2), "The kernel execution did not produce the expected result"
        print("The kernel execution produced the expected results!")
    except ValueError as e:
        print(f"Error: {e}")

    # Step 9: Free GPU memory
    gpu_array.free()

# # Initialize CUDA driver
# cuda.init()

def test_invalid_kernel_execution():
    kernel_code = """
    __global__ void invalid_kernel(float *array) {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        array[idx] = idx;
    }
    """
    
    kernel_manager = compile_kernel(kernel_code)
    invalid_kernel = kernel_manager.get_function("invalid_kernel")
    
    shape = (128,)
    dtype = np.float32
    gpu_array = allocate(shape, dtype)
    
    # Get the maximum allowed block size for the current GPU
    device = cuda.Device(0)  # Assume device 0 is being used
    max_threads_per_block = device.get_attributes().get(cuda.device_attribute.MAX_THREADS_PER_BLOCK)
    
    print(f"Max threads per block for device 0: {max_threads_per_block}")
    
    # Set an invalid block size larger than the maximum allowed by the GPU
    block_size = (max_threads_per_block + 1, 1, 1)  # Block size too large
    grid_size = (128, 1, 1)  # Keep grid small
    
    try:
        invalid_kernel(gpu_array.gpu_buffer, block=block_size, grid=grid_size)
        pytest.fail("Invalid kernel launch should have raised an error")
    except cuda.Error as e:
        # Check for the error message indicating the invalid argument
        print(f"Expected error occurred: {e}")
        assert "invalid argument" in str(e), f"Unexpected error: {e}"

    # Free the GPU memory
    gpu_array.free()