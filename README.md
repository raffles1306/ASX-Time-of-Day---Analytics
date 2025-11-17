# ASX-Time-of-Day-Analytics

Toolkit for analysing intraday time-of-day moves in ASX mining stocks.  
Pulls price data in 15-min slots (AWST), screens for decent swings, and spits out stats, Excel reports, and sector dashboards.

## Usage

1. Clone the repo
2. Run the main script  
3. Check out the Excel summaries and PNG dashboard

## Requirements

- Python 3
- pandas, numpy, yfinance, matplotlib, openpyxl

## What it does

- Grabs intraday price data for a bunch of ASX mining stocks  
- Crunches returns and patterns for each time period  
- Highlights best/worst trading windows  
- Makes sector-level and individual summary files

---
