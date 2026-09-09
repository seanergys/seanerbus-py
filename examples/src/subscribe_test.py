#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import seanerbus.client
from seanerbus.msg import TimeValueV1
import capnp
import asyncio
import sys


async def main():
    # Connect to the SeanerBUS
    c = seanerbus.client.Connection(
        "demobus://localhost:5398", "demobus://localhost:5398"
    )

    # Subscribe to the UUID given on the command line
    handle = await c.subscribe(sys.argv[1])

    while True:
        tv = TimeValueV1.from_capnp(await handle())
        print(tv.time.to_ns(), tv.value)


if len(sys.argv) != 2:
    print("subscribe_test.py UUID")
    exit(-1)

asyncio.run(capnp.run(main()))
