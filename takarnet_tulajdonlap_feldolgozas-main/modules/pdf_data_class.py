from modules.pdf_util import extract_property_data, split_line, extract_owners, pdf_terhek
import re
from config import logger


# Keres a szövegben "xxxx.xx.xx" formátumban szöveget, ha talál visszaadja, ha nem akkor None
def date_format(text):
    date = re.search(r'\d{4}\.\d{2}\.\d{2}', text)
    if date:
        return date.group()
    return None


class Owner:
    def __init__(self, input_text):
        self.tulajdoni_hanyad = ""
        self.erkezesi_ido = ""
        self.jogcim = ""
        self.jogallas = ""
        self.nev = ""
        self.szul_nev = ""
        self.szul_date = ""
        self.anyja_neve = ""
        self.iranyitoszam = ""
        self.helyseg = ""
        self.cim = ""
        self.split_text(input_text.split("\n"))

    def split_text(self, input_array):
        for line in input_array:
            if "bejegyzõ határozat, érkezési idõ:" in line:
                self.erkezesi_ido = line.split(":")[1].split("/")[-1]
            elif "jogcím:" in line:
                jog = line.split(":")
                self.jogcim = jog[1][1:].split()[0]
                for j in jog[2:]:
                    if date_format(j):
                        self.erkezesi_ido = date_format(j)
            elif "jogállás:" in line:
                self.jogallas = line.split(":")[1][1:]
            elif "tulajdoni hányad:" in line:
                self.tulajdoni_hanyad = line.split(":")[1][1:]
            elif "név   :" in line or " név: " in line:
                self.nev = line.split(":")[1][1:]
            elif "sz.név:" in line:
                self.szul_nev = line.split(":")[1][1:]
            elif "szül. :" in line:
                self.szul_date = line.split(":")[1][1:]
            elif "a.név :" in line:
                self.anyja_neve = line.split(":")[1][1:]
            elif "cím   :" in line or " cím:" in line:
                text = line.split(":")[1][1:]
                if text == "- -":
                    continue
                address = text.split(" ", 2)
                self.iranyitoszam = address[0]
                self.helyseg = address[1]
                self.cim = address[2]


class Property:
    def __init__(self, city, hrsz, pdf_path):
        self.telepules = city
        self.hrsz = hrsz
        self.muveles: str = ""
        self.minosegi_osztaly: str = ""
        self.termertek: str = ""
        self.aranykorona = ""
        self.tulajdonosok = []  # kizárólag Owner object tárolására
        self.teher = ""
        self.pdf_file_path = pdf_path
        self.extract_properties()

    def extract_properties(self):
        table = extract_property_data(self.pdf_file_path)
        owners = extract_owners(self.pdf_file_path)
        terhek_set = pdf_terhek(self.pdf_file_path)

        for teher in terhek_set:
            self.teher += f", {teher}" if self.teher else teher
        for owner in owners:
            self.tulajdonosok.append(Owner(owner))
            # logger.debug(f"Egy tulajdonos adatai sikeresen hozzáadva a {self.hrsz} tulajdonlap tulajdonosai közé.")
        lines = split_line(table)

        try:
            if lines[0][0] == "." or lines[0][0] == "-":  # Ha egy művelés van
                if len(lines) == 1:  # ha egy sor van a táblázat(minden adat egy sorban)
                    if len(lines[0]) == 5:  # ha megvan minden adat amire szükség van
                        self.muveles = lines[0][1]
                        self.minosegi_osztaly = lines[0][2]
                        self.termertek = lines[0][3]
                        self.aranykorona = lines[0][4]
                    else:                   # Ha több szóból áll a művelés
                        self.muveles = lines[0][1]
                        j = 1
                        while not lines[0][j].isdigit():
                            self.muveles += " "
                            self.muveles += lines[0][j]
                            j += 1
                            if lines[0][j].isdigit():
                                self.minosegi_osztaly += lines[0][j]
                                self.termertek = lines[0][j+1]
                                self.aranykorona = lines[0][j+2]
                elif len(lines) == 0:  # ha nem találja meg a táblázatot
                    raise Exception(f"Nem várt hiba történt a PDF fájl feldolgozása során. ({self.telepules}, {self.hrsz}) -nincs találat a táblázatra")
                else:  # Ha több minőségi osztály van, akkor ez az ág fut le.
                    if len(lines[0]) != 4:
                        self.muveles = lines[0][1]
                        j = 2
                        while not re.match(r'^[\d.]+$', lines[0][j]):
                            self.muveles += " "
                            self.muveles += lines[i][j]
                            j += 1
                        self.termertek = lines[0][j]
                        self.aranykorona = lines[0][j+1]
                        for i in range(1, len(lines)):
                            self.minosegi_osztaly += "," if self.minosegi_osztaly else ""
                            self.minosegi_osztaly += lines[i][0]
                    else:
                        self.muveles = lines[0][1]
                        self.termertek = lines[0][2]
                        self.aranykorona = lines[0][3]
                        for i in range(1, len(lines)):
                            self.minosegi_osztaly += "," if self.minosegi_osztaly else ""
                            self.minosegi_osztaly += lines[i][0]

            elif lines[0][0] == "a":    # Ha több művelés van
                self.termertek = lines[-1][4]
                self.aranykorona = lines[-1][5]
                for i in range(len(lines)-1):
                    if lines[i][0].isdigit():
                        self.minosegi_osztaly += "," if self.minosegi_osztaly else ""
                        self.minosegi_osztaly += lines[i][0]
                    else:
                        if len(lines[i]) == 5:
                            if not lines[i][2].isdigit():
                                raise Exception(f"Nem várt hiba történt a PDF fájl feldolgozása során. ({self.telepules}, {self.hrsz}) (-több szavas művelés?)")
                            self.minosegi_osztaly += "," if self.minosegi_osztaly else ""
                            self.minosegi_osztaly += lines[i][2]

                        self.muveles += "," if self.muveles else ""
                        self.muveles += lines[i][1]
                        j = 2
                        while not lines[i][j].isdigit() and "." not in lines[i][j]:
                            self.muveles += " "
                            self.muveles += lines[i][j]
                            j += 1
                            if lines[i][j].isdigit():
                                if 10 > int(lines[i][j]) >= 0:
                                    self.minosegi_osztaly += "," if self.minosegi_osztaly else ""
                                    self.minosegi_osztaly += lines[i][j]

            else:
                logger.warning(f"Nem várt hiba történt a PDF fájl feldolgozása során. ({self.telepules}, {self.hrsz})")
        except IndexError:
            logger.warning(f"Nem várt hiba történt a {self.telepules} {self.hrsz} file feldolgozása során. Manuálisan kell feltölteni az excel táblázatba.")
        logger.info(f"{self.hrsz} tulajdonlapról az adatok kinyerve. Összesen {len(self.tulajdonosok)} db tulajdonos.")


