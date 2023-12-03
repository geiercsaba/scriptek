import PyPDF2
from config import logger


# paraméterként egy pdf file-t kap, melyből kinyeri az ingatlan adatira vonatkozó részt(táblázat).
def extract_property_data(file_path):
    with open(file_path, 'rb') as file:
        page = PyPDF2.PdfReader(file).pages[0]
        text = page.extract_text()
        start_index = text.find("------------------------------------------------------------------------------------------------")
        end_index = text.find("\n \n", start_index)

        # Ha nincs meg a start_index vagy end_index
        if start_index == -1 or end_index == -1:
            raise Exception("Váratlan hiba lépett fel a programban")

        extracted_data = text[start_index+97:end_index]
        return extracted_data.strip()


# Megkeresi a tulajdonosi adatokra vonatkozó részeket és visszatér egy k elemű tömbbel, ahol k a tulajdonosok száma.
def extract_owners(file_path):
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        res = []

        for page in pdf.pages:
            text = page.extract_text()
            start = 0
            while True:
                start_idx = text.find("tulajdoni hányad: ", start)
                if start_idx == -1:
                    break
                end_idx = text.find("\n \n", start_idx)
                if end_idx == -1:
                    break
                    
                res.append(text[start_idx:end_idx].strip())
                start = end_idx + len("\n \n")
    logger.debug(f"{len(res)} db tulajdonos adat átadva.")
    return res


def pdf_terhek(file_path):
    with open(file_path, 'rb') as file:
        terhek = set()
        pdf = PyPDF2.PdfReader(file)

        for page in pdf.pages:
            text = page.extract_text()
            if "Özvegyi jog" in text:
                terhek.add("Özvegyi jog")
            if "Vezetékjog" in text:
                terhek.add("Vezetékjog")
            if "Végrehajtási jog" in text:
                terhek.add("Végrehajtási jog")
            if "Vételi jog" in text:
                terhek.add("vételi jog")
            if "Haszonélvezet" in text:
                terhek.add("haszonélvezeti jog")
            if "Jelzálog" in text:
                terhek.add("jelzálogjog")
            if "Út szolgalmi jog" in text:
                terhek.add("útszolgalmi jog")
            if "Átjárási szolgalmi jog" in text:
                terhek.add("átjárási szolgalmi jog")
            if "Bányaszolgalmi jog" in text:
                terhek.add("bányaszolgalmi jog")
            if "Földmérési jelek elhelyezését biztosító közérdekű használati jog" in text:
                terhek.add("Földmérési jelek elhelyezését biztosító közérdekű használati jog")
    return terhek

# Szavanként felvágja a szöveget és soronként egy tömbbe rendezi. k sor esetén k tömb lesz a kimenet
def split_line(text):
    lines = text.split('\n')
    array = []
    for line in lines:
        line_split = line.split()
        array.append(line_split)
    return array





