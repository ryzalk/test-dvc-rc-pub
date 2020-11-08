import os
import yaml
import pandas as pd


def main():

    with open('test-params.yaml', 'r') as curr_file:
        config = yaml.safe_load(curr_file)
    orig_data = pd.read_csv('titanic.csv')
    sliced_data = orig_data[:config['num_rows']]
    sliced_data.to_csv('sliced_data.csv')


if __name__ == "__main__":
    main()