import numpy as np

def generate_random_array(shape, dtype=np.float32, min_val=0.0, max_val=1.0):
    """
    Generate a random NumPy array with the specified shape and range.

    Args:
        shape (tuple): Shape of the array.
        dtype (data-type): Data type of the array. Default is np.float32.
        min_val (float): Minimum value of the random range.
        max_val (float): Maximum value of the random range.

    Returns:
        numpy.ndarray: A random array with the specified properties.
    """
    return np.random.uniform(low=min_val, high=max_val, size=shape).astype(dtype)

def compare_arrays(array1, array2, atol=1e-5):
    """
    Compare two arrays element-wise with tolerance. Raise an error if they do not match.

    Args:
        array1 (numpy.ndarray): First array to compare.
        array2 (numpy.ndarray): Second array to compare.
        atol (float): Absolute tolerance for comparison. Default is 1e-5.

    Raises:
        ValueError: If the arrays have different shapes or do not match within the tolerance.

    Returns:
        bool: True if the arrays are equal within the tolerance, False otherwise.
    """
    if array1.shape != array2.shape:
        raise ValueError(f"Array shapes do not match! Array1 shape: {array1.shape}, Array2 shape: {array2.shape}")

    if not np.allclose(array1, array2, atol=atol):
        diff = np.abs(array1 - array2)
        print("Arrays do not match within tolerance. Difference:")
        print(diff)
        raise ValueError("Arrays do not match within the tolerance!")

    return True

def reshape_array(array, new_shape):
    """
    Reshape a NumPy array to a new shape.

    Args:
        array (numpy.ndarray): The array to reshape.
        new_shape (tuple): The desired shape.

    Returns:
        numpy.ndarray: The reshaped array.
    """
    return np.reshape(array, new_shape)

def print_array_summary(array, name="Array"):
    """
    Print a summary of a NumPy array, including shape, dtype, and basic stats.

    Args:
        array (numpy.ndarray): The array to summarize.
        name (str): Name of the array (for display purposes).
    """
    print(f"{name} Summary:")
    print(f"  Shape: {array.shape}")
    print(f"  Data type: {array.dtype}")
    print(f"  Min: {np.min(array):.4f}, Max: {np.max(array):.4f}")
    print(f"  Mean: {np.mean(array):.4f}, Std: {np.std(array):.4f}")
