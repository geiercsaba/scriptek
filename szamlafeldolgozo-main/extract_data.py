import PyPDF2
from tkinter.filedialog import askdirectory
from openpyxl import Workbook


def write_to_excel(file_name, data):
    workbook = Workbook()
    worksheet = workbook.active

    columns = ["", "", "vas", "", "", "réz", "", "", "kábel", "", "", "alu", "", ""]
    worksheet.append(columns)

    columns = ["szerződés szám", "dátum", "súly(kg)", "egységár(eur)", "érték(eur)",
               "súly(kg)", "egységár(eur)", "érték(eur)", "súly(kg)", "egységár(eur)", "érték(eur)", "súly(kg)", "egységár(eur)", "érték(eur)"]
    worksheet.append(columns)

    for values in data:
        for value in values[0]:
            match value[3]:
                case "aluminium":
                    columns = [values[2], values[1], "", "", "", "", "", "", "", "", "", value[0], value[1], value[2]]
                    worksheet.append(columns)
                case "vas":
                    columns = [values[2], values[1], value[0], value[1], value[2], "", "", "", "", "", "", "", "", ""]
                    worksheet.append(columns)
                case "rez":
                    columns = [values[2], values[1], "", "", "", value[0], value[1], value[2], "", "", "", "", "", ""]
                    worksheet.append(columns)
                case "kabel":
                    columns = [values[2], values[1], "", "", "", "", "", "", value[0], value[1], value[2], "", "", ""]
                    worksheet.append(columns)

    workbook.save(filename=file_name)


def extract_numbers(text):
    parts = []
    while text:
        index = text.find(",")
        if index == -1:
            break
        index2 = text.find(" ", index)
        if index2 == -1:
            parts.append(text)
        else:
            parts.append(text[:index2])
        text = text[index2:].strip()

    parts2 = []
    for part in parts:
        part = part.replace(" ", "").replace(",", ".")
        part = float(part)
        parts2.append(part)
    return parts2


def extract_values(text, termek2, termek, szerzodes):
    # vas, réz, kábel, aluminium, egyeb
    # aluminium, vas, rez, kabel
    if "ACEL" in termek or "KOR" in termek or "VAS" in termek or "OLOM" in termek:
        tipus = "vas"
    elif "ALU" in termek or "FARBENY" in text:
        tipus = "aluminium"
    elif "REZ" in termek or "ZINK" in text or "ZINOK" in text:
        tipus = "rez"
    elif "KABEL" in termek or "KABLOVY" in text:
        tipus = "kabel"
    else:
        if "ACEL" in termek2 or "KOR" in termek2 or "VAS" in termek2 or "OLOM" in termek2 or "ACEL" in text:
            tipus = "vas"
        elif "ALU" in termek2:
            tipus = "aluminium"
        elif "REZ" in termek2 or "REZ" in text:
            tipus = "rez"
        elif "KABEL" in termek2:
            tipus = "kabel"
        else:
            tipus = "vas"

    index = text.find("KG")
    # 4 elemű tömb: suly, egysegar, ertek, tipus
    values = extract_numbers(text[index:][3:])
    values.append(tipus)
    return values


def extract_page(file_path):
    with open(file_path, 'rb') as file:
        page = PyPDF2.PdfReader(file).pages[0]
        text = page.extract_text().split("\n")
        values = []
        datum = ""
        szerzodes = ""
        for i, t in enumerate(text):
            if "FAKTÚRA č.:" in t:
                d = t[:10].split(".")
                datum = f"{d[2]}.{d[1]}.{d[0]}"
                szerzodes = t.split(":")[-1][1:]
            if "KG" in t:
                array = extract_values(t, text[i+1], text[i+2], szerzodes)
                if len(array) == 4:
                    values.append(array)
        return [values, datum, szerzodes]

def main():
    import os
    import glob

    mappa = "/Users/geiercsaba/Downloads"
    # mappa = askdirectory()
    shame = os.path.join(mappa, "*.pdf")
    files = glob.glob(shame)
    szamlak = []
    for file in files:
        szamlak.append(extract_page(file))
    print(len(szamlak))
    write_to_excel("/Users/geiercsaba/Desktop/anyagosszesito.xlsx", szamlak)

main()