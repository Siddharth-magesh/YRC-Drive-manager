# upload_large_files.py

import os
import io
import shutil
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import config
from colorama import init, Fore, Style

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

def upload_large_files(service, upload_folder_id, large_files_path):
    """
    Uploads all files from the large_files_path to the target Google Drive folder,
    organizing images and videos into separate subfolders.

    Parameters:
        service: Authorized Google Drive service instance.
        upload_folder_id (str): ID of the target Google Drive folder.
        large_files_path (str): Local path where large files are stored to be uploaded.
    """
    try:
        # Create subfolders 'images' and 'videos' inside the target folder
        subfolders = ['images', 'videos']
        subfolder_ids = create_subfolders(service, upload_folder_id, subfolders)

        files = os.listdir(large_files_path)
        if not files:
            print(Fore.YELLOW + "⚠ No large files available to upload.\n")
            return

        print(Fore.CYAN + f"📤 Starting upload of {len(files)} large files to folder ID: {upload_folder_id}\n")
        for file_name in files:
            file_path = os.path.join(large_files_path, file_name)
            mime_type = get_mime_type(file_path)

            if mime_type is None:
                print(Fore.YELLOW + f"⚠ Skipping '{file_name}': Unable to determine MIME type.\n")
                continue

            # Determine target subfolder based on MIME type
            if mime_type.startswith('image/'):
                target_subfolder_id = subfolder_ids['images']
                subfolder_type = 'images'
            elif mime_type.startswith('video/'):
                target_subfolder_id = subfolder_ids['videos']
                subfolder_type = 'videos'
            else:
                print(Fore.YELLOW + f"⚠ Skipping '{file_name}': Unsupported MIME type '{mime_type}'.\n")
                continue

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
    except Exception as e:
        print(Fore.RED + f"✖ An error occurred while uploading large files: {e}\n")
        sys.exit(1)

def get_mime_type(file_path):
    """
    Determines the MIME type of a file based on its extension.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        str or None: MIME type of the file or None if it cannot be determined.
    """
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def clean_up(large_files_path):
    """
    Deletes the local large_files directory and its contents.

    Parameters:
        large_files_path (str): Path to the local large_files directory.
    """
    try:
        if os.path.exists(large_files_path):
            shutil.rmtree(large_files_path)
            print(Fore.GREEN + f"✔ Cleaned up the local directory '{large_files_path}'.\n")
    except Exception as e:
        print(Fore.RED + f"✖ An error occurred during cleanup: {e}\n")

def main():
    """
    Main function to upload large files from local large_files directory to Google Drive
    and clean up the local directory after successful upload.
    """
    print(Fore.MAGENTA + "="*50)
    print(Fore.MAGENTA + "    Upload Large Files Process Started")
    print(Fore.MAGENTA + "="*50 + "\n")

    # Ensure the large_files directory exists
    if not os.path.exists(config.large_files_path):
        print(Fore.YELLOW + f"⚠ Large files directory '{config.large_files_path}' does not exist. Nothing to upload.\n")
        sys.exit(0)
    else:
        print(Fore.BLUE + f"📁 Large files directory '{config.large_files_path}' found.\n")

    # Authenticate and build the Google Drive service
    service = authenticate_drive(config.cred_file_path)

    # Upload the large files to target folder
    print(Fore.MAGENTA + "🔼 Initiating upload of large files...\n")
    upload_large_files(service, config.target_folder_id, config.large_files_path)

    # Conditionally clean up the large_files directory
    if config.clean_up_large_files_after_uploading:
        print(Fore.MAGENTA + "🧹 Cleaning up large files...\n")
        clean_up(config.large_files_path)
    else:
        print(Fore.YELLOW + "⚠ Skipping cleanup of large files as per configuration.\n")

    print(Fore.MAGENTA + "="*50)
    print(Fore.MAGENTA + "    Upload Large Files Process Completed Successfully")
    print(Fore.MAGENTA + "="*50 + "\n")

if __name__ == '__main__':
    main()
