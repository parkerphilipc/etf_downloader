from datetime import datetime
import json
import jsonschema
from pytz import timezone
import requests
from requests.adapters import HTTPAdapter
from typing import Type
from urllib3.util import Retry
import yaml


class YAMLLoadException(Exception):
    """An exception for failing to load YAML data """

    def __init__(self, message):
        super().__init__(message)


def create_timecode() -> str:
    """Creates a string of the current time """
    return datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d-%H-%M')


def download_file(url: str,
                  num_retries=3) -> requests.models.Response:
    """Downloads a file from a URL with retries """

    # Specify retry strategy
    retry_strategy = Retry(
        total=num_retries,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    with requests.Session() as session:

        session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

        response = session.get(url)
        response.raise_for_status()

    return response


def load_dataobjects_from_yaml(object_class: Type[any],
                               content_file_path: str,
                               schema_file_path: str) -> list:
    """Loads a list of dataclass objects from a YAML file """
    try:
        # Load content from yaml file
        with open(content_file_path, "r") as content_file:
            content = yaml.safe_load(content_file)
        
        # Load schema of yaml file in order to validate
        with open(schema_file_path, "r") as schema_file:
            schema = json.load(schema_file)

        # Validate schema
        jsonschema.validate(instance=content, schema=schema)

        # Populate data objects
        data_objects = [object_class(**item) for item in content]

    except (FileNotFoundError,
            yaml.YAMLError,
            jsonschema.exceptions.ValidationError) as e:
        raise YAMLLoadException(message=str(e))

    return data_objects
