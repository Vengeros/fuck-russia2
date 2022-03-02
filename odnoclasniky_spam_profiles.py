from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import os

CHROME_DRIVER_PATH = 'chromedriver'
VIDEO_ABSOLUTE_PATH = os.path.abspath("data/ukrain.mp4")

COOKIE_AUTH_CODE = 'YOUR AUTH CODE FROM COOKIE - `AUTHCODE`'

chrome_options = Options()
browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
browser.get('https://ok.ru/')
browser.add_cookie({'name': 'AUTHCODE', 'value': COOKIE_AUTH_CODE})
browser.refresh()

browser.implicitly_wait(5)

profile_links = open('odnoclasniky_profiles.txt', 'r').readlines()
for profile_link in profile_links:
    browser.get(profile_link)
    try:
        write_button = browser.find_element(By.XPATH, '//a[text()="Написать"]')
        write_button.click()
        msg_input = browser.find_element(By.XPATH, '//input[@class="attach-file"]')
        msg_input.send_keys(VIDEO_ABSOLUTE_PATH)
        browser.find_element(By.XPATH, '//msg-progress[@progress="1"]')# message here
        msg_input.find_element(By.XPATH, '//msg-button[@title="Отправить"]').click()
        sleep(1)
    except (ElementNotInteractableException, NoSuchElementException) as e:
        print(e)
        continue
