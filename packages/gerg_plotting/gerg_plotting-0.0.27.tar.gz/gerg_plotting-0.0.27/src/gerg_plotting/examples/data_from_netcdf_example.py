from gerg_plotting.tools.tools import data_from_netcdf
from gerg_plotting.plotting_classes.Histogram import Histogram
from gerg_plotting.plotting_classes.ScatterPlot import ScatterPlot

import xarray as xr

def data_from_netcdf_example():
    data = data_from_netcdf("example_data/sample_glider_data.nc",
                            interp_glider=True)
        
    hist = Histogram(data)
    hist.plot('lat')
    hist.show()

    scatter = ScatterPlot(data)
    scatter.hovmoller('temperature')
    scatter.show()
    scatter.hovmoller('chlor')
    scatter.show()

if __name__ == "__main__":
    data_from_netcdf_example()