import argparse
import logging
import os
from etf import parse_download, process_downloads
from etf import ETF
from util import create_timecode, load_dataobjects_from_yaml
from util import YAMLLoadException

def initialize_logger(timecode: str,
                      logs_info_path: str,
                      logs_errors_path: str) -> logging.Logger:
    """Initializes logging """

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Info
    info_handler = logging.FileHandler(os.path.join(logs_info_path, timecode))
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Error
    error_handler = logging.FileHandler(os.path.join(logs_errors_path, timecode))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Logger
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger

def setup(data_path: str,
          logs_path: str):
    """Initializes directories and logging """
    
    # Ensure that the directories for saving data and logs exist
    data_raw_path = os.path.join(data_path, "raw")
    data_parsed_path = os.path.join(data_path, "parsed")
    logs_info_path = os.path.join(logs_path, "info")
    logs_errors_path = os.path.join(logs_path, "errors")

    directories = [
        data_path,
        data_raw_path,
        data_parsed_path,
        logs_path,
        logs_info_path,
        logs_errors_path
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Initialize logging
    timecode = create_timecode() # timecode as an ID for this execution
    logger = initialize_logger(
        timecode=timecode,
        logs_info_path=logs_info_path,
        logs_errors_path=logs_errors_path
    )

    return logger, timecode, data_raw_path, data_parsed_path


def run(etf_config_path: str,
        etf_config_schema_path: str,
        data_path: str,
        logs_path: str,
        download_only: bool,
        specified_etfs: set[str]=None):
    """
    Executes a single run of:
    - Read ETF configurations from file
    - Download data and save to files
    - Parse data into CSV files 
    """

    # Run setup
    logger, timecode, data_raw_path, data_parsed_path = setup(data_path=data_path, logs_path=logs_path)
    
    try:
        # Load each ETF definition from the config file
        logger.info("Loading ETF configs from file")
        etfs = load_dataobjects_from_yaml(
            object_class=ETF,
            content_file_path=etf_config_path,
            schema_file_path=etf_config_schema_path
        )
        
        # If explicitly passed as an argument, filter to specified ETFs
        if specified_etfs is not None:
            etfs = [etf for etf in etfs if etf.ticker_symbol in specified_etfs]

        # Run download process for each ETF
        logger.info("Starting ETF processing")
        for etf in etfs:
            logger.info(f"Processing: {etf.ticker_symbol}")

            # Execute downloads
            successes = process_downloads(
                etf=etf,
                timecode=timecode,
                data_raw_path=data_raw_path,
                logger=logger
            )

            # Parse the downloaded files
            if not download_only:
                for success in successes:
                    parse_download(
                        file_path=success["file_path"],
                        output_path=data_parsed_path,
                        parsing_strategy=success["parsing_strategy"],
                        logger=logger
                    )

    except (YAMLLoadException) as e:
        logger.error(str(e))


if __name__ == '__main__':

    # Construct default arguments
    source_dir = os.path.dirname(__file__)
    default_etf_config_path = os.path.join(source_dir, "etf_config.yaml")
    default_etf_config_schema_path = os.path.join(source_dir, "etf_config_schema.json")
    default_data_path = os.path.join(os.path.dirname(source_dir), "data")
    default_logs_path = os.path.join(os.path.dirname(source_dir), "logs")

    # Parse given arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--etf_config_path', type=str, default=default_etf_config_path)
    parser.add_argument('--etf_config_schema_path', type=str, default=default_etf_config_schema_path)
    parser.add_argument('--data_path', type=str, default=default_data_path)
    parser.add_argument('--logs_path', type=str, default=default_logs_path)
    parser.add_argument('--download_only', type=bool, default=False)
    parser.add_argument('--etfs', type=str, nargs="+", default=None)

    args = parser.parse_args()

    # Run script
    run(
        etf_config_path=args.etf_config_path,
        etf_config_schema_path=args.etf_config_schema_path,
        data_path=args.data_path,
        logs_path=args.logs_path,
        download_only=args.download_only,
        specified_etfs=set(args.etfs) if args.etfs is not None else None
    )
