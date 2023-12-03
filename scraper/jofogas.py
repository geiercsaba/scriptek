from webdriver import *
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json


class Jofogas:
    def __init__(self):
        self.load_products()

    def load_products(self):
        ids = []
        pages = [range(55000)]

        max_workers = 100
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(load_products_page, page) for page in pages]

        for future in futures:
            ids.extend(future.result())

        append_xlsx(ids, "assets/jofogas.xlsx")
        upload_xlsx("jofogas.xlsx", "assets/jofogas.xlsx")


def load_products_thread(a, b):
    product_ids = []
    for i in range(a, b):
        try:
            p = load_products_page(i)
            if p == "DONE":
                return product_ids
            product_ids.extend(p)
        except Exception as e:
            print("Hiba keletkezett", i, e)
    return product_ids


def load_products_page(page_number):
    product_ids = []
    response = requests.get(f"https://www.jofogas.hu/magyarorszag?o={page_number}", proxies=PROXY, timeout=20)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all(class_="list-item")

        if len(products) == 0:
            return "DONE"

        for product in products:
            if product.find(class_="validPhone"):
                item_title = product.find(class_="item-title")
                link = item_title.find("a")["href"]
                name = item_title.find("a").text.strip()
                price = product.find(class_="price-value").text.strip()
                city = product.find(class_="cityname").text.strip()
                listing = {
                    "link": link,
                    "name": name,
                    "price": price,
                    "city": city,
                    "phone_number": get_phone_number(link)
                }
                if listing["phone_number"] != "":
                    product_ids.append(listing)
    print("oldal, kinyert_termékek", page_number, len(product_ids))
    return product_ids


def get_phone_number(link):
    try:
        list_id = max(re.findall(r'\d+', link), key=len, default=None)
        url = f'https://apiv2.jofogas.hu/v2/items/getPhone?list_id={list_id}'
        headers = {'api_key': 'jofogas-web-eFRv9myucHjnXFbj'}
        response = requests.get(url, headers=headers, proxies=PROXY, timeout=20)
        if response.status_code == 200:
            pn = json.loads(response.text)["phone"]
            return clean_pn(pn)
        return ""
    except Exception:
        return ""

if __name__ == "__main__":
    Jofogas()