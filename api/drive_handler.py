import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import config

class DriveHandler:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(config.DRIVE_KEY_PATH)
        self.service = build('drive', 'v3', credentials=creds)

    def get_new_files(self):
        """Lists files in the target folder."""
        query = f"'{config.DRIVE_FOLDER_ID}' in parents and trashed = false"
        results = self.service.files().list(q=query).execute()
        return results.get('files', [])

    def download_image(self, file_id):
        """Downloads Drive file to RAM."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()