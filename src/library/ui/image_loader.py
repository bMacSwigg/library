import io
import logging
import PIL.Image
import urllib.request

class CachedImageLoader:

    def __init__(self):
        self.urlmap = {}
        self.logger = logging.getLogger(__name__)

    def getImage(self, url):
        if url in self.urlmap:
            return self.urlmap[url]
        else:
            img = self._load(url)
            self.urlmap[url] = img
            return img

    def _load(self, url):
        try:
            with urllib.request.urlopen(url) as u:
                data = u.read()
            return PIL.Image.open(io.BytesIO(data))
        except ValueError as e:
            if url:
                self.logger.warning('URL %s could not be loaded' % url)
            return PIL.Image.new('RGB', (128,192), (0,0,0))
