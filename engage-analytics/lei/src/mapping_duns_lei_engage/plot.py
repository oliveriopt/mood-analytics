import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("test.csv",index_col="index")
df.hist(column="Number_DUNS", bins=50)
print(df.head())
plt.show()