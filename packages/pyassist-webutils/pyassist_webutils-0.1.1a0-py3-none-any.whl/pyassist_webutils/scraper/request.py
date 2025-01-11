import requests
from pyassist_utils.utils import Utilities

class RequestUtils(Utilities):
  def __init__(self, **kwargs):
    if "name" not in kwargs:
        kwargs["name"] = (f"{__class__}".split("'")[1])
    self.get_logger(**kwargs)
    self.debug(f"Initialized: {kwargs['name']}")

  def get_webpage(self, url):
    response = requests.get(url)
    return response.content