from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import xarray as xr

from pygridsio.grid import Grid
from pygridsio.grid_to_xarray import grids_to_xarray, read_grid
from pygridsio.resources.netherlands_shapefile.shapefile_plot_util import get_netherlands_shapefile


def zoom_on_grid(ax, grid=None, z=None, x=None, y=None, zoom_buffer=10000):
    if grid is not None:
        z = grid.z
        x = grid.gridx
        y = grid.gridy

    # if all values are nan simply return
    if np.isnan(z).all():
        return

    not_nan_locs = np.argwhere(~np.isnan(z))
    x_all = []
    y_all = []
    for coords in not_nan_locs:
        x_all.append(coords[1])
        y_all.append(coords[0])

    minx = x[np.min(x_all)]
    maxx = x[np.max(x_all)]
    miny = y[np.min(y_all)]
    maxy = y[np.max(y_all)]
    ax.set_xlim([minx - zoom_buffer, maxx + zoom_buffer])
    ax.set_ylim([miny - zoom_buffer, maxy + zoom_buffer])
    ax.set_xlim([minx - zoom_buffer, maxx + zoom_buffer])
    ax.set_ylim([miny - zoom_buffer, maxy + zoom_buffer])


def plot_grid(grid: Grid | xr.DataArray | xr.Dataset, axes=None, outfile=None, show=False, cmap="viridis", vmin=None, vmax=None, zoom=True, zoom_buffer=10000, custom_shapefile=None, add_netherlands_shapefile=False,
              shapefile_alpha=0.5):
    """
    Plot a custom grid class

    Parameters
    ----------
    grid
        The grid object; either custom or a xarray.DataArray
    ax (optional)
        An axes object to plot the grid onto; if not provided a figure and axes object will be created
    outfile (optional)
        The file to save the figure to; if not provided then will show instead of save the figure
    cmap (optional)
        The colour map to use; if not provided matplotlib default will be used
    vmin (optional)
        The minimum value for the colourmap
    vmax (optional)
        The maximum value for the colourmap
    zoom (optional)
        Zoom onto the non-nan part of the grid.
    zoom_buffer (optional)
        A space around the non-nan part of the grid to be added if zoom is applied
    add_netherlands_shapefile (optional)
        Adds a shapefile of the netherlands to the background of the plot
    shapefile_alpha (optional)
        Controls the transparency of the shapefile

    Returns
    -------

    """
    NGrids = 1
    if type(grid) == Grid:
        grid = grids_to_xarray([grid], labels=["grid1"])
    elif type(grid) == xr.DataArray:
        if len(grid.dims) == 2:
            NGrids = 1
        else:
            NGrids = len(grid.grid)
    elif type(grid) == xr.Dataset:
        raise TypeError("Datasets are not yet supported for grid plotting. Plot each grid variable individually instead.")

    # sort out the list of axes objects
    if axes is None:
        fig, axes_list = plt.subplots(1, NGrids, figsize=(6 * NGrids, 5))
        if NGrids == 1:
            axes_list = [axes_list]
    else:
        if type(axes) == list or type(axes) == np.ndarray:
            axes_list = axes
        else:
            axes_list = [axes]

    # plot each grid
    for i in range(NGrids):
        if NGrids == 1:
            grid.plot(ax=axes_list[i], x="x", y="y", cmap=cmap, vmin=vmin, vmax=vmax)
        else:
            grid.isel(grid=i).plot(ax=axes_list[i], x="x", y="y", cmap=cmap, vmin=vmin, vmax=vmax)
        if zoom:
            zoom_on_grid(axes_list[i], z=grid.data, x=grid.x, y=grid.y, zoom_buffer=zoom_buffer)
        axes_list[i].tick_params(axis='both', which='major', labelsize=8)

    if add_netherlands_shapefile:
        shapefile = get_netherlands_shapefile()
        [shapefile.plot(ax=ax, alpha=shapefile_alpha, edgecolor="k", zorder=-1) for ax in axes_list]

    if custom_shapefile is not None:
        [custom_shapefile.plot(ax=ax, alpha=shapefile_alpha, edgecolor="k", zorder=-1) for ax in axes_list]

    if outfile is not None:
        plt.savefig(outfile)

    if show:
        plt.show()


