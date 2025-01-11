import numpy as np
import torch


class ArraySummer:
    def sum_two_arrays(self, array1, array2):
        if isinstance(array1, np.ndarray) and isinstance(array2, np.ndarray):
            return np.add(array1, array2)
        elif isinstance(array1, torch.Tensor) and isinstance(array2, torch.Tensor):
            return torch.add(array1, array2)
        elif isinstance(array1, (list, tuple)) and isinstance(array2, (list, tuple)):
            return [a + b for a, b in zip(array1, array2)]
        else:
            raise TypeError("Both inputs must be either numpy arrays, torch tensors, or lists/tuples of numbers")
