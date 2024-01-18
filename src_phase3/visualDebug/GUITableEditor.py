import datetime
import tkinter as tk
import openpyxl
from pandastable import Table
import pandas as pd
import os


class TableEditor(tk.Frame):

    def __init__(self, parent=None):
        self.parent = parent
        tk.Frame.__init__(self)
        self.main = self.master
        # self.main.geometry('600x400+200+100')
        self.main.title('Edit 1a Table')

        f = tk.Frame(self.main)
        f.pack(fill=tk.BOTH, expand=True)

        self.file_name_original_pdf = '1a_test.xlsx'
        self.create_new_1a(file_name=self.file_name_original_pdf);

        # Load the dataframe and set it as an instance attribute
        self.df = pd.read_excel(self.file_name_original_pdf)

        self.table = Table(f, dataframe=self.df, showtoolbar=True, showstatusbar=True, maxcellwidth=200)
        self.table.show()

        self.add_column_button = tk.Button(self.main, text='Add Column', command=self.add_column)
        self.add_column_button.pack()

        self.save_file_button = tk.Button(self.main, text='Save WNT edits', command=self.save_changes)
        self.save_file_button.pack()

    def save_changes(self):
        self.df.to_excel(self.file_name_original_pdf, index=False)
        print("Changes saved to Excel!")

    def create_new_1a(self, src: str = 'src/pipeline/visualDebug/1a_template.xlsx', target_folder: str = '', file_name: str = '1a_test.xlsx'):
        workbook = openpyxl.load_workbook(src)

        target_path = os.path.join(target_folder, file_name)

        if os.path.exists(target_path):
            base, extension = os.path.splitext(file_name)
            current_time = datetime.datetime.now()
            file_name = f"{base}_({current_time.timestamp()}){extension}"
            target_path = os.path.join(target_folder, file_name)

        workbook.save(target_path)

    def add_column(self):
        template_excel_column = 'src/pipeline/visualDebug/1a_template.xlsx'
        template_column = pd.read_excel(template_excel_column, usecols=['Persoon 1'])

        # Ensure the new column length matches the DataFrame's length
        while len(template_column) < len(self.df):
            template_column = template_column.append(pd.Series([None]), ignore_index=True)
        template_column = template_column[:len(self.df)]

        col_name = f"Persoon {len(self.df.columns)}"
        self.df[col_name] = template_column

        # Update the table view
        self.table.model.df = self.df
        self.table.redraw()

app = TableEditor()
app.mainloop()
