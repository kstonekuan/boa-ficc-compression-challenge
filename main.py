from src.checker import Checker
from src.eventGenerator import EventGenerator
from src.db import DB
from src.compressionEngine import CompressionEngine
from src.utilities import get_testcase
from src.stats import print_stats
import time
import os

def main():
    if not os.path.exists('output'):
        os.makedirs('output/party_proposals')
        os.makedirs('output/compression_reports/party_level')
        os.makedirs('output/compression_reports/book_level')
        os.makedirs('output/exclusions')
        os.makedirs('output/data_checks')
        os.makedirs('output/temp')

    X = get_testcase()
    db = DB('input', 'output')
    try:
        party_a_trades_input = db.load(f'party_a_trades_input_{X}.csv')
        multiparty_trades_input = db.load(f'multiparty_trades_input_{X}.csv')
    except:
        print(f"Missing inputs for testcase {X}. Ensure they are in the input folder and named: party_a_trades_input_{X}.csv, multiparty_trades_input_{X}.csv")
        exit(1)

    # Compression
    time_start = time.time()
    compressionEngine = CompressionEngine()
    trades, exclusion = compressionEngine.get_valid_trades(party_a_trades_input, multiparty_trades_input)
    db.save(trades, f'temp/trades_{X}.csv')
    db.save(exclusion, f'exclusions/exclusion_{X}.csv')
    compressionEngine.run_compression(trades.copy())
    report = compressionEngine.get_report(trades.copy(), False)
    db.save(report, f'compression_reports/party_level/compression_report_{X}.csv')
    report_book = compressionEngine.get_report(trades.copy(), True)
    db.save(report_book, f'compression_reports/book_level/compression_report_bookLevel_{X}.csv')
    time_compression = time.time()
    print(f"Compression Engine completed in {time_compression-time_start:.2f} seconds.")

    # Proposal
    eventGenerator = EventGenerator()
    proposal = eventGenerator.get_full_proposal(report.copy())
    db.save(proposal, f'temp/full_proposal_{X}.csv')
    party_proposals = eventGenerator.split_party_proposals(trades.copy(), proposal.copy())
    for k, v in party_proposals.items():
        db.save(v, f'party_proposals/party_{k}_proposal_{X}.csv')
    time_proposal = time.time()
    print(f"Event Generator completed in {time_proposal-time_compression:.2f} seconds.")

    # Data Check
    checker = Checker()
    data_check = checker.get_report(party_proposals.copy())
    db.save(data_check, f'data_checks/data_check_{X}.csv')
    time_check = time.time()
    print(f"Checker completed in {time_check-time_proposal:.2f} seconds.")

    # Stats
    print_stats(party_proposals.copy(), data_check.copy())

if __name__ == "__main__":
    main()