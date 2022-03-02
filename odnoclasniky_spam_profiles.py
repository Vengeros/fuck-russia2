from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import os
import queue
import threading
import random


CHROME_DRIVER_PATH = 'chromedriver'
VIDEO_ABSOLUTE_PATH = os.path.abspath("data/ukrain.mp4")

TOKENS = [
    'zXNvThL2k_ypv4_djhS6wFdhyGm0SQ3nrBPSzquUldHA6tJ9Rk4ilLgZ_dmT1bcJbCUVN9N0Bl0k2HbOgdsayzCA7C-5eV33ZZ8yZh_cod9wmP7c-uCGkykBU03t1uqEX-At8mU8hchSBYLv_4',
    # 'JgbOIuU7mgOwWLlMVQhWxKXLNqNzYoPRuBA1W9wx6y7hIqeecfv61sdy7Zb0qquHSBAwmGADBkocpgb7pZeIPzdKQVzv-qAC5m13LsiTFAMA8NvMxul_eGu7iIZS635optl4M3HZOEArB65j_4',
    # 'hHaCgGUzvAE30Ve61RgyqlJ81cmqduTgntaFq6cbVBOGdKY6h1_nW2uCi8diBU8oLc5eVNZ35RuPW4DaWViYtjmZfPfujwPyU8_eYjkm4y-jubxWVyAbqdQy4KQLsDyHZB8UUyZo3REy50M6_4',
]

profile_links_queue = queue.Queue()
profile_links = open('odnoclasniky_profiles.txt', 'r').readlines()
random.shuffle(profile_links)


for profile_link in profile_links:
    profile_links_queue.put(profile_link)


def task(profile_links_queue, token):
    chrome_options = Options()
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
    browser.get('https://ok.ru/')
    browser.add_cookie({'name': 'AUTHCODE', 'value': token})
    browser.refresh()
    browser.implicitly_wait(3)

    for _ in range(50):
        profile_link = profile_links_queue.get()
        browser.get(profile_link)
        try:
            write_button = browser.find_element(By.XPATH, '//*[@id="hook_Block_MainMenu"]/div/ul/li[2]/a')
            write_button.click()
            msg_input = browser.find_element(By.XPATH, '//input[@class="attach-file"]')
            msg_input.send_keys(VIDEO_ABSOLUTE_PATH)
            browser.find_element(By.XPATH, '//msg-progress[@progress="1"]')
            msg_input.find_element(By.XPATH, '//*[@id="msg_layer"]/msg-app/main/msg-page/div[2]/msg-chat/main/section/footer/msg-posting-form/div/div[1]/div[3]/msg-button[3]').click()
            sleep(1)
            browser.find_element(By.XPATH, '//*[text()="Вы слишком часто отправляете сообщения разным пользователям. Повторите попытку позже."]')
            sleep(60 * 5)
            # sleep(5)  # todo: remove
        except (ElementNotInteractableException, NoSuchElementException):
            pass
        profile_links_queue.task_done()


for token in TOKENS:
    worker = threading.Thread(target=task, args=(profile_links_queue, token,), daemon=True)
    worker.start()

profile_links_queue.join()
