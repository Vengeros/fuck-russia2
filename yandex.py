from random import choice
from time import sleep
import os

from onlinesimru import GetNumbers
from selenium import webdriver
from selenium.webdriver.common.by import By

ONLINE_SIM_TOKEN = os.environ['ONLINE_SIM_TOKEN']
CHROME_DRIVER_PATH = 'chromedriver'

PICKUP_ADDRESS = 'Москва, Красная площадь, 1'
NUMBER_TAXI_CALL = 10
RANDOM_ADDRESSES = ['Полянка']

onlinesim = GetNumbers(ONLINE_SIM_TOKEN)

for _ in range(NUMBER_TAXI_CALL):
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    browser.implicitly_wait(15)
    browser.get('https://taxi.yandex.rs/en_rs/')

    address_a = browser.find_element(By.XPATH, '//input[@id="address-a"]')
    address_a.send_keys(PICKUP_ADDRESS)
    address_a.click()
    browser.find_element(By.XPATH, '//*[@id="address-a-popup"]/ul/li[1]').click()

    address_b = browser.find_element(By.XPATH, '//input[@id="address-b"]')
    address_b.send_keys(choice(RANDOM_ADDRESSES))

    number = onlinesim.get(service='yandex', number=True)
    phone_field = browser.find_element(By.XPATH, '//input[@name="fieldPhone"]')
    phone_field.send_keys(number['number'])

    car_list = browser.find_elements(By.XPATH, '//div[@class="FieldTariff"]//div[@role="listitem"]')[:8]
    for car in car_list:
        sleep(1)
        car.click()
        order_button = browser.find_element(By.XPATH, '//*[@id="application"]/div[1]/div[3]/section[1]/button')
        if order_button.get_attribute('aria-disabled') == 'false':
            order_button.click()
            for _ in range(7):
                try:
                    sleep(3)
                    auth_code = onlinesim.stateOne(tzid=number['tzid'], message_to_code=1, msg_list=0)['msg']
                except KeyError:
                    sleep(3)
            browser.find_element(By.XPATH, '//input[@id="AuthConfirm"]').send_keys(auth_code)

            browser.find_element(By.XPATH, '//button[@type="submit"][@aria-disabled="false"]').click()
            break
    sleep(5)
