import subprocess
import sys
import os
import platform
import ctypes
import requests
import subprocess
from PIL import Image
import pytesseract


class OCRMain:
    def __init__(self):
        pass

    def extract_coordinate(self, img, left, top, right, bottom):
        pass

    def extract_image(self, img):
        pass


class OCRInstall:
    # code to determine whether user is admin
    def __is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    # code to run installation process of Tesseract as admin
    def __run_as_admin(self, command, folder=None):
        try:
            subprocess.run(['powershell', 'Start-Process', '-Verb', 'RunAs', '-FilePath', command], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running as admin: {e}")

    # installation of Tesseract
    def __install_tesseract(self):
        system_platform = platform.system().lower()

        if system_platform == 'windows':
            # Download the Tesseract installer
            tesseract_installer_url = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe'
            installer_path = 'tesseract_installer.exe'

            try:
                # Download the installer
                response = requests.get(tesseract_installer_url)
                with open(installer_path, 'wb') as installer_file:
                    installer_file.write(response.content)

                # Run the installer with elevated privileges
                self.run_as_admin(installer_path)

                # Remove the downloaded installer
                os.remove(installer_path)

            except Exception as e:
                print(f"Error downloading or running installer: {e}")
        else:
            print(f"Unsupported platform: {system_platform}")

    def run(self):
        # Run the script with elevated privileges
        if self.is_admin():
            self.install_tesseract()
        else:
            # Re-run only the Tesseract installation with elevated privileges
            tesseract_install_command = os.path.join(os.getcwd(), 'tesseract_installer.exe')
            self.run_as_admin(tesseract_install_command)

        # Install required packages
        subprocess.run(['pip', 'install', 'pytesseract', 'Pillow'])

        # set path to the tesseract executable, CHANGE THIS IF YOU SAVED IT SOMEWHERE ELSE
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'