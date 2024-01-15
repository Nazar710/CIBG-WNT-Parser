import tkinter as tk
import threading
import os 

class LoadingWindow(tk.Toplevel):
    def __init__(self, parent, file_name, path, selected_files):
        super().__init__(parent)
        # self.iconbitmap(os.path.join(os.getcwd(),os.path.join("images","icon.ico"))) #gives path to images/icon.ico (os agnostic)
        self.title("LOADING")
        self.file_name = file_name  # Store the file name
        self.path = path  # Store the path
        self.selected_files = selected_files  # Store the list of selected files

        # Calculate the position to center the loading window on the screen
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - 500) // 2  # Window width is set to 300
        y = (screen_height - 200) // 2  # Window height is set to 100
        self.geometry("500x200+{}+{}".format(x, y))

        # Display the list of selected files
        selected_files_label = tk.Label(self, text="Selected PDF files:", font=("Arial", 10))
        selected_files_label.pack(pady=5)
        for file_path in selected_files:
            file_label = tk.Label(self, text=file_path, font=("Arial", 10))
            file_label.pack()

        loading_label = tk.Label(self, text=f"Generating {self.file_name} in {self.path}...", font=("Arial", 10))
        loading_label.pack(pady=5)

    def simulate_loading(self):
        import time
        time.sleep(5)  # Simulate a 5-second delay
        self.destroy()  # Close the loading window when done