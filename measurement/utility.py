from numpy import newaxis, concatenate


class NoMeasurementError(RuntimeError):
    pass


def _expand_arrays_to_2_dims(obj, slicer=None):
    """Adds an extra dimension to arrays (in dictionaries), when arrays have only one dimension. This makes handling
     the arrays uniformly easier. Recursive function.
     Parameters
        ----------
        obj : dict, ndarray
            The object to convert. Either a dictionary of ndarrays or an ndarray.
     """

    if isinstance(obj, dict):
        return {name: _expand_arrays_to_2_dims(obj[name], slicer) for name in obj.keys()}
    elif obj.ndim < 2:
        return obj[newaxis, slicer]
    else:
        return obj[slicer]


def _concatenate(obj1, obj2):
    if obj1 is None:
        return obj2
    elif isinstance(obj1, tuple):
        assert isinstance(obj2, tuple), "Both objects must be of the same type"
        return tuple((_concatenate(o1, o2) for o1, o2 in zip(obj1, obj2)))
    elif isinstance(obj1, dict):
        assert isinstance(obj2, dict), "Both objects must be of the same type"
        return {name: _concatenate(obj1[name], obj2[name]) for name in obj1.keys()}
    else:
        return concatenate((obj1, obj2), axis=0)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
