import time

from webdriver import *
import threading

class CVOnline:
    def __init__(self):
        print("CVOnline.hu frissítése szükséges")
        time.sleep(5)
        exit(1)
        # self.cv = self.load_cv()
        # self.create_xlsx()

    def load_cv(self):
        """
        az összes CV lementése.
        :return: az összes CV amit ki kell nyerni egy tömbben
        """
        cv_array = []
        threads = []
        for i in range(10):
            thread = threading.Thread(target=lambda i=i: cv_array.extend(load_list(i * 2000, i * 2000 + 2000)))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return cv_array

    def create_xlsx(self):
        parts = list(split_set(5, self.cv))
        rows = []
        threads = []
        for p in parts:
            thread = threading.Thread(target=lambda p=p: rows.extend(load_cvs(p)))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        append_xlsx(rows, "assets/cvonline.xlsx")
        upload_xlsx("cvonline.xlsx", "assets/cvonline.xlsx")

def load_list(start, stop):
    driver = create_chromedriver()
    cvonline_login(driver)
    i = start
    cv_array = []
    while i < stop:
        driver.get(f"https://www.cvonline.hu/hu/oneletrajzok?f%5B0%5D=user%253Alast_login%3Alast_month&page={i}")
        i += 1
        rows = driver.find_elements(By.CLASS_NAME, "views-row")

        if len(rows) == 0:
            break

        for cv in rows:
            # Mindegyik CV-ről lemenjük a nevet, a linket és a várost majd egy dict-be tesszük és hozzáadjuk a tömbhöz
            try:
                cv_name = cv.find_element(By.CLASS_NAME, "recruiter-resume-link").text
                cv_link = cv.find_element(By.CLASS_NAME, "recruiter-resume-link").get_attribute("href")
                cv_city = cv.find_element(By.CLASS_NAME, "field-name--field-location").find_element(By.CLASS_NAME, "field__items").text
                cv_dict = {
                    "name": cv_name,
                    "link": cv_link,
                    "city": cv_city
                }
                print(cv_dict)
                cv_array.append(cv_dict)
            except Exception as e:
                pass

    print(f"CVOnline.hu kinyerve összesen: {stop-start} oldal és {len(cv_array)} CV")
    return cv_array


def load_cvs(array):
    driver = create_chromedriver()
    cvonline_login(driver)
    new_array = []
    for a in array:
        driver.get(a["link"])
        phone_number = get_text(driver, ".field--name-field-resume-phone .field__item")
        name = a["name"]
        city = a["city"]
        email = get_text(driver, ".mail .field-item")
        salary = get_text(driver, ".field--name-field-resume-desired-salary-term .field__item")
        position = get_text(driver, ".field--name-field-resume-job-title .field__item")
        position2 = get_text(driver, ".field--name-field-resume-jobpref-field .field__item")
        status = get_text(driver, ".field--name-field-resume-career-status .field__item")
        availability = get_text(driver, ".field--name-field-resume-job-availability .field__item")
        expreience = get_text(driver, ".field--name-field-cvonline-resume-years-exp .field__item")
        term = get_text(driver, ".field--name-field-resume-employment-term .field__item")
        licence = get_text(driver, ".field--name-field-resume-driving-licences .field__item")

        dict = {
            "link": a["link"],
            "name": name,
            "phone_number": clean_pn(phone_number),
            "city": city,
            "email": email,
            "position": position,
            "terulet": position2,
            "status": status,
            "availability": availability,
            "expreience": expreience,
            "term": term,
            "salary": salary,
            "licence": licence,
        }
        print(dict, ",")
        new_array.append(dict)
    return new_array


def cvonline_login(driver):
    driver.get("https://www.cvonline.hu/hu/user/login")
    driver.find_element(By.ID, "edit-name").send_keys("email")
    driver.find_element(By.ID, "edit-pass").send_keys("pass")
    driver.find_element(By.ID, "edit-pass").send_keys(Keys.RETURN)

if __name__ == "__main__":
    CVOnline()
