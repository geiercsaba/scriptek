import threading
from webdriver import *

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "assets/drive_cred.json"


class Ingatlan:
    def __init__(self):
        self.load_products()

    def load_products(self):
        ids = set()
        threads = []
        print("kiado")
        for g in range(1):
            thread = threading.Thread(target=lambda g=g: ids.update(get_listings(g * 450, (g + 1) * 450), "kiado"))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # print("elado")
        # threads = []
        # for g in range(3):
        #     thread = threading.Thread(target=lambda g=g: ids.update(get_listings(g * 3300, (g+1) * 3300)))
        #     threads.append(thread)
        #     thread.start()
        #
        # for thread in threads:
        #     thread.join()

        previus_set = load_set("ingatlan")
        different_elements = ids.difference(previus_set)
        previus_set.update(different_elements)
        save_set("ingatlan", previus_set)


        part = split_set(3, different_elements)
        rows = []
        threads = []
        for g in part:
            thread = threading.Thread(target=lambda g=g: rows.extend(get_phone_number(g)))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        append_xlsx(rows, "assets/ingatlan.xlsx")
        upload_xlsx("ingatlan.xlsx", "assets/ingatlan.xlsx")


def get_listings(start, stop, list_type="elado"):
    rows = set()
    for i in range(start, stop):
        try:
            driver = create_chromedriver()
            driver.get(f"https://ingatlan.com/lista/{list_type}?page={i}")
            cards = driver.find_elements(By.CLASS_NAME, "listing-card")

            for c in cards:
                href_tag = c.get_attribute("href")
                rows.add(href_tag)
            driver.quit()
            print(f"get_listings: {i}, {len(cards)} {len(rows)}\n")
        except Exception as e:
            input("hiba: " + str(e))
    return rows


def get_phone_number(link):
    objects = []
    for l in link:
        try:
            driver = create_chromedriver()
            driver.get(l)
            click_btn(driver, "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            click_btn(driver, "[data-testid='reveal-phone-number-button']")
            name = get_text(driver, "#hero-contact > div.d-flex.flex-fill.flex-column.justify-content-around.px-0 > div.d-flex.align-items-center.justify-content-center.my-4 > div.col-print.print-flex-1 > span")
            address = get_text(driver, "div.d-flex.flex-column.flex-grow-1 > span.card-title.px-0.fw-bold.fs-4.mb-0.font-family-secondary")
            price = get_text(driver, "#hero > div:nth-child(2) > div.col-xl-8.col-12 > div.row.card.border-ash.bg-white.rounded-5.p-4.mt-3.me-xl-1 > div.row.justify-content-center.border.border-ash.rounded-5.mt-3.py-2.px-0.px-md-2.mx-auto > div.listing-property.justify-content-around.col-12.col-sm.col-print.d-flex.flex-column.text-center.print-border-end.border-sm-end.border-1.border-ash.fs-7.font-family-secondary > span.fw-bold.fs-5.text-nowrap > span")
            phone_number = get_text_with_wait(driver, ".revealed-contact-phone-numbers .contact-phone-number")
            obj = {
                "link": l,
                "name": name,
                "address": address,
                "price": price,
                "phone_number": clean_pn(phone_number)
            }
            if obj["phone_number"]:
                objects.append(obj)
            print(obj)
            driver.quit()
        except Exception as e:
            print("hiba: ", e)

    return objects

if __name__ == "__main__":
    Ingatlan()