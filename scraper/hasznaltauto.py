from webdriver import *
import threading
import re
import requests
from bs4 import BeautifulSoup
from drive import upload_xlsx
from concurrent.futures import ThreadPoolExecutor


class Hasznaltauto:
    def __init__(self):
        self.load_products()

    def load_products(self):
        driver = create_chromedriver()
        driver.get("https://www.hasznaltauto.hu/")
        click_btn(driver, "#didomi-notice-agree-button")
        click_btn(driver, ".lower-section__button___m4u_1")
        get_text_with_wait(driver, ".talalati-sor")
        link = driver.current_url
        driver.quit()

        threads = []
        ids = set()

        for g in range(0, 30):
            thread = threading.Thread(target=lambda g=g: ids.update(load_products_tread(g * 140, (g+1) * 140, link)))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        previus_set = load_set("hasznaltauto")
        different_elements = ids.difference(previus_set)
        save_set("hasznaltauto_preload", different_elements)
        previus_set.update(different_elements)
        save_set("hasznaltauto", previus_set)

        max_workers = 15
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(load_product_info, pid) for pid in different_elements]

        rows = []
        for future in futures:
            rows.extend(future.result())

        append_xlsx(rows, "assets/hasznaltauto.xlsx")
        upload_xlsx("hasznaltauto.xlsx", "assets/hasznaltauto.xlsx")


def load_products_tread(i, j, link):
    product_ids = set()
    for i in range(i, j):
        try:
            product_ids.update(load_products_page(link, i))
        except:
            pass
    return product_ids


def load_products_page(link, page_number):
    product_ids = set()
    response = requests.get(f"{link}/page{page_number}", proxies=PROXY, timeout=20)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all(class_="talalati-sor")

        for product in products:
            elado = product.select_one(".trader-name").get_text().strip()

            if elado == "Magánszemély":
                kod = product.select_one(".talalatisor-hirkod").get_text().strip()
                list_id = re.findall(r'\d+', kod)
                if list_id:
                    product_ids.add(list_id[0])
        print(page_number, len(product_ids))
    return product_ids


def load_product_info(product_id, first=True):
    try:
        response = requests.get(f"https://www.hasznaltauto.hu/{product_id}", proxies=PROXY, timeout=60)
        data = {
            'id': product_id,
            'type': 'hirdetes',
            'index': '1',
            'captchaResponse': captcha_pn(f"https://www.hasznaltauto.hu/{product_id}")
        }

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            phone_response = requests.post('https://www.hasznaltauto.hu/captcha/reveal-phone-number', proxies=PROXY,
                                           data=data, headers={'x-requested-with': 'XMLHttpRequest'}, timeout=60)

            l = {
                "id": product_id,
                "price": get_text_bs4(soup, "ListingPagePrice-secondary"),
                "evjarat": get_text_bs4(soup, "adview__year"),
                "phone_number": clean_pn(phone_response.text),
                "name": get_text_bs4(soup, "mdi-business"),
                "location": get_text_bs4(soup, "contact-button-adview-map").split("Térkép megtekintése")[0]
            }

            print(l)
            if l["phone_number"] != "":
                return [l]
            return []
    except Exception as e:
        if first:
            print("Try again", e)
            return load_product_info(product_id, False)
        print("sec try", e)
        return []



if __name__ == "__main__":
    Hasznaltauto()