# process_content.py

import os
import io
import shutil
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import config

def authenticate_drive(creds_file):
    """
    Authenticates and returns the Google Drive service object.
    
    Parameters:
        creds_file (str): Path to the credentials JSON file.
        
    Returns:
        service: Authorized Google Drive service instance.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("Loaded existing credentials from 'token.json'.")
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("Refreshed expired credentials.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
                print("Authenticated new credentials.")
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                print("Saved new credentials to 'token.json'.")
        service = build('drive', 'v3', credentials=creds)
        print("Google Drive service built successfully.")
        return service
    except FileNotFoundError:
        print(f"Error: Credentials file '{creds_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        sys.exit(1)

def download_images_videos(service, folder_id, download_path):
    """
    Downloads all images and videos from the specified Google Drive folder.
    
    Parameters:
        service: Authorized Google Drive service instance.
        folder_id (str): ID of the source Google Drive folder.
        download_path (str): Local path to save downloaded files.
    """
    try:
        query = f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed=false"
        print(f"Searching for images and videos in folder ID: {folder_id}")
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            print('No image or video files found in the source folder.')
            return

        print(f"Found {len(items)} files to download.")
        for item in items:
            file_id = item['id']
            file_name = item['name']
            file_path = os.path.join(download_path, file_name)
            try:
                request = service.files().get_media(fileId=file_id)
                fh = io.FileIO(file_path, 'wb')
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                print(f"Starting download of '{file_name}'...")
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Downloading '{file_name}': {int(status.progress() * 100)}%")
                print(f"Successfully downloaded '{file_name}'.")
            except Exception as e:
                print(f"Failed to download '{file_name}': {e}")
    except Exception as e:
        print(f"An error occurred while listing or downloading files: {e}")
        sys.exit(1)

def upload_to_drive(service, upload_folder_id, upload_path):
    """
    Uploads all files from the specified local directory to the target Google Drive folder.
    
    Parameters:
        service: Authorized Google Drive service instance.
        upload_folder_id (str): ID of the target Google Drive folder.
        upload_path (str): Local path where files are stored to be uploaded.
    """
    try:
        files = os.listdir(upload_path)
        if not files:
            print('No files available to upload.')
            return

        print(f"Starting upload of {len(files)} files to folder ID: {upload_folder_id}")
        for file_name in files:
            file_path = os.path.join(upload_path, file_name)
            try:
                file_metadata = {
                    'name': file_name,
                    'parents': [upload_folder_id]
                }
                media = MediaFileUpload(file_path, resumable=True)
                print(f"Uploading '{file_name}'...")
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"Successfully uploaded '{file_name}' with File ID: {file.get('id')}.")
            except Exception as e:
                print(f"Failed to upload '{file_name}': {e}")
    except Exception as e:
        print(f"An error occurred while uploading files: {e}")
        sys.exit(1)

def clean_up(download_path):
    """
    Deletes the local download directory and its contents.
    
    Parameters:
        download_path (str): Path to the local download directory.
    """
    try:
        if os.path.exists(download_path):
            shutil.rmtree(download_path)
            print(f"Cleaned up the local directory '{download_path}'.")
    except Exception as e:
        print(f"An error occurred during cleanup: {e}")

def main():
    """
    Main function to orchestrate the download and upload of images and videos within Google Drive.
    """
    print("Process started.")
    # Ensure the download directory exists
    if not os.path.exists(config.download_path):
        try:
            os.makedirs(config.download_path)
            print(f"Created download directory at '{config.download_path}'.")
        except Exception as e:
            print(f"Failed to create download directory '{config.download_path}': {e}")
            sys.exit(1)
    else:
        print(f"Download directory '{config.download_path}' already exists.")

    # Authenticate and build the Google Drive service
    service = authenticate_drive(config.cred_file_path)

    # Download images and videos from the source folder
    print("Initiating download process...")
    download_images_videos(service, config.source_folder_id, config.download_path)

    # Upload the downloaded files to the target folder
    print("Initiating upload process...")
    upload_to_drive(service, config.target_folder_id, config.download_path)

    # Optionally, clean up the downloaded files
    print("Cleaning up downloaded files...")
    clean_up(config.download_path)

    print("Process completed successfully.")
    #print("\n\n<===== Make Sure to Delete the Contents Downloaded in Your Local =====>")

if __name__ == '__main__':
    main()
