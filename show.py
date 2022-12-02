#!/usr/bin/env python3

from typing import Optional

from torrent import Torrent

class Show(object):
    def __init__(self,
                    fromDict: Optional[dict[str, object]],
                    name: Optional[str] = '',
                    minQuality: Optional[int] = Torrent.QUALITY_UNKNOWN,
                    maxQuality: Optional[int] = Torrent.QUALITY_ANY,
                ) -> None:
    # Set properties:
        self.name: str = name
        self.minQuality: int = minQuality
        self.maxQuality: int = maxQuality
        self.lastSeason: int = 0
        self.lastEpisode: int = 0
    # Parse from Dict:
        if (fromDict != None):
            self.__fromDict__(fromDict)
        return
    
##########################
# To / From Dict:
##########################
    def __toDict__(self) -> dict[str, object]:
        showDict = {
            'name': self.name,
            'minQuality': self.minQuality,
            'maxQuality': self.maxQuality,
            'lastSeason': self.lastSeason,
            'lastEpisode': self.lastEpisode,
        }
        return showDict
    
    def __fromDict__(self, fromDict:dict[str,object]) -> None:
        self.name = fromDict['name']
        self.minQuality = fromDict['minQuality']
        self.maxQuality = fromDict['maxQuality']
        self.lastSeason = fromDict['lastSeason']
        self.lastEpisode = fromDict['lastEpisode']
        return

#####################
# Helpers:
#####################
    def seen(self, torrent:Torrent):
        if (self.lastSeason < torrent.season):
            self.lastSeason = torrent.season
        if (self.lastEpisode < torrent.episode):
            self.lastEpisode = torrent.episode
        return