import csv
import os
import queue
import random
import threading
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException, \
    ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROME_DRIVER_PATH = os.path.abspath('chromedriver')
VIDEO_ABSOLUTE_PATH = os.path.abspath('data/ukrain.mp4')
PROFILES_TXT = os.path.abspath('data/odnoclasniky_profiles.txt')
PROFILES_CSV = os.path.abspath('data/odnoclasniky_profiles.csv')
MSG_COUNT = 10
SIMULTANEOUS_ACCOUNTS = 7

ACCOUNTS = [
    *[{'login': acc[0], 'password': acc[1]} for acc in csv.reader(open('data/accounts.txt', 'r'), delimiter=':')]
]

random.shuffle(ACCOUNTS)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def send_messages_task(profile_links_queue, account):
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
    browser.get('https://ok.ru/')
    browser.implicitly_wait(3)

    if token := account.get('AUTHCODE'):
        browser.add_cookie({'name': 'AUTHCODE', 'value': token})
        browser.refresh()
    elif (login := account.get('login')) and (password := account.get('password')):
        browser.find_element(By.XPATH, '//input[@id="field_email"]').send_keys(login)
        browser.find_element(By.XPATH, '//input[@id="field_password"]').send_keys(password)
        browser.find_element(By.XPATH, '//input[@type="submit"]').click()

    messages_sent = 0

    for i in range(MSG_COUNT):
        profile_link = profile_links_queue.get()
        browser.get(profile_link)
        try:
            write_button = browser.find_element(By.XPATH, '//*[@id="hook_Block_MainMenu"]/div/ul/li[2]/a')
            write_button.click()
            sleep(1)
            msg_input = browser.find_element(By.XPATH, '//input[@class="attach-file"]')
            msg_input.send_keys(VIDEO_ABSOLUTE_PATH)
            upload_done_xpath = '//msg-progress[@progress="1"]'
            WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.XPATH, upload_done_xpath)))
            browser.find_element(By.XPATH, upload_done_xpath)
            msg_input.find_element(By.XPATH, '//*[@id="msg_layer"]/msg-app/main/msg-page/div[2]/msg-chat/main/section/footer/msg-posting-form/div/div[1]/div[3]/msg-button[3]').click()
            sleep(1)
            try:
                browser.find_element(By.XPATH, '//*[text()="???? ?????????????? ?????????? ?????????????????????? ?????????????????? ???????????? ??????????????????????????. ?????????????????? ?????????????? ??????????."]')
                profile_links_queue.task_done()
                break
            except NoSuchElementException:
                messages_sent += 1
        except (ElementNotInteractableException,
                NoSuchElementException,
                TimeoutException,
                ElementClickInterceptedException) as e:
            print(f'{type(e)}: {e}')
        profile_links_queue.task_done()
    if accounts_left := (MSG_COUNT - 1 - i):
        for i in range(accounts_left):
            profile_link = profile_links_queue.get()
            profile_links_queue.task_done()
    print(f'{account.get("login") or account.get("token")} work is done, sent {messages_sent} messages!')


def main():
    profile_links_queue = queue.Queue()
    if not os.path.exists(PROFILES_CSV):
        profile_links = open(PROFILES_TXT, 'r').readlines()
        with open(PROFILES_CSV, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['account', 'proceeded'])
            profile_links = list(set(profile_links))
            data = [[profile_link.strip('\n'), 0] for profile_link in profile_links]
            writer.writerows(data)

    profiles = list(csv.DictReader(open(PROFILES_CSV, 'r', encoding='UTF8')))
    random.shuffle(profiles)

    profiles = profiles[:MSG_COUNT * len(ACCOUNTS)]

    for profile in profiles:
        profile_links_queue.put(profile['account'])

    for account_chunk in chunks(ACCOUNTS, SIMULTANEOUS_ACCOUNTS):
        workers = []
        for account in account_chunk:
            worker = threading.Thread(target=send_messages_task, args=(profile_links_queue, account,), daemon=True)
            workers.append(worker)

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

    profile_links_queue.join()
    print(f"ALL DONE! EVERY ACCOUNT ({len(ACCOUNTS)}) TRIED TO SEND {MSG_COUNT} MESSAGES!")


if __name__ == '__main__':
    main()
