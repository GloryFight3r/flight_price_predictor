from logging import exception
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
import os
from datetime import date, timedelta
import pandas as pd
from selenium.webdriver.common.keys import Keys

url: str = "https://www.google.com/travel/flights?tfs=CBwQARoaEgoyMDIzLTEwLTA4agwIAhIIL20vMGZ0anhAAUgBcAGCAQsI____________AZgBAg&hl=en-GB&curr=EUR"

driver = webdriver.Chrome()
current_day = date.today()
patterns = [r"(\d+) days ago - €(\d+)", r"(\d+) day ago - €(\d+)", "Today - €(\d+)"]

IDLE_TIME = 1.3

destinations = [
    ("Sofia", "Eindhoven", "23 Aug"), 
    ("Canada", "Rome", "23 Aug"),
    ("Canada", "Rome", "2 Sep")
]

destinations = [("Sofia", "Eindhoven", "{} Aug".format(i)) for i in range(6, 32)]

for departs_from, arrives_at, date in destinations:
    cur_file_name = '{}.csv'.format(date)
    cur_dir = '../data/{}-{}/'.format(departs_from, arrives_at)
    
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
    driver.get(url)
    sleep(IDLE_TIME)
    try:
        # gets rid of the google accept all window
        buttons = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button')
        if len(buttons) > 0:
            buttons[0].click()
        
        sleep(IDLE_TIME)
        # enter departure
        departs_field = driver.find_elements(By.TAG_NAME, 'input')[0]#lJj3Hd')#//*[@id="i21"]/div[6]/div[2]/div[2]')#/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div[2]/div[1]/div/input')
        departs_field.clear()
        departs_field.send_keys(departs_from)
        sleep(IDLE_TIME)
        departs_from_listbox = driver.find_element(By.CLASS_NAME, 'DFGgtd')#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        departs_from_listbox.find_elements(By.TAG_NAME, 'li')[0].click()
        
        sleep(IDLE_TIME)
        # enter arrival
        arrives_field = driver.find_elements(By.TAG_NAME, 'input')[2]#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        arrives_field.clear()
        arrives_field.send_keys(arrives_at)
        sleep(IDLE_TIME)
        arrives_at_listbox = driver.find_element(By.CLASS_NAME, 'DFGgtd')#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        arrives_at_listbox.find_elements(By.TAG_NAME, 'li')[0].click()

        sleep(IDLE_TIME)

        # input date
        date_field = driver.find_elements(By.TAG_NAME, 'input')[4]#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        date_field.clear()
        for i in range(10):
            date_field.send_keys(Keys.BACKSPACE)
        date_field.send_keys(date)
        sleep(IDLE_TIME)

        # click on button to search
        search_button = driver.find_element(By.CSS_SELECTOR, '[aria-label=Search]')
        search_button.click()
        sleep(IDLE_TIME)
        driver.find_element(By.XPATH, "//div[text()='View price history']").click()
        sleep(IDLE_TIME)

        # click on grid
        button = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[4]/div')
        button.click()
 
        sleep(IDLE_TIME)

        prices = driver.find_elements(By.CLASS_NAME, 'pKrx3d-JNdkSc')
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
        destinations.append((departs_from, arrives_at, date))
        print(e)
    df.drop_duplicates(subset=['Price at Date'], keep="last", inplace=True)
    df.to_csv(cur_dir + cur_file_name, index=False)
driver.quit()

