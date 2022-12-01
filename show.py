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