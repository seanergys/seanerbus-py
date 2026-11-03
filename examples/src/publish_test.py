#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import seanerbus.client
from seanerbus.msg import TimeValueV1
from seanerbus.time import Time
import capnp
from time import sleep
import asyncio
import sys


async def main():
    # Connect to the SeanerBUS
    c = seanerbus.client.Connection(
        "seanerbroker://localhost:5398", "seanerbroker://localhost:5398"
    )

    value = 0.0
    while True:
        # Publish a TimeValueV1 to the UUID given on the command line
        handle = await c.publish(sys.argv[1], TimeValueV1(Time.now(), value).to_capnp())
        await handle()
        value = value + 1.0
        sleep(1)


if len(sys.argv) != 2:
    print("subscribe_test.py UUID")
    exit(-1)

asyncio.run(capnp.run(main()))
