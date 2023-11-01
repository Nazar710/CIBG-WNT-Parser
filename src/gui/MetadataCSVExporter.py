import csv

from MetadataList import MetadataList

class MetadataCSVExporter:
    def __init__(self, metadata_list):
        self.metadata_list = metadata_list

    def export_to_csv(self, filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["Institution Name", "Manager Name", "Salary", "Page Number"])
            
            # Write each metadata item
            for metadata_item in self.metadata_list.get_metadata():
                writer.writerow([
                    metadata_item["institution_name"],
                    metadata_item["manager_name"],
                    metadata_item["salary"],
                    metadata_item["page_number"]
                ])
        print(f"Data exported to {filename}")

# Example usage:
metadata_list = MetadataList()
metadata_list.add_metadata("CIBG", "Ahmed", 50000, 14)
metadata_list.add_metadata("CIBG", "Robbert", 60000, 42)
metadata_list.add_metadata("Maastricht University", "Mark", 60000, 33)

exporter = MetadataCSVExporter(metadata_list)
exporter.export_to_csv("metadata.csv")
