
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FOLDER_ID = '1aPneu8d9rQKC_9Wbr7FAK-pRzcUyN_VN'
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

EXCLUDE_DIRS = {'.git', '__pycache__', '.github'}  # folders to skip
EXCLUDE_FILES = {'credentials.json', 'upload_all_files.py'}  # files to skip
EXCLUDE_EXTENSIONS = {'.sample'}  # extensions to skip

def should_skip(file_path):
    filename = os.path.basename(file_path)

    if filename in EXCLUDE_FILES:
        return True
    if any(file_path.startswith(f"./{d}/") for d in EXCLUDE_DIRS):
        return True
    if os.path.splitext(filename)[1] in EXCLUDE_EXTENSIONS:
        return True
    if filename.startswith("."):  # skip hidden files like `.gitignore`
        return True
    return False

def upload_file(service, file_path):
    if should_skip(file_path):
        print(f"⏭️ Skipped: {file_path}")
        return

    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)

    # Check if file exists
    result = service.files().list(q=f"name='{file_name}' and '{FOLDER_ID}' in parents and trashed=false").execute()
    files = result.get('files', [])

    if files:
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"🔁 Updated: {file_name}")
    else:
        metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        service.files().create(body=metadata, media_body=media).execute()
        print(f"✅ Uploaded: {file_name}")

def upload_all_files():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    for root, _, files in os.walk("."):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, start=".")
            upload_file(service, f"./{rel_path}")

if __name__ == '__main__':
    upload_all_files()
