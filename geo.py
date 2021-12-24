#!/usr/bin/python3.8
# coding=utf-8

import os
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import sklearn.cluster
import sklearn.mixture

# muzete pridat vlastni knihovny

# Primárně se počítá, že budete pracovat s následujícími externími knihovnami: numpy,
# pandas, seaborn, matplotlib, scipy, scikit-learn, geopandas, contextily a použijete techniky
# představené na přednáškách. Můžete použít libovolné knihovny zmíněné na přednáškách,
# další pouze po schválení.  Nyní nejste omezeni, zda musíte používat Seaborn, Matplotlib
# a podobně. Volba knihoven a nástrojů je jen na vás.


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """
    Converts pandas.DataFrarme into pandas.GeoDataFrame with correct EPSG coding.

    Rows in data frame with invalid coordinates (np.nan) are deleted. CRS is set to "EPSG:5514".

    Parameters:
        df : pd.DataFrame
            Data frame to be converted.

    Returns:
        geopandas.GeoDataFrame
            Converted data frame.
    """

    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")

    # Drop rows with non-valid values
    gdf.drop(gdf[np.isnan(gdf.d) | np.isnan(gdf.e)].index, inplace=True)

    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None, show_figure: bool = False):
    """
    Plot 6 maps visualizing accidents position for years 2018-2020 both for highways and first class roads for VYS
    region.

    Parameters:
        gdf : pd.geoDataFrame
            Data.
        fig_location : str
            Path to save the figure, if None, figure is not saved.
        show_figure : bool
            If true, figure window is shown.
    """

    gdf = gdf[gdf["region"] == "VYS"]
    # Turn off warning for chained assignment
    pd.options.mode.chained_assignment = None
    gdf["p2a"] = pd.to_datetime(gdf["p2a"])
    gdf = gdf.to_crs("EPSG:3857")

    fig, axs = plt.subplots(3, 2, figsize=(11, 12))
    axs = axs.flatten()

    dt2018 = pd.to_datetime("2018-01-01 00:00:00")
    dt2019 = pd.to_datetime("2019-01-01 00:00:00")
    dt2020 = pd.to_datetime("2020-01-01 00:00:00")
    dt2021 = pd.to_datetime("2021-01-01 00:00:00")

    # Plot accidents into map
    gdf[(gdf["p36"] == 0) & (gdf["p2a"] >= dt2018) & (gdf["p2a"] < dt2019)].plot(
        ax=axs[0], markersize=1, color="tab:green", label="nehody VYS kraj: dialnice (2018)", alpha=0.5)
    gdf[(gdf["p36"] == 1) & (gdf["p2a"] >= dt2018) & (gdf["p2a"] < dt2019)].plot(
        ax=axs[1], markersize=1, color="tab:red", label="nehody VYS kraj: cesty prvej triedy (2018)", alpha=0.5)
    gdf[(gdf["p36"] == 0) & (gdf["p2a"] >= dt2019) & (gdf["p2a"] < dt2020)].plot(
        ax=axs[2], markersize=1, color="tab:green", label="nehody VYS kraj: dialnice (2019)", alpha=0.5)
    gdf[(gdf["p36"] == 1) & (gdf["p2a"] >= dt2019) & (gdf["p2a"] < dt2020)].plot(
        ax=axs[3], markersize=1, color="tab:red", label="nehody VYS kraj: cesty prvej triedy (2019)", alpha=0.5)
    gdf[(gdf["p36"] == 0) & (gdf["p2a"] >= dt2020) & (gdf["p2a"] < dt2021)].plot(
        ax=axs[4], markersize=1, color="tab:green", label="nehody VYS kraj: dialnice (2020)", alpha=0.5)
    gdf[(gdf["p36"] == 1) & (gdf["p2a"] >= dt2020) & (gdf["p2a"] < dt2021)].plot(
        ax=axs[5], markersize=1, color="tab:red", label="nehody VYS kraj: cesty prvej triedy (2020)", alpha=0.5)

    # Set basemap and styling
    for ax in axs:
        ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.CartoDB.Voyager)
        ax.axis("off")
        ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()

    if fig_location:
        path = ''
        folders = fig_location.split(os.path.sep)[:-1]

        for folder in folders:
            if not os.path.isdir(path := os.path.join(path, folder)):
                os.mkdir(path)

        plt.savefig(fig_location)

    if show_figure:
        plt.show()

    plt.close(fig)


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None, show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    pass


if __name__ == "__main__":
    print("reading pickle and creating GeoDataFrame...")
    gdf = make_geo(pd.read_pickle("ignore_data/3/accidents.pkl.gz"))

    print("plot_geo...")
    plot_geo(gdf, "geo.png", True)

    print("plot_cluster...")
    plot_cluster(gdf, "cluster.png", True)
