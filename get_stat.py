#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt


def plot_stat(data_source, fig_location=None, show_figure=False):
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    x_labels = ["SS na přerušovanou žlutou",
                "SS mimo provoz",
                "dopravními značkami",
                "přenosnými dopravními značkami",
                "neoznačena",
                "žádná"]

    y_labels = list(DataDownloader.regions.keys())

    # data matrices for both graphs
    data1 = np.zeros((6, 14), np.uint)  # Absolute graph
    data2 = np.empty((6, 14), np.half)  # Relative graph

    # Calculate linear values for absolute graph
    for i in range(6):
        for j in range(14):
            data1[i, j] = np.count_nonzero(np.logical_and(
                data_source["p24"] == i,
                data_source["region"] == y_labels[j].encode()
            ))

    # Calculate percentage values for relative graph
    for i in range(6):
        for j in range(14):
            data2[i, j] = np.count_nonzero(np.logical_and(
                data_source["p24"] == i,
                data_source["region"] == y_labels[j].encode())
            ) / np.count_nonzero(data_source["p24"] == i) * 100

    im1 = ax1.imshow(data1)
    im2 = ax2.imshow(data2)

    ax1.set_xticks(np.arange(len(x_labels)))
    ax1.set_yticks(np.arange(len(y_labels)))
    ax2.set_xticks(np.arange(len(x_labels)))
    ax2.set_yticks(np.arange(len(y_labels)))

    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    ax1.set_title("Harvest of local farmers (in tons/year)")
    ax2.set_title("Harvest of local farmers (in tons/year)")
    fig.tight_layout()

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
