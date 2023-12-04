import os
import platform
import ctypes
import pandas as pd
import requests
import subprocess
import pytesseract
import matplotlib.pyplot as plt
from PIL import Image
from pdf2image import convert_from_path
import shutil

class OCRMain:
    @staticmethod
    def on_file(input_file: str, temp_output_folder: str = '../OCR/tmppages/'):
        """
        Args:
            input_file: path of the pdf file
            temp_output_folder: place where temporarily images are stored of every page of the pdf file
        Returns: array with text objects where every index refers to a text object of a single page
        """
        OCRMain.__convert_pdf_to_img(input_file, temp_output_folder)
        text_objects = OCRMain.__extract_text_from_images(temp_output_folder)

        return [str(text_obj) for text_obj in text_objects]

    @staticmethod
    def __extract_text_from_images(input_folder: str = '../OCR/tmppages/'):
        '''
        Args:
            input_folder:   path to the folder where images are located
        Returns:            array with text objects where every index refers to a text object of a single page
        '''
        OCRInstall.set_path()

        output_text = []

        # Get a list of all image files in the input folder
        image_files = [f for f in os.listdir(input_folder) if
                       f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        for image_file in image_files:
            # Construct full path for the image
            image_path = os.path.join(input_folder, image_file)

            # Open the image
            with Image.open(image_path) as img:
                # Perform OCR on the image
                custom_config = r'--psm 6'  # Adjust the configuration as needed
                text = pytesseract.image_to_string(img, config=custom_config)

                # Append the extracted text to the output array
                output_text.append(text)

        #shutil.rmtree(input_folder)

        return output_text

    @staticmethod
    def __convert_pdf_to_img(input_file: str, output_folder: str ='../OCR/tmppages/'):
        """
        Args:
            input_file: path to the pdf file
            output_folder: path to the output folder
        Returns:
        """


        # Store Pdf with convert_from_path function
        images = convert_from_path(input_file,poppler_path = r"C:\Program Files\Poppler\poppler-23.11.0\Library\bin")

        # If folder doesn't exist, create it
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for i in range(len(images)):
            # Save pages as images to folder tmppages
            images[i].save(output_folder + os.path.splitext(os.path.basename(input_file))[0] + '-' + str(i) + '.jpg', 'JPEG')


    @staticmethod
    def extract_coordinate(image_file_name: str, coordinate_tuple: tuple, path: str = '../OCR/testfiles/', psm:int=6):
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
    def extract_image(path: str, psm: int =6):
        """
        scans an image and outputs text
        @param path:            path for finding the files
        @param psm:             changing the configuration settings of Tesseract, see documentation: https://muthu.co/all-tesseract-ocr-options/
        @return:                pandas dataframe with text and each line break is a new row
        """
        custom_config = r'--psm ' + str(psm)

        img = Image.open(path)
        text = pytesseract.image_to_string(img, config=custom_config)
        return text


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

if __name__ == "__main__":
    ocr = OCRMain.on_file("C:/Users/noahc/Downloads/labeling/DigiMV2020_J6RF69VN57_0_09179857_Accountantsverklaring_5427_I Care B.V..pdf")
    print(ocr[0])





