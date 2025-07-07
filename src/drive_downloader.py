import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import json
import base64
from dotenv import load_dotenv

from src.utils import logger

class GoogleDriveDownloader:
    def __init__(self):
        """
        Initialize the Google Drive service using a service account key file.
        """
        try:
            load_dotenv()
            encoded = os.getenv("GOOGLE_CREDENTIALS_BASE64")
            if not encoded:
                raise ValueError("GOOGLE_CREDENTIALS_BASE64 is not set in the environment.")
            
            decoded = base64.b64decode(encoded).decode('utf-8')
            credentials_info = json.loads(decoded)

            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )

            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Google Drive API client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive client: {e}")
            raise

    def _download_file(self, file_id: str) -> bytes:
        """
        Downloads a file from Google Drive using its file ID and returns the content as bytes.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO()
            downloader = MediaIoBaseDownload(file_bytes, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            logger.debug(f"Downloaded file with ID: {file_id}")
            return file_bytes.getvalue()
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return None
        
    def download_file(self, link):
        file_id = self.extract_drive_file_id(link)
        return self._download_file(file_id)
        
    @staticmethod
    def extract_drive_file_id(link: str) -> str:
        patterns = [
            r"uc\?id=([^&]+)",
            r"open\?id=([^&]+)",
            r"/file/d/([a-zA-Z0-9_-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        return None

