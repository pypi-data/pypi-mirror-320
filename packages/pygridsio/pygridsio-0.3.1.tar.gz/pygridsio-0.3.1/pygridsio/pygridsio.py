from pathlib import Path

import xarray as xr

from pygridsio.grid import Grid
from pygridsio.grid_to_xarray import grid_to_xarray, grids_to_xarray, grids_to_xarray_dataset
from pygridsio.netcdfIO import read_netcdf_to_custom_grid, write_to_netcdf_raster


def read_grid(filename: str | Path, grid_format : str = None) -> Grid:
    """providing the filename of a grid (in either .asc or .zmap) read in the grid and return a grid object
    Parameters
    ----------
    filename

    Returns
    -------
        A custom Grid object
    """
    if Path(filename).suffix == '.nc':
        return read_netcdf_to_custom_grid(filename)
    return Grid(str(filename), grid_format = grid_format)


def read_grid_to_xarray(filename: str | Path, grid_format : str = None) -> xr.DataArray:
    """providing the filename of a grid (in either .asc or .zmap) read in the grid and
    return an xarray object with dimensions: x, y, grid

    Parameters
    ----------
    filename

    Returns
    -------
        A xr.DataArray object
    """
    return grid_to_xarray(read_grid(filename, grid_format))


def read_grids_to_xarray(filenames: list[str] | list[Path], labels: list[str] | None = None, grid_template: Grid | str | Path = None, grid_format : str = None) -> xr.DataArray:
    """providing a list of filenames of multiple grids (in either .asc or .zmap) read in each grid and return
    a xarray object with dimensions:
    -x, y, grid
    -All grids must have the same dimensions.
    -Optionally: provide a list of labels, to name each grid under the xarray "grid" dimension.

    Parameters
    ----------
    filenames
    labels

    Returns
    -------

    """
    grids = [read_grid(filename, grid_format) for filename in filenames]
    if labels is None:
        labels = [Path(filename).stem for filename in filenames]

    if grid_template is not None and type(grid_template) is not Grid:
        grid_template = read_grid(grid_template)

    return grids_to_xarray(grids, labels=labels, grid_template=grid_template)


def read_grids_to_xarray_dataset(filenames: list[str] | list[Path], labels: list | None = None, grid_template: Grid | str | Path = None, grid_format : str = None) -> xr.Dataset:
    """providing a list of filenames of multiple grids (in either .asc or .zmap) read in each grid and return
    a xarray object with dimensions:
    -x, y, grid
    -All grids must have the same dimensions.
    -Optionally: provide a list of labels, to name each grid under the xarray "grid" dimension.

    Parameters
    ----------
    grid_template
    filenames
    labels

    Returns
    -------

    """
    grids = [read_grid(filename, grid_format) for filename in filenames]
    if labels is None:
        labels = [Path(filename).stem for filename in filenames]

    if grid_template is not None and type(grid_template) is not Grid:
        grid_template = read_grid(grid_template)

    return grids_to_xarray_dataset(grids, labels=labels, grid_template=grid_template)

def write_grid(grids : Grid | xr.DataArray | xr.Dataset, filename : Path):
    """Write grid to .asc, .zmap or .nc, currently only the custom Grid class supports writing to .asc and .zmap"""
    if type(filename) is not Path:
        filename = Path(filename)
    if filename.suffix in [".asc",".zmap"] and type(grids) is not Grid:
        raise ValueError("Only custom Grid classes are supported for writing to .asc or .zmap")
    if filename.suffix == ".nc":
        write_to_netcdf_raster(grids,filename)
        return
    grids.write(str(filename))