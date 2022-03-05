import csv
import queue
import threading
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROME_DRIVER_PATH = 'chromedriver'
SVINO_PUBLICS = [
    'https://ok.ru/pricolypro/members',
    'https://ok.ru/handmade24/members',
    'https://ok.ru/womenlike/members',
    'https://ok.ru/ntv/members',
    'https://ok.ru/semyajornal/members',
    'https://ok.ru/coooking/members',
    'https://ok.ru/group53082395443390/members'
]

ACCOUNTS = [
    {'AUTHCODE': 'zXNvThL2k_ypv4_djhS6wFdhyGm0SQ3nrBPSzquUldHA6tJ9Rk4ilLgZ_dmT1bcJbCUVN9N0Bl0k2HbOgdsayzCA7C-5eV33ZZ8yZh_cod9wmP7c-uCGkykBU03t1uqEX-At8mU8hchSBYLv_4'},
    *[{'login': acc[0], 'password': acc[1]} for acc in csv.reader(open('data/accounts.txt', 'r'), delimiter=':')]
]

write_queue = queue.Queue()
publics_queue = queue.Queue()
for public_link in SVINO_PUBLICS:
    publics_queue.put(public_link)


def task(publics_queue, account):
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
    browser.get('https://ok.ru/')

    if token := account.get('AUTHCODE'):
        browser.add_cookie({'name': 'AUTHCODE', 'value': token})
        browser.refresh()

    elif (login := account.get('login')) and (password := account.get('password')):
        browser.find_element(By.XPATH, '//input[@id="field_email"]').send_keys(login)
        browser.find_element(By.XPATH, '//input[@id="field_password"]').send_keys(password)
        browser.find_element(By.XPATH, '//input[@type="submit"]').click()

    browser.implicitly_wait(5)

    try:
        WebDriverWait(browser, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="hook_FormButton_button_accept"]'))).click()
    except TimeoutException:
        pass

    public_link = publics_queue.get()
    browser.get(public_link)

    while True:
        try:
            more_button = browser.find_element(By.XPATH, '//*[text()="Показать ещё"]')
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(0.1)

            while not more_button.is_displayed() or not more_button.is_enabled():
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(0.1)

                if len(browser.find_elements(By.XPATH,
                                             '//div[@class="ugrid_i"]//a[@class="user-grid-card_img"]')) > 4000:
                    break
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                sleep(0.5)

            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(0.3)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable(more_button))
            more_button.click()
        except (NoSuchElementException, TimeoutException):
            break

    profiles_elements = browser.find_elements(By.XPATH, '//div[@class="ugrid_i"]//a[@class="user-grid-card_img"]')
    profiles_links = [elem.get_attribute('href') for elem in profiles_elements]

    with open('data/odnoclasniky_profiles.txt', mode='a', encoding='utf-8') as myfile:
        myfile.write('\n'.join(profiles_links) + '\n')

    browser.quit()
    publics_queue.task_done()


for _, account in zip(SVINO_PUBLICS, ACCOUNTS):
    worker = threading.Thread(target=task, args=(publics_queue, account,), daemon=True)
    worker.start()

publics_queue.join()
