"""Access to Foresight timeseries data."""

import re
from datetime import datetime, timezone
from json import loads
from typing import Optional
from uuid import UUID

from gql import Client, gql
from pandas import DataFrame, Series, to_datetime


def get_value(
    client: Client, entity_id: UUID, moment: Optional[datetime] = None
) -> float:
    """Retrieve the latest value of a `foresight:Datapoint` entity before a point in time (default=now).

    Parameters
    ----------
    client : Client
        The GQL client to use.
    entity_id : str
        The ID of the entity to retrieve the value for.
    moment : Optional[datetime], optional
        The point in time to retrieve a value for, by default `datetime.now(tz=timezone.utc)`.

    Returns
    -------
    float
        The numeric value at the specified moment.

    Raises
    ------
    RuntimeError
        When the value cannot be retrieved from the server.
    RuntimeError
        When the retrieved value cannot be converted to float.

    """
    if not moment:
        moment = datetime.now(tz=timezone.utc)
    query = gql("""
    query value($entityId: ID!, $eventTime: DateTime) {
        entity(id: $entityId) {
            trait(id: "foresight:Datapoint") {
                quantity(key: "Value") {
                    value(eventTime: $eventTime) {
                        value
                    }
                }
            }
        }
    }
    """)
    variables = {"entityId": entity_id, "eventTime": moment.isoformat()}
    response = client.execute(query, variables)
    try:
        return float(response["entity"]["trait"]["quantity"]["value"]["value"])
    except KeyError:
        raise RuntimeError("Cloud not retrieve value.")
    except ValueError:
        raise RuntimeError(
            f"Could not parse value {response['entity']['trait']['quantity']['value']['value']}"
        )


def get_values(
    client: Client, entity_id: UUID, start: datetime, end: Optional[datetime] = None
) -> Series:
    """Retrieve values of a `foresight:Datapoint` entity for a time range. The most recent value before 'start' is included, 'end' defaults to 'now'.

    Parameters
    ----------
    client : Client
        The GQL client to use.
    entity_id : str
        The ID of the entity to retrieve values for.
    start : datetime
        The starting point in time from which to receive values. Must include timezone info.
        The most recent value before this point is also included in the response.
    end : Optional[datetime], optional
        The end point in time until which to receive values. Must include timezone info. By default `datetime.now(tz=timezone.utc)`.

    Returns
    -------
    Series
        A Pandas Series containing the timestamped values within the specified range.

    Raises
    ------
    ValueError
        When start or end datetimes are not timezone-aware.
    RuntimeError
        When values cannot be retrieved from the server.

    """
    if not end:
        end = datetime.now(tz=timezone.utc)
    if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:
        raise ValueError("The start parameter must be timezone aware.")
    if end.tzinfo is None or end.tzinfo.utcoffset(end) is None:
        raise ValueError("The end parameter must be timezone aware.")
    query = gql("""
    query value($entityId: ID!, $startEventTime: DateTime!, $endEventTime: DateTime!) {
        entity(id: $entityId) {
            name
            trait(id: "foresight:Datapoint") {
                quantity(key: "Value") {
                    values(startEventTime: $startEventTime endEventTime: $endEventTime) {
                        eventTime
                        value
                    }
                }
            }
        }
    }
    """)
    variables = {
        "entityId": entity_id,
        "startEventTime": start.isoformat(),
        "endEventTime": end.isoformat(),
    }
    response = client.execute(query, variables)
    try:
        values = response["entity"]["trait"]["quantity"]["values"]
        name = response["entity"]["name"]
    except KeyError:
        raise RuntimeError("Cloud not retrieve value.")
    frame = DataFrame(values).set_index("eventTime")
    frame.index = to_datetime(frame.index, format="ISO8601")
    frame["value"] = frame["value"].astype(float)
    series = frame["value"]
    series.name = name
    return series


def get_all_values(text: str) -> list[DataFrame]:
    """Extract all pairs of id, name, and values from a graph query and return them as a list of DataFrames.

    The query needs to be of the form:

    ```
    id
    name
    trait(id: "foresight:Datapoint") {
        quantity(key: "Value") {
            values(startEventTime: "2024-10-01T00:00:00Z", endEventTime: "2024-10-02T00:00:00Z") {
                eventTime
                value
            }
        }
    }
    ```

    Parameters
    ----------
    text : str
        The string form of the query, usually `str(fs_client.execute(query))`.
        Must contain id, name, and datapoint values in the expected format.

    Returns
    -------
    list[DataFrame]
        A list of DataFrames, one for each id-name-values combination found in the string.
        Each DataFrame is indexed by timestamp and contains a value column named "{name}|{id}".

    """
    values_regex = re.compile(
        r"'id'\:\s*'([\:\w\s\-_]*?)',\s*'name'\:\s*'([\w\s\-_]*?)',\s*'trait':\s*{'quantity'\:\s*\{'values'\:\s*\[([\{'\w\:\-\s\.\},]*)"
    )
    dfs = []
    for m in values_regex.findall(text):
        eid = m[0].split(":")[-1]
        name = m[1]
        values = f"[{m[2]}]".replace("'", '"')
        df = DataFrame(
            [
                {"ts": v["eventTime"], f"{name}|{eid}": float(v["value"])}
                for v in loads(values)
            ]
        )
        df = df.set_index("ts")
        df.index = to_datetime(df.index, format="ISO8601")
        dfs.append(df)
    return dfs
