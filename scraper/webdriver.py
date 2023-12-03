import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import pickle
from itertools import islice
from captchatools import new_harvester, captchaExceptions
from selenium import webdriver
import pandas as pd
import re
import os
from drive import upload_xlsx, drop_duplicates
import platform
ua = UserAgent()


PROXY = {
  'http': 'http',
  'https': 'https'
}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # #  # # # # # # # # Selenium # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_text_bs4(bs, selector):
    try:
        return bs.find(class_=selector).text.strip()
    except Exception as e:
        return ""


def create_chromedriver(headless=True):
    if platform.system() == "Linux":
        chrome_service = Service(executable_path="assets/chromedriver-linux64/chromedriver")
    else:
        chrome_service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-remote-fonts")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-cookies")
    options.add_argument('--disable-images')
    options.add_argument("--disable-css")
    if platform.system() == "Linux":
        options.add_argument("--headless")
        PROXY = "p.webshare.io:9999"
        options.add_argument('--proxy-server=%s' % PROXY)
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-extensions')
    else:
        if headless:
            options.add_argument("--headless=new")
        options.add_extension("assets/proxy_auth.zip")
    driver = webdriver.Chrome(service=chrome_service, options=options)
    return driver


def get_text(driver, selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element.text
    except Exception as e:
        return ""


def get_text_with_wait(driver, selector, wait=10):
    try:
        element = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        return element.text
    except Exception as e:
        return ""


def click_btn(driver, selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
    except Exception as e:
        pass


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # #  # # # Set mentése és betöltése # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def save_set(file, set):
    with open(f"assets/{file}", 'wb') as f:
        pickle.dump(set, f)


def load_set(file):
    try:
        with open(f"assets/{file}", 'rb') as f:
            my_set = pickle.load(f)
            return my_set
    except FileNotFoundError:
        return set()


def split_set(db, input_set):
    if db <= 0 or not input_set:
        return []
    part_size = len(input_set) // db
    parts = []

    it = iter(input_set)
    for _ in range(db):
        part = set(islice(it, part_size))
        parts.append(part)
    return parts


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # #  # # # # # Egyéb műveletek  # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

CAPTCHA_API_KEY = "apikey"

def captcha_telekom(url):
    try:
        harvester = new_harvester(
            api_key=CAPTCHA_API_KEY,
            solving_site="captchaai",
            captcha_type="v2",
            sitekey="6LdjnjcUAAAAAOggdk4bYrBcm5F6qxZlMgfQLmlr",
            captcha_url=url,
            invisible_captcha=True
        )
        answer = harvester.get_token()
        return answer
    except captchaExceptions.NoBalanceException:
        time.sleep(10)
        return captcha_pn(url)


def captcha_pn(url):
    try:
        harvester = new_harvester(
            api_key=CAPTCHA_API_KEY,
            solving_site="captchaai",
            captcha_type="v2",
            sitekey="6LfPBMAaAAAAAG-Cz259OmmHyQJZRGgDOHyrbOH7",
            captcha_url=url,
            invisible_captcha=True
        )
        answer = harvester.get_token()
        return answer
    except captchaExceptions.NoBalanceException:
        time.sleep(5)
        return captcha_pn(url)


def clean_pn(pn):
    """Egy telefonszámot 362012345678 formátumra alakít át"""
    pn = re.sub(r'[^0-9]', '', str(pn))
    if pn[:6] == "003606":
        pn = "36" + pn[6:]
    if pn[:2] == "06":
        pn = "36" + pn[2:]
    if pn[:2] == "00":
        pn = pn[2:]
    return pn


def append_xlsx(arr, file_path):
    df = pd.DataFrame(arr)
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            df.to_excel(writer, sheet_name="Sheet1", header=False, startrow=writer.sheets["Sheet1"].max_row, index=False)
    else:
        df.to_excel(file_path, index=False)

