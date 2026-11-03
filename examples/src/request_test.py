#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import seanerbus.client
from seanerbus.msg import HelloWorldReqV1, HelloWorldResV1
import capnp
import asyncio
import sys


async def main():
    # Connect to the SeanerBUS
    c = seanerbus.client.Connection(
        "seanerbroker://localhost:5398", "seanerbroker://localhost:5398"
    )

    # Send a HelloWorldReqV1 to the UUID given on the command line.
    # Interpret the result as a HelloWorldResV1
    handle = await c.request(sys.argv[1], HelloWorldReqV1("Hello World").to_capnp())

    msg = HelloWorldResV1.from_capnp(await handle())

    print(f"Got a Response: {msg.msg}")


if len(sys.argv) != 2:
    print("request_test.py UUID")
    exit(-1)

asyncio.run(capnp.run(main()))
