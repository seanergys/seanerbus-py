#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import seanerbus.client
from seanerbus.msg import TimeValueV1
import capnp
import asyncio
import uuid
import sys


async def main():
    # Connect to the SeanerBUS
    c = await seanerbus.client.Connection.connect("localhost", 5398)

    # Subscribe to the UUID given on the command line
    await c.subscribe(uuid.UUID(sys.argv[1]))

    while True:
        # read incoming messages from the bus, interpreting them as TimeValueV1's
        tv = TimeValueV1.from_capnp(await c.read_msg())
        print("time=", tv.time, "value=", tv.value)


if len(sys.argv) != 2:
    print("subscribe_test.py UUID")
    exit(-1)

asyncio.run(capnp.run(main()))
