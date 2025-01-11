from .bs4 import BeautifulSoup, BS4Utils
from pandas import DataFrame, read_html, concat, read_csv

class PandasScrapperUtils(BS4Utils):
  def __init__(self, **kwargs):
    if "name" not in kwargs:
        kwargs["name"] = (f"{__class__}".split("'")[1])
    self.get_logger(**kwargs)
    self.debug(f"Initialized: {kwargs['name']}")

  def get_links_in_table(self, table):
    return [a["href"] for a in table.find_all("a", href=True)]

  def get_links_from_tables(self, page_content: str, first: bool = True):
    soup = BeautifulSoup(page_content, features="html.parser")
    if first:
      table = soup.find("table")
      return self.get_links_in_table(table)
    else:
      tables = soup.find_all("table")
      links = []
      for table in tables:
        links.append(self.get_links_in_table(table))
      return links

  def extract_single_table_from_url(self, url: str):
    page_content = super().get_webpage(url)
    return read_html(page_content)[0]

  def extract_single_table_and_links_from_url(self, url: str):
    page_content = super().get_webpage(url)
    links = self.get_links_from_tables(page_content)
    return read_html(page_content)[0], links

  def extract_multiple_tables_with_links_from_url(self, url: str):
    page_content = self.get_webpage(url)
    links = self.get_links_from_tables(page_content, first=False)
    return read_html(page_content), links

  def extract_multiple_tables_from_url(self, url: str):
    page_content = self.get_webpage(url)
    return read_html(page_content)
