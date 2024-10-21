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

#transform dataframe, drop columns which we don't need anymore for further computation. fill missing values
def transform_dataframe(df_final):
  df_final = df_final.drop(columns=['contracts', 'parsed_contracts'])
  df_final = df_final.drop_duplicates().reset_index(drop=True)
  df_final['contract_date'] = df_final['contract_date'].apply(lambda x: pd.to_datetime(x) if x is not None else None)
  df_final['summa'] = df_final['summa'].replace("", None)
  df_final['claim_date'] = pd.to_datetime(df_final['claim_date'])
  df_final['loan_summa'] = df_final['loan_summa'].replace("", 0)

  return df_final
df_final = transform_dataframe(df_final)
df_final.head()


