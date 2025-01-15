import pycuda.driver as cuda
import time

class Profiler:
    """
    A utility class for profiling CUDA operations and kernel executions.
    """

    @staticmethod
    def time_kernel(kernel_function, grid, block, *args, **kwargs):
        """
        Measure the execution time of a CUDA kernel.

        Args:
            kernel_function: The compiled CUDA kernel function.
            grid (tuple): Grid dimensions (number of blocks).
            block (tuple): Block dimensions (threads per block).
            *args: Positional arguments to pass to the kernel.
            **kwargs: Keyword arguments (e.g., stream).

        Returns:
            float: Execution time in milliseconds.
        """
        start_event = cuda.Event()
        end_event = cuda.Event()

        start_event.record()
        kernel_function(*args, block=block, grid=grid, **kwargs)
        end_event.record()
        end_event.synchronize()

        return start_event.time_till(end_event)

    @staticmethod
    def time_function(func, *args, **kwargs):
        """
        Measure the execution time of any Python function.

        Args:
            func: The function to time.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            float: Execution time in seconds.
        """
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        return (end_time - start_time) * 1000  # Return time in milliseconds
