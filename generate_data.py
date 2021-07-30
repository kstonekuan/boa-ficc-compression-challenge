import random
import pandas as pd
import os

if not os.path.exists('mock_input'):
    os.mkdir('mock_input')

class Party:
    def __init__(self, label):
        self.label = label
        self.book = f"1BK{label}"
        self.next_tradeID = 1

    def get_next_tradeID(self):
        id = self.next_tradeID
        self.next_tradeID += 1
        return f'{self.label}{id}'

class CCP:
    def __init__(self):
        self.next_CCPTradeID = 1
        self.currency = 'AUD'
    
    def get_next_CCPTradeID(self):
        id = self.next_CCPTradeID
        self.next_CCPTradeID += 1
        return f'CCP{id}'

try:
    print("*--Generating mock data--*")
    print("Provide number of parties:")
    num_party = int(input())
    if num_party < 2: raise ValueError("Enter at least 2 for parties")
    print("Provide number of trades:")
    num_trades = int(input())
    if num_trades < 1: raise ValueError("Enter at least 1 for trades")
    print("Provide number of maturity dates:")
    num_dates = int(input())
    if num_dates < 1: raise ValueError("Enter at least 1 for dates")
except ValueError as err:
    print(err)

ccp = CCP()
parties = [Party(chr(x + ord('A'))) for x in range(num_party)]
columns = ['Party', 'Book', 'TradeID', 'PAY/RECEIVE', 'Currency', 'MaturityDate', 'Cpty', 'CCPTradeID', 'Notional']
trades = []
dates = [pd.to_datetime('2021-12-31')]
for i in range(1, num_dates):
    dates.append(dates[0] + pd.DateOffset(years=i))

for _ in range(num_trades):
    notional = random.randint(1000, 999999)
    party = random.choice(parties)
    cpty = random.choice(parties)
    while (cpty.label == party.label):
        cpty = random.choice(parties)
    date = random.choice(dates)
    CCPTradeID = ccp.get_next_CCPTradeID()
    
    new_input = pd.DataFrame(columns=columns)
    new_input.loc[0] = [party.label, party.book, party.get_next_tradeID(), 'P', ccp.currency, date, cpty.label, CCPTradeID, notional]
    new_input.loc[1] = [cpty.label, cpty.book, cpty.get_next_tradeID(), 'R', ccp.currency, date, party.label, CCPTradeID, notional]
    trades.append(new_input)

trade_inputs = pd.concat(trades).sort_values(by=['Party', 'TradeID'])
party_a_trades_input_mock = trade_inputs[trade_inputs['Party'] == 'A']
multiparty_trades_input_mock = trade_inputs[trade_inputs['Party'] != 'A']

party_a_trades_input_mock.to_csv('mock_input/party_a_trades_input_mock.csv', index=False)
multiparty_trades_input_mock.to_csv('mock_input/multiparty_trades_input_mock.csv', index=False)
