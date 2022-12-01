#!/usr/bin/env python3

from typing import Optional
from datetime import datetime, date
import pytz
import re
import requests
import os
from subprocess import check_call, CalledProcessError
from common import MONTH_NUMBER_BY_LONG_NAME, MONTH_NUMBER_BY_SHORT_NAME, __downloadFile__
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
    QUALITY_UNKNOWN: int = 0
    QUALITY_240P: int = 1
    QUALITY_360P: int = 2
    QUALITY_480P: int = 3
    QUALITY_540P: int = 4
    QUALITY_720P: int = 5
    QUALITY_1080P: int = 6
    QUALITY_2160P: int = 7
    QUALITY_ANY: int = 8
# Encodings:
    ENCODING_UNKNOWN: str = 'unknown'
    ENCODING_XVID: str = 'xvid'
    ENCODING_H264: str = 'h264'
    ENCODING_H265: str = 'h265'
    ENCODING_X264: str = 'x264'
    ENCODING_X265: str = 'x265'

    def __init__(self,
                    rawData: Optional[dict[str,object]] = None,
                    fromDict: Optional[dict[str, object]] = None,
                ) -> None:
        if (rawData != None):
            self.__fromRawData__(rawData)
        elif (fromDict != None):
            self.__fromDict__(fromDict)
        else:
            errorMessage = "Either rawData or fromDict must be defined."
            raise RuntimeError(errorMessage)
        return

##################
# Init:
##################
    def __fromRawData__(self, rawData: dict[str, object]) -> None:
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
        if (rawData['small_screenshot'] == ''):
            self.smallScreenshot = None
        elif (rawData['small_screenshot'][:6] == 'https:'):
            self.smallScreenshot = rawData['small_screenshot']
        else:
            self.smallScreenshot: str = "https:" + rawData['small_screenshot']
        if (rawData['large_screenshot'] == ''):
            self.largeScreenshot = None
        if (rawData['large_screenshot'][:6] == 'https:'):
            self.largeScreenshot = rawData['large_screenshot']
        else:
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
            print(self.title)
            airedDateYMDMatch = re.match(r'^.*(?P<year>\d{4}) (?P<month>\d+) (?P<day>\d+).*$', self.title )
            airedDateDMYMatch = re.match(r'^.* (?P<day>\d+)(th|st)? (?P<month>\w+) (?P<year>\d{4})', self.title)
            if (airedDateYMDMatch != None):
                self.airedDate = date(int(airedDateYMDMatch['year']), int(airedDateYMDMatch['month']), int(airedDateYMDMatch['day']))
            elif (airedDateDMYMatch != None):
                if (airedDateDMYMatch['month'].lower() in MONTH_NUMBER_BY_SHORT_NAME.keys()):
                    month = MONTH_NUMBER_BY_SHORT_NAME[airedDateDMYMatch['month'].lower()]
                elif (airedDateDMYMatch['month'].lower() in MONTH_NUMBER_BY_LONG_NAME.keys()):
                    month = MONTH_NUMBER_BY_LONG_NAME[airedDateDMYMatch['month'].lower()]
                else:
                    month = None
                if (month == None):
                    self.airedDate = None
                else:
                    self.airedDate = date(int(airedDateDMYMatch['year']), month, int(airedDateDMYMatch['day']))
# Parse season and episode for premiere:
        self.isPremiere: bool = False
        if (self.season == 1 and self.episode == 1):
            self.isPremiere = True
# Parse title for show name:
        print(rawData['title'])

        return

##################
# To / From Dict:
##################
    def __toDict__(self) -> dict[str, object]:
        torrentDict = {
            'id': self.id,
            'hash': self.hash,
            'filename': self.filename,
            'title': self.title,
            'episodeLink': self.episodeLink,
            'torrent': self.torrent,
            'magnet': self.magnet,
            'imdbId': self.imdbId,
            'season': self.season,
            'episode': self.episode,
            'smallScreenshot': self.smallScreenshot,
            'largeScreenshot': self.largeScreenshot,
            'seeds': self.seeds,
            'peers': self.peers,
            'releaseDate': self.releaseDate.timestamp(),
            'size': self.size,
            'isSeason': self.isSeason,
            'quality': self.quality,
            'encoding': self.encoding,
            'airedDate': self.airedDate.isoformat(),
            'isPremiere': self.isPremiere,
        }
        return torrentDict

    def __fromDict__(self, fromDict:dict[str, object]) -> None:
        self.id = fromDict['id']
        self.hash = fromDict['hash']
        self.filename = fromDict['filename']
        self.title = fromDict['title']
        self.episodeLink = fromDict['episodeLink']
        self.torrent = fromDict['torrent']
        self.magnet = fromDict['magnet']
        self.imdbId = fromDict['imdbId']
        self.season = fromDict['season']
        self.episode = fromDict['episode']
        self.smallScreenshot = fromDict['smallScreenshot']
        self.largeScreenshot = fromDict['largeScreenshot']
        self.seeds = fromDict['seeds']
        self.peers = fromDict['peers']
        self.releaseDate = pytz.utc.localize(datetime.fromtimestamp(fromDict['releaseDate']))
        self.size = fromDict['size']
        self.isSeason = fromDict['isSeason']
        self.quality = fromDict['quality']
        self.encoding = fromDict['encoding']
        self.airedDate = date.fromisoformat(fromDict['airedDate'])
        self.isPremiere = fromDict['isPremiere']
##################
# Methods:
##################
    def downloadTorrent(self, destPath:str) -> str:
        """
            Download the torrent file to the directory specified by destPath.
            @param: str, destPath, the directory to download the torrent to.
            @return: str, response. Path to the downloaded file
        """
        filePath = os.path.join(destPath, self.filename)
        __downloadFile__(self.torrent, filePath)
        return filePath
    
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
    
    def downloadSmallScreenshot(self, destPath) -> str:
        """
            Downloads a small screenshot of the torrent.
            @param: str, destPath. Directory to save the screenshot in to.
            @return: str, filePath. Complete path to the downloaded file, or "<NO-SCREENSHOT>" if unavailable.
        """
        if (self.smallScreenshot == None):
            return "<NO-SCREENSHOT>"
        fileName = self.smallScreenshot.split('/')[-1]
        filePath = os.path.join(destPath, fileName)
        __downloadFile__(self.smallScreenshot, filePath)
        return filePath
    
    def downloadLargeScreenshot(self, destPath) -> str:
        """
            Downloads a large screenshot of the torrent.
            @param: str, destPath. Directory to save the screenshot in to.
            @return: str, filePath. Complete path to the downloaded file, or "<NO-SCREENSHOT>" if unavailable.
        """
        if (self.largeScreenshot == None):
            return "<NO-SCREENSHOT>"
        fileName = self.largeScreenshot.split('/')[-1]
        filePath = os.path.join(destPath, fileName)
        __downloadFile__(self.largeScreenshot, filePath)
        return filePath
