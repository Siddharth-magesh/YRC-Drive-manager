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
from colorama import init, Fore, Style
from PIL import Image
from PIL.ExifTags import TAGS
import cv2
import mimetypes


# Initialize colorama
init(autoreset=True)

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
            print(Fore.GREEN + "✔ Loaded existing credentials from 'token.json'.")
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print(Fore.GREEN + "🔄 Refreshed expired credentials.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
                print(Fore.GREEN + "✔ Authenticated new credentials.")
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                print(Fore.GREEN + "💾 Saved new credentials to 'token.json'.")
        service = build('drive', 'v3', credentials=creds)
        print(Fore.GREEN + "✔ Google Drive service built successfully.\n")
        return service
    except FileNotFoundError:
        print(Fore.RED + f"✖ Error: Credentials file '{creds_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"✖ An error occurred during authentication: {e}")
        sys.exit(1)

def download_images_videos(service, folder_id, download_path, large_files_path, size_threshold):
    """
    Downloads all images and videos from the specified Google Drive folder.
    Files exceeding the size_threshold are downloaded to large_files_path instead of download_path.

    Parameters:
        service: Authorized Google Drive service instance.
        folder_id (str): ID of the source Google Drive folder.
        download_path (str): Local path to save downloaded files.
        large_files_path (str): Local path to save large files.
        size_threshold (int): Maximum file size in bytes for immediate upload.
    """
    try:
        page_token = None
        while True:
            query = f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed=false"
            print(Fore.CYAN + "🔍 Searching for images and videos in the source folder...")
            
            # Get files and handle pagination
            results = service.files().list(
                q=query, 
                fields="nextPageToken, files(id, name, mimeType, size)", 
                pageToken=page_token
            ).execute()
            items = results.get('files', [])

            if not items:
                print(Fore.YELLOW + "⚠ No more image or video files found in the source folder.\n")
                break

            print(Fore.CYAN + f"📂 Found {len(items)} files to process.\n")
            for item in items:
                file_id = item['id']
                file_name = item['name']
                mime_type = item['mimeType']
                file_size = int(item.get('size', 0))  # size is in bytes

                if file_size > size_threshold:
                    # Move to large_files_path
                    large_file_path = os.path.join(large_files_path, file_name)
                    print(Fore.MAGENTA + f"📁 File '{file_name}' exceeds the size threshold ({file_size} bytes). Moving to 'large_files' folder.")
                    try:
                        request = service.files().get_media(fileId=file_id)
                        fh = io.FileIO(large_file_path, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)

                        done = False
                        print(Fore.MAGENTA + f"⏳ Starting download of large file '{file_name}'...")
                        while not done:
                            status, done = downloader.next_chunk()
                            if status:
                                print(Fore.MAGENTA + f"🔄 Downloading '{file_name}': {int(status.progress() * 100)}%")
                        print(Fore.GREEN + f"✔ Successfully downloaded large file '{file_name}' to '{large_files_path}'.\n")
                    except Exception as e:
                        print(Fore.RED + f"✖ Failed to download large file '{file_name}': {e}\n")
                    continue  # Skip uploading this file now

                # Download to download_path
                file_path = os.path.join(download_path, file_name)
                try:
                    request = service.files().get_media(fileId=file_id)
                    fh = io.FileIO(file_path, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)

                    done = False
                    print(Fore.BLUE + f"⏳ Starting download of '{file_name}'...")
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            print(Fore.BLUE + f"🔄 Downloading '{file_name}': {int(status.progress() * 100)}%")
                    print(Fore.GREEN + f"✔ Successfully downloaded '{file_name}'.\n")
                except Exception as e:
                    print(Fore.RED + f"✖ Failed to download '{file_name}': {e}\n")
            
            # Check if there is another page of results
            page_token = results.get('nextPageToken')
            if not page_token:
                break  # No more pages, exit the loop
    except Exception as e:
        print(Fore.RED + f"✖ An error occurred while listing or downloading files: {e}\n")
        sys.exit(1)


def create_subfolders(service, parent_folder_id, subfolder_names):
    """
    Creates subfolders inside the parent folder if they do not already exist.

    Parameters:
        service: Authorized Google Drive service instance.
        parent_folder_id (str): ID of the parent Google Drive folder.
        subfolder_names (list): List of subfolder names to create.

    Returns:
        dict: Mapping of subfolder names to their respective IDs.
    """
    subfolder_ids = {}
    for name in subfolder_names:
        # Check if subfolder already exists
        query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{name}' and '{parent_folder_id}' in parents and trashed = false"
        try:
            results = service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            if files:
                subfolder_ids[name] = files[0]['id']
                print(Fore.GREEN + f"✔ Subfolder '{name}' already exists with ID: {files[0]['id']}.")
            else:
                # Create the subfolder
                file_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder_id]
                }
                folder = service.files().create(body=file_metadata, fields='id').execute()
                subfolder_ids[name] = folder.get('id')
                print(Fore.GREEN + f"✔ Created subfolder '{name}' with ID: {folder.get('id')}.")
        except Exception as e:
            print(Fore.RED + f"✖ Failed to create or find subfolder '{name}': {e}\n")
            sys.exit(1)
    print()  # Add a newline for better readability
    return subfolder_ids

