#!/usr/bin/env python3

from typing import Optional
import requests
from requests.exceptions import HTTPError
from json import JSONDecodeError
from datetime import datetime, date
import pytz
from time import sleep
import re
from common import __typeError__
from torrent import Torrent

RATE_LIMIT_PER_SECOND: int = 4
RATE_LIMIT_SLEEP_VALUE: float = 1 / RATE_LIMIT_PER_SECOND

API_URL = 'https://eztv.re/api/get-torrents'


class EZTVApi(object):
    LAST_CHECK: datetime = pytz.utc.localize(datetime.fromtimestamp(0))
    @staticmethod
    def __buildUrl__(limit:Optional[int]=100, page:Optional[int]=1, imdbId: Optional[str]=None) -> str:
        if (limit < 1 or limit > 100):
            errorMessage = "num must be 1-100 inclusive"
            raise ValueError(errorMessage)
        if (imdbId != None):
            url = API_URL + '?imdb_id=%s&limit=%i&page=%i' % (imdbId, limit, page)
        else:
            url = API_URL + '?limit=%i&page=%i' % (limit, page)
        return url

    @classmethod
    def setLastCheck(cls, __value:datetime) -> datetime:
        if (isinstance(__value, datetime) == False):
            __typeError__("value", "datetime", __value)
        returnValue = cls.LAST_CHECK
        if (__value.tzinfo is not None and __value.utcoffset is not None):
            cls.LAST_CHECK = __value.astimezone(pytz.UTC)
        else:
            cls.LAST_CHECK = pytz.utc.localize(__value)
        return returnValue

    @classmethod
    def getLastCheck(cls) -> datetime:
        return cls.LAST_CHECK

    def getTorrents(self, limit:Optional[int]=100, page:Optional[int]=1, imdbId:Optional[str]=None) -> tuple[bool, str | list[Torrent]]:
    # Make the reqest:
        url = self.__buildUrl__(limit=limit, page=page, imdbId=imdbId)
        try:
            response = requests.get(url)
            response.raise_for_status()
            response = response.json()
            self.LAST_CHECK = pytz.utc.localize(datetime.utcnow())
            sleep(RATE_LIMIT_SLEEP_VALUE)
        except HTTPError as e:
            return (False, "HTTPError: %s" % e.strerror)
        except JSONDecodeError as e:
            return (False, "JSONDecodeError: %s" % e.msg)
    # Parse the response:
        torrentList: list[Torrent] = []
        for rawTorrent in response['torrents']:
            torrentList.append( Torrent(rawTorrent) )
        return (True, torrentList)

    def getNew(self, limit:Optional[int]=100, imdbId:Optional[str]=None) -> tuple[bool, str |list[Torrent]]:
        success: bool
        result: list[Torrent] | str
        lastCheck: datetime = self.LAST_CHECK
        success, result = self.getTorrents(limit=limit, imdbId=imdbId)
        if (success == False):
            return (success, result) # Torrents it actuall a string
        return(success, [torrent for torrent in result if torrent.releaseDate > lastCheck])

    def getSeasons(self, limit:Optional[int]=100, page:Optional[int]=1, imdbId:Optional[str]=None) -> tuple[bool, str | list[Torrent]]:
        success: bool
        result: list[Torrent] | str
        success, result = self.getTorrents(limit=limit, page=page, imdbId=imdbId)
        if (success == False):
            return (success, result)
        return (success, [torrent for torrent in result if torrent.isSeason == True])