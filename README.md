linux requirments and setup:
sudo apt-get install tesseract-ocr-nld

#full setup
conda create -n cibg
conda activate cibg
conda install pip 

pip install -r requirements.txt

To run the program, run the pipeline.py file.

How to navigate the GUI:
Select an output folder, all the csv files of tables that the program extracted will be placed here. Output 
files will be of the form "PDF_FILE_NAME-PAGE_OF_TABLE-METHOD_TO_EXTRACT".
Then, press the browse files button and select the pdf's from which you would like to extract tables.
Click "extract tables" to start the extraction process. This might take a while.

Once the program is finished extracting, it will start the visual debugger. The visual debugger contains two windows.
The first contains all the tables that the program was able to extract. You can approve of tables here and doing so will remove them from the window. The other window opens when you select "files without 1a table found", here are located all the files from which the program extracted nothing.

Selecting one of the tables opens up a new window with on the left hand side the page from which the table was extracted and on the right hand side the table that the program found.
Within the table, it is possible to make edits that are then directly saved into the output folder. The "Save Changes" button saves the changes to the CSV file. The "Undo Changes" button will revert to what the CSV file was like when you opened the window.

Right clicking on a column gives you the option to add a column or remove one. Right clicking on a row does the same for a row.

Closing both windows will close the program.