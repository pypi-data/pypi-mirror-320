# Module: ExpressVPN Auto Rotate GUI

## Overview
This module provides a graphical user interface (GUI) for managing the ExpressVPN Auto Rotate functionality. It utilizes PyQt5 for the interface and Firebase for cloud data management. The application allows users to manage VPN rotations and view benchmark data.

## Installation
Ensure to install the required packages:
```bash
pip install PyQt5 firebase-admin fake-useragent
```

## Usage Example
To run the application, simply execute the module:
```python
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
```

## Classes
### 1. MainWindow  
This is the main application window that provides controls for user input and VPN management.

**Features:**  
- A button to trigger the VPN rotation.  
- Display for current location.  
- Progress bar for updating status.  
- Options to select rotation types (USA, Canada, Complete).

### 2. RotateVpnThread  
A worker thread that handles the background execution of VPN rotations, ensuring the main GUI remains responsive.

**Parameters:**  
- `rotation_count`: The number of rotations to perform.  
- `interval`: Time to wait between rotations.  
- `rotate_in_usa`: Flag for USA rotations.  
- `rotate_in_canada`: Flag for Canada rotations.  
- `rotate_complete`: Flag for complete rotations.  
- `nvar_key`: The Nvar key for licensing validation.

### 3. Security  
This class handles security and licensing functions, including key validation and machine identification.

**Key Methods:**  
- `get_machine_info()`: Retrieves machine information.  
- `generate_serial()`: Generates a unique serial based on an provided order_id and CPU info.  
- `check_serial()`: Validates the serial number against registered devices.  
- `get_or_create_session()`: Manages sessions for licensing.

### 4. BenchmarkWindow  
Displays benchmarking information for the current user.

### 5. GlobalBenchmarkWindow  
Displays global benchmark statistics across all users.

## Error Handling
The module includes basic error handling for managing Firebase interactions, VPN rotation failures, and issues during benchmark data retrieval.

## Conclusion
This module offers a comprehensive GUI for managing ExpressVPN connections, enabling users to easily perform operations while ensuring security with licensing checks and monitoring redundancy. By incorporating Firebase for data management, it provides a robust backend for management features.
