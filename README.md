# Google Drive Content Processor

A Python-based tool to automate the transfer of images and videos between folders within the same Google Drive account. This script downloads all images and videos from a specified source folder and uploads them to a target folder, streamlining the organization and management of your Google Drive content.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up Conda Environment](#2-set-up-conda-environment)
  - [3. Install Required Libraries](#3-install-required-libraries)
- [Configuration](#configuration)
  - [1. OAuth 2.0 Credentials](#1-oauth-20-credentials)
  - [2. Update `config.py`](#2-update-configpy)
    - [Source Folder ID](#source-folder-id)
    - [Target Folder ID](#target-folder-id)
    - [Credentials File Path](#credentials-file-path)
    - [Download Path](#download-path)
- [Usage](#usage)
  - [Running the Script](#running-the-script)
- [Folder Structure](#folder-structure)
- [Error Handling](#error-handling)
- [Cleanup](#cleanup)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features

- **Automated File Transfer:** Seamlessly download and upload images and videos between Google Drive folders.
- **Structured Configuration:** Easily manage settings through a dedicated `config.py` file.
- **Error Handling:** Comprehensive try-except blocks to handle potential issues gracefully.
- **Progress Feedback:** Informative print statements to monitor the script's progress.
- **Environment Management:** Utilize Conda to manage dependencies and maintain a consistent Python environment.

---

## Prerequisites

Before setting up and running the script, ensure you have the following:

- **Python 3.10:** The script is optimized for Python version 3.10.
- **Anaconda:** To create and manage the Conda environment.
- **Google Account:** Access to Google Drive.
- **Internet Connection:** Required for accessing Google Drive APIs.

---

## Installation

### 1. Clone the Repository

First, clone this repository to your local machine using Git. If you don't have Git installed, download it from [here](https://git-scm.com/downloads).

```bash
git clone https://github.com/Siddharth-magesh/YRC-Drive-manager.git
cd YRC-Drive-manager
```

_Replace `your-username` with your actual GitHub username if applicable._

### 2. Set Up Conda Environment

It's recommended to use Conda to manage the Python environment for this project.

1. **Install Anaconda:** If you haven't installed Anaconda, download and install it from [here](https://www.anaconda.com/products/distribution).

2. **Create a New Conda Environment:**

   Open your terminal or Anaconda Prompt and execute the following command to create a new environment named `gdrive_env` with Python 3.10:

   ```bash
   conda create -n gdrive_env python=3.10
   ```

3. **Activate the Environment:**

   ```bash
   conda activate gdrive_env
   ```

### 3. Install Required Libraries

With the Conda environment activated, install the necessary Python libraries using `pip`:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

_These libraries are essential for interacting with the Google Drive API._

---

## Configuration

Proper configuration is crucial for the script to function correctly. This involves obtaining OAuth 2.0 credentials and specifying folder IDs.

### 1. OAuth 2.0 Credentials

To interact with Google Drive, you need OAuth 2.0 credentials. Instead of setting this up yourself, please contact the current Technical YRC lead to obtain the necessary OAuth credentials.

- **Contact Information:**

  - **Name:** Siddharth Magesh
  - **Email:** [siddharthmagesh007@gmail.com](mailto:siddharthmagesh007@gmail.com)

  - **Name:** tarakesh
  - **Email:** [siddharthmagesh007@gmail.com](mailto:siddharthmagesh007@gmail.com)

**Steps:**

1. **Request Credentials:**

   - Send an email to the Technical YRC lead requesting the OAuth 2.0 credentials for the Google Drive Content Processor.

2. **Receive Credentials:**

   - The Technical YRC lead will provide you with the `credentials.json` file required for authentication.

3. **Place Credentials:**
   - Save the received `credentials.json` file in the project directory or a secure location of your choice.

**Note:** Ensure that the `credentials.json` file is kept secure and not exposed publicly.

### 2. Update `config.py`

The `config.py` file holds all the configuration parameters required by the script. Below is a breakdown of each parameter and how to set them.

#### Source Folder ID

- **Description:** The unique identifier of the Google Drive folder from which you want to download images and videos.
- **How to Obtain:**
  1. Open Google Drive in your browser.
  2. Navigate to the source folder.
  3. Look at the URL in the address bar. It will look something like this:
     ```
     https://drive.google.com/drive/u/0/folders/1A2B3C4D5E6F7G8H9I0J
     ```
  4. The string after `/folders/` is the **Source Folder ID** (`1A2B3C4D5E6F7G8H9I0J` in this example).

#### Target Folder ID

- **Description:** The unique identifier of the Google Drive folder where you want to upload the downloaded images and videos.
- **How to Obtain:**
  Follow the same steps as for the Source Folder ID to locate the Target Folder ID.

#### Credentials File Path

- **Description:** The path to your Google Drive API credentials JSON file.
- **How to Set:**
  If you placed `credentials.json` in the project directory, set this parameter as follows:
  ```python
  cred_file_path = 'credentials.json'
  ```

#### Download Path

- **Description:** The local directory where downloaded files will be temporarily stored before uploading.
- **How to Set:**
  You can specify any valid directory path. By default, it's set to `./downloaded_files`.
  ```python
  download_path = './downloaded_files'
  ```

#### Complete `config.py` Example

```python
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
cred_file_path = 'credentials.json'

# Download Path:
# The local directory where downloaded files will be temporarily stored before uploading.
download_path = './downloaded_files'
```

**Important:** Replace `'your_source_folder_id_here'` and `'your_target_folder_id_here'` with your actual Google Drive Folder IDs.

---

## Usage

With the environment set up and configurations in place, you can now run the script to transfer files between Google Drive folders.

### Running the Script

1. **Activate Conda Environment:**

   Ensure that the Conda environment is activated. If not, activate it using:

   ```bash
   conda activate gdrive_env
   ```

2. **Run the Script:**

   Execute the `process_content.py` script using Python:

   ```bash
   python process_content.py
   ```

3. **Authenticate with Google Drive:**

   - On the first run, a browser window will open prompting you to authorize the application to access your Google Drive.
   - Log in with your Google account and grant the necessary permissions.
   - The script will save the authentication tokens in `token.json` for future runs.

4. **Monitor the Output:**

   The script will print messages indicating the progress of downloading and uploading files, as well as any errors encountered.

5. **Completion:**

   Once the process is complete, the script will clean up the downloaded files from the local `downloaded_files` directory.

---

## Folder Structure

Here's an overview of the project's folder structure:

```
google-drive-content-processor/
│
├── config.py
├── process_content.py
├── credentials.json
├── token.json
├── downloaded_files/          # Created automatically during script execution
│   ├── image1.jpg
│   ├── video1.mp4
│   └── ... (other downloaded images and videos)
├── README.md
└── environment.yml            # (Optional) If using Conda environment file
```

- **config.py:** Stores configuration parameters such as folder IDs and credential paths.
- **process_content.py:** The main script that handles downloading and uploading of files.
- **credentials.json:** Google Drive API credentials file (provided by Technical YRC lead).
- **token.json:** Stores authentication tokens after the first run.
- **downloaded_files/:** Temporary directory where files are downloaded before uploading.
- **README.md:** Documentation and instructions (this file).
- **environment.yml:** (Optional) For sharing the Conda environment configuration.

---

## Error Handling

The script includes comprehensive error handling to manage potential issues gracefully. Here's how it handles various scenarios:

- **Missing Credentials File:**
  - If `credentials.json` is not found, the script will print an error message and exit.
- **Invalid Folder IDs:**
  - If the specified `source_folder_id` or `target_folder_id` is incorrect or does not exist, the script will notify you and exit.
- **Network Issues:**
  - The script handles network interruptions during download and upload processes, printing relevant error messages.
- **File Access Issues:**
  - If the script lacks permissions to create directories or write files locally, it will inform you and exit.

**Note:** Always monitor the script's output to identify and address any issues promptly.

---

## Cleanup

After successfully transferring files, the script performs a cleanup by deleting the local `downloaded_files` directory to free up space. If you wish to retain the downloaded files for any reason, you can modify or remove the cleanup function in `process_content.py`.

---

## Security Considerations

- **Protect Credentials:**
  - Ensure that `credentials.json` and `token.json` are kept secure. Do not expose these files publicly or commit them to version control systems like GitHub.
- **Use `.gitignore`:**
  - If using Git for version control, add `credentials.json` and `token.json` to your `.gitignore` file to prevent accidental commits.
- **Environment Variables:**
  - For enhanced security, consider using environment variables or secret management tools to handle sensitive information instead of storing paths directly in `config.py`.

---

## Troubleshooting

Here are some common issues and their solutions:

### 1. **Authentication Errors**

- **Symptom:** The browser does not open for authentication, or you receive an error after attempting to authenticate.
- **Solution:**
  - Ensure that `credentials.json` is correctly placed in the project directory.
  - Contact the Technical YRC lead if you encounter issues with the OAuth credentials.
  - Verify that the OAuth consent screen is properly configured.

### 2. **Invalid Folder IDs**

- **Symptom:** The script cannot find the specified source or target folder.
- **Solution:**
  - Double-check the folder IDs in `config.py`.
  - Ensure that the folders exist in your Google Drive and that you have access to them.

### 3. **Permission Denied Errors**

- **Symptom:** The script cannot create directories or write files locally.
- **Solution:**
  - Verify that you have the necessary permissions for the specified `download_path`.
  - Choose a different directory where you have write access.

### 4. **API Quota Exceeded**

- **Symptom:** The script fails due to exceeding Google Drive API usage limits.
- **Solution:**
  - Wait for the quota to reset (usually after 24 hours).
  - Optimize the script to make fewer API calls, if possible.

### 5. **Unexpected Script Termination**

- **Symptom:** The script exits unexpectedly without completing the process.
- **Solution:**
  - Check the terminal output for error messages.
  - Ensure that all dependencies are correctly installed and that the Conda environment is active.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- **Google Drive API:** Thanks to the developers of the Google Drive API for providing comprehensive tools to interact with Google Drive programmatically.
- **OpenAI:** For providing the language model that assisted in developing this project.
- **Conda Community:** For creating and maintaining the Conda environment management system.

---

Feel free to reach out to the Technical YRC lead at [siddharthmagesh007@gmail.com](mailto:siddharthmagesh007@gmail.com) if you encounter any issues or have suggestions for improvements!
