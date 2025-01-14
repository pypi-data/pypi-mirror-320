import math
import numpy as np
from attrs import define,field,asdict
from pprint import pformat
import cmocean
from typing import Iterable
from scipy.signal import welch
import matplotlib.dates as mdates
import copy


from gerg_plotting.modules.calculations import rotate_vector
from gerg_plotting.modules.filters import filter_nan
from gerg_plotting.modules.utilities import calculate_pad


from gerg_plotting.data_classes.Bounds import Bounds
from gerg_plotting.data_classes.Variable import Variable


@define(slots=False,repr=False)
class Data:
    """
    Represents a spatial dataset with various oceanographic or atmospheric variables.

    Attributes
    ----------
    lat : Iterable | Variable | None
        Latitude values or Variable object containing latitude data
    lon : Iterable | Variable | None
        Longitude values or Variable object containing longitude data
    depth : Iterable | Variable | None
        Depth values or Variable object containing depth data
    time : Iterable | Variable | None
        Time values or Variable object containing temporal data
    bounds : Bounds, optional
        Geographic and depth bounds for the dataset
    custom_variables : dict
        Dictionary to store additional custom variables
    temperature : Iterable, Variable, or None, optional
        Temperature data, in °C, with optional colormap and range specifications.
    salinity : Iterable, Variable, or None, optional
        Salinity data with optional colormap and range specifications.
    density : Iterable, Variable, or None, optional
        Density data, in kg/m³, with optional colormap and range specifications.
    u : Iterable, Variable, or None, optional
        Zonal velocity (u-component) in m/s, with optional colormap and range specifications.
    v : Iterable, Variable, or None, optional
        Meridional velocity (v-component) in m/s, with optional colormap and range specifications.
    w : Iterable, Variable, or None, optional
        Vertical velocity (w-component) in m/s, with optional colormap and range specifications.
    speed : Iterable, Variable, or None, optional
        Speed data, derived or directly assigned, in m/s, with optional colormap and range specifications.
    chlor : Iterable, Variable, or None, optional
        Chlorophyll data, in μg/L, with optional colormap and range specifications.
    cdom : Iterable, Variable, or None, optional
        CDOM data, in ppb, with optional colormap and range specifications.
    turbidity : Iterable, Variable, or None, optional
        Turbidity data, in m-1 sr-1, with optional colormap and range specifications.
    bounds : Bounds
        Spatial bounds of the data.
    """
    # Dims
    lat: Iterable|Variable|None = field(default=None)
    lon: Iterable|Variable|None = field(default=None)
    depth: Iterable|Variable|None = field(default=None)
    time: Iterable|Variable|None = field(default=None)
    # Vars
    temperature: Iterable|Variable|None = field(default=None)
    salinity: Iterable|Variable|None = field(default=None)
    density: Iterable|Variable|None = field(default=None)
    u: Iterable|Variable|None = field(default=None)
    v: Iterable|Variable|None = field(default=None)
    w: Iterable|Variable|None = field(default=None)
    speed: Iterable|Variable|None = field(default=None)
    cdom: Iterable|Variable|None = field(default=None)
    chlor: Iterable|Variable|None = field(default=None)
    turbidity: Iterable|Variable|None = field(default=None)

    # Bounds
    bounds:Bounds = field(default=None)
    
    # Custom variables dictionary to hold dynamically added variables
    custom_variables: dict = field(factory=dict)


    def __attrs_post_init__(self) -> None:
        """
        Post-initialization hook for setting up variables.

        This method is automatically called after the class is instantiated.
        """
        self._init_dims()
        self._format_datetime()
        self._init_variables()  # Init variables


    def _init_variables(self) -> None:
        """
        Initialize default variables with predefined configurations.

        Adds colormaps, units, and variable-specific ranges for default variables.
        """
        self._init_variable(var='temperature', cmap=cmocean.cm.thermal, units='°C', vmin=None, vmax=None)
        self._init_variable(var='salinity', cmap=cmocean.cm.haline, units=None, vmin=None, vmax=None)
        self._init_variable(var='density', cmap=cmocean.cm.dense, units="kg/m\u00B3", vmin=None, vmax=None)
        self._init_variable(var='u', cmap=cmocean.cm.balance, units="m/s", vmin=None, vmax=None)
        self._init_variable(var='v', cmap=cmocean.cm.balance, units="m/s", vmin=None, vmax=None)
        self._init_variable(var='w', cmap=cmocean.cm.balance, units="m/s", vmin=None, vmax=None)
        self._init_variable(var='speed', cmap=cmocean.cm.speed, units="m/s", vmin=None, vmax=None)
        self._init_variable(var='cdom', cmap=cmocean.cm.matter, units="ppb", vmin=None, vmax=None)
        self._init_variable(var='chlor', cmap=cmocean.cm.algae, units="μg/L", vmin=None, vmax=None)
        self._init_variable(var='turbidity', cmap=cmocean.cm.turbid, units="m-1 sr-1", vmin=None, vmax=None)


    def calculate_speed(self,include_w:bool=False) -> None:
        """
        Calculate the speed from velocity components.

        Parameters
        ----------
        include_w : bool, optional
            If True, includes the vertical velocity (w-component) in the speed calculation.
            Defaults to False.
        """
        if self.speed is None:
            if include_w:
                if self.check_for_vars(['u','v','w']):
                    self.speed = np.sqrt(self.u.data**2 + self.v.data**2 + self.w.data**2)
                    self._init_variable(var='speed', cmap=cmocean.cm.speed, units="m/s", vmin=None, vmax=None)  
            if self.check_for_vars(['u','v']):
                self.speed = np.sqrt(self.u.data**2 + self.v.data**2)
                self._init_variable(var='speed', cmap=cmocean.cm.speed, units="m/s", vmin=None, vmax=None)


    def calcluate_PSD(self,sampling_freq,segment_length,theta_rad=None) -> tuple[np.ndarray,np.ndarray,np.ndarray]|tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
        """
        Calculate the power spectral density (PSD) using Welch's method.

        Parameters
        ----------
        sampling_freq : float
            Sampling frequency of the data in Hz.
        segment_length : int
            Length of each segment for Welch's method.
        theta_rad : float, optional
            Angle of rotation in radians. Rotates the u and v components if specified.

        Returns
        -------
        tuple
            A tuple containing the frequency array and PSD values for the velocity components.
            If the vertical component (w) is available, it is also included in the tuple.
        """

        u = self.u.data
        v = self.v.data
        if self.w is not None:
            w = self.w.data
        else:
            w = None

        # Rotate vectors if needed
        if theta_rad is not None:
            u,v = rotate_vector(u,v,theta_rad)

        # Filter out NaNs
        u = filter_nan(u)
        v = filter_nan(v)
        if w is not None:
            w = filter_nan(w)

        freq, psd_U = welch(u**2, fs=sampling_freq, nperseg=segment_length)
        _, psd_V = welch(v**2, fs=sampling_freq, nperseg=segment_length)
        if w is not None:
            _, psd_W = welch(w**2, fs=sampling_freq, nperseg=segment_length)

        # Register the new variables
        self.add_custom_variable(Variable(name='psd_freq',data=freq,cmap=cmocean.cm.thermal,units='cpd',label='Power Spectra Density Frequency (cpd)'),exist_ok=True)
        self.add_custom_variable(Variable(name='psd_u',data=psd_U,cmap=cmocean.cm.thermal,units='cm²/s²/cpd',label='Power Spectra Density U (cm²/s²/cpd)'),exist_ok=True)
        self.add_custom_variable(Variable(name='psd_v',data=psd_V,cmap=cmocean.cm.thermal,units='cm²/s²/cpd',label='Power Spectra Density V (cm²/s²/cpd)'),exist_ok=True)

        if w is None:
            return freq,psd_U,psd_V
        elif w is not None:
            self.add_custom_variable(Variable(name='psd_w',data=psd_W,cmap=cmocean.cm.thermal,units='cm²/s²/cpd',label='Power Spectra Density W (cm²/s²/cpd)'),exist_ok=True)
            return freq,psd_U,psd_V,psd_W
        

    def copy(self):
        """Creates a deep copy of the instrument object."""
        self_copy = copy.deepcopy(self)
        return self_copy
    

    def slice_var(self,var:str,slice:slice) -> np.ndarray:
        """Slices data for a specific variable."""
        return self[var].data[slice]


    def _has_var(self, key) -> bool:
        """Checks if a variable exists in the instrument."""
        return key in asdict(self).keys() or key in self.custom_variables
    

    def get_vars(self) -> list:
        """Gets a list of all available variables."""
        vars = list(asdict(self).keys()) + list(self.custom_variables.keys())
        vars = [var for var in vars if var!='custom_variables']
        return vars


    def __getitem__(self, key) -> Variable:
        """Allows accessing standard and custom variables via indexing."""
        if isinstance(key,slice):
            self_copy = self.copy()
            for var_name in self.get_vars():
                if isinstance(self_copy[var_name],Variable):
                    self_copy[var_name].data = self.slice_var(var=var_name,slice=key)
            return self_copy
        elif isinstance(key,list):
            self_copy = self.copy()
            for var_name in self.get_vars():
                if isinstance(self_copy[var_name],Variable):
                    self_copy[var_name].data = self[var_name].data[key]
            return self_copy
        elif self._has_var(key):
            return getattr(self, key, self.custom_variables.get(key))
        raise KeyError(f"Variable '{key}' not found. Must be one of {self.get_vars()}")    


    def __setitem__(self, key, value) -> None:
        """Allows setting standard and custom variables via indexing."""
        if self._has_var(key):
            if key in asdict(self):
                setattr(self, key, value)
            else:
                self.custom_variables[key] = value
        else:
            raise KeyError(f"Variable '{key}' not found. Must be one of {self.get_vars()}")


    def __repr__(self) -> None:
        '''Pretty printing'''
        return pformat(asdict(self),width=1)
    

    def _init_dims(self):
        """Initialize standard dimensions (lat, lon, depth, time) as Variable objects."""
        self._init_variable(var='lat', cmap=cmocean.cm.haline, units='°N', vmin=None, vmax=None)
        self._init_variable(var='lon', cmap=cmocean.cm.thermal, units='°E', vmin=None, vmax=None)
        self._init_variable(var='depth', cmap=cmocean.cm.deep, units='m', vmin=None, vmax=None)
        self._init_variable(var='time', cmap=cmocean.cm.thermal, units=None, vmin=None, vmax=None)

    def _format_datetime(self) -> None:
        """Format datetime data as numpy datetime64 objects."""
        if self.time is not None:
            if self.time.data is not None:
                self.time.data = self.time.data.astype('datetime64[ns]')

    def _init_variable(self, var: str, cmap, units, vmin, vmax) -> None:
        """
        Initialize a standard variable as a Variable object.

        Parameters
        ----------
        var : str
            Name of the variable to initialize
        cmap : matplotlib.colors.Colormap
            Colormap for variable visualization
        units : str
            Units of the variable
        vmin : float | None
            Minimum value for visualization
        vmax : float | None
            Maximum value for visualization
        """        
        if self._has_var(var):
            if not isinstance(self[var],Variable):
                if self[var] is not None:    
                    self[var] = Variable(
                        data=self[var],
                        name=var,
                        cmap=cmap,
                        units=units,
                        vmin=vmin,
                        vmax=vmax
                    )
        else:
            raise ValueError(f'{var} does not exist, try using the add_custom_variable method')
        
        
    def check_for_vars(self,vars:list) -> bool:
        """
        Verify that all required variables exist in the dataset.

        Parameters
        ----------
        vars : list
            List of variable names to check

        Returns
        -------
        bool
            True if all variables exist

        Raises
        ------
        ValueError
            If any required variables are missing
        """
        if len(vars) == 0:
            raise ValueError('No variables provided')
        vars = [var for var in vars if var is not None]
        vars = [var for var in vars if self[var] is None]
        if vars:
            raise ValueError(
                f"The following required variables are missing: {', '.join(vars)}. "
                "Please ensure the Data object includes data for all listed variables."
            )
        return True


    def date2num(self) -> list:
        """Converts time data to numerical values."""
        if self.time is not None:
            if self.time.data is not None:
                return list(mdates.date2num(self.time.data))
        else: raise ValueError('time variable not present')


    def detect_bounds(self,bounds_padding=0) -> Bounds:
        '''
        Detect the geographic bounds of the data, applying padding if specified.

        An intentional effect of this function:
            will only calculate the bounds when self.bounds is None,
            so that it does not overwrite the user's custom bounds,
            this will also ensure that the bounds is not repeatedly calculated unless desired,
            can recalculate self.bounds using a new bounds_padding value if self.bounds is set to None

        The depth bounds are not affected by the bounds padding, therfore the max and min values of the depth data are used

        Parameters
        ----------
        bounds_padding : float, optional
            Padding to add to the detected bounds, by default 0

        Returns
        -------
        Bounds
            Object containing the detected geographic and depth bounds
        """

        '''
        # If the user did not pass bounds
        if self.bounds is None:
            # Detect and calculate the lat bounds with padding
            if self.lat is not None:
                lat_min, lat_max = calculate_pad(self.lat.data, pad=bounds_padding)
            else:
                lat_min, lat_max = None, None
            # Detect and calculate the lon bounds with padding
            if self.lon is not None:
                lon_min, lon_max = calculate_pad(self.lon.data, pad=bounds_padding)
            else:
                lon_min, lon_max = None, None
            
            # depth_bottom: positive depth example: 1000
            # depth_top:positive depth example for surface: 0
            
            if self.depth is not None:
                depth_top, depth_bottom = calculate_pad(self.depth.data)
            else:
                depth_top, depth_bottom = None,None
                
            # Set the bounds
            self.bounds = Bounds(
                lat_min=lat_min,
                lat_max=lat_max,
                lon_min=lon_min,
                lon_max=lon_max,
                depth_bottom=depth_bottom,
                depth_top=depth_top
            )

        return self.bounds


    def add_custom_variable(self, variable: Variable, exist_ok:bool=False) -> None:
        """
        Add a custom Variable object accessible via both dot and dict syntax.

        Parameters
        ----------
        variable : Variable
            The Variable object to add
        exist_ok : bool, optional
            If True, replace existing variable if it exists, by default False

        Raises
        ------
        TypeError
            If provided object is not a Variable instance
        AttributeError
            If variable name already exists and exist_ok is False
        """
        if not isinstance(variable, Variable):
            raise TypeError(f"The provided object is not an instance of the Variable class.")
        
        if hasattr(self, variable.name) and not exist_ok:
            raise AttributeError(f"The variable '{variable.name}' already exists.")
        else:
            # Add to custom_variables and dynamically create the attribute
            self.custom_variables[variable.name] = variable
            setattr(self, variable.name, variable)


    def remove_custom_variable(self,variable_name) -> None:
        """
        Remove a custom variable from the instrument.

        Parameters
        ----------
        variable_name : str
            Name of the variable to remove
        """
        if variable_name in self.custom_variables:
            del self.custom_variables[variable_name]
        else:
            raise KeyError(f"Variable '{variable_name}' not found in custom variables. Must be one of {self.custom_variables.keys()}")