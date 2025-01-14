import matplotlib
import matplotlib.axes
import matplotlib.cm
import matplotlib.colorbar
import matplotlib.figure
import matplotlib.pyplot
from matplotlib.colors import Colormap
import matplotlib.dates as mdates
from attrs import define, field, asdict
from pprint import pformat
import cartopy.crs as ccrs

from gerg_plotting.data_classes.Data import Data
from gerg_plotting.modules.plotting import  colorbar

@define
class Plotter:
    """
    Base class for creating plots of data.

    Parameters
    ----------
    data : Data
        Data object containing variables to plot
    bounds_padding : float
        Padding to be applied to detected bounds
    fig : matplotlib.figure.Figure, optional
        Matplotlib figure object
    ax : matplotlib.axes.Axes, optional
        Matplotlib axes object
    nrows : int
        Number of rows in figure, default is 1
    cbar_nbins : int
        Number of bins for colorbar ticks, default is 5
    cbar_kwargs : dict
        Keyword arguments for colorbar customization

    Attributes
    ----------
    cbar : matplotlib.colorbar.Colorbar
        Colorbar object for the plot
    """
    
    data: Data = field(default=None)
    bounds_padding: float = field(default=0)

    fig: matplotlib.figure.Figure = field(default=None)
    ax: matplotlib.axes.Axes = field(default=None)

    nrows: int = field(default=1)

    cbar: matplotlib.colorbar.Colorbar = field(init=False)
    cbar_nbins: int = field(default=5)
    cbar_kwargs: dict = field(default={})

    def init_figure(self, fig=None, ax=None, figsize=(6.4, 4.8), three_d=False, geography=False) -> None:
        """
        Initialize figure and axes objects.

        Parameters
        ----------
        fig : matplotlib.figure.Figure, optional
            Pre-existing figure
        ax : matplotlib.axes.Axes, optional
            Pre-existing axes
        figsize : tuple, optional
            Figure dimensions (width, height)
        three_d : bool, optional
            Whether to create 3D plot
        geography : bool, optional
            Whether to create map projection

        Raises
        ------
        ValueError
            If both three_d and geography are True
        """
        
        # Guard clause: Ensure three_d and geography are not both True
        if three_d and geography:
            raise ValueError("Cannot set both 'three_d' and 'geography' to True. Choose one.")

        if fig is None and ax is None:
            # Create a new figure and axes
            if geography:
                # Initialize a figure with Cartopy's PlateCarree projection for geographic plots
                self.fig, self.ax = matplotlib.pyplot.subplots(
                    figsize=figsize,
                    subplot_kw={'projection': ccrs.PlateCarree()}
                )
            elif three_d:
                # Initialize a 3D figure
                self.fig, self.ax = matplotlib.pyplot.subplots(
                    figsize=figsize,
                    subplot_kw={'projection': '3d'}
                )
            else:
                # Standard 2D Matplotlib figure with no projection
                self.fig, self.ax = matplotlib.pyplot.subplots(figsize=figsize)
                
        elif fig is not None and ax is not None:
            # Use existing figure and axes
            self.fig = fig
            self.ax = ax
            self.nrows = len(self.fig.axes)  # Update the number of rows based on existing axes

            if three_d:
                # If it's a 3D plot, re-initialize the axes as a 3D plot
                index = [idx for idx, ax in enumerate(self.fig.axes) if ax is self.ax][0] + 1
                self.ax.remove()  # Remove existing 2D axis
                gs = self.ax.get_gridspec()  # Get grid specification
                self.ax = fig.add_subplot(gs.nrows, gs.ncols, index, projection='3d')

    def adjust_datetime_labels(self, rotation=30):
        """
        Adjust datetime labels on x-axis to prevent overlap.

        Parameters
        ----------
        rotation : int, optional
            Rotation angle for labels if overlap detected, default 30
        """
        # Get tick labels
        labels = self.ax.get_xticklabels()
        renderer = self.ax.figure.canvas.get_renderer()
        
        # Get bounding boxes for the labels
        bboxes = [label.get_window_extent(renderer) for label in labels if label.get_text()]
        
        if len(bboxes) < 2:  # No need to check if fewer than two labels
            return
        
        # Check for overlaps
        overlap = any(bboxes[i].overlaps(bboxes[i+1]) for i in range(len(bboxes) - 1))
        
        if overlap:
            # Apply rotation if overlap is detected
            matplotlib.pyplot.setp(labels, rotation=rotation, ha='right')
        else:
            # Ensure labels are not rotated
            matplotlib.pyplot.setp(labels, rotation=0, ha='center')

    def format_axes(self,xlabel,ylabel,zlabel=None,invert_yaxis:bool=False) -> None:
        """
        Format plot axes with labels and options.

        Parameters
        ----------
        xlabel : str
            Label for x-axis
        ylabel : str
            Label for y-axis
        invert_yaxis : bool, optional
            Whether to invert y-axis, default False
        """
        self.ax.set_xlabel(xlabel=xlabel)
        self.ax.set_ylabel(ylabel=ylabel)
        if zlabel is not None:
            self.ax.set_zlabel(zlabel=zlabel)
        if invert_yaxis:
            self.ax.invert_yaxis()
        self.adjust_datetime_labels()

    def get_cmap(self, color_var: str) -> Colormap:
        """
        Get colormap for specified variable.

        Parameters
        ----------
        color_var : str
            Name of variable for colormap

        Returns
        -------
        matplotlib.colors.Colormap
            Colormap for variable
        """
        # Return the variable's assigned colormap, or the default 'viridis' if none exists
        if self.data[color_var].cmap is not None:
            cmap = self.data[color_var].cmap
        else:
            cmap = matplotlib.pyplot.get_cmap('viridis')
        return cmap
    
    def add_colorbar(self, mappable: matplotlib.axes.Axes, var: str | None, divider=None, total_cbars: int = 2) -> None:
        """
        Add colorbar to plot.

        Parameters
        ----------
        mappable : matplotlib.axes.Axes
            Plot object to create colorbar for
        var : str or None
            Variable name for colorbar
        divider : optional
            Axes divider for colorbar positioning
        total_cbars : int, optional
            Total number of colorbars in plot, default 2

        Returns
        -------
        matplotlib.colorbar.Colorbar
            Created colorbar object
        """
        if var is not None:
            # Get the label for the colorbar
            cbar_label = self.data[var].get_label()
            if divider is not None:
                # Create a colorbar using the custom 'colorbar' function with divider
                self.cbar = colorbar(self.fig, divider, mappable, cbar_label, nrows=self.nrows, total_cbars=total_cbars)
            else:
                # Create a standard colorbar
                self.cbar = self.fig.colorbar(mappable, label=cbar_label)

            # Adjust the number of ticks on the colorbar
            self.cbar.ax.locator_params(nbins=self.cbar_nbins)

            # Format the colorbar for time-based variables
            if var == 'time':
                loc = mdates.AutoDateLocator()
                self.cbar.ax.yaxis.set_major_locator(loc)
                self.cbar.ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

            return self.cbar
        
    def save(self,filename,**kwargs):
        """
        Save figure to file.

        Parameters
        ----------
        filename : str
            Path to save figure
        **kwargs
            Additional arguments for savefig

        Raises
        ------
        ValueError
            If no figure exists
        """
        if self.fig is not None:
            self.fig.savefig(fname=filename,**kwargs)
        else:
            raise ValueError('No figure to save')
        
    def show(self):
        '''
        Show all open figures
        '''
        matplotlib.pyplot.show()
        
    def _has_var(self, key) -> bool:
        """
        Check if object has specified variable.

        Parameters
        ----------
        key : str
            Name of variable to check

        Returns
        -------
        bool
            True if variable exists, False otherwise
        """
        return key in asdict(self).keys()
    
    def get_vars(self) -> list:
        """
        Get list of all object variables.

        Returns
        -------
        list
            List of variable names
        """
        return list(asdict(self).keys())

    def __getitem__(self, key: str):
        """
        Enable dictionary-style access to class attributes.

        Parameters
        ----------
        key : str
            Name of attribute to access

        Returns
        -------
        Any
            Value of specified attribute

        Raises
        ------
        KeyError
            If attribute doesn't exist
        """
        if self._has_var(key):
            return getattr(self, key)
        raise KeyError(f"Variable '{key}' not found. Must be one of {self.get_vars()}")  

    def __setitem__(self, key, value) -> None:
        """
        Enable dictionary-style setting of class attributes.

        Parameters
        ----------
        key : str
            Name of attribute to set
        value : Any
            Value to assign to attribute

        Raises
        ------
        KeyError
            If attribute doesn't exist
        """
        if self._has_var(key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Variable '{key}' not found. Must be one of {self.get_vars()}")

    def __repr__(self) -> None:
        """
        Create string representation of class attributes.

        Returns
        -------
        str
            Formatted string of all attributes
        """
        return pformat(asdict(self),width=1)
