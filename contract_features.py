import pandas as pd
import json
from datetime import datetime

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

 
#count number of claims for last 180 days under feature name tot_claim_cnt_l180d
def calc_tot_claim_cnt_l180d(df):
    num_claims = df.copy()
    last_180 = datetime.today() - pd.DateOffset(days=180)
    num_claims = num_claims[num_claims['claim_date'] >= last_180]
    num_claims = num_claims.groupby(by='claim_date').agg({"claim_id":'count'}).reset_index().rename(columns={'claim_id':'tot_claim_cnt_l180d'})
    return num_claims

#dataframe of claims for last 180 days
num_claims = calc_tot_claim_cnt_l180d(df_final)

#now merge with base dataframe
df_final = df_final.merge(num_claims, on='claim_date', how='left')
df_final['tot_claim_cnt_l180d'] = df_final['tot_claim_cnt_l180d'].fillna(-3)

#sum of loans but without tbc loans
def calc_disb_bank_loan_wo_tbc(df):
  loan_summa_df = df.copy()
  loan_summa_df = loan_summa_df[~
    (
      (loan_summa_df['bank'].isna())
      |
      (loan_summa_df['bank'].isin(['LIZ', 'LOM', 'MKO', 'SUG']))
      |
      (loan_summa_df['contract_date'].isna())
    )
  ]
  sum_of_loan_summa = loan_summa_df.groupby(by='claim_date').agg({"loan_summa":'sum'}).reset_index().rename(columns={'loan_summa':'disb_bank_loan_wo_tbc'})
  return sum_of_loan_summa

sum_of_loan_summa = calc_disb_bank_loan_wo_tbc(df_final)
df_final = df_final.merge(sum_of_loan_summa, on='claim_date', how='left')
df_final['disb_bank_loan_wo_tbc'] = df_final['disb_bank_loan_wo_tbc'].fillna(-3)
df_final.head()