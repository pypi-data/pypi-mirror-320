# Module: ExpressVPN Auto Rotate

## Overview
This module is designed to manage and update the ExpressVPN using Firebase for cloud storage and real-time database functionalities. It automatically checks for new versions and downloads the necessary files, managing the whole process seamlessly.

## Installation
Ensure the following Python packages are installed:
```bash
pip install firebase-admin pyautogui psutil
```

## Usage Example
To utilize the functionality of this module, simply run it. It will check for new versions, download them if available, and install necessary dependencies:
```python
# Check for new versions and manage updates
Y, nova_versao, versao_atual, nome_versao_atual = nova_versao_disponivel(app1)
if Y:
    fazer_o_download_da_nova_versao(bucket, nome_versao_atual, nova_versao)
# Execute the main application
subprocess.Popen(comando_terminal, shell=True)
```

## Functions
### `fazendo_o_download_da_nova_versao(bucket, nome_versao_atual, nova_versao)`
Downloads a new version and extracts content from the zip files stored in Firebase.

**Parameters:**  
- `bucket`: Firebase storage bucket instance.  
- `nome_versao_atual`: Current version name.  
- `nova_versao`: New version to download.

### `fazendo_o_download_da_versao(bucket, nome_versao_atual, nova_versao)`
Downloads the current version files if no new version is available.

### `nova_versao_disponivel(app1)`
Checks whether a new version is available in the Firebase storage.

**Returns:**  
- `Boolean`: Indicates if a new version is found.  
- `nova_versao`: The new version number, if available.  
- `versao_atual`: Current version number.  
- `nome_versao_atual`: Current version name.

## Firebase Configuration
The module uses Firebase Admin SDK for managing database interaction and storage. Make sure to initialize Firebase correctly with service account credentials. Example of initialization:
```python
cred = credentials.Certificate(cred)
app1 = initialize_app(cred, {
    'storageBucket': 'your-bucket-name.appspot.com',
    'databaseURL': 'https://your-database-url.com'
})
```

## Conclusion
This module provides an automated way to manage ExpressVPN versioning, ensuring the latest updates are always available and installing necessary dependencies automatically. It utilizes Firebase for data storage and retrieval in an effective manner.
