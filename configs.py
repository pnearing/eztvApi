#!/usr/bin/env pyton3

from typing import Optional
import os
import json
from datetime import datetime, timedelta
import pytz
from subprocess import check_output, CalledProcessError
from common import __typeError__
from torrent import Torrent
from show import Show

class Configs(object):
    def __init__(self, filePath:str) -> None:
        self._filePath: str = filePath
        self.showList: list[Show] = []
        self.lastUpdate: datetime = pytz.utc.localize(datetime.fromtimestamp(0))
        self.updateInterval: timedelta = timedelta(minutes=15)
        self.downloadPath:str
        try:
            self.downloadPath = check_output(['xdg-user-dir', 'DOWNLOADS']).rstrip()
        except CalledProcessError:
            self.downloadPath = os.environ.get("HOME")
        self.downloadPremiere: bool = True
        try:
            self.__load__()
        except RuntimeError:
            self.__save__()
        return

########################
# Load / Save:
########################
    def __save__(self) -> None:
    # Create config object and json configs string:
        configDict = {
            'showList': [],
            'lastUpdate': self.lastUpdate.timestamp(),
            'updateInterval': self.updateInterval.total_seconds(),
            'downloadPath': self.downloadPath,
            'downloadPremiere': self.downloadPremiere,
        }
        for show in self.showList:
            configDict['showList'].append(show.__toDict__())
        jsonConfigs = json.dumps(configDict)
    # Try to open the file:
        try:
            fileHandle = open(self._filePath, 'w')
        except Exception as e:
            errorMessage = "FATAL: Failed to open '%s' for writing: %s" % (self._filePath, str(e.args))
            raise RuntimeError(errorMessage)
    # Write json to the file and close it:
        fileHandle.write(jsonConfigs)
        fileHandle.close()
        return
    
    def __load__(self) -> None:
    # Try to open the file:
        try:
            fileHandle = open(self._filePath, 'r')
        except Exception as e:
            errorMessage = "FATAL: Failed to open '%s' for reading: %s" % (self._filePath, str(e.args))
            raise RuntimeError(errorMessage)
    # Try to load json:
        try:
            configDict: dict[str, object] = json.loads(fileHandle.read())
            fileHandle.close()
        except json.JSONDecodeError as e:
            errorMessage = "FATAL: Failed to load JSON from '%s': %s" % (self._filePath, e.msg)
            raise RuntimeError(errorMessage)
    # Load values from config dict:
        self.showList = []
        for showDict in configDict['showList']:
            self.showList.append( Show(fromDict=showDict) )
        self.lastUpdate = pytz.utc.localize(datetime.fromtimestamp(configDict['lastUpdate']))
        self.updateInterval = timedelta(seconds=configDict['updateInterval'])
        self.downloadPath = configDict['downloadPath']
        self.downloadPremiere = configDict['downloadPremiere']
        return
########################
# Setters:
########################
    def setDownloadPath(self, __value:str) -> None:
        if (isinstance(__value, str) == False):
            __typeError__("value", "str", __value)
        if (os.path.exists(__value) == False):
            errorMessage = "path '%s' doesn't exist." % __value
            raise FileNotFoundError(errorMessage)
        self.downloadPath = __value
        self.__save__()
        return
    
    def setUpdateInterval(self, __value:int) -> None:
        if (isinstance(__value, int) == False):
            __typeError__("value", "int", __value)
        if (__value < 5):
            errorMessage = "value must be >= 5"
            raise ValueError(errorMessage)
        self.updateInterval = timedelta(minutes=__value)
        self.__save__()
        return

    def setDownloadPremiere(self, __value:bool) -> None:
        if (isinstance(__value, bool) == False):
            __typeError__('value', 'bool', __value)
        self.downloadPremiere = __value
        self.__save__()
        return

###########################
# Methods:
###########################
    def addShow(self,
                    name: str,
                    minQuality:Optional[int]=Torrent.QUALITY_UNKNOWN,
                    maxQuality:Optional[int]=Torrent.QUALITY_ANY
                ) -> Show:
        if (isinstance(name, str) == False):
            __typeError__("name", "str", name)
        if (isinstance(minQuality, int) == False):
            __typeError__("minQuality", "int", minQuality)
        if (isinstance(maxQuality, int) == False):
            __typeError__("maxQuality", "int", maxQuality)
        if (minQuality < Torrent.QUALITY_UNKNOWN or minQuality > Torrent.QUALITY_ANY):
            errorMessage = "minQuality must be in range %i -> %i" % (Torrent.QUALITY_UNKNOWN, Torrent.QUALITY_ANY)
            raise ValueError(errorMessage)
        if (maxQuality < Torrent.QUALITY_UNKNOWN or maxQuality > Torrent.QUALITY_ANY):
            errorMessage = "maxQuality must be in range %i -> %i" % (Torrent.QUALITY_UNKNOWN, Torrent.QUALITY_ANY)
            raise ValueError(errorMessage)
        if (minQuality > maxQuality):
            errorMessage = "minQuality must be less than or equal to maxQuality."
            raise ValueError(errorMessage)
        self.showList.append( Show(name=name, minQuality=minQuality, maxQuality=maxQuality) )
        self.__save__()