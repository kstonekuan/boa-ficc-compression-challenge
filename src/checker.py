import pandas as pd
import numpy as np

class Checker:
    
    def get_report(self, party_proposals: dict):
        data_check_columns = ['Party', 'TotalIn', 'TotalOut', 'NetOut', 'Original_Notional', 'Notional', 'Reduced']
        data_check = pd.DataFrame(columns=data_check_columns)
        row = 0

        for party, proposal in party_proposals.items():
            original_trades = proposal[proposal['Action'] != 'ADD']
            total_in = original_trades.loc[original_trades['PAY/RECEIVE'] == 'R', 'Notional'].sum()
            total_out = original_trades.loc[original_trades['PAY/RECEIVE'] == 'P', 'Notional'].sum()
            net_out = total_out - total_in
            original_notional = total_in + total_out
            notional = proposal.loc[proposal['Action'] != 'CXL', 'Notional'].sum()
            reduced = notional <= original_notional
            data_check.loc[row] = [party, total_in, total_out, net_out, original_notional, notional, reduced]
            row += 1

            data_check.loc[row] = ['Total', data_check['TotalIn'].sum(), data_check['TotalOut'].sum(), data_check['NetOut'].sum(), data_check['Original_Notional'].sum(), data_check['Notional'].sum(), None]
            data_check.loc[row, 'Reduced'] = data_check.loc[row, 'Notional'] < data_check.loc[row, 'Original_Notional']

        return data_check
