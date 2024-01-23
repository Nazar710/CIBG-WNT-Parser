import pandas as pd
from .FindBezoldiging import FinderAlgorithm  # Make sure to import the correct module
from .nameFind import KeywordFinder

class PDFProcessor:
    """
        processor class, given a list of names to look for in a PDF and the page to find it, extract a WNT table.
    """
    def __init__(self):
        self.results = []

    def process_pdf(self, pdf_path: str, target_page: int, names: list) -> None:
        
        try:
            target_page = int(target_page)
        except ValueError:
            #print(f"Invalid 'target_page' value: {target_page}")
            return  # Exit the method if the value is invalid

        if pdf_path and names:
            result_list = FinderAlgorithm(pdf_path, names, target_page - 1)

            self.results.append({
                'pdf_path': pdf_path,
                'names': names,
                'target_page': target_page,
                'result_list': result_list
            })
        else:
            #print("Invalid input values.")
            pass

    def return_results(self) -> list[pd.DataFrame]:
        """
        return list of dataframes
        """

        return [pd.DataFrame(result['result_list'], columns=[
                'bedragen x €', 'Bezoldiging', 'Functiegegevens', 'Aanvang en einde functievervulling',
                'Omvang dienstverband (als deeltijdfactor in fte)', 'Dienstbetrekking?', 'Beloning plus belastbare onkostenvergoedingen', 'Beloningen betaalbaar op termijn',
                'Subtotaal', 'Individueel toepasselijke bezoldigingsmaximum', '-/- Onverschuldigd betaald en nog niet terugontvangen bedrag',
                'Het bedrag van de overschrijding en de reden waarom de overschrijding al dan niet is toegestaan', 'Toelichting op de vordering wegens onverschuldigde betaling'
            ]) for result in self.results] 

    def save_results_to_csv(self, output_csv_path):

        for i, result in enumerate(self.results):
            result_df = pd.DataFrame(result['result_list'], columns=[
                'Name', 'Bezoldiging', 'Functie', 'functievervullingString',
                'Dienstverband', 'Dienstbetrekking', 'Beloning', 'Beloningen',
                'Subtotaal', 'Bezoldigingsmaximum', 'Onverschuldigd',
                'Overschrijding', 'Toelichting'
            ])

            # Save the results for each PDF to a separate CSV file
            output_csv_path = f'output_results_{i + 1}.csv'
            result_df.to_csv(output_csv_path, index=False)

    def display_results(self):
        #print(self.results)
        
        for result in self.results:
            #print(f"Results for PDF: {result['pdf_path']}")
            for name, result_data in zip(result['names'], result['result_list']):
                # print(f"Name: {result_data[0]}")
                # print(f"Bezoldiging: {result_data[1]}")
                # print(f"Functie: {result_data[2]}")
                # print(f"functievervullingString: {result_data[3]}")
                # print(f"Dienstverband : {result_data[4]}")
                # print(f"Dienstbetrekking: {result_data[5]}")
                # print(f"Beloning: {result_data[6]}")
                # print(f"Beloningen: {result_data[7]}")
                # print(f"Subtotaal: {result_data[8]}")
                # print(f"Bezoldigingsmaximum: {result_data[9]}")
                # print(f"Onverschuldigd: {result_data[10]}")
                # print(f"Overschrijding: {result_data[11]}")
                # print(f"Toelichting: {result_data[12]}")


                # print("N-------------------------------------------------N")
                pass

if __name__ == "__main__":
    

    # Example Usage:
    
    pdf_path="DigiMV2020_7FMRR3X2P7_0_05072572_Jaarrekening_6286_Stichting ZGR"
    pagenumber=30
    keyword_finder = KeywordFinder(f"pdfs/{pdf_path}.pdf")
    result = keyword_finder.find_keywords_with_context(pagenumber)
    keyword_finder.close()
    listofnames=result               

    pdf_processor = PDFProcessor()
    pdf_processor.process_pdf(pdf_path=pdf_path, target_page=pagenumber, names=listofnames)
    pdf_processor.save_results_to_csv(output_csv_path='output_results.csv')
    pdf_processor.display_results()
