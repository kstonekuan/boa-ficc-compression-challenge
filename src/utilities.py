import sys

def get_testcase():
    try:
        X = sys.argv[1]
        return X
    except:
        print("Please provide a testcase")
        exit(1)