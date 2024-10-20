# config.py

# Configuration file for Google Drive content processing

# Source Folder ID:
# The unique identifier of the Google Drive folder from which you want to download images and videos.
# Obtain this from the folder's URL in your browser.
source_folder_id = 'your_source_folder_id_here'

# Target Folder ID:
# The unique identifier of the Google Drive folder where you want to upload the downloaded images and videos.
# Obtain this from the folder's URL in your browser.
target_folder_id = 'your_target_folder_id_here'

# Credentials File Path:
# The path to your Google Drive API credentials JSON file.
# Ensure this file is kept secure and not exposed publicly.
cred_file_path = r'credentials_path.json'

# Download Path:
# The local directory where downloaded files will be temporarily stored before uploading.
download_path = './downloaded_files'

# Large Files Path:
# The local directory where files exceeding the size threshold will be stored for later upload.
# Ensure that this directory exists or the script has permission to create it.
large_files_path = './large_files'

# Size Threshold:
# The maximum file size (in bytes) allowed for immediate upload.
# Files exceeding this size will be moved to the large_files_path.
# Default is set to 300 KB. You can modify this value as needed.
size_threshold = 1 * 1024 * 1024 * 1024 # 1 GB  

# Cleanup Configuration:
# Determines whether to delete local directories after uploading.
clean_up_large_files_after_uploading = True
clean_up_downloaded_files_after_uploading = True
