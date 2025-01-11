from selenium.webdriver.common.by import By

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FireFoxService
# from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver import ChromeOptions, Chrome, Remote
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as BraveService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .bs4 import BeautifulSoup, BS4Utils

class Scraper(BS4Utils):

    driver = ""
    home_window = ""
    def __init__(self, **kwargs):
        
        """
        The __init__ function is called when the class is instantiated.
        It sets up the browser and driver for use in other functions.
        
        :param self: Represent the instance of the class
        :param **kwargs: Pass a variable number of keyword arguments to a function
        :return: An instance of the class
        :doc-author: Sabari
        """
        if "name" not in kwargs:
            kwargs["name"] = (f"{__class__}".split("'")[1])
        self.get_logger(**kwargs)
        self.debug(f"Initialized: {kwargs['name']}")

        browser = kwargs.get('browser', default="chrome")
        headless = kwargs.get('headless', default='False').lower() == "true"
        remote = kwargs.get('remote', default=None)
        user_data_dir = kwargs.get('user_data_dir', default=None)

        if browser == "chrome":
            options = ChromeOptions()
            if user_data_dir:
                options.add_argument(f"user-data-dir={user_data_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            if remote:
                self.driver =  Remote(remote, options=options)
            else:
                if headless:
                    options.add_argument("--headless")
                    options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
                # chrome_install_location = join(curr_dir, "chrome-linux64")
                # chromedriver_install_location = join(curr_dir, "chromedriver-linux64/chromedriver")
                # chrome_headless_shell_install_location = join(curr_dir, "chrome-headless-shell-linux64")'
                options.binary_location = "chrome_install_location"
                self.driver = Chrome(service=BraveService('chromedriver_install_location'), options=options)

        elif browser == "firefox":
            options = Options()
            options.add_argument("-headless")
            self.driver = Firefox(service=FireFoxService('geckodriver_location'), options=options)
        
    
    def get(self, url: str):
        
        """
        The get function takes a url as an argument and navigates to that url.
            
        
        :param self: Represent the instance of the class
        :param url: Tell the driver which url to go to
        :return: The url that is passed to it
        :doc-author: Sabari
        """
        self.driver.get(url)

    def wait_for_element_to_load(self, search_value: str, wait_time=10, by=By.XPATH):
        
        try:
            wait = WebDriverWait(self.driver, wait_time)
            return wait.until(EC.visibility_of_element_located((by, search_value)))
        except TimeoutException as e:
            return None

    def find_element_by_id(self, id, parent=None):
        
        """
        The find_element_by_id function finds an element by its id.
                Args:
                    id (str): The ID of the element to find.
                    parent (WebElement, optional): The parent WebElement to search within. Defaults to None, which searches the entire page for the given ID.
        
        :param self: Represent the instance of the class
        :param id: Identify the element
        :param parent: Specify the parent element of the element that is being searched for
        :return: The element with the specified id
        :doc-author: Sabari
        """
        if parent:
            return parent.find_element(By.ID, id)
        return self.driver.find_element(By.ID, id)

    def find_element_by_css_selector(self, selector, parent=None):
        
        """
        The find_element_by_css_selector function finds an element by css selector.
                Args:
                    selector (str): The CSS Selector to find the element with.
                    parent (WebElement, optional): The WebElement to search within for the given CSS Selector. Defaults to None, which searches from the root of the DOM tree.
        
        :param self: Represent the instance of the class
        :param selector: Find the element by css selector
        :param parent: Find the element within a parent element
        :return: A webelement object
        :doc-author: Sabari
        """
        if parent:
            return parent.find_element(By.CSS_SELECTOR, selector)
        return self.driver.find_element(By.CSS_SELECTOR, selector)
    
    def find_element_by_name(self, name, parent=None):
        
        """
        The find_element_by_name function finds an element by name.
                Args:
                    name (str): The value of the &quot;name&quot; attribute to search for.
                    parent (WebElement, optional): Parent WebElement to search within; defaults to None.
        
        :param self: Represent the instance of the object itself
        :param name: Find the element by name
        :param parent: Find an element within another element
        :return: A webelement object
        :doc-author: Sabari
        """
        if parent:
            return parent.find_element(By.NAME, name)
        return self.driver.find_element(By.NAME, name)
    
    def find_element_by_link_text(self, link_text, parent=None):
        
        """
        The find_element_by_link_text function finds an element by its link text.
                :Args:
                 - link_text: The text of the element to be found.  Either the exact text, or a substring.
        
        :param self: Represent the instance of the class
        :param link_text: Find the link text of an element
        :param parent: Find an element within another element
        :return: The element that contains the link text
        :doc-author: Sabari
        """
        if parent:
            return parent.find_element(By.LINK_TEXT, link_text)
        return self.driver.find_element(By.LINK_TEXT, link_text)
    
    def find_elements_by_tag_name(self, tag_name, parent=None):
        
        """
        The find_elements_by_tag_name function finds all elements with the given tag name.
                :Args:
                 - tag_name: The name of the tag to search for.
                 - parent: An optional parent element to scope the search within. Defaults to document root if not specified.
        
        :param self: Represent the instance of the class
        :param tag_name: Specify the tag name of the element to be found
        :param parent: Find the elements within a parent element
        :return: A list of elements
        :doc-author: Sabari
        """
        if parent:
            return parent.find_elements(By.TAG_NAME, tag_name)
        return self.driver.find_elements(By.TAG_NAME, tag_name)
    
    def find_elements_by_class_name(self, class_name, parent=None):

        """
        The find_elements_by_class_name function finds all elements with the given class name.
                
        
        :param self: Represent the instance of the class
        :param class_name: Identify the class name of the element you are trying to find
        :param parent: Specify the parent element of the class name
        :return: A list of elements that match the class name
        :doc-author: Sabari
        """
        if parent:
            return parent.find_elements(By.CLASS_NAME, class_name)
        return self.driver.find_elements(By.CLASS_NAME, class_name)

    def find_elements_by_xpath(self, xpath, parent=None):
        """
        The find_elements_by_xpath function is a wrapper for the Selenium WebDriver's find_elements function.
            It takes an xpath and returns a list of elements that match the xpath.
            If no parent element is specified, it will search from the root of the DOM.
        
        :param self: Represent the instance of the class
        :param xpath: Locate the element on the page
        :param parent: Find the elements within a parent element
        :return: A list of webelement objects
        :doc-author: Sabari
        """
        if parent:
            return parent.find_elements(By.XPATH, xpath)
        return self.driver.find_elements(By.XPATH, xpath)
    
    def open_new_tab(self, tab_name, url=None):
        """
        The open_new_tab function opens a new tab in the browser.
            The function takes two arguments:
                1) tab_name - A string that is used to identify the new tab.  This can be any string, but it should be unique for each open tab.  If you don't specify a name, then one will be generated for you (but this may not work as expected).
                2) url - An optional argument that specifies what URL to load into the newly opened window/tab.  If no URL is specified, then an empty page will be loaded.
        
        :param self: Reference the current instance of the class
        :param tab_name: Name the tab
        :param url: Open a new tab with the url specified
        :return: The driver
        :doc-author: Sabari
        """
        driver = self.driver
        self.home_window = driver.current_window_handle
        driver.execute_script(f"window.open('about:blank', '{tab_name}');")
        if url:
            driver.switch_to.window(f"{tab_name}")
            driver.get(url)
        self.switch_tab(self.home_window)
    
    def switch_home(self):
        """
        The switch_home function switches the current tab to the home window.
                
        
        :param self: Access the attributes and methods of a class
        :return: A tab
        :doc-author: Sabari
        """
        self.switch_tab(self.home_window)

    def switch_tab(self, tab_name):
        """
        The switch_tab function switches to the tab with the name passed in as an argument.
            Args:
                tab_name (str): The name of the tab you want to switch to. 
        
        
        :param self: Represent the instance of the class
        :param tab_name: Switch to a new tab
        :return: The name of the tab that is currently open
        :doc-author: Sabari
        """
        self.driver.switch_to.window(f"{tab_name}")

    def close(self):
        """
        The close function closes the browser window that is currently open.
            
        
        :param self: Represent the instance of the class
        :return: Nothing
        :doc-author: Sabari
        """
        self.driver.close()
