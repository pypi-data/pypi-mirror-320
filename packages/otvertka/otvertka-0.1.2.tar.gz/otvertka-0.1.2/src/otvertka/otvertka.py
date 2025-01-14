from os import getenv
from typing import List, Optional, Tuple

import clickhouse_connect
import numpy as np
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
    user = getenv("CH_USER")
    if user is None:
        raise ValueError("CH_USER not set")

    password = getenv("CH_PASSWORD")
    if password is None:
        raise ValueError("CH_PASSWORD not set")

    host = getenv("CH_HOST", "localhost")  # default to localhost if not set
    port = getenv("CH_PORT", "8123")  # default ClickHouse HTTP port

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


def generate_ab_test_data(
    group_names: list,
    num_observations_per_group: int,
    effect_size: float,
    base_retention_prob: float = 0.3,
    base_impressions_mean: float = 4,
    base_revenue_scale: float = 1.0,
) -> pd.DataFrame:
    """
    Generates a DataFrame with test data for A/B testing with specified parameters.

    Parameters
    ----------
    group_names : list
        A list of group names. The first group is treated as the control group, and the rest as test groups.
    num_observations_per_group : int
        The number of observations (rows) for each group.
    effect_size : float
        The effect size to be applied to the metrics within each test group.
        For retention, this is an absolute difference in probability points.
        For other metrics, this is used to adjust the means relative to control group.
    base_retention_prob : float, optional
        The base retention probability for the control group (default is 0.3).
    base_impressions_mean : float, optional
        The base mean for the impressions metric in the control group (default is 4).
    base_revenue_scale : float, optional
        The base scale for the revenue metric in the control group (default is 1.0).

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the generated test data with columns:
        - 'ab_group': The A/B group label (e.g., 'control', 'test_1', 'test_2').
        - 'geo': The geographic location ('US', 'GB', 'GE').
        - 'platform': The platform ('iOS', 'Android').
        - 'retention': The retention metric (1 or 0).
        - 'revenue': The revenue metric, following an exponential distribution.
        - 'impressions': The impressions metric, following a normal distribution with integer values.
        - 'install_date': The installation date (datetime), distributed between 4 and 2 weeks ago.

    Notes
    -----
    - The 'geo' column is distributed with 50% 'US', 25% 'GB', and 25% 'GE' for each group.
    - The 'platform' column is distributed with 30% 'iOS' and 70% 'Android' for each group.
    - For retention, effect size is applied as absolute difference in probability points.
    - For other metrics, effect size is applied multiplicatively relative to control group.
    - Install dates are distributed between 4 and 2 weeks ago from the current date.
    - The number of observations per date varies randomly by ±10% from the average.
    """
    if not group_names or len(group_names) < 2:
        raise ValueError(
            "group_names must contain at least two elements: one control group and one or more test groups."
        )

    today = pd.Timestamp.now().normalize()
    date_range = pd.date_range(
        end=today - pd.Timedelta(days=14), start=today - pd.Timedelta(days=28), freq="D"
    )

    geo_choices = ["US", "GB", "GE"]
    geo_probs = [0.5, 0.25, 0.25]
    platform_choices = ["iOS", "Android"]
    platform_probs = [0.3, 0.7]

    data = []
    num_dates = len(date_range)

    np.random.seed(42)

    for group in group_names:
        group_index = group_names.index(group)

        retention_prob = base_retention_prob + (effect_size * group_index)

        adjusted_effect = np.log(1 + effect_size)
        impressions_mean = base_impressions_mean * np.exp(adjusted_effect * group_index)
        revenue_scale = base_revenue_scale * np.exp(adjusted_effect * group_index)

        observations_per_date = np.zeros(num_dates, dtype=int)
        remaining = num_observations_per_group

        for i in range(num_dates - 1):
            base_count = remaining // (num_dates - i)
            variation = int(base_count * np.random.uniform(-0.1, 0.1))
            count = min(base_count + variation, remaining)
            observations_per_date[i] = count
            remaining -= count
        observations_per_date[-1] = remaining

        for date, num_obs in zip(date_range, observations_per_date):
            geos = np.random.choice(geo_choices, size=num_obs, p=geo_probs)
            platforms = np.random.choice(platform_choices, size=num_obs, p=platform_probs)
            retentions = np.random.binomial(1, retention_prob, size=num_obs)

            revenues = np.random.exponential(revenue_scale, size=num_obs)
            impressions = np.maximum(
                0,
                np.random.normal(impressions_mean, impressions_mean * 0.1, size=num_obs).astype(
                    int
                ),
            )

            data.extend(
                [
                    [group, geo, platform, retention, revenue, impression, date]
                    for geo, platform, retention, revenue, impression in zip(
                        geos, platforms, retentions, revenues, impressions
                    )
                ]
            )

    return pd.DataFrame(
        data,
        columns=[
            "ab_group",
            "geo",
            "platform",
            "retention",
            "revenue",
            "impressions",
            "install_date",
        ],
    )[["install_date", "ab_group", "geo", "platform", "retention", "revenue", "impressions"]]


