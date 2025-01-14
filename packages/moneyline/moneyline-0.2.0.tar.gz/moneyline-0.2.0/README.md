# Moneyline 
Moneyline is a python package meant to help detect arbitrage opportunities in sports (only for moneyline bets). It has the following functions:
fetch_and_process_odds_data(api_key, sports, regions), where the api key is a string, and sports and regions are lists of strings; returns df

group_event_odds(df)

find_arb_ml(result_df)

Run these functions sequentially to get the final dataframe that is structured to detect arbitrage and non-arbitrage opportunities


## Installation 
```bash 
pip install moneyline
