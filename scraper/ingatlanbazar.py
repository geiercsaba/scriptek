import requests
import json
from bs4 import BeautifulSoup
from webdriver import PROXY, append_xlsx, clean_pn
from drive import upload_xlsx
import threading



class IngatlanBazar:
    def __init__(self):
        results = []
        threads = []

        thread = threading.Thread(target=lambda: results.extend(get_page(100, "ingatlan-Elado-Haz")))
        thread.start()
        threads.append(thread)

        thread = threading.Thread(target=lambda: results.extend(get_page(3200, "ingatlan-Elado-Lakas")))
        thread.start()
        threads.append(thread)

        thread = threading.Thread(target=lambda: results.extend(get_page(100, "ingatlan-Elado-Nyaralo")))
        thread.start()
        threads.append(thread)

        thread = threading.Thread(target=lambda: results.extend(get_page(400, "ingatlan-Elado-Telek")))
        thread.start()
        threads.append(thread)

        thread = threading.Thread(target=lambda: results.extend(get_page(200, "ingatlan-Elado-Uzleti-ingatlan")))
        thread.start()
        threads.append(thread)

        thread = threading.Thread(target=lambda: results.extend(get_page(100, "alberlet-Kiado-Lakas-es-Haz")))
        thread.start()
        threads.append(thread)

        thread = threading.Thread(target=lambda: results.extend(get_page(100, "alberlet-Kiado-Uzleti-ingatlan")))
        thread.start()
        threads.append(thread)


        for thread in threads:
            thread.join()


        append_xlsx(results, "assets/ingatlanbazar.xlsx")
        upload_xlsx("ingatlanbazar.xlsx", "assets/ingatlanbazar.xlsx")

def get_page(count, page):
    results = []
    for i in range(count):
        try:
            results.extend(getPage(i, page))
        except:
            pass
    return results

def getPage(page, type):
    params = { 'page': page }
    response = requests.get(f'https://www.ingatlanbazar.hu/{type}', params=params, proxies=PROXY, timeout=20)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all('script')

        hits = []
        for script in script_tags:
            if 'jsonData' in script.text:
                records = json.loads(script.text.split("jsonData = ")[1].split("};")[0]+"}")
                for record in records["property-search"]["hits"]:
                    hit = {
                        "title": record["title"],
                        "originCreatedAt": record["originCreatedAt"],
                        "priceHUF": record["priceHUF"],
                        "priceEUR": record["priceEUR"],
                        "county": record["county"],
                        "ownerTel": clean_pn(record["ownerTel"]),
                        "ownerName": record["ownerName"],
                        "salesPersonTel": clean_pn(record["salesPersonTel"]),
                        "salesPersonName": record["salesPersonName"],
                        "salesPersonEmail": record["salesPersonEmail"],
                    }
                    hits.append(hit)
                print(f"Kinyerve {page} oldal: {len(hits)} találat")
                return hits
    return []

if __name__ == "__main__":
    IngatlanBazar()