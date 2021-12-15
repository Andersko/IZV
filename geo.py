#!/usr/bin/python3.8
# coding=utf-8

import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily
import sklearn.cluster
import numpy as np

# muzete pridat vlastni knihovny

# Primárně se počítá, že budete pracovat s následujícími externími knihovnami: numpy,
# pandas, seaborn, matplotlib, scipy, scikit-learn, geopandas, contextily a použijete techniky
# představené na přednáškách. Můžete použít libovolné knihovny zmíněné na přednáškách,
# další pouze po schválení.  Nyní nejste omezeni, zda musíte používat Seaborn, Matplotlib
# a podobně. Volba knihoven a nástrojů je jen na vás.


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """
    Converts pandas.DataFrarme into pandas.GeoDataFrame with correct EPSG coding.

    Rows in data frame with invalid coordinates (np.nan) are deleted.

    Parameters:
        df : pd.DataFrame
            Data frame to be converted.
    """

    print("creating GeoDataFrame...")
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["f"]), crs="EPSG:5514") # TODO dobry crs?

    # Drop rows with non-valid values
    gdf.drop(gdf[np.isnan(gdf.d) | np.isnan(gdf.e)].index, inplace=True)

    return gdf

def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None, show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody
     (dalnice vs prvni trida) pro roky 2018-2020 """
    pass

def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None, show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    pass

if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    print("reading pickle...")
    gdf = make_geo(pd.read_pickle("ignore_data/3/accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
