import pandas as pd

class DataParser:
    """
    Class that holds different strategies for parsing downloaded ETF data.
    Uses metaprogramming to call the named strategy.
    """

    @staticmethod
    def parse_data(parsing_strategy: str, file_path: str) -> pd.DataFrame:
        """Calls the given strategy function in this class """
        strategy = getattr(DataParser, parsing_strategy)
        return strategy(file_path=file_path)

    @staticmethod
    def ssga(file_path: str) -> pd.DataFrame:
        """Strategy for data from SSGA """
        # Read raw file
        df = pd.read_excel(file_path, header=None)

        # The data is in between the first two empty rows
        first_row = df[df.isnull().all(axis=1)].index[0] + 1
        last_row = df[df.isnull().all(axis=1)].index[1]
        df = df.iloc[first_row:last_row]

        # Set header, reset index
        df.columns = df.iloc[0]
        df = df[1:]
        df.reset_index(drop=True, inplace=True)

        return df

