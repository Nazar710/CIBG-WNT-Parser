import tabula

"""
(Sander Stokhof)

using tabula to extract tables from pdf.(text)
"""

tables = tabula.read_pdf("example_tables.pdf", pages="all")


for table in tables:
    print(table)