import tabula

tables = tabula.read_pdf("example_tables.pdf", pages="all")


for table in tables:
    print(table)