def plot_grid_comparison(grid1: Grid | str | Path, grid2: Grid | str | Path, outfile: str | Path, custom_shapefile=None, add_netherlands_shapefile=False, title1=None, title2=None, suptitle=None):
    if type(grid1) is not Grid:
        grid1 = read_grid(grid1)
    if type(grid2) is not Grid:
        grid2 = read_grid(grid2)
    if type(grid1) is not Grid or type(grid2) is not Grid:
        raise ValueError("Provided grids must be the custom grid type")

    # setup figure
    fig, axes = plt.subplots(ncols=3, nrows=2, figsize=(20, 8), height_ratios=[1, 0.5])
    grid_axes = [axes[0][0], axes[0][1], axes[0][2]]
    hist_axes = [axes[1][0], axes[1][1], axes[1][2]]
    fig.tight_layout(pad=5)

    diff_grid = grid1 - grid2
    grids = grids_to_xarray([grid1, grid2, diff_grid], labels=["grid1", "grid2", "grid difference"])

    # plotting the individual grids with the same values on the colour bars
    cmaps = ["viridis", "viridis", "coolwarm"]

    mins = []
    maxs = []
    if not np.isnan(grid1.z).all():
        mins.append(np.nanmin(grid1.z))
        maxs.append(np.nanmax(grid1.z))
    if not np.isnan(grid2.z).all():
        mins.append(np.nanmin(grid2.z))
        maxs.append(np.nanmax(grid2.z))
    if len(mins) == 0:
        mins = [1.0]
        maxs = [1.0]
    vmin, vmax = np.min(mins), np.max(maxs)

    if not np.isnan(diff_grid.z).all():
        max_abs_val = np.nanmax(np.abs(diff_grid.z))
    else:
        max_abs_val = 1.0

    plot_grid(grids.isel(grid=0), axes=grid_axes[0], cmap=cmaps[0], vmin=vmin, vmax=vmax, zoom=True, custom_shapefile=custom_shapefile, add_netherlands_shapefile=add_netherlands_shapefile)
    plot_grid(grids.isel(grid=1), axes=grid_axes[1], cmap=cmaps[1], vmin=vmin, vmax=vmax, zoom=True, custom_shapefile=custom_shapefile, add_netherlands_shapefile=add_netherlands_shapefile)
    plot_grid(grids.isel(grid=2), axes=grid_axes[2], cmap=cmaps[2], vmin=-max_abs_val, vmax=max_abs_val, zoom=True, custom_shapefile=custom_shapefile, add_netherlands_shapefile=add_netherlands_shapefile)

    # make histograms
    vmins = [vmin, vmin, -max_abs_val]
    vmaxs = [vmax, vmax, max_abs_val]
    for i in range(3):
        data = grids.isel(grid=i).data
        data = data[~np.isnan(data)]
        data = data.flatten()
        n, bins, patches = hist_axes[i].hist(data, bins=20)
        if i < 2:
            hist_axes[i].set_xlim(left=vmin, right=vmax)

        # Create a gradient color effect
        for j, p in enumerate(patches):
            cm = plt.get_cmap(cmaps[i])
            norm = mpl.colors.Normalize(vmin=vmins[i], vmax=vmaxs[i])
            plt.setp(p, 'facecolor', cm(norm(bins[j])))

    # add in the histogram from the other grid in the background:
    def add_background_hist(ax, data):
        data = data[~np.isnan(data)]
        data = data.flatten()
        ax.hist(data, bins=20, zorder=-1, color="lightgrey")

    add_background_hist(hist_axes[0], grids.isel(grid=1).data)
    add_background_hist(hist_axes[1], grids.isel(grid=0).data)

    # make titles
    minmax_string1 = f"min: {np.nanmin(grid1.z):.3f} max: {np.nanmax(grid1.z):.3f}"
    if title1 is None:
        grid_axes[0].set_title("grid 1")
    else:
        grid_axes[0].set_title(f"{title1}\n{minmax_string1}")

    minmax_string2 = f"min: {np.nanmin(grid1.z):.3f} max: {np.nanmax(grid1.z):.3f}"
    if title2 is None:
        grid_axes[1].set_title("grid 2")
    else:
        grid_axes[1].set_title(f"{title2}\n{minmax_string2}")

    if suptitle is not None:
        plt.suptitle(suptitle)
    addon = ""
    if not np.isnan(diff_grid.z).all():
        addon = f"\nmin: {np.nanmin(diff_grid.z):.3f} max: {np.nanmax(diff_grid.z):.3f}"
    grid_axes[2].set_title(f"difference (grid1 - grid2)" + addon)
    plt.savefig(outfile)
    plt.close()
