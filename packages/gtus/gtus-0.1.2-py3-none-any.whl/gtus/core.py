# core.py

from pytrends.request import TrendReq
import pandas as pd
import time
import json
from requests.exceptions import RequestException
import asyncio
import aiohttp
import warnings

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

class GTUS:
    def __init__(self, queries, states=None, timeframe='today 5-y', delay=5, gprop='', wait_time=10):
        self.pytrend = TrendReq()
        self.queries = queries
        self.states = states or [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]
        self.timeframe = timeframe
        self.delay = delay
        self.gprop = gprop
        self.all_data = {}
        self.wait_time = wait_time

    def fetch_state_trends(self, query, state, max_retries=3, backoff_factor=1.5):
        for attempt in range(max_retries):
            try:
                self.pytrend.build_payload(
                    kw_list=[query],
                    timeframe=self.timeframe,
                    geo='US-' + state,
                    gprop=self.gprop
                )
                state_trends = self.pytrend.interest_over_time()
                if state_trends.empty:
                    print(f"No data found for query '{query}' in state '{state}'.")
                    return None
                return state_trends
            except RequestException as e:
                if attempt == max_retries - 1:
                    print(f"Error fetching data for query '{query}' in state '{state}': {e}")
                    return None
                wait_time = self.delay * (backoff_factor ** attempt)
                time.sleep(wait_time)
            except Exception as e:
                print(f"Unexpected error for query '{query}' in state '{state}': {e}")
                return None
            finally:
                time.sleep(self.wait_time)

    def collect_all_trends(self):
        # Group states into batches of 5
        for i in range(0, len(self.states), 5):
            state_batch = self.states[i:i + 5]  # Get a batch of up to 5 states
            for state in state_batch:
                state_data = {}
                # Group queries into batches of 5
                for j in range(0, len(self.queries), 5):
                    query_batch = self.queries[j:j + 5]  # Get a batch of up to 5 queries
                    for query in query_batch:
                        result = self.fetch_state_trends(query, state)
                        if result is not None and not result.empty:
                            state_data[query] = result
                self.all_data[state] = state_data

    def export_to_json(self, filename="google_trends_by_state.json"):
        nested_data = {}
        for state, query_data in self.all_data.items():
            nested_data[state] = {
                query: df.to_dict(orient='records')  # Convert DataFrame to a list of records
                for query, df in query_data.items()
                if not df.empty
            }

        # Save the nested dictionary to JSON
        with open(filename, 'w') as f:
            json.dump(nested_data, f, indent=4)
        print(f"Data exported to {filename}")

    def export_to_excel(self, filename="google_trends_by_state.xlsx"):
        if not self.all_data:
            print("No data to export.")
            return  # Skip export if there's no data

        with pd.ExcelWriter(filename) as writer:
            for state, query_data in self.all_data.items():
                if query_data:  # Only export if there's data for the state
                    combined_data = pd.concat(
                        [df.rename(columns={query: query}) for query, df in query_data.items()], axis=1
                    ).drop(columns=['isPartial'], errors='ignore')  # Remove 'isPartial' column
                    combined_data.to_excel(writer, sheet_name=state[:31])
        print(f"Data exported to {filename}")

    def create_consolidated_dataframe(self):
        all_data = []

        # Create a DataFrame with all dates and states from the data
        for state, query_data in self.all_data.items():
            for query, df in query_data.items():
                if not df.empty:
                    # Reset index to make 'date' a column
                    df = df.reset_index()
                    
                    # Create a temporary DataFrame with 'date', 'State', and query values
                    temp_df = df[['date']].copy()
                    temp_df[query] = df[query]
                    temp_df['State'] = state
                    
                    # Append the temporary DataFrame to the all_data list
                    all_data.append(temp_df)

        # Concatenate all temporary DataFrames into one
        if all_data:
            consolidated_df = pd.concat(all_data, ignore_index=True)
            
            # Pivot the DataFrame to have states and queries in the desired format
            consolidated_df = consolidated_df.pivot_table(index=['date', 'State'], 
                                                           values=self.queries, 
                                                           aggfunc='first')
            
            # Fill missing values with NA
            consolidated_df.fillna(value=pd.NA, inplace=True)

            # Reset index to make 'date' and 'State' regular columns
            consolidated_df_reset = consolidated_df.reset_index()

            return consolidated_df_reset
        else:
            print("No data available to create a consolidated DataFrame.")
            return pd.DataFrame()  # Return an empty DataFrame if no data is available

class AsyncGTUS(GTUS):
    async def fetch_state_trends_async(self, query, state, session, max_retries=3, backoff_factor=1.5):
        for attempt in range(max_retries):
            try:
                payload = {
                    'hl': 'en-US',
                    'tz': 360,
                    'req': {
                        'comparisonItem': [
                            {
                                'geo': {'country': f'US-{state}'},
                                'time': self.timeframe,
                                'keyword': query
                            }
                        ],
                        'category': 0,
                        'property': self.gprop
                    }
                }
                async with session.post("https://trends.google.com/trends/api/widgetdata", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    print(f"Error fetching data for query '{query}' in state '{state}': {e}")
                    return None
                wait_time = self.delay * (backoff_factor ** attempt)
                await asyncio.sleep(wait_time)
        return None

    async def collect_all_trends_async(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for state in self.states:
                for query in self.queries:
                    tasks.append(self.fetch_state_trends_async(query, state, session))

            results = await asyncio.gather(*tasks)
            # Process results (left as an exercise to map results back into self.all_data)

# Example usage
if __name__ == "__main__":
    queries = ["telemedicine", "remote work"]
    states = ["CA", "NY"]

    gtus = GTUS(queries, states)
    gtus.collect_all_trends()
    gtus.export_to_json()
    gtus.export_to_excel()

    # Create a consolidated DataFrame
    consolidated_df = gtus.create_consolidated_dataframe()
    print(consolidated_df.head())
