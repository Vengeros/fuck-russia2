from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CHROME_DRIVER_PATH = 'chromedriver'
MESSAGE = 'HHH'

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
        msg_input = browser.find_element(By.XPATH, '//msg-input[@name="input"]')
        msg_input.send_keys(MESSAGE)  # message here
        msg_input.find_element(By.XPATH, '//msg-button[@title="Отправить"]').click()
    except ElementNotInteractableException:
        continue
