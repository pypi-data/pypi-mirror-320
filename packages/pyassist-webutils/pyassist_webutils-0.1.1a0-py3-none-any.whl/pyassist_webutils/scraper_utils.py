import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait
from pandas import DataFrame, read_html, concat, read_csv
from datetime import datetime

from pyassist_utils.utils import Utilities






def format_name(name: str):
  return name.replace(" ", "-").lower()


def iloc(df: DataFrame, row: int, col: int):
  try:
    return str(df.iloc[row, col])
  except IndexError:
    return ""
  except AttributeError:
    return ""