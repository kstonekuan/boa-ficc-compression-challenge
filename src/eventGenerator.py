import pandas as pd
import numpy as np

class EventGenerator:

    def get_no_split_trade(self, curr_trades_rec: pd.DataFrame, curr_trades_pay: pd.DataFrame, date: pd.DatetimeIndex, proposal_columns: list):
        proposal = pd.DataFrame(columns=proposal_columns)
        curr_trades_no_split = curr_trades_rec.reset_index().merge(curr_trades_pay.reset_index(), how='inner', on='Notional', suffixes=('_r', '_p'))
        
        if len(curr_trades_no_split) == 0: return [], None, None
        
        trade = curr_trades_no_split.loc[0]
        proposal.loc[0] = [trade['Party_r'], None, None, 'R', curr_trades_rec['Currency'].iat[0], date, trade['Party_p'], None, trade['Notional'], None]
        proposal.loc[1] = [trade['Party_p'], None, None, 'P', curr_trades_pay['Currency'].iat[0], date, trade['Party_r'], None, trade['Notional'], None]
        
        return proposal, trade['index_r'], trade['index_p']

    def get_split_trade(self, rec: pd.DataFrame, pay: pd.DataFrame, date: pd.DatetimeIndex, proposal_columns: list):
        proposal = pd.DataFrame(columns=proposal_columns)
        min_notional = min(rec['Notional'].iat[0], pay['Notional'].iat[0])
        proposal.loc[0] = [rec['Party'].iat[0], None, None, 'R', rec['Currency'].iat[0], date, pay['Party'].iat[0], None, min_notional, None]
        proposal.loc[1] = [pay['Party'].iat[0], None, None, 'P', pay['Currency'].iat[0], date, rec['Party'].iat[0], None, min_notional, None]
        
        return proposal, min_notional

    def get_full_proposal(self, report: pd.DataFrame):

        proposal_columns = ['Party', 'Book', 'TradeID', 'PAY/RECEIVE', 'Currency', 'MaturityDate', 'Cpty', 'CCPTradeID', 'Notional', 'Action']
        new_trades = []

        dates = sorted(report['MaturityDate'].unique())
        for date in dates:
            curr_trades = report[(report['CompressionType'] == 'Partial') & (report['MaturityDate'] == date)].copy()
            curr_trades_rec = curr_trades[curr_trades['PAY/RECEIVE'] == 'R'].copy()
            curr_trades_pay = curr_trades[curr_trades['PAY/RECEIVE'] == 'P'].copy()

            # Check if any trades can be done without splitting
            new_trade, index_r, index_p = self.get_no_split_trade(curr_trades_rec, curr_trades_pay, date, proposal_columns)
            while len(new_trade) == 2:
                new_trades.append(new_trade)
                curr_trades_rec.drop([index_r], inplace=True)
                curr_trades_pay.drop([index_p], inplace=True)
                new_trade, index_r, index_p = self.get_no_split_trade(curr_trades_rec, curr_trades_pay, date, proposal_columns)

            # Split up trades (does not matter how?)
            while len(curr_trades_rec) > 0 and len(curr_trades_pay) > 0:
                index_r = curr_trades_rec.head(1).index
                index_p = curr_trades_pay.head(1).index

                new_trade, minus_amt = self.get_split_trade(curr_trades_rec.loc[index_r], curr_trades_pay.loc[index_p], date, proposal_columns)
                new_trades.append(new_trade)

                curr_trades_rec.loc[index_r, 'Notional'] -= minus_amt
                curr_trades_pay.loc[index_p, 'Notional'] -= minus_amt

                curr_trades_rec = curr_trades_rec[curr_trades_rec['Notional'] != 0]
                curr_trades_pay = curr_trades_pay[curr_trades_pay['Notional'] != 0]
            
            # Can check that pd.concat(new_trades).groupby(['Party']).sum() has same notional as curr_trades for first iteration only

        proposal = pd.concat(new_trades, ignore_index=True)
        return proposal

    def split_party_proposals(self, trades: pd.DataFrame, proposal: pd.DataFrame):
        # Separate into parties
        last_CCPTradeID = max(trades['CCPTradeID'].str[3:].astype(int))
        trades['Action'] = None
        parties = sorted(trades['Party'].unique())
        party_proposals = dict()

        for party in parties:
            proposal_party = proposal[proposal['Party'] == party].copy()
            trades_party = trades[trades['Party'] == party].copy()
            last_TradeID = max(trades_party['TradeID'].str[1:].astype(int))
            proposal_party['Book'] = trades_party['Book'].iat[0]
            
            # Check if any trades need not be canceled
            no_cancel = proposal_party.reset_index().merge(trades_party.reset_index(), how='inner', on=['Notional', 'Cpty', 'MaturityDate', 'PAY/RECEIVE', 'Currency'], suffixes=('_p', '_t'))
            proposal_party.drop(no_cancel['index_p'], inplace=True)
            trades_party.loc[no_cancel['index_t'], 'Action'] = '-None-'
            
            # Set Actions and IDs
            proposal_party['Action'].fillna('ADD', inplace=True)
            numIDs = len(proposal_party)
            proposal_party['TradeID'] = range(last_TradeID + 1, last_TradeID + 1 + numIDs)
            proposal_party['TradeID'] = party + proposal_party['TradeID'].astype(str)
            proposal_party['CCPTradeID'] = range(last_CCPTradeID + 1, last_CCPTradeID + 1 + numIDs)
            proposal_party['CCPTradeID'] = 'CCP' + proposal_party['CCPTradeID'].astype(str)
            last_CCPTradeID += numIDs
            
            trades_party['Action'].fillna('CXL', inplace=True)
            
            party_proposals[party] = pd.concat([proposal_party, trades_party]).sort_values(by=['TradeID'])
        
        return party_proposals