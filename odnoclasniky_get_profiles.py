import signal
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROME_DRIVER_PATH = 'chromedriver'
SVINO_PUBLICS = [
    'https://ok.ru/pricolypro/members'
]

COOKIE_AUTH_CODE = 'YOUR AUTH CODE FROM COOKIE - `AUTHCODE`'


def handler(signum, frame):
    print('Nothing to load more')
    raise NoSuchElementException()


chrome_options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
browser.get('https://ok.ru/')
browser.add_cookie({'name': 'AUTHCODE', 'value': COOKIE_AUTH_CODE})
browser.refresh()
browser.implicitly_wait(5)

signal.signal(signal.SIGALRM, handler)

for public in SVINO_PUBLICS:
    browser.get(public)

    while True:
        try:
            more_button = browser.find_element(By.XPATH, '//*[text()="Показать ещё"]')
            signal.alarm(7)
            while not more_button.is_displayed() or not more_button.is_enabled():
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(0.5)
            signal.alarm(0)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable(more_button))
            more_button.click()
        except NoSuchElementException:
            break

    profiles_elements = browser.find_elements(By.XPATH, '//div[@class="ugrid_i"]//a[@class="user-grid-card_img"]')
    profile_links = [elem.get_attribute('href') for elem in profiles_elements]

    with open('odnoclasniky_profiles.txt', mode='a', encoding='utf-8') as myfile:
        myfile.write('\n'.join(profile_links))
