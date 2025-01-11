from .request import RequestUtils
from bs4 import BeautifulSoup

class BS4Utils(RequestUtils):
  def __init__(self, **kwargs):
    if "name" not in kwargs:
        kwargs["name"] = (f"{__class__}".split("'")[1])
    self.get_logger(**kwargs)
    self.debug(f"Initialized: {kwargs['name']}")
  
  def get_webpage(self, url):
    content = super().get_webpage(url)
    return BeautifulSoup(content, features="html.parser")