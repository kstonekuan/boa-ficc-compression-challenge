# Bank of America FICC Code to Connect 2021 Trade compression

Challenge is to compress a list of multiple trades between parties to get the least number of trades between all parties.

## Usage

Place input files into `input` folder.

Run one testcase X directly from python file:

```bash
python3 main.py X
```

Or run multiple testcases from X to Y (both inclusive) using shell script:

```bash
sh run.sh -s X -e Y
```

## Generating mock data

First run the generator, e.g.:

```bash
python3 generate_data.py
*--Generating mock data--*
Provide number of parties:
5
Provide number of trades:
100
Provide number of maturity dates:
3
```

Files will be generated in `mock_input` folder. Move them to `input` folder in order to run program on this input.

```bash
python3 main.py mock
```