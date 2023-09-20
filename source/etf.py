import logging
import os
from dataclasses import dataclass
from parsing import DataParser
from util import download_file


@dataclass
class ETF:
    """A representation of an ETF """
    name: str
    ticker_symbol: str
    data_sources: list
    

def create_data_parsed_filename(raw_filename: str, file_extension: str) -> str:
    """Creates filename for parsed data file """
    base_filename = os.path.basename(raw_filename)
    raw_filename_no_ext = "".join(base_filename.split(".")[:-1])
    return f"{raw_filename_no_ext}.{file_extension}"


def create_data_raw_filename(timecode: str,
                             ticker_symbol: str,
                             source_id: str,
                             file_extension: str) -> str:
    """Creates filename for raw data file """
    return f"{timecode}_{ticker_symbol}_{source_id}.{file_extension}"


def parse_download(file_path: str,
                   output_path: str,
                   parsing_strategy: str,
                   logger: logging.Logger):
    """Parses a raw downloaded file into a CSV according to a given strategy """
    if parsing_strategy != "":
        try:
            # Parse raw file into dataframe
            logger.info(f"Parsing file: {file_path}")
            parsed_data = DataParser.parse_data(
                parsing_strategy=parsing_strategy,
                file_path=file_path
            )

            # Write out dataframe to CSV
            output_filename = create_data_parsed_filename(
                raw_filename=file_path,
                file_extension="csv"
            )
            output_file_path = os.path.join(output_path, output_filename)
            logger.info(f"Writing file: {output_file_path}")
            output_params = {
                "sep": ",",
                "header": True,
                "index": False,
                "date_format": "%Y-%m-%d",
                "quotechar": '"',
            }
            parsed_data.to_csv(output_file_path, **output_params)

        except Exception as e:
            logger.error(str(e))


def process_downloads(etf: ETF,
                      timecode: str,
                      data_raw_path: str,
                      logger: logging.Logger) -> list[dict]:
    """Downloads each source data file for a given ETF """

    successes = []

    # Iterate over each data source for the ETF
    for data_source in etf.data_sources:

        url = data_source["url"]
        source_id = data_source["source_id"]

        try:
            # Download
            logger.info(f"Downloading data source: {url}")
            response = download_file(url=url)
            
            # Save raw file
            file_extension = url.split(".")[-1] if "." in url else ""
            filename = create_data_raw_filename(
                timecode=timecode,
                ticker_symbol=etf.ticker_symbol,
                source_id=source_id,
                file_extension=file_extension
            )
            file_path = os.path.join(data_raw_path, filename)

            logger.info(f"Writing file: {file_path}")
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Record download success
            successes.append(
                {
                    "file_path": file_path,
                    "parsing_strategy": data_source["parsing_strategy"]
                }
            )

        except Exception as e:
            logger.error(str(e))

    return successes
