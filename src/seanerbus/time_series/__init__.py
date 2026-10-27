# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from ..client import Connection
from ..msg import Aggregate, HistoryReqV1, HistoryResV1, History, msg_capnp, ErrorResV1
from ..naming import resolve


async def get_aggregate(
    conn: Connection,
    entity: str,
    start_time: int,
    end_time: int,
    interval_max: int = 0,
) -> Aggregate:
    """Get one aggregate value over the time interval [start_time, end_time]

    :param entity: Entity of the metric to query
    :param start_time: Start of the interval
    :param end_time: End of the interval
    :param interval_max: TODO: Document. Leave on 0 for now"""
    db_entity = await resolve(conn, {"service": "time_series_db"})

    if not db_entity:
        raise RuntimeError("Time-series Database is not online!")

    db_entity = str(db_entity[0])

    handle = await conn.request(
        db_entity,
        HistoryReqV1(
            entity, start_time, end_time, interval_max, "aggregate"
        ).to_capnp(),
    )

    response = await handle()
    if response.payload_type_as_int() == msg_capnp.MessageTypes.errorResV1:
        err = ErrorResV1.from_capnp(response)
        raise RuntimeError("Could not get History Aggregate: " + err.what)

    res = HistoryResV1.from_capnp(response)

    if res.hist.type == "aggregate":
        return res.hist.aggr[0]
    else:
        raise RuntimeError("Requested an aggregate, got raw values instead!")


async def get_timeline(
    conn: Connection,
    entity: str,
    start_time: int,
    end_time: int,
    interval_max: int = 0,
) -> History:
    """Get a timeline of historic metric data over the time interval [start_time, end_time]

    :param entity: Entity of the metric to query
    :param start_time: Start of the interval
    :param end_time: End of the interval
    :param interval_max: TODO: Document. Leave on 0 for now"""
    db_entity = await resolve(conn, {"service": "time_series_db"})

    if not db_entity:
        raise RuntimeError("Time-series Database is not online!")

    db_entity = str(db_entity["entities"][0])

    handle = await conn.request(
        db_entity,
        HistoryReqV1(
            entity, start_time, end_time, interval_max, "flexTimeline"
        ).to_capnp(),
    )
    response = await handle()

    if response.payload_type_as_int() == msg_capnp.MessageTypes.errorResV1:
        err = ErrorResV1.from_capnp(response)
        raise RuntimeError("Could not get History Timeline: " + err.what)
    res = HistoryResV1.from_capnp(response)

    return res.hist
