#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import zipfile, os, requests, re

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).

class DataDownloader:
    """ TODO: dokumentacni retezce

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

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

        resp = requests.get(self.url)
        paths = re.findall('<td><button href="#" onclick="download\(\'(data/[datagisrok\-0-9]*\.zip)\'\)" class="btn btn-sm btn-primary">ZIP</button></td>', resp.text)

        if os.path.isdir(folder):
            paths_to_download = []

            for path in paths:
                if not os.path.isfile(folder + path[4:]):
                    paths_to_download.append(path)

            self.download_data(paths_to_download)
        else:
            if os.path.isfile(folder):
                os.remove(folder)

            os.mkdir(folder)
            self.download_data(paths)

    def download_data(self, paths):
        for path in paths:
            print('Downloading: ' + self.url + path)
            with requests.get(self.url + path, stream=True) as resp:
                with open(self.folder + path[4:], 'wb') as file:
                    for chunk in resp.iter_content(chunk_size=128):
                        file.write(chunk)

    def parse_region_data(self, region):
        pass

    def get_dict(self, regions=None):
        pass


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)

DataDownloader = DataDownloader()
# DataDownloader.download_data()

        # try:
        #     os.mkdir(self.folder)
        # except FileExistsError:
        #     pass  # File already exists

