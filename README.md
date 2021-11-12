# Zero Hash stream challenge

This project is meant to gather real-time data from coinbase and calculate VWAP value for specific pairs of cypto-currency.

The Vwap class' methods are well documented and self-explanatory

## Requirements

- python 3.9+ recommended
- Install libraries in requirements.txt

## How to use it

Just run the main.py file, and you will get streamed VWAP values on your console output.

Tests can be run with "pytest tests --cov=app --cov-report term-missing" command.

## Features

- 100% test coverage on the class Vwap.
- Aims to use the most efficient implementation possible for gathering and streaming the data.
- List of coin pairs to be calculated can be customized at the class' instantiation.
- Could be run asynchronously with other future modules.