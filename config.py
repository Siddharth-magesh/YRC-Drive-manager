# config.py

# Configuration file for Google Drive content processing

# Source Folder ID:
# The unique identifier of the Google Drive folder from which you want to download images and videos.
# You can find this ID in the URL when you open the folder in your browser.
# Example URL: https://drive.google.com/drive/u/0/folders/1A2B3C4D5E6F7G8H9I0J
# The Folder ID is the part after '/folders/' (e.g., '1A2B3C4D5E6F7G8H9I0J')
source_folder_id = 'your_source_folder_id_here'

# Target Folder ID:
# The unique identifier of the Google Drive folder where you want to upload the downloaded images and videos.
# Similar to the source_folder_id, obtain this from the folder's URL in your browser.
target_folder_id = 'your_target_folder_id_here'

# Credentials File Path:
# The path to your Google Drive API credentials JSON file.
# This file contains the OAuth 2.0 Client IDs and should be downloaded from the Google Cloud Console.
# Ensure that this file is kept secure and not exposed publicly.
cred_file_path = r'Set the Path of the OAuth Key'

# Download Path:
# The local directory where downloaded files will be temporarily stored before uploading.
# Ensure that this directory exists or the script has permission to create it.
# Delete the Contents after the uploading is done
download_path = './downloaded_files'
