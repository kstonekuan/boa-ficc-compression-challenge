import pandas as pd
import numpy as np

class CompressionEngine:

    def get_valid_trades(self, party_a_trades_input: pd.DataFrame, multiparty_trades_input: pd.DataFrame):
        # Consolidate all trades
        party_a_trades_input['MaturityDate'] = pd.to_datetime(party_a_trades_input['MaturityDate'], infer_datetime_format=True)
        multiparty_trades_input['MaturityDate'] = pd.to_datetime(multiparty_trades_input['MaturityDate'], infer_datetime_format=True)
        trades = pd.concat([party_a_trades_input, multiparty_trades_input])

        # Only the trades (identified by the same CCPTradeID) that are submitted by both parties should be included in the compression.
        valid_ids = trades[trades['CCPTradeID'].duplicated()]['CCPTradeID']
        exclusion = trades[~trades['CCPTradeID'].isin(valid_ids)].sort_values(by='CCPTradeID').reset_index(drop=True)

        trades = trades[trades['CCPTradeID'].isin(valid_ids)]

        return trades, exclusion

    def run_compression(self, trades: pd.DataFrame):
        # Set notionals to pay as negative
        trades.loc[trades['PAY/RECEIVE'] == 'P', 'Notional'] *= -1

        # Compress trades by summing
        self.compressed_trades = trades.groupby(['Party', 'MaturityDate', 'Currency']).sum().reset_index() # Use this for midway sanity check compressed_trades.groupby(["Party"]).sum()

        # Set notional back to positive
        self.compressed_trades.loc[self.compressed_trades['Notional'] > 0, 'PAY/RECEIVE'] = 'R'
        self.compressed_trades.loc[self.compressed_trades['Notional'] < 0, 'PAY/RECEIVE'] = 'P'
        self.compressed_trades['Notional'] = np.abs(self.compressed_trades['Notional'])

        # Keep first books for book level report
        self.first_books = trades[['Party', 'Book']].groupby(['Party']).first()

    def get_report(self, trades: pd.DataFrame, book_level: bool):
        # Generate compression report

        # Based on book_level flag
        if book_level:
            report_columns = ['Party', 'Book', 'Currency', 'MaturityDate', 'PAY/RECEIVE', 'CompressionType', 'Original_Notional', 'Notional', 'CompressionRate']
            merge_columns = ['Party', 'Book', 'Currency', 'MaturityDate', 'PAY/RECEIVE']
            group_columns = ['Party', 'Book', 'PAY/RECEIVE','MaturityDate', 'Currency']
            sort_columns = ['Party', 'Book', 'Currency', 'MaturityDate', 'PAY/RECEIVE']
            if 'Book' not in self.compressed_trades.columns: self.compressed_trades = self.compressed_trades.merge(self.first_books, on=['Party'])
        else:
            report_columns = ['Party', 'Currency', 'MaturityDate', 'PAY/RECEIVE', 'CompressionType', 'Original_Notional', 'Notional', 'CompressionRate']
            merge_columns = ['Party', 'Currency', 'MaturityDate', 'PAY/RECEIVE']
            group_columns = ['Party', 'PAY/RECEIVE','MaturityDate', 'Currency']
            sort_columns = ['Party', 'Currency', 'MaturityDate', 'PAY/RECEIVE']
            if 'Book' in self.compressed_trades.columns: del self.compressed_trades.columns
        
        group_trades = trades.groupby(group_columns).sum().reset_index()
        report = pd.concat([pd.DataFrame(columns=report_columns), group_trades])
        report[['Original_Notional', 'Notional']] = report[['Notional', 'Original_Notional']]
        report = report.merge(self.compressed_trades, on=merge_columns, how='left', suffixes=['_old', None])
        del report['Notional_old']
        report['Notional'].fillna(0, inplace=True)
        report['Notional'] = report['Notional'].astype(int)
        CompressionRate = ((report['Original_Notional'] - report['Notional']) / report['Original_Notional'] * 100).astype(float).round(2)
        report['CompressionRate'] = CompressionRate.astype(str) + "%"
        report.loc[CompressionRate == 100, 'CompressionType'] = 'Termination'
        report['CompressionType'].fillna('Partial', inplace=True)
        report = report[report_columns]

        return report.sort_values(by=sort_columns)
