import pycuda.driver as cuda
import pycuda.compiler as compiler
import hashlib

class KernelCompilationError(Exception):
    pass

class KernelManager:
    """
    A class to manage CUDA kernel compilation and execution.
    """

    def __init__(self, kernel_source):
        """
        Initialize the kernel manager with CUDA source code.

        Args:
            kernel_source (str): The CUDA kernel source code as a string.
        """
        self.kernel_source = kernel_source
        self.module = None

    def compile(self, options=None):
        """
        Compile the CUDA source code.

        Args:
            options (list): Additional compiler options (e.g., ['--use_fast_math']).
        """
        try:
            self.module = compiler.SourceModule(self.kernel_source, options=options)
        except compiler.CompileError as e:
            raise KernelCompilationError(f"Kernel compilation failed: {e}")

    def get_function(self, function_name):
        """
        Retrieve a compiled CUDA function.

        Args:
            function_name (str): The name of the kernel function.

        Returns:
            pycuda.driver.Function: The compiled CUDA kernel function.
        """
        if self.module is None:
            raise RuntimeError("Kernel source has not been compiled. Call compile() first.")
        return self.module.get_function(function_name)


class KernelCache:
    """
    A kernel caching mechanism to avoid recompilation.
    """
    _cache = {}

    @staticmethod
    def get_or_compile(kernel_source, options=None):
        key = hashlib.md5(kernel_source.encode()).hexdigest()
        if key not in KernelCache._cache:
            kernel_manager = KernelManager(kernel_source)
            kernel_manager.compile(options)
            KernelCache._cache[key] = kernel_manager
        return KernelCache._cache[key]


# Utility function for kernel compilation
def compile_kernel(kernel_source, options=None):
    """
    Compile a CUDA kernel source code.

    Args:
        kernel_source (str): The CUDA kernel source code as a string.
        options (list): Additional compiler options (e.g., ['--use_fast_math']).

    Returns:
        KernelManager: A KernelManager object managing the compiled kernel.
    """
    return KernelCache.get_or_compile(kernel_source, options)
