# A WORKDIR_PATH változó értéke a munkakönyvtár
# Munkakönyvtár subdir.-ek (save_to, certificates, log) létrehozása szükséges!

WORKDIR_PATH = "/Users/geiercsaba/Desktop/SolarKit_WorkDir"
PDF_SAVE_PATH = WORKDIR_PATH + "/save_to"
CERTIFICATES_PATH = WORKDIR_PATH + "/certificates/VTKM6916.pem"
LOGGER_FILE_PATH = WORKDIR_PATH + "/log"

import logging
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOGGER_FILE_PATH + "/log_info.log")
logger.addHandler(file_handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

