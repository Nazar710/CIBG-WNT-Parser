import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sbn

if __name__ == "__main__":
    df = pd.read_excel("data_labeling.xlsx")

    normale_table = df["Table type"][df["Table type"] == 1].count()
    scanned_tables = df["Table type"][df["Table type"] == 2].count()
    white_space_table = df["Table type"][df["Table type"] == 3].count() #and true free text
    no_wnt_table = df["Table type"][df["Table type"] == 4].count()


    sbn.barplot({"normal table":normale_table,"scanned table":scanned_tables,"white space table":white_space_table,"no wnt table":no_wnt_table})
    plt.ylabel("count")
    plt.title("dataset distribution")
    plt.show()