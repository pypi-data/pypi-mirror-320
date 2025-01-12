# Module: ExpressVPN Auto Rotate Version Controller

## Overview
This module is responsible for managing the version control of the ExpressVPN application by downloading updates directly from Firebase Storage. It extracts the relevant files and ensures the application is up to date.

## Installation
Make sure to install the required Python packages:
```bash
pip install firebase-admin pyautogui psutil
```

## Usage Example
To use the functionality of this module, simply run the function to download the latest version:
```python
fazendo_o_download_da_nova_versao(bucket)
```

## Firebase Configuration
This module initializes Firebase Admin SDK with service account credentials to access Firebase Storage and Realtime Database.

```python
cred = credentials.Certificate(cred)
app1 = initialize_app(cred, {
    'storageBucket': 'expressvpnautorotate.appspot.com',
    'databaseURL': 'https://expressvpnautorotate-default-rtdb.firebaseio.com'
})
bucket = storage.bucket(app=app1)
```

## Functions
### `fazendo_o_download_da_nova_versao(bucket)`
Downloads the latest version files stored in Firebase Storage, extracts them, and cleans up temporary files.

**Parameters:**  
- `bucket`: Firebase storage bucket instance.

### Error Handling
The function includes basic error handling. If an error occurs during the download or extraction process, it will print an error message indicating the issue.

## Conclusion
This module provides an automated way to maintain and update the ExpressVPN application efficiently using Firebase for storage management. Ensure that Firebase is properly configured before running this module.
