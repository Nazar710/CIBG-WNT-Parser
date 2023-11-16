import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
from LoadingWindow import LoadingWindow
import os

class PDFProcessorApp:
    def __init__(self, root):
        self.root = root
        self.init_gui()

    def init_gui(self):
        self.root.title("PDF Processor")
        self.root.iconbitmap(os.path.join(os.getcwd(),os.path.join("images","icon.ico")))
        self.root.configure(bg="white")
        self.set_window_geometry(600, 600)

        self.selected_pdf_files = []  # Use a list to store multiple selected files
        self.file_name_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.root.resizable(False, False)

        self.create_image_label()
        self.create_entry_bars()  # Create entry bars for file name and path

        self.create_select_file_button()
        self.enable_drag_and_drop()
        self.create_drag_and_drop_label()
        self.add_extract_button()
        self.create_output_folder_browse_button()  # Create a button to browse the output folder
        self.create_additional_files_label()  # Create a label for additional files
        self.selected_file_labels = []  # Use a list to store multiple file labels

    def set_window_geometry(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_image_label(self):
        image = tk.PhotoImage(file=os.path.join(os.getcwd(),os.path.join("images","image333.png")))
        self.image_label = tk.Label(self.root, image=image)
        self.image_label.image = image
        self.image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def create_select_file_button(self):
        self.select_file_button = tk.Button(self.root, text="Browse...", font=("Arial bold", 14), command=self.select_pdf_file,
                                            bg="white", fg="#2596be", borderwidth=2, relief="solid")
        self.select_file_button.place(relx=0.5, rely=0.72, anchor=tk.CENTER)

    def enable_drag_and_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def create_drag_and_drop_label(self):
        self.drag_and_drop_label = tk.Label(self.root, text="Drag and Drop pdf files here ...", font=("Arial bold", 14),
                                            bg="WHITE", padx=20, pady=10)
        self.drag_and_drop_label.place(relx=0.5, rely=0.58, anchor=tk.CENTER)

        self.or_label = tk.Label(self.root, text="OR", font=("Arial", 14), bg="WHITE", padx=20, pady=10)
        self.or_label.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    def select_pdf_file(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for file_path in file_paths:
            if file_path:
                self.selected_pdf_files.append(file_path)
                self.process_pdf_file(file_path)

    def process_pdf_file(self, file_path):
        print(f"Processing PDF file: {file_path}")
        self.hide_drag_and_drop_elements()
        self.update_extract_button_state()
        self.show_selected_file_label(file_path)
        self.update_additional_files_label()

    def on_drop(self, event):
        file_paths = event.data.split()
        for file_path in file_paths:
            if file_path.lower().endswith(".pdf"):
                self.selected_pdf_files.append(file_path)
                self.process_pdf_file(file_path)

    def hide_drag_and_drop_elements(self):
        self.drag_and_drop_label.place_forget()
        self.select_file_button.place_forget()
        self.or_label.place_forget()

    def update_extract_button_state(self):
        if self.selected_pdf_files:
            self.extract_button.config(state=tk.NORMAL)
        else:
            self.extract_button.config(state=tk.DISABLED)

    def show_selected_file_label(self, file_path):
        if len(self.selected_file_labels) < 4:
            file_label = tk.Label(self.root, text=f"Selected File: {file_path}", font=("Arial", 10),
                                  bg="WHITE", padx=10, pady=10)
            file_label.place(relx=0.5, rely=len(self.selected_file_labels) * 0.05 + 0.58, anchor=tk.CENTER)
            self.selected_file_labels.append(file_label)
            self.create_delete_button(file_path, file_label)

    def create_delete_button(self, file_path, file_label):
        delete_button = tk.Button(file_label, text="X", font=("Arial", 5), bg="red", fg="white",
                                  command=lambda: self.remove_selected_file(file_path, file_label))
        delete_button.place(relx=0.95, rely=0.1, anchor=tk.CENTER)

    def remove_selected_file(self, file_path, file_label):
        self.selected_pdf_files.remove(file_path)
        file_label.place_forget()
        self.selected_file_labels.remove(file_label)
        self.update_extract_button_state()
        self.show_drag_and_drop_elements()  # Show the drag and drop elements again

    def show_drag_and_drop_elements(self):
        self.drag_and_drop_label.place(relx=0.5, rely=0.58, anchor=tk.CENTER)
        self.select_file_button.place(relx=0.5, rely=0.72, anchor=tk.CENTER)
        self.or_label.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    def create_loading_window(self):
        file_name = self.file_name_var.get()
        path = self.path_var.get()

        # Pass the selected PDF files list to the LoadingWindow instance
        loading_window = LoadingWindow(self.root, file_name=file_name, path=path, selected_files=self.selected_pdf_files)

        # Print the list of selected PDF files
        print("Selected PDF files:", self.selected_pdf_files)

        loading_thread = threading.Thread(target=loading_window.simulate_loading)
        loading_thread.start()

    def add_extract_button(self):
        self.extract_button = tk.Button(self.root, text="Extract PDF", font=("Arial", 14), command=self.create_loading_window,
                                        bg="#2596be", fg="white", borderwidth=1, relief="solid", state=tk.DISABLED)
        self.extract_button.place(relx=0.5, rely=0.92, anchor=tk.CENTER)

    def create_entry_bars(self):
        outputFileName = tk.Label(self.root, text="Output file name", font=("Arial bold", 15),bg="WHITE")
        outputFileName.place(relx=0.4, rely=0.3, anchor=tk.E)
    
        file_name_entry = tk.Entry(self.root, textvariable=self.file_name_var, font=("Arial ", 14))
        file_name_entry.place(relx=0.35, rely=0.35, anchor=tk.CENTER)

        OutputFolder = tk.Label(self.root, text="Output folder", font=("Arial bold", 15),bg="WHITE")
        OutputFolder.place(relx=0.35, rely=0.40, anchor=tk.E)
        
        path_entry = tk.Entry(self.root, textvariable=self.path_var, font=("Arial ", 14))
        path_entry.place(relx=0.35, rely=0.45, anchor=tk.CENTER)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_var.set(folder_path)

    def create_output_folder_browse_button(self):
        output_folder_browse_button = tk.Button(self.root, text="Browse", font=("Arial bold", 10), command=self.select_output_folder,
                                            bg="white", fg="#25BCBE", borderwidth=2, relief="solid")
        output_folder_browse_button.place(relx=0.65, rely=0.45, anchor=tk.CENTER)

    def create_additional_files_label(self):
        self.additional_files_label = tk.Label(self.root, text="", font=("Arial", 10), bg="WHITE", padx=20, pady=10)
        self.additional_files_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def update_additional_files_label(self):
        num_additional_files = len(self.selected_pdf_files) - 4
        if num_additional_files > 0:
            self.additional_files_label.config(text=f"and {num_additional_files} more files")
        else:
            self.additional_files_label.config(text="")
    def getPdfFiles(self):
        return self.selected_pdf_files

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFProcessorApp(root)
    root.mainloop()
