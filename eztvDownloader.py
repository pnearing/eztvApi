#!/usr/bin/env python3

import argparse

from eztvAPI import EZTVApi
from configs import Configs
from torrent import Torrent

configFile = '.eztvDownloader'



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="EZTV torrent downloader.")
    parser.add_argument('--addShow', help='--addShow, Add a show to the download list.Requires --name, --minQuality, --maxQuality', action='store_true')
    parser.add_argument('--name', help='--name NAME, show name.')
    parser.add_argument('--minQuality', help='--minQuality QUALITY (0-8)', type=int)
    parser.add_argument('--maxQuality', help='--maxQuality QUALITY (0-8)', type=int)
    parser.add_argument('--config', help='--config, Set config option, reqires one of: --firstEpisode, --firstSeason, --downloadPath', action='store_true')
    parser.add_argument('--firstEpisode', help='--firstEpisode BOOL, Download first episodes.', type=bool)
    parser.add_argument('--firstSeason', help='--firstSeason BOOL, Download first seasons', type=bool)
    parser.add_argument('--downloadPath', help='--downloadPath PATH, Directory to download files to.', type=str)
    args = parser.parse_args()

# Load config:
    configs = Configs(configFile)

# Add Show:
    if (args.addShow == True):
        error: bool = False
        if (args.name == None):
            print("ERROR: --name is required.")
            error = True
        if (args.minQuality == None):
            print("ERROR: --minQuality is required.")
            error = True
        if (args.maxQuality == None):
            print("ERROR: --maxQuality is required.")
            error = True
        if (error == True):
            parser.print_help()
            exit(1)
        configs.addShow(name=args.name, minQuality=args.minQuality, maxQuality=args.maxQuality)
        exit(0)
# Configs:
    elif (args.config == True):
        if (args.firstEpisode == None and args.firstSeason == None and args.downloadPath == None):
            print ("ERROR: --config requires at least one of --firstEpisode, --firstSeason, --downloadPath to be set.")
            parser.print_help()
            exit(1)
        if (args.firstEpisode != None):
            configs.setDownloadPremiere(args.firstEpisode)
        if (args.firstSeason != None):
            configs.setDownloadFirstSeason(args.firstSeason)
        if (args.downloadPath != None):
            configs.setDownloadPath(args.downloadPath)
        exit (0)









    api = EZTVApi()
    success, result = api.getNew()

    if (success == False):
        print("ERROR: Failed to fetch torrents: %s" % result)
        exit(1)
    torrentsToDownload:list[Torrent] = []
    for torrent in result:
        for show in configs.showList:
            if (torrent.name.lower().find(show.name.lower()) > -1):
                if (torrent.quality >= show.minQuality and torrent.quality <= show.maxQuality):
                    if (torrent not in configs.downloadedTorrents):
                        print("Downloading '%s'..." % torrent.title)
                        torrent.downloadTorrent(configs.downloadPath)
                        torrentsToDownload.append(torrent)
                        show.seen(torrent)

        if (configs.downloadPremiere == True and torrent.isPremiere == True):
            if (torrent.quality >= configs.premiereMinQuality and torrent.quality <= configs.premiereMaxQuality):
                if (torrent not in configs.downloadedTorrents):
                    print("Downloading '%s'..." % torrent.title)
                    torrentsToDownload.append(torrent)
        elif (configs.downloadFirstSeason == True and torrent.isFirstSeason == True):
            if (torrent.quality >= configs.firstSeasonMinQuality and torrent.quality <= configs.firstSeasonMaxQuality):
                if (torrent not in configs.downloadedTorrents):
                    print("Downloading '%s'..." % torrent.title)
                    torrentsToDownload.append(torrent)
    for torrent in torrentsToDownload:
        torrent.downloadTorrent(configs.downloadPath)
        configs.torrentDownloaded(torrent)


    exit(0)