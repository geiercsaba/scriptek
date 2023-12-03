from modules.excel_control import load_excel, write_to_excel
from modules.takarnet_acces import download_all_pdf
from config import logger, WORKDIR_PATH
from tkinter.filedialog import askopenfilename

# Bemeneti excel betöltése, tulajdonlapok letöltése és kimeneti_excel file létrehozása a munkakönyvtárba
array = load_excel(askopenfilename(filetypes=[("Bemeneti file", "*.xlsx")]))
excel_save_path = WORKDIR_PATH + "/kimeneti_excel.xlsx"
write_to_excel(excel_save_path, download_all_pdf(array))

input("Press any key to Close")







