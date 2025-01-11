import numpy as np


def lat_min_smaller_than_max(instance, attribute, value) -> None:
    """
    Validate that minimum latitude is smaller than maximum latitude.

    Parameters
    ----------
    instance : object
        The class instance being validated
    attribute : attrs.Attribute
        The attribute being validated
    value : float or None
        The value to validate

    Raises
    ------
    ValueError
        If lat_min is greater than or equal to lat_max
    """
    if value is not None:
        if value >= instance.lat_max:
            raise ValueError("'lat_min' must be smaller than 'lat_max'")


def lon_min_smaller_than_max(instance, attribute, value) -> None:
    """
    Validate that minimum longitude is smaller than maximum longitude.

    Parameters
    ----------
    instance : object
        The class instance being validated
    attribute : attrs.Attribute
        The attribute being validated
    value : float or None
        The value to validate

    Raises
    ------
    ValueError
        If lon_min is greater than or equal to lon_max
    """
    if value is not None:
        if value >= instance.lon_max:
            raise ValueError("'lon_min' must be smaller than 'lon_max'")


def is_flat_numpy_array(instance, attribute, value) -> None:
    """
    Validate that a value is a 1-dimensional NumPy array.

    Parameters
    ----------
    instance : object
        The class instance being validated
    attribute : attrs.Attribute
        The attribute being validated
    value : array_like
        The value to validate

    Raises
    ------
    ValueError
        If value is not a NumPy array or is not 1-dimensional
    """
    if not isinstance(value, np.ndarray):
        raise ValueError(f"{attribute.name} must be a NumPy array or a list convertible to a NumPy array")
    if value.ndim != 1:
        raise ValueError(f"{attribute.name} must be a flat array")
