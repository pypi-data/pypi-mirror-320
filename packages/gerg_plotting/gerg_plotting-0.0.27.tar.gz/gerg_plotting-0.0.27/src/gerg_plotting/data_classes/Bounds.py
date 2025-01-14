from attrs import define,field,validators,asdict
from pprint import pformat

from gerg_plotting.modules.validations import lat_min_smaller_than_max,lon_min_smaller_than_max

@define
class Bounds:
    """
    Represents geographic and depth bounds for a spatial dataset.

    Attributes
    ----------
    lat_min : float | int | None
        Minimum latitude of the bounds. Must be smaller than `lat_max`.
    lat_max : float | int | None
        Maximum latitude of the bounds.
    lon_min : float | int | None
        Minimum longitude of the bounds. Must be smaller than `lon_max`.
    lon_max : float | int | None
        Maximum longitude of the bounds.
    depth_bottom : float | int | None
        Maximum depth value (positive, in meters). Represents the bottom of the range.
    depth_top : float | int | None
        Minimum depth value (positive, in meters). Represents the top of the range (e.g., surface).
    vertical_scaler : float | int | None
        A scaling factor applied to depth values. Default is 1.
    vertical_units : str | None
        Units for the vertical depth values. Default is "m".
    """

    lat_min: float | int | None = field(
        default=None,
        validator=[validators.instance_of(float | int | None), lat_min_smaller_than_max]
    )
    lat_max: float | int | None = field(default=None)

    lon_min: float | int | None = field(
        default=None,
        validator=[validators.instance_of(float | int | None), lon_min_smaller_than_max]
    )
    lon_max: float | int | None = field(default=None)

    depth_bottom: float | int | None = field(default=None)  # Maximum depth (in meters)
    depth_top: float | int | None = field(default=None)  # Minimum depth (in meters)

    vertical_scaler: float | int | None = field(default=1)  # Depth scaling factor
    vertical_units: str | None = field(default='m')  # Depth units

    def _has_var(self, key: str) -> bool:
        """
        Checks if a given key is an attribute of the Bounds object.

        Parameters
        ----------
        key : str
            The attribute name to check.

        Returns
        -------
        bool
            True if the attribute exists, False otherwise.
        """
        return key in asdict(self).keys()

    def __getitem__(self, key: str) -> float | int | None:
        """
        Retrieves the value of a given attribute.

        Parameters
        ----------
        key : str
            The name of the attribute.

        Returns
        -------
        float | int | None
            The value of the attribute.

        Raises
        ------
        KeyError
            If the attribute does not exist.
        """
        if self._has_var(key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __setitem__(self, key: str, value: float | int | None) -> None:
        """
        Sets the value of a given attribute.

        Parameters
        ----------
        key : str
            The name of the attribute.
        value : float | int | None
            The new value for the attribute.

        Raises
        ------
        KeyError
            If the attribute does not exist.
        """
        if self._has_var(key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Attribute '{key}' not found")

    def __repr__(self) -> str:
        """
        Generates a string representation of the Bounds object.

        Returns
        -------
        str
            A formatted string showing the attributes and their values.
        """
        # Use `pformat` to create a human-readable representation of the attributes.
        return pformat(asdict(self), indent=1, width=2, compact=True, depth=1)
