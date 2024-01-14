import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import fitz 
import datetime
from tkinter import Canvas, Scrollbar, ttk, messagebox
from PIL import Image, ImageTk
import os, sys
import pandas as pd
import openpyxl
from pandastable import Table
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdfWrapper import PDF_wrapper

class PDFViewer:

    def __init__(self, wrapperlist):
        self.root = TkinterDnD.Tk()
        self.root.title('extracted tables')
        self.wrapperList = wrapperlist
        self.root.geometry("600x800")
        # Create the Treeview
        self.tree = ttk.Treeview(self.root)

        # Define columns
        self.tree['columns'] = ('file_name', 'page_number', 'csv_file', 'status')

        # Format columns
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('file_name', anchor=tk.W, width=120)
        self.tree.column('page_number', anchor=tk.CENTER, width=80)
        self.tree.column('status', anchor=tk.CENTER, width=80)

        # Create headings
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('file_name', text='File Name', anchor=tk.W)
        self.tree.heading('page_number', text='Page Number', anchor=tk.CENTER)
        self.tree.heading("csv_file", text = 'csv_file', anchor = tk.CENTER)
        self.tree.heading("status", text = 'status', anchor = tk.CENTER)

        # Add data to the treeview
        self.load_wrapper(wrapperlist)

        # Bind the select event
        self.tree.bind('<<TreeviewSelect>>', self.on_pdf_select)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_wrapper(self, wrapperlist):
        """Load all the pdf's that are in the wrapper list."""
        for pdfwrap in wrapperlist:
            for page in pdfwrap.pages:
                if page.has_1a_table:
                    self.tree.insert('', 'end', values=(page.pdf_path, page.page_number, page.csv_path, page.csv_method))

    def display_pdf(self, pdf_path, target_page, new_window):
        """Open a PDF file in a new window with navigation buttons, zoom functionality, and scrollbars."""
        f = tk.Frame(new_window)
        f.pack(side="left", fill=tk.BOTH, expand=True)

        # Create a canvas and add scrollbars
        canvas = tk.Canvas(f, width=650, height=800)
        vbar = tk.Scrollbar(f, orient='vertical', command=canvas.yview)
        hbar = tk.Scrollbar(f, orient='horizontal', command=canvas.xview)
        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        canvas.grid(row = 1, column = 0, rowspan=8, columnspan = 6)
        vbar.grid(row = 1, rowspan = 8, column = 6, sticky = "ns")
        hbar.grid(row = 9, column = 0, columnspan = 6, sticky = "ew")

        # Load the PDF file
        pdf = fitz.open(pdf_path)
        self.current_page_number = target_page
        self.zoom_level = 1.0  # Initial zoom level

        def render_page(page_number, zoom_level):
            page = pdf.load_page(page_number)
            mat = fitz.Matrix(zoom_level, zoom_level)  # Zoom factor
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(image=img)
            canvas.delete("all")  # Clear previous image
            canvas.create_image(0, 0, image=photo, anchor='nw')
            canvas.config(scrollregion=canvas.bbox('all'))
            canvas.image = photo  # keep a reference
            self.current_page_number = page_number

        render_page(target_page, self.zoom_level)
        
        # Navigation and Zoom Buttons
        nav_frame = tk.Frame(f)
        nav_frame.grid(row = 0, column = 0, columnspan = 6)

        prev_button = tk.Button(nav_frame, text="Previous", command=lambda: render_page(self.current_page_number - 1, self.zoom_level))
        next_button = tk.Button(nav_frame, text="Next", command=lambda: render_page(self.current_page_number + 1, self.zoom_level))
        zoom_in_button = tk.Button(nav_frame, text="Zoom In", command=lambda: update_zoom(0.1))
        zoom_out_button = tk.Button(nav_frame, text="Zoom Out", command=lambda: update_zoom(-0.1))

        prev_button.pack(side="left")
        next_button.pack(side="right")
        zoom_in_button.pack(side="left")
        zoom_out_button.pack(side="right")

        def update_zoom(delta):
            self.zoom_level += delta
            render_page(self.current_page_number, self.zoom_level)

        def check_buttons():
            prev_button['state'] = tk.NORMAL if self.current_page_number > 0 else tk.DISABLED
            next_button['state'] = tk.NORMAL if self.current_page_number < pdf.page_count - 1 else tk.DISABLED
        check_buttons()
        
    def display_table(self,csv_path,window,pdf_name):
        f = tk.Frame(window, width=650, height=800)
        f.pack(side = "right", fill="none", expand=True)
        self.file_name_original_csv = csv_path
        self.window = window
        # just for testing: check if the csv is in excel format and handle it as excel, otherwise as csv
        if ".xlsx" in csv_path:
            self.df = pd.read_excel(self.file_name_original_csv)
        else:
            self.df = pd.read_csv(self.file_name_original_csv)
        
        # Create a backup of the DataFrame
        self.df_backup = self.df.copy() 
        
        self.table = Table(f, dataframe=self.df, showtoolbar=True, showstatusbar=True, maxcellwidth=200, height = 600, width = 2000)
        self.table.show()
        
        buttons = tk.Frame(f)
        self.add_column_button = tk.Button(buttons, text='Add Column', command=self.add_column)
        self.add_column_button.pack()

        self.save_file_button = tk.Button(buttons, text='Confirm changes', command=self.save_changes)
        self.save_file_button.pack()
        
        self.undo_button = tk.Button(buttons, text='Undo Changes', command=self.undo_changes)
        self.undo_button.pack()
        buttons.grid(row=0, column=0)
        
        buttons.grid(row = 0, column = 0)
        
    
    def undo_changes(self):
        response = messagebox.askyesno("Confirm Undo", "Are you sure you want to undo all changes?",parent = self.window)
        if response:
            self.df = self.df_backup.copy()
            self.table.model.df = self.df
            self.table.redraw()
            self.save_changes()
        
        
    def save_changes(self):
        if ".xlsx" in self.file_name_original_csv:
            self.df.to_excel(self.file_name_original_csv, index=False)
        else:
            self.df.to_csv(self.file_name_original_csv, index = False)
        popup = tk.Toplevel(self.window)
        popup.title("Save Confirmation")
        label = tk.Label(popup, text="changes saved")
        label.pack()
        popup.after(1000, popup.destroy)
        

    def create_new_1a(self, csv_path, target_folder, file_name):
        workbook = openpyxl.load_workbook(csv_path)

        target_path = os.path.join(target_folder, file_name)

        if os.path.exists(target_path):
            base, extension = os.path.splitext(file_name)
            current_time = datetime.datetime.now()
            file_name = f"{base}_({current_time.timestamp()}){extension}"
            target_path = os.path.join(target_folder, file_name)

        workbook.save(target_path)

    def add_column(self):
        template_excel_column = 'src/pipeline/visualDebug/1a_template.xlsx'
        template_column = pd.read_excel(template_excel_column, usecols=['Persoon 1']).squeeze()

        # Ensure the new column length matches the DataFrame's length
        while len(template_column) < len(self.df):
            template_column = pd.concat([template_column,pd.Series([None])], ignore_index=True)
        template_column = template_column[:len(self.df)]

        col_name = f"Persoon {len(self.df.columns)}"
        self.df[col_name] = template_column

        # Update the table view
        self.table.model.df = self.df
        self.table.redraw()
        
        
    def on_pdf_select(self, event):
        """Handle the selection of a PDF file from the Treeview."""
        w = event.widget
        selected_item = w.selection()[0]  # Get selected item
        pdf_name, page_str, csv_file, csv_method = w.item(selected_item, 'values')
        page = int(page_str)

        # Create a new window to display the PDF
        new_window = tk.Toplevel(self.root)
        new_window.title(os.path.basename(pdf_name))
        new_window.geometry("2000x2000")

        # Display the PDF and the table in the new window
        self.display_pdf(pdf_name, page - 1, new_window)
        self.display_table(csv_file, new_window,pdf_name)

 
    def run(self):
        """Start the GUI loop."""
        self.root.mainloop()

# folder_path = 'dataProcessing/allPDF_1'
# pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
wrappers = []
wrapper1 = PDF_wrapper("wnt_not_scanned","src\pipeline\wnt_not_scanned.pdf")
wrapper1.add_page(35,True,False,True,'src\pipeline\speedy_candidates_results.csv', "exact match coördinate")
wrappers.append(wrapper1)
wrapper2 = PDF_wrapper("wnt_scan","src\pipeline\wnt_scan.pdf")
wrapper2.add_page(34,False,True,True,"src/pipeline/visualDebug/1a_template.xlsx", "ocr")
wrappers.append(wrapper2)
viewer = PDFViewer(wrappers)
viewer.run()