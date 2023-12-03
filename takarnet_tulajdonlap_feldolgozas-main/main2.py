from config import logger
from tkinter.filedialog import askopenfilename, askdirectory
from modules.excel_control import folder_to_excel

# Támogatott formátum: "Tullap_{város}_{hrsz1}_{hrsz2}"
folder_to_excel(askdirectory())

input("Press any key to Close")