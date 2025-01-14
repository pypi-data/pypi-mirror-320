from core import GTUS,AsyncGTUS
import pandas as pd
queries = ["telemedicine", "remote work", "dance"]
states = ["TX","CA", "GA"]
gtus = GTUS(queries, states, timeframe="2022-01-01 2023-01-01", wait_time=14)

gtus.collect_all_trends()

gtus.export_to_excel("google_trends_data.xlsx")
gtus.export_to_json("google_trends_data.json")
consolidated_df = gtus.create_consolidated_dataframe()




# Display the DataFrame
print(consolidated_df.head(10))
