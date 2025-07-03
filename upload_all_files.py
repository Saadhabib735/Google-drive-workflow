import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FOLDER_ID = '1aPneu8d9rQKC_9Wbr7FAK-pRzcUyN_VN'  # Replace with your folder ID
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

def upload_file_to_drive(service, file_path):
    file_name = os.path.basename(file_path)
    query = f"name='{file_name}' and '{FOLDER_ID}' in parents and trashed=false"
    existing_files = service.files().list(q=query).execute().get('files', [])

    media = MediaFileUpload(file_path, resumable=True)
    if existing_files:
        file_id = existing_files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"🔁 Updated: {file_name}")
    else:
        file_metadata = {
            'name': file_name,
            'parents': [FOLDER_ID]
        }
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"✅ Uploaded: {file_name}")

def upload_all_files():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    for root, _, files in os.walk("."):
        for file in files:
            if file in ['upload_all_files.py', 'credentials.json']:
                continue  # Skip script and credentials
            file_path = os.path.join(root, file)
            upload_file_to_drive(service, file_path)

if __name__ == '__main__':
    upload_all_files()

