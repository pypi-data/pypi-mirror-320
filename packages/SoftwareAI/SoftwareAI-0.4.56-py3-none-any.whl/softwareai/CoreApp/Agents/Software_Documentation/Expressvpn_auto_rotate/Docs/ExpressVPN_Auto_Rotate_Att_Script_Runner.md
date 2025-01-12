# Module: ExpressVPN Auto Rotate Att Script Runner

## Overview
This module is responsible for running the `att.py` script, which is a part of the ExpressVPN Auto Rotate functionality. The script is executed using a subprocess call, ensuring it runs in a separate process without blocking the main application.

## Usage Example
To execute the `att.py` script, the following code can be used:
```python
import subprocess
subprocess.run(["Dependenc/Python/pythonw", "Dependenc/att.py"])
```

## Description
- The `subprocess.run` function is utilized to run the `att.py` script located in the `Dependenc` directory with the Python interpreter specified.
- The use of `pythonw` allows the script to run without opening a command prompt window, which is useful for GUI applications or background tasks.

## Error Handling
The current implementation does not include error handling or validation of the subprocess call. It is recommended to check the return code of the subprocess for successful execution and handle any potential exceptions.

## Conclusion
This module serves as a simple interface for executing the `att.py` script within the ExpressVPN Auto Rotate package. By utilizing `subprocess`, it allows for efficient execution of scripts while maintaining application responsiveness.
