# example_usage.py

import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from core import GTUS

def main():
    # Define your queries and states
    queries = ["telemedicine", "remote work", "artificial intelligence", "climate change", "blockchain", "trump", "clinton"]
    states = ["CA", "NY", "TX", "FL", "IL"]  # You can add more states as needed

    # Create an instance of the GTUS class
    gtus = GTUS(queries,states,timeframe='today 5-y', wait_time=15)

    # Collect trends for the specified queries and states
    gtus.collect_all_trends()

    # Export the collected data to JSON
    #gtus.export_to_json()

    # Export the collected data to Excel
    #gtus.export_to_excel()

    # Create a consolidated DataFrame and print the first few rows
    consolidated_df = gtus.create_consolidated_dataframe()
    print(consolidated_df.info())

if __name__ == "__main__":
    main()