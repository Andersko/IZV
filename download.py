#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import datetime
import io
import os
import re
import sys
import requests
import zipfile
import gzip
import numpy as np
import pickle as pkl
from bs4 import BeautifulSoup


# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy,
# matplotlib, BeautifulSoup. Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27",
               "p28", "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53",
               "p55a", "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r",
               "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        self.__cache = {region: None for region in list(self.regions.keys())}

        # http paths resolve from html
        self.paths = []
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tr_tag in soup.find_all('tr'):
            self.paths.append(tr_tag.findChildren('button', class_='btn btn-sm btn-primary')[-1]['onclick'][10:-2])

        # download missing files
        if os.path.isdir(folder):
            paths = []

            for path in self.paths:
                if not os.path.isfile(folder + path[4:]):
                    paths.append(path)

            self.download_data(paths)
        else:
            if os.path.isfile(folder):
                os.remove(folder)

            os.mkdir(folder)
            self.download_data(self.paths)

    def download_data(self, paths):
        for path in paths:
            print('Downloading "' + self.url + path + '"')
            with requests.get(self.url + path, stream=True) as resp:
                with open(self.folder + path[4:], 'wb') as file:
                    for chunk in resp.iter_content(chunk_size=128):
                        file.write(chunk)

    def parse_region_data(self, region):
        print('Parsing region "' + region + '" (' + self.regions[region] + ')')

        region_data_lists = {dict_header: [] for dict_header in self.headers}

        # Parsing
        for path in self.paths:
            with zipfile.ZipFile(self.folder + path[4:], 'r') as zipf:
                with zipf.open(self.regions[region] + '.csv', 'r') as csvf:
                    reader = csv.reader(io.TextIOWrapper(csvf, encoding='cp1250'), delimiter=';')
                    for row in reader:
                        for i in [*range(0, 2), 4, *range(6, 31), 32, 41]:
                            region_data_lists[self.headers[i]].append(int(row[i]))

                        for i in [2, 31, 33, *range(35, 41), *range(42, 45), *range(60, 62), 63]:
                            if row[i] == '':
                                region_data_lists[self.headers[i]].append(-1)
                            else:
                                region_data_lists[self.headers[i]].append(int(row[i]))

                        for i in [*range(45, 51)]:
                            try:
                                region_data_lists[self.headers[i]].append(float(re.sub('[,]', '.', row[i], 1)))
                            except ValueError:
                                region_data_lists[self.headers[i]].append(np.nan)

                        for i in [*range(51, 60), 62]:
                            region_data_lists[self.headers[i]].append(row[i])

                        if row[34] == '' or row[34] == 'XX':
                            region_data_lists[self.headers[34]].append(-1)
                        else:
                            region_data_lists[self.headers[34]].append(int(row[34]))

                        parsed_time = row[5].zfill(4)
                        if int(parsed_time[2:]) >= 60 or int(parsed_time[:-2]) >= 24 or int(parsed_time) < 0:
                            region_data_lists[self.headers[5]].append(-1)
                        else:
                            region_data_lists[self.headers[5]].append(int(row[5]))

                        parsed_date = row[3].split('-')
                        try:
                            datetime.datetime(int(parsed_date[0]), int(parsed_date[1]), int(parsed_date[2]))
                            if len(parsed_date) > 3:
                                raise IndexError
                        except ValueError or IndexError:
                            region_data_lists[self.headers[3]].append('')
                        else:
                            region_data_lists[self.headers[3]].append(row[3])

        # Append another list of tags to data
        region_data_lists["region"] = [region] * len(region_data_lists[self.headers[0]])

        # Parsing done, create numpy arrays with correct data types from lists
        region_data_arrays = self.init_region_data_dict()
        for key, value in region_data_arrays.items():
            region_data_arrays[key] = np.concatenate(
                [region_data_arrays[key], np.array(region_data_lists[key], value.dtype)]
            )

        return region_data_arrays

    def init_region_data_dict(self):
        data_types = [np.ulonglong, np.ubyte, np.int_, 'datetime64[D]', np.ubyte, np.short, np.ubyte, np.ubyte,
                      np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ushort, np.ubyte, np.ubyte, np.ubyte, np.int_,
                      np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ubyte,
                      np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.ubyte, np.byte, np.ubyte, np.byte, np.byte,
                      np.byte, np.byte, np.byte, np.byte, np.byte, np.byte, np.int_, np.byte, np.byte, np.byte,
                      np.single, np.single, np.single, np.single, np.single, np.single, 'U60', 'U60', 'a10',
                      'U30', 'U40', 'a30', 'a20', 'U30', 'U30', np.int_, np.int_, 'a40', np.byte, 'a3']

        for i in range(len(data_types)):
            data_types[i] = np.array([], data_types[i])

        return dict(zip(self.headers + ['region'], data_types))

    def get_dict(self, regions=None):
        if not regions:
            regions = list(self.regions.keys())

        for region in regions:
            if region not in list(self.regions.keys()):
                print('Invalid region name', file=sys.stderr)
                exit(-1)

        # Initialize dict(header:np.ndarray(empty)) for concatenation
        regions_data = self.init_region_data_dict()

        for region in regions:
            if region_data := self.__cache[region]:
                pass
            elif region_data := self.load_dict_cache(region):
                self.__cache[region] = region_data
            else:
                region_data = self.parse_region_data(region)
                self.save_dict_cache(region, region_data)
                self.__cache[region] = region_data

            for key in region_data:
                regions_data[key] = np.concatenate([regions_data[key], region_data[key]])

        return regions_data

    def save_dict_cache(self, region, region_data):
        with gzip.open(self.folder + os.path.sep + re.sub('{}', region, self.cache_filename, 1), 'wb', 6) as f:
            pkl.dump(region_data, f)

    def load_dict_cache(self, region):
        try:
            with gzip.open(self.folder + os.path.sep + re.sub('{}', region, self.cache_filename, 1), 'rb', 6) as f:
                return pkl.load(f)
        except FileNotFoundError:
            return False


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)

if __name__ == '__main__':
    DD = DataDownloader()
    d = DD.get_dict(['JHC', 'PLK', 'ULK'])

    print('DataSet info:')
    for header, npArr in d.items():
        print('header/key(' + header + '), npArrType(' + str(npArr.dtype) + '), npArrSize(' + str(npArr.size) +
              '), npArrValues(' + re.sub('\n', ' ', str(npArr)) + ')')

    print('\nThere are ' + str(np.unique(d['region']).size) + ' regions in DataSet: ', end='')
    for region_name in np.unique(d['region']):
        print(region_name.decode('UTF-8') + ' ', end='')
    print()

# Resources
# https://stackoverflow.com/questions/7332841/add-single-element-to-array-in-numpy (second answer)
