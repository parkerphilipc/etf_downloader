# ETF Downloader

## Running Script
```
python main.py
```

flags:
- `--etf_config_path` (optional, default=`.`):
  - Path to `.yaml` file that specifies ETFs
- `--etf_config_schema_path` (optional, default=`.`):
  - Path to `.json` file that specifies the ETF `.yaml` file format
- `--data_path` (optional, default=`./data`):
  - Path to the directory to save data
- `--logs_path` (optional, default=`./logs`):
  - Path to the directory to save logs
- `--download_only` (optional, default=`False`):
  - Whether to only download and not parse ETF data
- `--etfs` (optional, defaults to all):
  - Explicitly only process the list of ETFs with these ticker symbols

## `etf_config.yaml`

- List of ETFs to download
- Supports multiple data sources for each ETF. All will be downloaded.


```
- name: name of ETF
  ticker_symbol: ticker symbol of ETF
  data_sources:
    - source_id: unique identifier to use for this data source
      url: url of the file
      parsing_strategy: parsing strategy to use to parse file. see: `source/parsing.py`
```

Example:
```
- name: "SPDR® S&P 500® ETF Trust"
  ticker_symbol: "SPY"
  data_sources:
    - source_id: "ssga"
      url: "https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx"
      parsing_strategy: "ssga"
```