def handle_outliers(
    df: pd.DataFrame,
    target_column: str,
    threshold_quantile: float = 0.995,
    handling_method: str = "replace_max",
    grouping_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Handle outliers in a specified column based on quantile thresholds.

    This function identifies and handles outliers in the specified `target_column` of the
    DataFrame by calculating a threshold value based on the given quantile. Depending on
    the chosen handling method, outliers can be replaced with the threshold value,
    the median value, or removed entirely. Outliers can be processed either globally
    or within groups defined by `grouping_column`.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data to be processed.
    target_column : str
        The name of the column where outliers should be identified and handled.
    threshold_quantile : float, optional
        The quantile value used to define the outlier threshold. Values above this
        quantile are considered outliers. Default is 0.995.
    handling_method : str, optional
        The method used to handle outliers. Can be one of:
        - "replace_max": Replace outliers with the threshold value
        - "replace_median": Replace outliers with the median value
        - "drop": Remove rows containing outliers
        Default is "replace_max".
    grouping_column : str, optional
        Column name to use for grouped processing. If provided, outliers will be
        handled separately within each group. Default is None.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with outliers handled according to the specified method.

    Raises
    ------
    ValueError
        If an invalid handling_method is provided.
    """
    # Return early if binary metric
    if df[target_column].isin([0, 1]).all():
        print("Binary metrics don't support outlier handling")
        return df.copy()

    # Validate handling method
    valid_handling_methods = {"replace_max", "replace_median", "drop"}
    if handling_method not in valid_handling_methods:
        raise ValueError(f"handling_method must be one of: {valid_handling_methods}")

    processed_df = df.copy()

    if grouping_column:
        processed_groups = []
        for group_value in df[grouping_column].unique():
            # Extract current group data
            group_mask = df[grouping_column] == group_value
            current_group = df.loc[group_mask].copy()

            # Calculate threshold and identify outliers
            threshold_value = current_group[target_column].quantile(threshold_quantile)
            outliers_mask = current_group[target_column] > threshold_value

            # Handle outliers based on specified method
            if handling_method == "replace_max":
                current_group.loc[outliers_mask, target_column] = threshold_value
            elif handling_method == "replace_median":
                current_group.loc[outliers_mask, target_column] = current_group[
                    target_column
                ].median()
            elif handling_method == "drop":
                current_group = current_group[~outliers_mask]

            processed_groups.append(current_group)

        processed_df = pd.concat(processed_groups, axis=0)
    else:
        # Process entire dataset without grouping
        threshold_value = df[target_column].quantile(threshold_quantile)
        outliers_mask = processed_df[target_column] > threshold_value

        if handling_method == "replace_max":
            processed_df.loc[outliers_mask, target_column] = threshold_value
        elif handling_method == "replace_median":
            processed_df.loc[outliers_mask, target_column] = processed_df[target_column].median()
        elif handling_method == "drop":
            processed_df = processed_df[~outliers_mask]

    return processed_df
