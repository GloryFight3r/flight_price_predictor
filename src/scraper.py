from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import csv


# scrape destinations

url: str = "https://www.google.com/travel/flights?tfs=CBwQARoaEgoyMDIzLTEwLTA4agwIAhIIL20vMGZ0anhAAUgBcAGCAQsI____________AZgBAg&hl=en-GB&curr=EUR"

driver = webdriver.Chrome()

driver.get(url)

patterns = [r"(\d+) days ago - €(\d+)", r"(\d+) day ago - €(\d+)", "Today - €(\d+)"]

with open('../data/plane_logs', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["From", "To", "Days Ago", "Price"])
    departs_from:str = "Paris"
    arrives_at:str = "Eindhoven"
    date:str = "8 Aug"

    try:
        # gets rid of the google accept all window
        button = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button')
        button.click()
        
        sleep(1)
        # enter departure
        departs_field = driver.find_elements(By.TAG_NAME, 'input')[0]#lJj3Hd')#//*[@id="i21"]/div[6]/div[2]/div[2]')#/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div[2]/div[1]/div/input')
        departs_field.clear()
        departs_field.send_keys(departs_from)
        sleep(1)
        departs_from_listbox = driver.find_element(By.CLASS_NAME, 'DFGgtd')#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        departs_from_listbox.find_elements(By.TAG_NAME, 'li')[0].click()
        
        sleep(1)
        # enter arrival
        arrives_field = driver.find_elements(By.TAG_NAME, 'input')[2]#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        arrives_field.clear()
        arrives_field.send_keys(arrives_at)
        sleep(1)
        arrives_at_listbox = driver.find_element(By.CLASS_NAME, 'DFGgtd')#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        arrives_at_listbox.find_elements(By.TAG_NAME, 'li')[0].click()

        sleep(1)

        # input date
        date_field = driver.find_elements(By.TAG_NAME, 'input')[4]#//*[@id="i21"]/div[4]/div/div/div[1]/div/div/input')
        date_field.clear()
        date_field.send_keys(date)
        sleep(1)

        # click on button to search
        search_button = driver.find_element(By.CSS_SELECTOR, '[aria-label=Search]')
        search_button.click()
        sleep(3)
        driver.find_element(By.XPATH, "//div[text()='View price history']").click()
        sleep(1)

        # click on grid
        button = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[4]/div')
        button.click()
 
        sleep(1)

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
            writer.writerow([departs_from, arrives_at, day, price])
        sleep(0.1)
    except Exception:
        print("AS")

driver.quit()

