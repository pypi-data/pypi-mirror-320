import requests
import pandas as pd

def fetch_and_process_odds_data(api_key, sports, regions):
    all_odds_data = {}
    rows = []

    # Loop through each sport/league to get and process data
    for sport in sports:
        sport = sport.strip()  # Clean up whitespace
        print(f"\nFetching odds data for {sport}...")
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"

        # Define query parameters
        params = {
            'apiKey': api_key,
            'regions': ','.join(regions),  # Join regions list into a comma-separated string
            'markets': 'h2h'
        }

        # Make the GET request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            odds_data = response.json()  # Parse the JSON response
            all_odds_data[sport] = odds_data  # Store data for each sport

            # Process the odds data into rows
            for game in odds_data:
                sport_title = game['sport_title']
                commence_time = game['commence_time']
                home_team = game['home_team']
                away_team = game['away_team']

                for bookmaker in game.get('bookmakers', []):
                    bookmaker_name = bookmaker['title']

                    for market in bookmaker.get('markets', []):
                        market_key = market['key']
                        last_update = market['last_update']

                        # Extract odds for each outcome
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            outcome_name = outcome['name']
                            price = outcome['price']

                            # Append a row with the relevant data
                            rows.append({
                                'Sport': sport_title,
                                'Commence Time': commence_time,
                                'Home Team': home_team,
                                'Away Team': away_team,
                                'Bookmaker': bookmaker_name,
                                'Market': market_key,
                                'Last Update': last_update,
                                'Outcome': outcome_name,
                                'Odds': price
                            })
        else:
            print(f"Error for {sport}: {response.status_code}")
            print(response.text)

    # Convert list of rows to a DataFrame
    df = pd.DataFrame(rows)

    # Display the DataFrame
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.expand_frame_repr', False)  # Don't wrap rows
    pd.set_option('display.width', 1000)
    print(df)
    return df


def group_event_odds(df):
    df = df[df['Market'] != 'h2h_lay']
    df["Commence Time"] = pd.to_datetime(df["Commence Time"])
    df["Last Update"] = pd.to_datetime(df["Last Update"])
    # Calculate the difference and remove the days part
    df['Time Difference'] = pd.to_datetime(df['Commence Time']) - pd.to_datetime(df['Last Update'])

            # convert to hours
    df['Time Difference (Hours)'] = df['Time Difference'].dt.total_seconds() / 3600

    sport_mapping = {
        'La Liga - Spain': 'Soccer',
        'EPL': 'Soccer',
        'Serie A - Italy': 'Soccer',
        'Ligue 1 - France': 'Soccer',
        'Bundesliga - Germany': 'Soccer',
        'MLS': 'Soccer',
        'NBA': 'Basketball',
        'ATP Paris Masters': 'Tennis',
        'NCAAF': 'College Football',
        'Test Matches': 'Cricket',
        'One Day Internationals': 'Cricket',
        'International Twenty20': 'Cricket'
        }
    
    # Map the Sports column to the new Sport Type column
    df['Sport Type'] = df['Sport'].map(sport_mapping)



    #   Assuming df is your DataFrame and 'Last Update' is in datetime format
    df['Last Update'] = pd.to_datetime(df['Last Update'])  # Convert to datetime if not already

    # Extract the hour and convert it to 1-24 format
    df['Hour Bucket'] = df['Last Update'].dt.hour + 1
    df = df.sort_values('Last Update', ascending=False)

    # Drop duplicates to keep the most recent odds for each unique combination of 'Sport', 'Commence Time', 'Home Team', 'Away Team', 'Bookmaker', 'Market', 'Outcome'
    df = df.drop_duplicates(subset=['Sport', 'Commence Time', 'Home Team', 'Away Team', 'Bookmaker', 'Market', 'Outcome', ])

    # Initialize lists to store the processed rows
    grouped_data = []

    # Iterate through each unique event
    for _, group in df.groupby(['Sport', 'Commence Time', 'Home Team', 'Away Team', 'Bookmaker', 'Market', 'Time Difference', 'Sport Type', "Hour Bucket"]):
        # Create a dictionary for storing the combined row
        event_data = group.iloc[0][['Sport', 'Commence Time', 'Home Team', 'Away Team', 'Bookmaker', 'Market', 'Time Difference', 'Sport Type', 'Hour Bucket']].to_dict()

        # Set default odds for each outcome type
        event_data['odds1'] = 0
        event_data['odds2'] = 0
        event_data['odds3'] = 0

        # Populate the odds fields
        for _, row in group.iterrows():
            if row['Outcome'] == row['Home Team']:
                event_data['odds1'] = row['Odds']
            elif row['Outcome'] == row['Away Team']:
                event_data['odds2'] = row['Odds']
            elif row['Outcome'] == 'Draw':
                event_data['odds3'] = row['Odds']

        # Append the combined row to the list
        grouped_data.append(event_data)

    # Create a new DataFrame from the grouped data
    result_df = pd.DataFrame(grouped_data)

    # Add columns for the probabilities (1/odds)
    result_df['probability1'] = result_df['odds1'].apply(lambda x: 1/x if x > 0 else 0)
    result_df['probability2'] = result_df['odds2'].apply(lambda x: 1/x if x > 0 else 0)
    result_df['probability3'] = result_df['odds3'].apply(lambda x: 1/x if x > 0 else 0)

    # Add a column for the total probability sum
    result_df['total_probability'] = result_df['probability1'] + result_df['probability2'] + result_df['probability3']

    return result_df

def find_arb_ml(result_df):
    result_df['event_name']=result_df['Home Team']+'_'+result_df['Away Team']
    results = []

    for event, group in result_df.groupby('event_name'):
    # Get the row with the minimum probability1 for the event
        min_odds_1_row = group.loc[group['probability1'].idxmin()]

    # Get the row with the minimum probability2 for the event
        min_odds_2_row = group.loc[group['probability2'].idxmin()]

    # Get the row with the minimum probability3 for the event
        min_odds_3_row = group.loc[group['probability3'].idxmin()]

    # Extract relevant values
        odds_1_prob = min_odds_1_row['probability1']
        odds_2_prob = min_odds_2_row['probability2']
        odds_3_prob = min_odds_3_row['probability3']
        bookmaker_1 = min_odds_1_row['Bookmaker']
        bookmaker_2 = min_odds_2_row['Bookmaker']
        bookmaker_3 = min_odds_3_row['Bookmaker']

    # Calculate the sum of the minimum probabilities
        odds_sum = odds_1_prob + odds_2_prob + odds_3_prob

    # Determine if it's an arbitrage opportunity
        arbitrage = 1 if odds_sum < 1 else 0

    # Append the results to the list
        results.append({
            'event_name': event,
            'odd_1_prob': odds_1_prob,
            'bookmaker_1': bookmaker_1,
            'odd_2_prob': odds_2_prob,
            'bookmaker_2': bookmaker_2,
            'odd_3_prob': odds_3_prob,
            'bookmaker_3': bookmaker_3,
            'odds_sum': odds_sum,
            'arbitrage': arbitrage,
            'Time Difference': min_odds_1_row['Time Difference'],  # Assuming time difference is the same for all rows in the event
            'Sport Type': min_odds_1_row['Sport Type'],
            'Hour Bucket': min_odds_1_row['Hour Bucket']

        })
    
    return pd.DataFrame(results)


