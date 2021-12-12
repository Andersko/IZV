#!/usr/bin/env python3.9
# coding=utf-8

""" Containing functions for visualizing data from Czech police department (represented as pandas dataframe structure).

Note:
    Made as school project on VUT FIT to IZV course by Andrej Pavlovič <xpavlo14@vutbr.cz>. 3 out of 4 functions are not
    implemented due to time shortage. :(
"""

import pandas as pd
import numpy as np
import sys


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """ Loads data and transform them to pandas.DataFrame with correct data types.

    If error occurs during opening a file, function exits script.

        Parameters:
            filename : str
                Path to file with data.
            verbose : bool
                If true, on stdout will be printed total size in MB of precessed data before and after converting data
                types to pandas.

        Returns:
            pandas.DataFrame
                Data frame with passed data.
    """
    try:
        df = pd.read_pickle(filename)
    except Exception as e:
        print("run time error: " + format(e), file=sys.stderr)
        exit(-1)
    else:
        if verbose:
            print(f"orig_size={sys.getsizeof(df)/1_048_576:.1f} MB")

        for column in df.columns:
            df[column].replace(r"(^\s*$)", np.NAN, regex=True, inplace=True)
            if column in ["p36", "p37", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
                          "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24",
                          "p27", "p28", "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51",
                          "p52", "p53", "p55a", "p57", "p58", "a", "b", "d", "e", "f", "g", "j", "p5a"]:
                df[column] = pd.to_numeric(df[column], downcast='signed')
            elif column in ["k", "l", "n", "o", "p", "q", "r", "s", "t", "h", "i"]:
                df[column] = df[column].astype('category')
            elif column == "p2a":
                df["date"] = df[column].astype("datetime64[M]")

        if verbose:
            print(f"new_size={sys.getsizeof(df)/1_048_576:.1f} MB")

        return df
