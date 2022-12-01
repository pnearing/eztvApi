#!/usr/bin/env python3
from typing import Any, NoReturn
import requests
################################
# Type checking helper:
################################
def __typeError__(varName:str, validTypeName:str, var:Any) -> NoReturn:
    errorMessage = "%s must be of type %s, not: %s" % (varName, validTypeName, str(type(var)))
    raise TypeError(errorMessage)

################################
# Month Names Long:
################################
MONTH_NAMES_LONG: tuple[str] = ("notamonth", "january", "febuary", "march", "april", "may", "june", "july", "august",
                            "september", "october", "november", "december")
MONTH_NUMBER_BY_LONG_NAME: dict[str, int] = {
    "january": 1, "febuary": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9,
    "october": 10, "november": 11, "december": 12
}
################################
# Month Names Short:
################################
MONTH_NAMES_SHORT: tuple[str] = ("notamonth", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
                                    "nov", "dec")
MONTH_NUMBER_BY_SHORT_NAME: dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11,
    "dec": 12
}

###############################
# Helper funcitons:
###############################
def __downloadFile__(url:str, destFile:str) -> str:
    # Try to open the torrent url:
        try:
            response = requests.get(url)
        except Exception as e:
            errorMessage = "Failed to open url '%s': %s" % (url, str(e.args))
            raise RuntimeError(errorMessage)
    # Try to open the destination file:
        try:
            fileHandle = open(destFile, 'wb')
        except Exception as e:
            errorMessage = "Failed to open '%s' for writing: %s" % (destFile, str(e.args))
            raise RuntimeError(errorMessage)
    # Write the data to the file:
        fileHandle.write(response.content)
        fileHandle.close()
        return destFile
