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
        for show in configs.showList:
            if (torrent.name.find(show.name) > -1):
                if (torrent.quality >= show.minQuality and torrent.quality <= show.maxQuality):
                    if (torrent not in configs.downloadedTorrents):
                        torrent.downloadTorrent(configs.downloadPath)
                        show.seen(torrent)
                        configs.torrentDownloaded(torrent)

        if (configs.downloadPremiere == True and torrent.isPremiere == True):
            if (torrent.quality >= configs.premiereMinQuality and torrent.quality <= configs.premiereMaxQuality):
                if (torrent not in configs.downloadedTorrents):
                    torrent.downloadTorrent(configs.downloadPath)
                    configs.torrentDownloaded(torrent)
        elif (configs.downloadFirstSeason == True and torrent.isFirstSeason == True):
            if (torrent.quality >= configs.firstSeasonMinQuality and torrent.quality <= configs.firstSeasonMaxQuality):
                if (torrent not in configs.downloadedTorrents):
                    torrent.downloadTorrent(configs.downloadPath)
                    configs.torrentDownloaded(torrent)


    exit(0)