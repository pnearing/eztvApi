#!/usr/bin/env python3

import argparse

from eztvAPI import EZTVApi
from configs import Configs

configFile = '.eztvDownloader'



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="EZTV torrent downloader.")

# Load config:
    configs = Configs(configFile)

    api = EZTVApi()
    success, result = api.getNew()

    if (success == False):
        print("ERROR: Failed to fetch torrents: %s" % result)
        exit(1)
    for torrent in result:
        torrent.downloadSmallScreenshot("/home/streak/Doccuments/eztvApi/")
    exit(0)