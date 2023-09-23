class MetadataList:
    def __init__(self):
        self.metadata_list = []

    def add_metadata(self, institution_name, manager_name, salary, page_number):
        metadata_item = {
            "institution_name": institution_name,
            "manager_name": manager_name,
            "salary": salary,
            "page_number": page_number,
        }
        self.metadata_list.append(metadata_item)

    def get_metadata(self):
        return self.metadata_list

    def display_metadata(self):
        for metadata_item in self.metadata_list:
            print(f"Institution Name: {metadata_item['institution_name']}")
            print(f"Manager Name: {metadata_item['manager_name']}")
            print(f"Salary: {metadata_item['salary']}")
            print(f"Page Number: {metadata_item['page_number']}")
            print("-" * 20)

# Example usage:
metadata_list = MetadataList()
metadata_list.add_metadata("CIBG", "Ahmed", 50000, 14)
metadata_list.add_metadata("CIBG", "Robbert", 60000, 42)

metadata_list.display_metadata()
