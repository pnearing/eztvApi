#!/usr/bin/env python3

from typing import Optional
import requests
from requests.exceptions import HTTPError
from json import JSONDecodeError
from datetime import datetime
import pytz
from time import sleep
from common import __typeError__
from torrent import Torrent

RATE_LIMIT_PER_SECOND: int = 4
RATE_LIMIT_SLEEP_VALUE: float = 1 / RATE_LIMIT_PER_SECOND

API_URL = 'https://eztv.re/api/get-torrents'

class EZTVApi(object):
    """Class to request torrents from the EZTV web api."""
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
        """Sets the last checked datetime property.
            @param: value, a datetime, if timezone unaware it defaults to UTC
            @return: a datetime, the previous last check value."""
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
        """Returns the datetime timezone aware (utc) of the last time the torrents were checked.
            Initializes to the epoch."""
        return cls.LAST_CHECK

    def getTorrents(self, limit:Optional[int]=100, page:Optional[int]=1, imdbId:Optional[str]=None) -> tuple[bool, str | list[Torrent]]:
        """
            Get a list of torrents from eztv.
            @param: limit: Optional[int], The maximum number of torrents to return. Valid values: 1-100 inclusive.
            @param: page: Optional[int], The page to retrieve. Valid values > 0.
            @param: imdbId: Optional[str], the imdb id of a show, retreives only episodes from that show.
            @return: tuple[bool, str | list[Torrent]],
                    returnValue[0]:bool, success, True if torrents were successfully retreived. False if an HTTP or JSON error occurs.
                    returnValue[1]: str | list[Torrent], results. If success (returnValue[0]) is False, then results is a string with the accoring error message.
                                                                  If success (returnValue[0]) is True, then results is a list of Torrent objects.
        """
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

    def getNew(self, limit:Optional[int]=100) -> tuple[bool, str |list[Torrent]]:
        """
            Get new torrents since last check time.
            @param: int, limit. Maximum number of torrents to retrieve. Valid values: 1-100
            @return: tuple[bool, str | list[Torrent]]
                returnValue[0]: bool, success. True if torrents were successfully retrieved, False if an HTTP or JSON error occured.
                returnValue[1]: str | list[Torrent], results.
                            if success (returnValue[0]) == False then results is a string containg the error message.
                            if success (returnValue[0]) == True then results is a list of Torrent objects.
        """
        success: bool
        result: list[Torrent] | str
        lastCheck: datetime = self.LAST_CHECK
        success, result = self.getTorrents(limit=limit)
        if (success == False):
            return (success, result) # Torrents it actuall a string
        return(success, [torrent for torrent in result if torrent.releaseDate > lastCheck])

    def getSeasons(self, limit:Optional[int]=100, page:Optional[int]=1, imdbId:Optional[str]=None) -> tuple[bool, str | list[Torrent]]:
        """
            Get season packs.
            @param: int, limit. Maximum number of torrents to retrieve. Valid values: 1-100
            @param: int, page. Page to retreive.
            @param: str, imdb id. IMDB id of the show to retreive.
            @return: tuple[bool, str | list[Torrent]]
                returnValue[0]: bool, success. True if torrents were successfully retreived, False if an HTTP or JSON error occured.
                returnValue[1]: str | list[Torrent], results.
                    if success (returnValue[0]) == False then results is a string with the error message.
                    if success (returnValue[0]) == True, then reuslts is a list of Torrent objects.
        """
        success: bool
        result: list[Torrent] | str
        success, result = self.getTorrents(limit=limit, page=page, imdbId=imdbId)
        if (success == False):
            return (success, result)
        return (success, [torrent for torrent in result if torrent.isSeason == True])