def push_file(file_name,target_subfolder_id,subfolder_type,file_path,service):
    try:
        file_metadata = {
            'name': file_name,
            'parents': [target_subfolder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        print(Fore.BLUE + f"⏳ Uploading '{file_name}' to '{subfolder_type}' subfolder...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(Fore.GREEN + f"✔ Successfully uploaded '{file_name}' with File ID: {file.get('id')}.\n")
    except Exception as e:
        print(Fore.RED + f"✖ Failed to upload '{file_name}': {e}\n")

def group_photo_compactabilty_check(image_path, cascade_path='haarcascade_frontalface_default.xml'):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)

    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return 0

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.05, 
        minNeighbors=8,  
        minSize=(20, 20),  
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    if len(faces) > config.group_photo_threshold_person_count:
        print(f"Number of faces detected in {image_path}: {len(faces)}")
        return True
    else:
        return False


def upload_to_drive(service, upload_folder_id, upload_path):
    """
    Uploads all files from the specified local directory to the target Google Drive folder,
    organizing images and videos into separate subfolders.

    Parameters:
        service: Authorized Google Drive service instance.
        upload_folder_id (str): ID of the target Google Drive folder.
        upload_path (str): Local path where files are stored to be uploaded.
    """
    try:
        # Create subfolders 'images' and 'videos' inside the target folder
        subfolders = ['images', 'videos','DSLR','GroupPhotos','geotaged']
        subfolder_ids = create_subfolders(service, upload_folder_id, subfolders)

        files = os.listdir(upload_path)
        if not files:
            print(Fore.YELLOW + "⚠ No files available to upload.\n")
            return

        print(Fore.CYAN + f"📤 Starting upload of {len(files)} files to folder ID: {upload_folder_id}\n")
        for file_name in files:
            file_path = os.path.join(upload_path, file_name)
            mime_type = get_mime_type(file_path)

            if mime_type is None:
                print(Fore.YELLOW + f"⚠ Skipping '{file_name}': Unable to determine MIME type.\n")
                continue

            # Determine target subfolder based on MIME type
            
            if mime_type.startswith('image/'):
                target_subfolder_id = subfolder_ids['images']
                subfolder_type = 'images'
                push_file(
                    file_name=file_name,
                    file_path=file_path,
                    subfolder_type=subfolder_type,
                    target_subfolder_id=target_subfolder_id,
                    service=service
                )
                if 'DSC' in file_name:
                    target_subfolder_id = subfolder_ids['DSLR']
                    subfolder_type = 'DSLR'
                    if group_photo_compactabilty_check(image_path=file_path):
                        target_subfolder_id = subfolder_ids['GroupPhotos']
                        subfolder_type = 'GroupPhotos'
                        push_file(
                            file_name=file_name,
                            file_path=file_path,
                            subfolder_type=subfolder_type,
                            target_subfolder_id=target_subfolder_id,
                            service=service
                        )
                    else:
                        push_file(
                            file_name=file_name,
                            file_path=file_path,
                            subfolder_type=subfolder_type,
                            target_subfolder_id=target_subfolder_id,
                            service=service
                        )

                elif 'GPS' in file_name:
                    target_subfolder_id = subfolder_ids['geotaged']
                    subfolder_type = 'geotaged'
                    push_file(
                        file_name=file_name,
                        file_path=file_path,
                        subfolder_type=subfolder_type,
                        target_subfolder_id=target_subfolder_id,
                        service=service
                    )
                elif group_photo_compactabilty_check(image_path=file_path):
                    target_subfolder_id = subfolder_ids['GroupPhotos']
                    subfolder_type = 'GroupPhotos'
                    push_file(
                        file_name=file_name,
                        file_path=file_path,
                        subfolder_type=subfolder_type,
                        target_subfolder_id=target_subfolder_id,
                        service=service
                    )
                else:
                    pass
            elif mime_type.startswith('video/'):
                target_subfolder_id = subfolder_ids['videos']
                subfolder_type = 'videos'
                push_file(
                    file_name=file_name,
                    file_path=file_path,
                    subfolder_type=subfolder_type,
                    target_subfolder_id=target_subfolder_id,
                    service=service
                )
            else:
                print(Fore.YELLOW + f"⚠ Skipping '{file_name}': Unsupported MIME type '{mime_type}'.\n")
                continue

    except Exception as e:
        print(Fore.RED + f"✖ An error occurred while uploading files: {e}\n")
        sys.exit(1)

def get_mime_type(file_path):
    """
    Determines the MIME type of a file based on its extension.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        str or None: MIME type of the file or None if it cannot be determined.
    """ 
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def clean_up(download_path):
    """
    Deletes the local download directory and its contents.
    
    Parameters:
        download_path (str): Path to the local download directory.
    """
    try:
        if os.path.exists(download_path):
            shutil.rmtree(download_path)
            print(Fore.GREEN + f"✔ Cleaned up the local directory '{download_path}'.\n")
    except Exception as e:
        print(Fore.RED + f"✖ An error occurred during cleanup: {e}\n")

def main():
    """
    Main function to orchestrate the download and upload of images and videos within Google Drive.
    """
    print(Fore.MAGENTA + "="*50)
    print(Fore.MAGENTA + "    Google Drive Content Processor Started")
    print(Fore.MAGENTA + "="*50 + "\n")

    # Ensure the download directory exists
    if not os.path.exists(config.download_path):
        try:
            os.makedirs(config.download_path)
            print(Fore.GREEN + f"✔ Created download directory at '{config.download_path}'.\n")
        except Exception as e:
            print(Fore.RED + f"✖ Failed to create download directory '{config.download_path}': {e}\n")
            sys.exit(1)
    else:
        print(Fore.BLUE + f"📁 Download directory '{config.download_path}' already exists.\n")

    # Ensure the large_files directory exists
    if not os.path.exists(config.large_files_path):
        try:
            os.makedirs(config.large_files_path)
            print(Fore.GREEN + f"✔ Created large files directory at '{config.large_files_path}'.\n")
        except Exception as e:
            print(Fore.RED + f"✖ Failed to create large files directory '{config.large_files_path}': {e}\n")
            sys.exit(1)
    else:
        print(Fore.BLUE + f"📁 Large files directory '{config.large_files_path}' already exists.\n")

    # Authenticate and build the Google Drive service
    service = authenticate_drive(config.cred_file_path)

    # Download images and videos from the source folder
    print(Fore.MAGENTA + "🔽 Initiating download process...\n")
    download_images_videos(service, config.source_folder_id, config.download_path, config.large_files_path, config.size_threshold)

    # Upload the downloaded files to target folder
    print(Fore.MAGENTA + "🔼 Initiating upload process...\n")
    upload_to_drive(service, config.target_folder_id, config.download_path)

    # Conditionally clean up the downloaded_files directory
    if config.clean_up_downloaded_files_after_uploading:
        print(Fore.MAGENTA + "🧹 Cleaning up downloaded files...\n")
        clean_up(config.download_path)
    else:
        print(Fore.YELLOW + "⚠ Skipping cleanup of downloaded files as per configuration.\n")

    print(Fore.MAGENTA + "="*50)
    print(Fore.MAGENTA + "    Google Drive Content Processor Completed Successfully")
    print(Fore.MAGENTA + "="*50 + "\n")

if __name__ == '__main__':
    main()
