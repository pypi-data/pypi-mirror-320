from typing import Any, Dict, List, TypedDict, Type
import re
import requests
import pandas as pd
import logging

MAX_LIMIT = 9999999

logging.basicConfig(level=logging.INFO)

def parse_mud_config(file_path: str):
    with open(file_path, "r") as f:
        content = f.read()
    
    # Extract tables and schemas
    table_pattern = r"(\w+):\s*{\s*schema:\s*{([^}]+)},\s*key:\s*\[([^]]+)]"
    matches = re.findall(table_pattern, content)

    tables = {}
    for table_name, schema_block, keys in matches:
        schema = {
            k.strip(): v.strip().strip('"')
            for k, v in re.findall(r"(\w+):\s*\"?(\w+\[\]?|\w+)\"?", schema_block)
        }
        keys = [k.strip().strip('"') for k in keys.split(",")]
        tables[table_name] = {"schema": schema, "key": keys}

    return tables


class BaseTable:
    RESERVED_SQL_KEYWORDS = {"exists", "from", "values", "limit", "index"}

    def __init__(self, sdk, table_name, schema, keys):
        self.sdk = sdk
        self.table_name = table_name
        self.schema = schema
        self.keys = keys

    def _escape_column_name(self, column_name):
        """Escape column names that are reserved SQL keywords."""
        return f'"{column_name}"' if column_name in self.RESERVED_SQL_KEYWORDS else column_name

    def get(self, limit=1000, **filters):
        """
        Query the table with optional filters.

        Args:
            limit (int): Maximum number of rows to retrieve. Default is 1000.
            **filters: Key-value pairs to filter the query.

        Returns:
            List[Dict[str, Any]]: A list of records from the table.
        """
        select_columns = ", ".join(self.schema.keys())
        where_clause = " AND ".join(
            f"{self._escape_column_name(key)}={repr(value)}" for key, value in filters.items()
        )
        query = f"SELECT {select_columns} FROM {self.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += f" LIMIT {limit};"

        payload = [{"address": self.sdk.world_address, "query": query}]
        response = self.sdk.post(payload)
        return self._parse_response(response)

    def _parse_response(self, response):
        if "result" not in response or not response["result"]:
            return None  # Return None if there are no results
        results = response["result"][0]
        if not results:  # Check if the results array is empty
            return None
        headers, *rows = results
        return [dict(zip(headers, row)) for row in rows]

    
    def to_dataframe(self, limit=MAX_LIMIT, **filters):
        """
        Downloads the table and converts it to a Pandas DataFrame.

        Args:
            limit (int): Maximum number of rows to retrieve. Default is MAX_LIMIT.
            **filters: Key-value pairs to filter the query.

        Returns:
            pd.DataFrame: A DataFrame containing the table data.
        """
        rows = self.get(limit=limit, **filters)
        return pd.DataFrame(rows)

class TableRegistry:
    def __init__(self, sdk):
        self.sdk = sdk
        self.SOLIDITY_TO_PYTHON_TYPE = self._generate_solidity_to_python_type_map()

    @staticmethod
    def _generate_solidity_to_python_type_map():
        """
        Generate a mapping of all Solidity integer types to Python int.
        """
        solidity_types = {}
        for bits in range(8, 257, 8):
            solidity_types[f"int{bits}"] = int
            solidity_types[f"uint{bits}"] = int
        solidity_types.update({"bool": bool, "address": str, "string": str, "bytes32": bytes, "bytes": bytes})
        return solidity_types

    def register_table(self, table_name, schema, keys):
        schema_typed_dict = TypedDict(
            f"{table_name}Schema",
            {k: self.SOLIDITY_TO_PYTHON_TYPE.get(v, Any) for k, v in schema.items()}
        )

        def get(self, limit=1000, **filters):
            """
            Query the table with optional filters.

            Args:
                limit (int): Maximum number of rows to retrieve. Default is 1000.
                **filters: Key-value pairs to filter the query.

            Returns:
                List[Dict[str, Any]]: A list of records from the table.
            """
            select_columns = ", ".join(self._escape_column_name(col) for col in self.schema.keys())
            where_clause = " AND ".join(
                f"{self._escape_column_name(key)}={repr(value)}" for key, value in filters.items()
            )
            query = f"SELECT {select_columns} FROM {self.table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            query += f" LIMIT {limit};"

            payload = [{"address": self.sdk.world_address, "query": query}]
            response = self.sdk.post(payload)
            return self._parse_response(response)

        table_class = type(table_name, (BaseTable,), {"get": get})
        table_instance = table_class(self.sdk, table_name, schema, keys)
        setattr(self, table_name, table_instance)


class MUDIndexerSDK:
    def __init__(self, indexer_url, world_address, mud_config_path):
        self.indexer_url = indexer_url
        self.world_address = world_address
        self.tables = TableRegistry(self)
        self._parsed_tables = parse_mud_config(mud_config_path)
        for table_name, table_info in self._parsed_tables.items():
            self.tables.register_table(table_name, table_info["schema"], table_info["key"])

    def post(self, payload):
        response = requests.post(self.indexer_url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")
        return response.json()

    def get_table_names(self):
        return list(self._parsed_tables.keys())


class MUDIndexerSDK:
    def __init__(self, indexer_url, world_address, mud_config_path):
        self.indexer_url = indexer_url
        self.world_address = world_address
        self.tables = TableRegistry(self)
        self._parsed_tables = parse_mud_config(mud_config_path)
        for table_name, table_info in self._parsed_tables.items():
            self.tables.register_table(table_name, table_info["schema"], table_info["key"])

    def post(self, payload):
        response = requests.post(self.indexer_url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")
        return response.json()

    def get_table_names(self):
        return list(self._parsed_tables.keys())

    def dl_tables_as_dataframes(self):
        """
        Downloads all tables from the indexer and returns them as a dictionary of Pandas DataFrames.

        Returns:
            dict: A dictionary where each key is a table name, and the value is a Pandas DataFrame.
        """
        table_names = self.get_table_names()
        table_dataframes = {}

        for table_name in table_names:
            try:
                logging.info(f"Downloading table: {table_name}")

                # Fetch all rows in a single call
                rows = self.tables.__getattribute__(table_name).get(limit=9999999)

                if rows:
                    # Convert rows to a DataFrame and store in the dictionary
                    table_dataframes[table_name] = pd.DataFrame(rows)
                else:
                    logging.warning(f"No data found for table {table_name}.")
                    table_dataframes[table_name] = pd.DataFrame()  # Empty DataFrame for consistency

            except Exception as e:
                logging.error(f"Failed to download table {table_name}: {str(e)}")
                table_dataframes[table_name] = pd.DataFrame()  # Empty DataFrame on error

        return table_dataframes
