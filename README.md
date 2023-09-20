# ETF Downloader

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
