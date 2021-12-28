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

    fig, axs = plt.subplots(3, 2, figsize=(9, 7))
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
    """
    Plot map visualizing accidents positions for first class roads for VYS region grouping them into clusters.

    Parameters:
        gdf : pd.geoDataFrame
            Data.
        fig_location : str
            Path to save the figure, if None, figure is not saved.
        show_figure : bool
            If true, figure window is shown.
    """

    gdf = gdf[(gdf["region"] == "VYS") & (gdf["p36"] == 1)]
    gdf = gdf.to_crs("EPSG:3857")

    coords = np.dstack([gdf.geometry.x, gdf.geometry.y]).reshape(-1, 2)
    # Skúšal som iba toto, vyšlo mi to na prvý pokus celkom správne, aj algoritmus ale aj počet clusterov 25 je jediný
    # čo som skúsil, vychádzalo mi to viac-menej pekne keď som si na druhý graf na porovnanie dal zobraziť nehody vo VYS
    # na c. 1. triedy všetky v datasete a nastavil si nízku alphu 0.1 tak som to porovnával okom a prišlo mi že to
    # zhlukovanie sa mi spravilo pekne, zhluky s nižšou farbou boli v porovnávanom grafe alfou skoro úplne prázdne,
    # ešte som si to potom skúsil pustiť pre JHM a porovnal so vzorovým grafom zo zadania a celkom sa podobali až na pár
    # menších rozdielov
    model = sklearn.cluster.MiniBatchKMeans(n_clusters=25)
    db = model.fit(coords)
    gdf["cluster"] = db.labels_
    gdf["cnt"] = gdf.groupby("cluster")["cluster"].transform("count")

    fig, ax = plt.subplots(figsize=(8, 7))

    gdf.plot(ax=ax, column="cnt", legend=True, markersize=2)
    ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.CartoDB.Voyager)
    ax.axis("off")

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


if __name__ == "__main__":
    print("reading pickle and creating GeoDataFrame...")
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))

    print("plot_geo...")
    plot_geo(gdf, "geo.png", True)

    print("plot_cluster...")
    plot_cluster(gdf, "cluster.png", True)
