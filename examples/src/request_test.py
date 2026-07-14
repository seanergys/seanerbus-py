#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import seanerbus.client
from seanerbus.msg import HelloWorldReqV1, HelloWorldResV1
import capnp
import asyncio
import uuid
import sys


async def main():
    # Connect to the SeanerBUS
    c = await seanerbus.client.Connection.connect("localhost", 5398)

    # Send a HelloWorldReqV1 to the UUID given on the command line.
    # Interpret the result as a HelloWorldResV1
    msg = HelloWorldResV1.from_capnp(
        await c.request(
            uuid.UUID(sys.argv[1]), HelloWorldReqV1("Hello World").to_capnp()
        )
    )

    print(f"Got a Response: {msg.msg}")


if len(sys.argv) != 2:
    print("request_test.py UUID")
    exit(-1)

asyncio.run(capnp.run(main()))
