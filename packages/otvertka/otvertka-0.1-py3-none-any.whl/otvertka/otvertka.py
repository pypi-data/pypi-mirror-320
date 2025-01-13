from os import getenv
from typing import List, Tuple

import clickhouse_connect
import pandas as pd
import pendulum
from pingouin import print_table as pt


def fetch_data(sql_query: str) -> pd.DataFrame:
    """
    Execute a SQL query against a ClickHouse database and return the result as a DataFrame.

    This function connects to a ClickHouse database using the specified connection parameters,
    executes the provided SQL query, and returns the results as a pandas DataFrame. The shape
    of the resulting DataFrame is printed to the console.

    Parameters
    ----------
    sql_query : str
        The SQL query to be executed against the ClickHouse database.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the result set of the executed SQL query.

    Raises
    ------
    ValueError
        If required environment variables (CH_USER, CH_PASSWORD) are not set.
    """
    user = getenv('CH_USER')
    if user is None:
        raise ValueError('CH_USER not set')

    password = getenv('CH_PASSWORD')
    if password is None:
        raise ValueError('CH_PASSWORD not set')

    host = getenv('CH_HOST', 'localhost')  # default to localhost if not set
    port = getenv('CH_PORT', '8123')  # default ClickHouse HTTP port

    client = clickhouse_connect.get_client(
        host=host,
        port=port,
        user=user,
        password=password,
        connect_timeout=100,
        send_receive_timeout=1000,
    )

    df = client.query_df(
        query=sql_query,
        encoding="utf-8",
        use_none=True,
        use_na_values=True,
        use_extended_dtypes=True,
    )

    print(df.shape)

    return df


def get_table_info(table_name: str) -> pd.DataFrame:
    """
    Retrieve and display information about a table in the 'default' database.

    This function fetches and displays the partition key information and column
    descriptions for the specified table in the 'default' database. It first queries
    the `system.tables` table to get the partition key of the table and then queries
    the table structure using the `describe table` command. The results are displayed
    and returned as a pandas DataFrame.

    Parameters
    ----------
    table_name : str
        The name of the table for which information is to be retrieved.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the description of the table's columns, including their
        names and types, sorted by type and name.
    """
    q_partition = f"""select table, partition_key from system.tables where database = 'default' and table = '{table_name}' """
    df_partition = fetch_data(q_partition)
    pt(df_partition)
    q_describe = f"""describe table {table_name}"""
    df_describe = fetch_data(q_describe)
    df_describe = df_describe[["name", "type"]].sort_values(by=["type", "name"])
    pt(df_describe)


def get_dates_tuples(
    start_date: str, end_date: str, days_interval: int = 15
) -> List[Tuple[str, str]]:
    """
    Splits the date range between start_date and end_date into periods of specified length.

    Args:
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        days_interval (int, optional): Number of days in each period. Defaults to 15.

    Returns:
        List[Tuple[str, str]]: A list of tuples with start and end dates of each period.
    """
    start = pendulum.parse(start_date)
    end = pendulum.parse(end_date)

    date_ranges: List[Tuple[str, str]] = []
    current_date = start

    while current_date <= end:
        period_start = current_date
        period_end = min(current_date.add(days=days_interval - 1), end)
        date_ranges.append((period_start.to_date_string(), period_end.to_date_string()))

        # Move to the next period
        current_date = period_end.add(days=1)

    return date_ranges
