from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler
from scrapy.core.downloader.contextfactory import BrowserLikeContextFactory

class CustomHttpsHandler(HTTP11DownloadHandler):
    def __init__(self, settings, crawler=None):
        contextFactory = BrowserLikeContextFactory()
        super().__init__(settings, crawler)
        self._contextFactory = contextFactory
