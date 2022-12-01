|pyversions| |licence|

***eztvApi*** is a Python 3 API for eztv using the requests module
which can be installed on debian based systems using apt install python3-requests

Usage example can be found in eztvDownloader.py

Basic Usage
-----------
..code-block:: python
    from eztvApi import eztvApi
    api = EZTVApi()
    success, results = api.getTorrents()
    if (success == False): # If success is false, results is a string with the error message
        print("ERROR: %s" % results)
    for torrent in results:
        print(torrent.title)

