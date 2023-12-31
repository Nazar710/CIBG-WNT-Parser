"""
wrapper class for PDF file and its candidate pages
author: john nazarenko 
date: 09/01/2024  
"""


class PDF_wrapper:
    """
    A class to represent a wrapper around a PDF document.

    Attributes:
        _file_name (str): The name of the PDF file.
        _pages (list): A list of candidate_pages objects representing the pages of the PDF.

    Methods:
        file_name: Get or set the name of the PDF file.
        pages: Get the list of candidate_pages objects.
        add_page: Add a new candidate page to the PDF.
    """

    def __init__(self, file_name):
        """
        Constructs all the necessary attributes for the PDF_wrapper object.

        Parameters:
            file_name (str): The name of the PDF file.
        """
        self._file_name = file_name
        self._pages = []

    @property
    def file_name(self):
        """Get or set the file name of the PDF."""
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def pages(self):
        """Get the list of candidate_pages in the PDF."""
        return self._pages

    def add_page(self, page_number, selectable, scanned, has_1a_table, csv_path):
        """
        Add a new candidate page to the PDF.

        Parameters:
            page_number (int): The page number in the PDF.
            selectable (bool): True if the page content is selectable, False otherwise.
            scanned (bool): True if the page is scanned, False otherwise.
            has_1a_table (bool): True if the page contains a 1a table, False otherwise.
            csv_path (str): The file path to the CSV representation of the page.
        """
        new_page = self.candidate_pages(self, page_number, selectable, scanned, has_1a_table, csv_path)
        self._pages.append(new_page)

    class candidate_pages:
        """
        A class to represent a candidate page in a PDF.

        Attributes:
            parent_pdf (PDF_wrapper): The parent PDF_wrapper instance.
            _page_number (int): The page number in the PDF.
            _selectable (bool): True if the page content is selectable, False otherwise.
            _scanned (bool): True if the page is scanned, False otherwise.
            _has_1a_table (bool): True if the page contains a 1a table, False otherwise.
            _csv_path (str): The file path to the CSV representation of the page.

        Methods:
            page_number: Get or set the page number.
            selectable: Get or set the selectable status.
            scanned: Get or set the scanned status.
            has_1a_table: Get or set the presence of a 1a table.
            csv_path: Get or set the CSV file path.
            get_file_name: Get the file name of the parent PDF.
        """

        def __init__(self, parent_pdf, page_number, selectable, scanned, has_1a_table, csv_path):
            """
            Constructs all the necessary attributes for the candidate_pages object.

            Parameters:
                parent_pdf (PDF_wrapper): The parent PDF_wrapper instance.
                page_number (int): The page number in the PDF.
                selectable (bool): True if the page content is selectable, False otherwise.
                scanned (bool): True if the page is scanned, False otherwise.
                has_1a_table (bool): True if the page contains a 1a table, False otherwise.
                csv_path (str): The file path to the CSV representation of the page.
            """
            self.parent_pdf = parent_pdf
            self._page_number = page_number
            self._selectable = selectable
            self._scanned = scanned
            self._has_1a_table = has_1a_table
            self._csv_path = csv_path

        @property
        def page_number(self):
            """Get or set the page number of the candidate page."""
            return self._page_number

        @page_number.setter
        def page_number(self, value):
            self._page_number = value

        @property
        def selectable(self):
            """Get or set the selectable status of the candidate page."""
            return self._selectable

        @selectable.setter
        def selectable(self, value):
            self._selectable = value

        @property
        def scanned(self):
            """Get or set the scanned status of the candidate page."""
            return self._scanned
        
        @scanned.setter
        def scanned(self, value):
            self._scanned = value

        @property
        def has_1a_table(self):
            """Get or set the presence of a 1a table on the candidate page."""
            return self._has_1a_table
        
        @has_1a_table.setter
        def has_1a_table(self, value):
            self._has_1a_table = value

        @property
        def csv_path(self):
            """Get or set the CSV file path of the candidate page."""
            return self._csv_path
        
        @csv_path.setter
        def csv_path(self, value):
            self._csv_path = value

        def get_file_name(self):
            """Get the file name of the parent PDF."""
            return self.parent_pdf.file_name
        
        def __repr__(self):
            return f"candidate_pages({self.parent_pdf}, {self.page_number}, {self.selectable}, {self.scanned}, {self.has_1a_table}, {self.csv_path})"
        
       

           
