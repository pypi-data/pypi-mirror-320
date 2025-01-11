from attrs import define
import numpy as np
import matplotlib.pyplot as plt
from gerg_plotting.plotting_classes.Plotter import Plotter
from gerg_plotting.modules.utilities import calculate_range

@define
class Histogram(Plotter):
    """
    A class for plotting histograms from instrument data using matplotlib.

    This class provides methods for creating 1D, 2D, and 3D histograms from data.
    Inherits from Plotter class for basic plotting functionality.
    """

    def get_2d_range(self, x: str, y: str, **kwargs) -> tuple[list,dict]:
        """
        Calculate or retrieve the range for 2D histograms.

        Parameters
        ----------
        x : str
            Name of the x-axis variable
        y : str
            Name of the y-axis variable
        **kwargs : dict
            Optional keyword arguments including 'range' for custom ranges

        Returns
        -------
        tuple
            (range_list, modified_kwargs)
            - range_list : calculated or provided range values
            - modified_kwargs : kwargs with 'range' removed if present
        """
        # If 'range' is not in kwargs, calculate it based on the instrument data
        if 'range' not in kwargs.keys():
            range = [
                calculate_range(self.data[x].data),  # Calculate range for x variable
                calculate_range(self.data[y].data)   # Calculate range for y variable
            ]
        # If 'range' exists in kwargs, use it and remove it from kwargs
        else:
            range = kwargs['range']  # Retrieve range from kwargs
            kwargs.pop('range')      # Remove 'range' from kwargs
        # Return the range and the modified kwargs (without 'range')
        return range, kwargs

    def plot(self, var: str, fig=None, ax=None, **kwargs) -> None:
        """
        Plot a 1D histogram of the given variable.

        Parameters
        ----------
        var : str
            Name of the variable to plot
        fig : matplotlib.figure.Figure, optional
            Figure object to use for plotting
        ax : matplotlib.axes.Axes, optional
            Axes object to use for plotting
        **kwargs : dict
            Additional keyword arguments passed to matplotlib.pyplot.hist
        """
        # Initialize the figure and axis
        self.init_figure(fig, ax)
        # Plot a histogram of the selected variable data
        self.ax.hist(self.data[var].data, **kwargs)
        # Set the y-axis label to 'Count'
        self.ax.set_ylabel('Count')
        # Set the x-axis label to the variable's label
        self.ax.set_xlabel(self.data[var].get_label())

    def plot2d(self, x: str, y: str, fig=None, ax=None, **kwargs) -> None:
        """
        Plot a 2D histogram for the x and y variables.

        Parameters
        ----------
        x : str
            Name of the x-axis variable
        y : str
            Name of the y-axis variable
        fig : matplotlib.figure.Figure, optional
            Figure object to use for plotting
        ax : matplotlib.axes.Axes, optional
            Axes object to use for plotting
        **kwargs : dict
            Additional keyword arguments passed to matplotlib.pyplot.hist2d
        """
        # Initialize the figure and axis
        self.init_figure(fig, ax)
        # Get the range for the 2D histogram and update kwargs
        range, kwargs = self.get_2d_range(x, y, **kwargs)
        # Plot a 2D histogram using the x and y data
        hist = self.ax.hist2d(self.data[x].data, self.data[y].data, range=range, **kwargs)
        # Set the x-axis label to the x variable's label
        self.ax.set_xlabel(self.data[x].get_label())
        # Set the y-axis label to the y variable's label
        self.ax.set_ylabel(self.data[y].get_label())
        # Add a colorbar to represent the count values
        cbar = plt.colorbar(hist[3], ax=self.ax, label='Count', orientation='horizontal')

    def plot3d(self, x: str, y: str, fig=None, ax=None, **kwargs) -> None:
        """
        Plot a 3D surface plot based on a 2D histogram.

        Parameters
        ----------
        x : str
            Name of the x-axis variable
        y : str
            Name of the y-axis variable
        fig : matplotlib.figure.Figure, optional
            Figure object to use for plotting
        ax : matplotlib.axes.Axes, optional
            Axes object to use for plotting
        **kwargs : dict
            Additional keyword arguments passed to numpy.histogram2d
        """
        # Import the colormap from matplotlib
        from matplotlib import cm
        # Initialize the figure and axis for a 3D plot
        self.init_figure(fig, ax, three_d=True)
        # Get the range for the 2D histogram and update kwargs
        range, kwargs = self.get_2d_range(x, y, **kwargs)
        # Calculate a 2D histogram for the x and y data
        h, xedges, yedges = np.histogram2d(self.data[x].data, self.data[y].data, range=range, **kwargs)
        # Create a mesh grid using the edges of the histogram bins
        X, Y = np.meshgrid(xedges[1:], yedges[1:])
        # Plot a 3D surface plot of the histogram data
        self.ax.plot_surface(X, Y, h, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        # Set the z-axis label to 'Count' and rotate it to face upward
        self.ax.zaxis.set_rotate_label(False)
        self.ax.set_zlabel('Count', rotation=90)
        # Set the x-axis label to the x variable's label
        self.ax.set_xlabel(self.data[x].get_label())
        # Set the y-axis label to the y variable's label
        self.ax.set_ylabel(self.data[y].get_label())
        # Set the initial viewing angle for the 3D plot
        self.ax.view_init(elev=30, azim=45)
