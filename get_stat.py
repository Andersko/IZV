#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

def plot_stat(data_source, fig_location=None, show_figure=False):
    y_labels = ["žádná",
                "SS na přerušovanou žlutou",
                "SS mimo provoz",
                "dopravními značkami",
                "přenosnými dopravními značkami",
                "neoznačena"]

    x_labels = list(DataDownloader.regions.keys())

    # Data matrices for both graphs
    data1 = np.zeros((len(y_labels), len(x_labels)), np.uint)    # Absolute graph
    data2 = np.empty((len(y_labels), len(x_labels)), np.single)  # Relative graph

    # Calculate linear values for absolute graph
    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            data1[i, j] = np.count_nonzero(np.logical_and(
                data_source["p24"] == i,
                data_source["region"] == x_labels[j].encode()
            ))

    # Calculate percentage values for relative graph
    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            data2[i, j] = data1[i, j] / np.sum(data_source["p24"] == i) * 100

    # Create masked arrays (to mask zero data spots to white color)
    data1_masked = np.ma.masked_where(data1 == 0, data1)
    data2_masked = np.ma.masked_where(data2 == 0, data2)

    plt.rcParams.update({'font.size': 8})

    fig, (ax1, ax2) = plt.subplots(2)

    im1 = ax1.imshow(data1_masked, norm=LogNorm())
    im2 = ax2.imshow(data2_masked)

    ax1.set_xticks(np.arange(len(x_labels)))
    ax1.set_yticks(np.arange(len(y_labels)))
    ax2.set_xticks(np.arange(len(x_labels)))
    ax2.set_yticks(np.arange(len(y_labels)))

    ax1.set_xticklabels(x_labels)
    ax1.set_yticklabels(y_labels)
    ax2.set_xticklabels(x_labels)
    ax2.set_yticklabels(y_labels)

    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    ax1.set_title("Absolutně")
    ax2.set_title("Relativně vůči příčině")

    # Create color bars
    cbar1 = ax1.figure.colorbar(im1, ax=ax1)
    cbar2 = ax2.figure.colorbar(im2, ax=ax2)
    cbar1.ax.set_ylabel("Počet nehod [log]", rotation=-90, va="bottom")
    cbar2.ax.set_ylabel("Podíl nehod pro danou příčinu [%]", rotation=-90, va="bottom")
    cbar1.ax.minorticks_off()

    # Without this line
    # UserWarning: Warning: converting a masked element to nan.
    ax1.xaxis_date()

    fig.tight_layout()

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


if __name__ == '__main__':
    import argparse
    from download import DataDownloader

    parser = argparse.ArgumentParser()

    parser.add_argument("--fig_location")
    parser.add_argument("--show_figure")

    args = parser.parse_args()
    fig_location = args.fig_location
    show_figure = args.show_figure

    data_source = DataDownloader().get_dict()

    plot_stat(data_source, fig_location, show_figure)
