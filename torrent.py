#!/usr/bin/env python3

from typing import Optional
from datetime import datetime, date
import pytz
import re
import requests
import shutil
import os
from subprocess import check_call, CalledProcessError

class Torrent(object):
    """
        Class to store a single torrent from EZTV.
    
        Stores all the details available from EZTV.

    Types:
        Quality types: str
            QUALITY_UNKNOWN
            QUALITY_240P
            QUALITY_360P
            QUALITY_480P
            QUALITY_540P
            QUALITY_720P
            QUALITY_1080P
            QUALITY_2160P
        Encoding types:
            ENCODING_UNKNOWN
            ENCODING_XVID
            ENCODING_H264
            ENCODING_H265
            ENCODING_X264
            ENCODING_X265
    
        Methods:
            downloadTorrent(destPath) Downloads the torrent to the directory specified.
            openMagnet() Uses xdg-open to open the torrent magnet link in the preferred torrent client.
    """
# Qualities:
    QUALITY_UNKNOWN: str = 'unknown'
    QUALITY_240P: str = '240p'
    QUALITY_360P: str = '360p'
    QUALITY_480P: str = '480p'
    QUALITY_540P: str = '540p'
    QUALITY_720P: str = '720p'
    QUALITY_1080P: str = '1080p'
    QUALITY_2160P: str = '2160p'
# Encodings:
    ENCODING_UNKNOWN: str = 'unknown'
    ENCODING_XVID: str = 'xvid'
    ENCODING_H264: str = 'h264'
    ENCODING_H265: str = 'h265'
    ENCODING_X264: str = 'x264'
    ENCODING_X265: str = 'x265'

    def __init__(self, rawData:dict[str,object]):
# Parse and store raw data:
        self.id: int = rawData['id']
        self.hash: str = rawData['hash']
        self.filename: str = rawData['filename']
        self.title: str = rawData['title']
        self.episodeLink: str = rawData['episode_url']
        self.torrent: str = rawData['torrent_url']
        self.magnet: str = rawData['magnet_url']
        self.imdbId: str = rawData['imdb_id']
        self.season: int = int(rawData['season'])
        self.episode: int = int(rawData['episode'])
        self.smallScreenshot: str = "https:" + rawData['small_screenshot']
        self.largeScreenshot: str = "https:" + rawData['large_screenshot']
        self.seeds: int = rawData['seeds']
        self.peers: int = rawData['peers']
        self.releaseDate = pytz.utc.localize(datetime.fromtimestamp(rawData['date_released_unix']))
        self.size: int = rawData['size_bytes']
# Check if this is a whole season download:
        self.isSeason: bool = False
        if (self.season != 0 and self.episode == 0):
            self.isSeason = True
# Parse title for quality:
        self.quality: str
        if (self.title.lower().find('2160p') > -1):
            self.quality = self.QUALITY_2160P
        elif (self.title.lower().find('1080p') > -1):
            self.quality = self.QUALITY_1080P
        elif (self.title.lower().find('720p') > -1):
            self.quality = self.QUALITY_720P
        elif (self.title.lower().find('540p') > -1):
            self.quality = self.QUALITY_540P
        elif (self.title.lower().find('360p') > -1):
            self.quality = self.QUALITY_360P
        elif (self.title.lower().find('240p') > -1):
            self.quality = self.QUALITY_240P
        else:
            self.quality = self.QUALITY_UNKNOWN
# Parse title for encoding:
        self.encoding: str
        if (self.title.lower().find('x264') > -1):
            self.encoding = self.ENCODING_X264
        elif (self.title.lower().find('x265') > -1):
            self.encoding = self.ENCODING_X265
        elif (self.title.lower().find('xvid') > -1):
            self.encoding = self.ENCODING_XVID
        elif (self.title.lower().find('h264') > -1):
            self.encoding = self.ENCODING_H264
        elif (self.title.lower().find('h265') > -1):
            self.encoding = self.ENCODING_H265
        else:
            self.encoding = self.ENCODING_UNKNOWN
# Parse title for aired date
        self.airedDate: Optional[date] = None
        if (self.episode == 0 and self.season == 0):
            airedDateRegex = re.compile(r'(?P<year>2\d{3}) (?P<month>\d+) (?P<day>\d+)')
            airedDateMatch = airedDateRegex.match(self.title)
            if (airedDateMatch != None):
                self.airedDate = date(airedDateMatch['year'], airedDateMatch['month'], airedDateMatch['day'])
        return

##################
# Methods:
##################
    def downloadTorrent(self, destPath:str) -> tuple[bool, str]:
        """
            Download the torrent file to the directory specified by destPath.
            @param: str, destPath, the directory to download the torrent to.
            @return: tuple[bool, str]
                returnValue[0], bool, success. True if the torrent was successfully downloaded. False if not.
                returnValue[1], str, response.
                    if success (returnValue[0]) == True response is the file path.
                    if success (returnValue[1]) == False response is an error message.
        """
        filePath = os.path.join(destPath, self.filename)
    # Try to open the torrent url:
        try:
            response = requests.get(self.torrent)
        except Exception as e:
            errorMessage = "Failed to open url '%s': %s" % (self.torrent, str(e.args))
            return (False, errorMessage)
    # Try to open the destination file:
        try:
            fileHandle = open(filePath, 'wb')
        except Exception as e:
            errorMessage = "Failed to open '%s' for writing: %s" % (filePath, str(e.args))
            return (False, errorMessage)
    # Write the data to the file:
        fileHandle.write(response.content)
        fileHandle.close()
        return (True, filePath)
    
    def openMagnet(self) -> bool:
        """
            Calls xdg-open to open the prefered torrent client on linux.
            @return: bool, success. True if the magnet was successfuly opened. False if not.
        """
        try:
            check_call(['xdg-open', self.magnet])
        except CalledProcessError:
            return False
        return True
