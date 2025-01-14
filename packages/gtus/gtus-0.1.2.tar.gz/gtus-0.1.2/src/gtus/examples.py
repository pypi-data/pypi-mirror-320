from core import GTUS
queries = ["remote work", "telehealth"]
states=["AK", "TX", "AL"]

# Initialize GTUS object
gtus1 = GTUS(queries, states,timeframe="2022-01-01 2023-01-01")
gtus1.collect_all_trends()
gtus1.export_to_excel("google_trends_df.xlsx")
consolidated_df = gtus1.create_consolidated_dataframe()
print(consolidated_df.head())
