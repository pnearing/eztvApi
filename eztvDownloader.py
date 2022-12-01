#!/usr/bin/env python3

import os
import feedparser
import re
import requests

from eztvAPI import EZTVApi

# apiUrl = 'https://eztv.re/api/get-torrents?limit=100&page=1'

ezrssUrl = 'https://eztv.re/ezrss.xml'



if __name__ == '__main__':

    api = EZTVApi()
    success, result = api.getNew()

    if (success == False):
        print("ERROR: Failed to fetch torrents: %s" % result)
        exit(1)
    
    for torrent in result:
        print(torrent.title)
        if (torrent.title.find('Secret Nazi Expeditions') > -1):
            if (torrent.quality == torrent.QUALITY_1080P):
                print(torrent.magnet)
                torrent.openMagnet()
    exit(0)