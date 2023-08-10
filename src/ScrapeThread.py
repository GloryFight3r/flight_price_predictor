from multiprocessing import Process
import os
import re
from datetime import date, timedelta
from time import sleep

import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

# get current date
current_day = date.today()

# pattern to look for while matching
patterns = [r"(\d+) days ago - €(\d+)", r"(\d+) day ago - €(\d+)", "Today - €(\d+)"]

# wait time between pages loading
IDLE_TIME = 3

# wait time for elements to appear/become clickable
WAIT_TIME = 5

class ScrapeThread(Process):
    def __init__(self, url, work_list):
        Process.__init__(self)
        self.url = url

        # flights to be scraped by current worker
        self.work_list = work_list

    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # do not show the browser

        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)

        for departs_from, arrives_at, date in self.work_list:
            self.scrape(driver, departs_from, arrives_at, date)
        
        driver.close()

    def scrape(self, driver, departs_from: str, arrives_at: str, date: str, retries: int = 0):
        # IMPORTANT
        # Worker might fail scraping a page if some element has not been successfully loaded
        # therefore we might have to retry scraping it

        if retries >= 6: # we give the worker 6 tries to scrape the page
            return
        cur_file_name:str = '{}-{}-{}.csv'.format(departs_from, arrives_at, date)
        cur_dir:str = '../data/multiple_data/'
        
        df = pd.DataFrame({
            "Price at Date":[],
            "Price in EUR":[]
        })
        try:
            if cur_file_name in os.listdir(cur_dir):
                df = pd.read_csv(cur_dir + cur_file_name)
        except FileNotFoundError as e:
            os.mkdir(cur_dir)
            print("No such dir")
        try:
            driver.get(self.url)
            # gets rid of the google accept all window
            buttons = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button')

            if len(buttons) > 0:
                buttons[0].click()
            
            # enter departure
            sleep(IDLE_TIME)

            departs_field = wait_for_elements(driver, (By.TAG_NAME, 'input'))[0]
            departs_field.clear()
            departs_field.send_keys(departs_from)
            departs_from_listbox = wait_for_element(driver, (By.CLASS_NAME, 'DFGgtd'))
            departs_from_listbox.find_elements(By.TAG_NAME, 'li')[0].click()
            
            # enter arrival
            arrives_field = wait_for_elements(driver, (By.TAG_NAME, 'input'))[2]
            arrives_field.clear()
            arrives_field.send_keys(arrives_at)
            arrives_at_listbox = wait_for_element(driver, (By.CLASS_NAME, 'DFGgtd'))

            arrives_at_listbox.find_elements(By.TAG_NAME, 'li')[0].click()

            # input date
            sleep(1)
            date_field = wait_for_elements(driver, (By.TAG_NAME, 'input'))[4]
            date_field.clear()
            for i in range(10):
                date_field.send_keys(Keys.BACKSPACE) # delete the date in the current field
            date_field.send_keys(date)

            sleep(1)
            # click on button to search
            search_button = wait_to_be_clickable(driver, (By.CSS_SELECTOR, '[aria-label=Search]'))
            search_button.click()

            sleep(3)
            
            # close the tab that might have been opened and overlap with the graph show button
            overlap_button = wait_to_be_clickable(driver, (By.CLASS_NAME, 'I0Kcef'))
            if overlap_button != None:
                overlap_button.click()

            wait_to_be_clickable(driver, (By.XPATH, "//div[text()='View price history']")).click()

            sleep(2)

            prices = wait_for_elements(driver, (By.CLASS_NAME, 'pKrx3d-JNdkSc'))
            print(len(prices), departs_from, arrives_at)
            if len(prices) == 0:
                self.scrape(driver, departs_from, arrives_at, date, retries + 1)
                return
            for x in prices:
                info:str = x.find_element(By.CLASS_NAME,'pKrx3d').get_attribute('aria-label')

                day = 0
                price = 0
                has_matched = False

                for k, pattern in enumerate(patterns):
                    match = re.search(pattern, info)
                    
                    # there are three match cases and we go through each of them until we find a match
                    if match:
                        has_matched = True
                        day = 0
                        price = 0
                        if k == 2:
                            day = 0
                            price = int(match.group(1))
                        else:
                            day = int(match.group(1))
                            price = int(match.group(2))
                        break
                # save the data
                assert has_matched
                df.loc[len(df)] = [(current_day - timedelta(days=day)).strftime("%Y/%m/%d"), price]
        except Exception as e:
            print(e)
            self.scrape(driver, departs_from, arrives_at, date, retries + 1)
            return
        # we need the line below in case you want to gather more data by running the scraper on a later day
        # we keep the newest data
        df.drop_duplicates(subset=['Price at Date'], keep="last", inplace=True)
        df.to_csv(cur_dir + cur_file_name, index=False)

def wait_for_element(cur_driver, wanted):
    """ Wait for the element to become clickable

    Args:
        cur_driver (): web driver
        wanted (): (By.*, [path])

    Returns: Either the element or None if no such element becomes clickable
        
    """
    try:
        element = WebDriverWait(cur_driver, WAIT_TIME).until(
          EC.element_to_be_clickable(wanted),
        )
        return element
    except Exception:
        return None

def wait_to_be_clickable(cur_driver, wanted):
    """ Wait for the element to be clickable

    Args:
        cur_driver (): web driver
        wanted (): (By.*, [path])


    Returns: Either the element or None if no such element becomes clickable
        
    """
    try:
        element = WebDriverWait(cur_driver, WAIT_TIME).until(
            EC.element_to_be_clickable(wanted),
        )
        return element
    except Exception:
        return None

def wait_for_elements(cur_driver, wanted):
    """ Wait for elements to be present

    Args:
        cur_driver (): web driver
        wanted (): (By.*, [path])

    Returns: Either a list of elements or None if no such elements appear

    """
    try:
        element = WebDriverWait(cur_driver, WAIT_TIME).until(
            EC.presence_of_all_elements_located(wanted)
        )
        return element
    except Exception:
        return []

