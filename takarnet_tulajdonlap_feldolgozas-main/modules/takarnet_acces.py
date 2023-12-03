from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from urllib3.exceptions import InsecureRequestWarning
import requests
from modules.pdf_data_class import Property
from config import logger, CERTIFICATES_PATH, PDF_SAVE_PATH


def download_pdf(link, file_name):
    session = requests.Session()
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    response = session.get(link, cert=CERTIFICATES_PATH, verify=False)

    if response.status_code == requests.codes.ok:
        with open(file_name, 'wb') as file:
            file.write(response.content)
    else:
        logger.warning(f"Nem sikerült letölteni a tulajdonlapot! Manuálisan kell letölteni. \nLink a letöltéshez: {link}")
    logger.debug("Tulajdoni lap sikeresen letöltve a mappába!")


def download_all_pdf(records):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www4.takarnet.hu/frames5.html")

    tulajdonosok_array = []
    # Keresési mezők kitöltése
    for element in records:
        # Navigálás a keresési mezők kitöltéséhez
        try:
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "lenyeg")))
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fomenu")))
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Tulajdoni lap másolat"))).click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "E-hiteles tulajdoni lap másolat"))).click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "- Lekérdezés helyrajzi szám szerint"))).click()
        except TimeoutException:
            logger.warning("Nem várt hiba történt. Nem sikerült a keresési mezők oldalára navigálni.")
            raise Exception("Nem várt hiba történt. Nem sikerült a keresési mezők oldalára navigálni.")

        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "lenyeg")))
        logger.debug("Takarnet betöltve, keresési mezők kitöltése")

        hrsz = element[1].split("/")
        kulbel = "2" if hrsz[0][0] == "0" else "1"  # zártkert nincs
        driver.find_element(By.NAME, "kero_nev").send_keys("Helionergy Holding Kft.")
        driver.find_element(By.NAME, "kero_cim2").send_keys("Déri Miksa utca 6. 1. lház. 2.em.2.")
        driver.find_element(By.NAME, "kero_cim3").send_keys("1084")
        driver.find_element(By.NAME, "helyseg").send_keys(element[0])
        Select(driver.find_element(By.NAME, "fekves")).select_by_value(kulbel) #Jelenleg zártkert nincs
        driver.find_element(By.NAME, "hrsztol").send_keys(hrsz[0])
        driver.find_element(By.NAME, "hrsz1tol").send_keys(hrsz[1])
        driver.find_element(By.NAME, "jogalap").send_keys("Naperőmű célhely ellenőrzés")
        driver.find_element(By.XPATH, "/html/body/form[2]/table[2]/tbody/tr/td[1]/input[4]").click()
        logger.debug("Keresési mezők kitöltve, tulajdonlap keresése folyamatban.")

        try:
            table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[2]/tbody/tr/td[1]/center[2]/table/tbody")))
            href_tr = table.find_elements(By.TAG_NAME, "tr")
            href_cell = href_tr[1].find_element(By.TAG_NAME, "a")
            href_cell.click()
            pdf_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/table[2]/tbody/tr/td[1]/a")))
            href_value = pdf_link.get_attribute("href")
            save_path = PDF_SAVE_PATH + f"/Tullap_{element[0]}_{hrsz[0]}_{hrsz[1]}.pdf"
            download_pdf(href_value, save_path)
            tulajdonosok_array.append(Property(element[0], element[1], save_path))
        except TimeoutException:
            logger.warning(f"Nincs találat az alábbi tulajdonlapra: {element[0]}, {element[1]}")

        driver.refresh()

        # Nem tesztelt funkció!! A pdf-ek bezárását kezeli a túl sok memóriafelhasználás miatt.
        start_window = driver.current_window_handle
        start_url = driver.current_url
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            current_url = driver.current_url
            if current_url != start_url:
                driver.close()
        driver.switch_to.window(start_window)
        # Nem tesztelt kód vége

    driver.quit()
    return tulajdonosok_array
