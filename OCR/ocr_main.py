import os
import platform
import ctypes
import pandas as pd
import requests
import subprocess
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt


class OCRMain:
    @staticmethod
    def extract_coordinate(image_file_name: str, coordinate_tuple: tuple, path: str = '../OCR/testfiles/', psm=6):
        """
        Scans specific coordinates within an image and outputs text
        It also plots the original and cropped image

        @param image_file_name: file name of the image in the path
        @param coordinate_tuple:     a tuple of coordinates (left, top, right, bottom)
        @param path:            path for finding the files
        @param psm:             changing the configuration settings of Tesseract, see documentation: https://muthu.co/all-tesseract-ocr-options/
        @return:                pandas dataframe with text and each line break is a new row
        """

        custom_config = r'--psm ' + str(psm)

        img = Image.open(path + image_file_name)
        cropped_img = img.crop(coordinate_tuple)
        text = pytesseract.image_to_string(cropped_img, config=custom_config)

        print(text)
        plt.imshow(img)
        plt.title('Original image')
        plt.show()
        plt.imshow(cropped_img)
        plt.title('Cropped image')
        plt.show()

        # Split the text into lines
        lines = text.split('\n')

        # Create a DataFrame with each line as a new row
        df = pd.DataFrame({'Text': lines})

        return df

    @staticmethod
    def extract_image(image_file_name: str, path: str = '../OCR/testfiles/', psm=6):
        """
        scans an image and outputs text

        @param image_file_name: file name of the image in the path
        @param path:            path for finding the files
        @param psm:             changing the configuration settings of Tesseract, see documentation: https://muthu.co/all-tesseract-ocr-options/
        @return:                pandas dataframe with text and each line break is a new row
        """
        custom_config = r'--psm ' + str(psm)

        img = Image.open(path + image_file_name)
        text = pytesseract.image_to_string(img, config=custom_config)

        print(text)

        # Split the text into lines
        lines = text.split('\n')

        # Create a DataFrame with each line as a new row
        df = pd.DataFrame({'Text': lines})

        return df


class OCRInstall:
    @staticmethod
    def __is_admin():
        """
        code to determine whether user is admin
        @return:
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


    @staticmethod
    def __run_as_admin(command, folder=None):
        """
        Code to run installation process of Tesseract as admin
        @return:
        """
        try:
            subprocess.run(['powershell', 'Start-Process', '-Verb', 'RunAs', '-FilePath', command], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running as admin: {e}")

    #
    @staticmethod
    def __install_tesseract():
        """
        Downloads and installs Tesseract
        @return:
        """
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
                OCRInstall.__run_as_admin(installer_path)

                # Remove the downloaded installer
                os.remove(installer_path)

            except Exception as e:
                print(f"Error downloading or running installer: {e}")
        else:
            print(f"Unsupported platform: {system_platform}")

    @staticmethod
    def install():
        """
        This method downloads and installs the pytesseract engine and package depending on the OS you have
        It also ensures admin rights for installation purposes

        @return:
        """
        # Run the script with elevated privileges
        if OCRInstall.__is_admin():
            OCRInstall.__install_tesseract()
        else:
            # Re-run only the Tesseract installation with elevated privileges
            tesseract_install_command = os.path.join(os.getcwd(), 'tesseract_installer.exe')
            OCRInstall.__run_as_admin(tesseract_install_command)

        # Install required packages
        subprocess.run(['pip', 'install', 'pytesseract', 'Pillow'])

        OCRInstall.set_path()

    @staticmethod
    def set_path(path: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        """
        sets path to the tesseract executable, CHANGE THIS IF YOU SAVED IT SOMEWHERE ELSE
        @param path: path to the Tesseract executable
        @return:
        """
        pytesseract.pytesseract.tesseract_cmd = path

#OCRInstall.install()
OCRInstall.set_path()
coordinates = (0, 0, 120, 120)
ocr = OCRMain.extract_coordinate(image_file_name='2_clean_top.png', coordinate_tuple=coordinates, psm=6)
print(ocr)