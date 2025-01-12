import pandas as pd
import pandas_ta_remake as ta

df = pd.DataFrame() # Empty DataFrame

df = df.ta.ticker("aapl")

print(df.head())
