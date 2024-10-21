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
    
# Parse the 'contracts' column
df['parsed_contracts'] = df['contracts'].apply(parse_contracts)
df.head()




