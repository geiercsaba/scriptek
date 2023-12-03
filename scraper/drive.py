import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "assets/drive_cred.json"

def upload_xlsx(file_name, file_path):
    try:
        creds, _ = google.auth.default()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': file_name,
            'parents': ['folder']
        }
        media = MediaFileUpload(file_path, mimetype='application/vnd.ms-excel')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    except Exception:
        print("Nem sikerült feltölteni az excel táblázatot a Google Drive-ra.")


def drop_duplicates(file_path, column_name=None):
    df = pd.read_excel(file_path)
    df = df.drop_duplicates(file_path)
    if isinstance(column_name, list):
        df = df.drop_duplicates(subset=[column_name])
    df.to_excel(file_path, index=False)
    pass

