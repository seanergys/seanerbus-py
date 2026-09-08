#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import seanerbus.client
from seanerbus.msg import TimeValueV1
import capnp
from time import sleep
import asyncio
import sys


async def main():
    # Connect to the SeanerBUS
    c = seanerbus.client.Connection(
        "demobus://localhost:5398", "demobus://localhost:5398"
    )

    time = 0
    value = 0.0
    while True:
        # Publish a TimeValueV1 to the UUID given on the command line
        handle = await c.publish(sys.argv[1], TimeValueV1(time, value).to_capnp())
        await handle()
        time = time + 1
        value = value + 1.0
        sleep(1)


if len(sys.argv) != 2:
    print("subscribe_test.py UUID")
    exit(-1)

asyncio.run(capnp.run(main()))
