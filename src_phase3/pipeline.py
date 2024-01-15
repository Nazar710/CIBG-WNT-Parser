import a1checker.a1checkerMain as a1checkerMain 


if __name__ == "__main__":
    treshold = 0.7 

    Extractor = a1checkerMain.extractor()
    checker = a1checkerMain.a1checker()

    wrappedPdfs =[checker.is1aOrNot(pdfobj,treshold) for pdfobj in Extractor.extract("pdfs")]

    