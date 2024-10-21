import pandas as pd
import json

# Load the CSV
df = pd.read_csv('C:/Users/Ana/Desktop/DE Assessment/data.csv')

# Define the contract parsing function
def parse_contracts(contract):
    if pd.isna(contract):
        return None
    try:
        return json.loads(contract)
    except (ValueError, TypeError):
        return None
    
# Parse the 'contracts' column and create parsed_contracts feature
df['parsed_contracts'] = df['contracts'].apply(parse_contracts)

# Expand the contracts while keeping NaN intact
expanded_rows = []
indices = []  # To keep track of the original DataFrame index

for idx, contracts in enumerate(df['parsed_contracts']):
    if isinstance(contracts, list):
        for contract in contracts:
            if isinstance(contract, dict):
                expanded_rows.append(contract)
                indices.append(idx)  # Track the original index



# If we have expanded rows, create a DataFrame from them
if expanded_rows:
    df_expanded = pd.DataFrame(expanded_rows)

    # Add the original indices to the expanded DataFrame
    df_expanded['original_index'] = indices

    # Merge the expanded rows back to the original DataFrame
    df_final = df.merge(df_expanded, left_index=True, right_on='original_index', how='left')

    # Drop the helper 'original_index' column
    df_final = df_final.drop(columns=['original_index'])
else:
    df_final = df.copy()
df_final.head()


