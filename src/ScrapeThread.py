from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
from selenium import webdriver
import pandas as pd
import os
from selenium.webdriver.common.by import By
from time import sleep
import re
from datetime import date, timedelta
from multiprocessing import Process

current_day = date.today()
patterns = [r"(\d+) days ago - €(\d+)", r"(\d+) day ago - €(\d+)", "Today - €(\d+)"]


IDLE_TIME = 1.4
WAIT_TIME = 2.5

class ScrapeThread(Process):
    def __init__(self, url, work_list):
        Process.__init__(self)
        self.url = url

        self.work_list = work_list

    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')

        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        for departs_from, arrives_at, date in self.work_list:
            self.scrape(driver, departs_from, arrives_at, date)
        
        driver.close()

    def scrape(self, driver, departs_from, arrives_at, date, retries = 0):
        if retries >= 6:
            return
        cur_file_name = '{}-{}.csv'.format(departs_from, arrives_at)
        cur_dir = '../data/{}/'.format(date)
        
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
            
            # e.5nter departure
            departs_field = wait_for_elements(driver, (By.TAG_NAME, 'input'))[0]
            departs_field.clear()
            departs_field.send_keys(departs_from)
            departs_from_listbox = wait_for_element(driver, (By.CLASS_NAME, 'DFGgtd'))
            sleep(IDLE_TIME)
            departs_from_listbox.find_elements(By.TAG_NAME, 'li')[0].click()
            
            # enter arrival
            arrives_field = wait_for_elements(driver, (By.TAG_NAME, 'input'))[2]
            arrives_field.clear()
            arrives_field.send_keys(arrives_at)
            #sleep(IDLE_TIME)
            arrives_at_listbox = wait_for_element(driver, (By.CLASS_NAME, 'DFGgtd'))
            sleep(IDLE_TIME)
            arrives_at_listbox.find_elements(By.TAG_NAME, 'li')[0].click()

            # input date
            sleep(IDLE_TIME)
            date_field = wait_for_elements(driver, (By.TAG_NAME, 'input'))[4]
            date_field.clear()
            for i in range(10):
                date_field.send_keys(Keys.BACKSPACE)
            date_field.send_keys(date)

            # click on button to search
            search_button = wait_to_be_clickable(driver, (By.CSS_SELECTOR, '[aria-label=Search]'))
            search_button.click()
            sleep(IDLE_TIME)
            
            overlap_button = wait_to_be_clickable(driver, (By.CLASS_NAME, 'I0Kcef'))
            if overlap_button != None:
                overlap_button.click()

            wait_to_be_clickable(driver, (By.XPATH, "//div[text()='View price history']")).click()

            sleep(IDLE_TIME)
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
        df.drop_duplicates(subset=['Price at Date'], keep="last", inplace=True)
        df.to_csv(cur_dir + cur_file_name, index=False)

def wait_for_element(cur_driver, wanted):
    try:
        element = WebDriverWait(cur_driver, WAIT_TIME).until(
          EC.element_to_be_clickable(wanted),
        )
        return element
    except Exception:
        return None

def wait_to_be_clickable(cur_driver, wanted):
    try:
        element = WebDriverWait(cur_driver, WAIT_TIME).until(
            EC.element_to_be_clickable(wanted),
        )
        return element
    except Exception:
        return None

def wait_for_elements(cur_driver, wanted):
    try:
        element = WebDriverWait(cur_driver, WAIT_TIME).until(
            EC.presence_of_all_elements_located(wanted)
        )
        return element
    except Exception:
        return []
