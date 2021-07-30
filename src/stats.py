import pandas as pd
import numpy as np

def print_stats(party_proposals: dict, data_check: pd.DataFrame):
    print("*------------------------*")    
    print("Final compression results:")

    for party, proposal in party_proposals.items():
        print(f"    Party: {party}")
        old_trades = len(proposal[proposal['Action'] != 'ADD'])
        new_trades = len(proposal[proposal['Action'] != 'CXL'])
        trade_reduction = (old_trades - new_trades) / old_trades * 100
        print(f"        Total trades reduced by {trade_reduction:.2f}% from {old_trades} to {new_trades}")
        old_notional = data_check.loc[data_check['Party'] == party, 'Original_Notional'].iat[0]
        new_notional = data_check.loc[data_check['Party'] == party, 'Notional'].iat[0]
        notional_reduction = (old_notional - new_notional) / old_notional * 100
        print(f"        Total notional reduced by {notional_reduction:.2f}% from {old_notional} to {new_notional}")

    print("*------------------------*")
