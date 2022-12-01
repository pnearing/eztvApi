#!/usr/bin/env python3

from typing import Optional
from datetime import datetime, date
import pytz
import re

class Torrent(object):
    QUALITY_UNKNOWN: str = 'unknown'
    QUALITY_240P: str = '240p'
    QUALITY_360P: str = '360p'
    QUALITY_480P: str = '480p'
    QUALITY_540P: str = '540p'
    QUALITY_720P: str = '720p'
    QUALITY_1080P: str = '1080p'
    QUALITY_2160P: str = '2160p'

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
        if (re.match(r'2160[pP]', self.title) != None):
            self.quality = self.QUALITY_2160P
        elif (re.match(r'1080[pP]', self.title) != None):
            self.quality = self.QUALITY_1080P
        elif (re.match(r'720[pP]', self.title) != None):
            self.quality = self.QUALITY_720P
        elif (re.match(r'540[pP]', self.title) != None):
            self.quality = self.QUALITY_540P
        elif (re.match(r'360[pP]', self.title) != None):
            self.quality = self.QUALITY_360P
        elif (re.match(r'240[pP]', self.title) != None):
            self.quality = self.QUALITY_240P
        else:
            self.quality = self.QUALITY_UNKNOWN
# Parse title for aired date
        self.airedDate: Optional[date] = None
        if (self.episode == 0 and self.season == 0):
            airedDateRegex = re.compile(r'(?P<year>2\d{3}) (?P<month>\d+) (?P<day>\d+)')
            airedDateMatch = airedDateRegex.match(self.title)
            if (airedDateMatch != None):
                self.airedDate = date(airedDateMatch['year'], airedDateMatch['month'], airedDateMatch['day'])

        return
