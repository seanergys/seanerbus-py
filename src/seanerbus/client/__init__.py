# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import capnp
import os
import seanerbus_cpp_py
import asyncio

capnp.remove_import_hook()
msg_capnp = capnp.load(os.path.dirname(os.path.abspath(__file__)) + "/internal.capnp")


def conn_handler(conn: seanerbus_cpp_py.Connection):
    conn.handle()


class MsgHandle:
    def __init__(self, queue: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg]):
        self.queue: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg] = queue

    async def __call__(self) -> seanerbus_cpp_py.Message:
        res = await self.queue.get()

        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()


class VoidHandle:
    def __init__(self, queue: asyncio.Queue[seanerbus_cpp_py.ExpectedVoid]):
        self.queue: asyncio.Queue[seanerbus_cpp_py.ExpectedVoid] = queue

    async def __call__(self) -> None:
        res = await self.queue.get()

        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()


class Connection:
    """A connection to the dataplane"""

    def __init__(self, pub_sub_endpoint: str, req_res_endpoint: str):
        self.conn: seanerbus_cpp_py.Connection = seanerbus_cpp_py.Connection(
            pub_sub_endpoint, req_res_endpoint
        )
        asyncio.get_event_loop().add_reader(
            self.conn.get_fd(), lambda: conn_handler(self.conn)
        )

    async def subscribe(self, subscribe_to: seanerbus_cpp_py.Address):
        """Subscribes to publish messages from the address subscribe_to.
        When messages are published to this address, they will be forwarded to this client and can be read with read_msg()"""
        q: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg] = asyncio.Queue()
        if isinstance(subscribe_to, str):
            self.conn.subscribe(
                seanerbus_cpp_py.Address(subscribe_to),
                lambda conn, msg: q.put_nowait(msg),
            )
        else:
            self.conn.subscribe(subscribe_to, lambda conn, msg: q.put_nowait(msg))

        return MsgHandle(q)

    async def register_endpoint(self, register_to: str) -> MsgHandle:
        """Registers a req/res service at register_to. requests to this address will be then forwarded to this client"""

        q: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg] = asyncio.Queue()
        self.conn.register_endpoint(
            seanerbus_cpp_py.Address(register_to),
            lambda conn, msg: q.put_nowait(msg),
        )

        return MsgHandle(q)

    async def publish(self, addr: str, payload: tuple[int, bytes]):
        """Publishes the payload to the given address"""
        msg = seanerbus_cpp_py.Message(
            seanerbus_cpp_py.Address(addr), payload[0], payload[1]
        )
        q: asyncio.Queue[seanerbus_cpp_py.ExpectedVoid] = asyncio.Queue()

        self.conn.publish(msg, lambda conn, res: q.put_nowait(res))

        return VoidHandle(q)

    async def request(self, addr: str, payload: tuple[int, bytes]):
        """Publishes the payload to the given address"""
        msg = seanerbus_cpp_py.Message(
            seanerbus_cpp_py.Address(addr), payload[0], payload[1]
        )
        q: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg] = asyncio.Queue()

        self.conn.request(msg, lambda conn, res: q.put_nowait(res))

        return MsgHandle(q)

    async def respond_to(
        self, from_msg: seanerbus_cpp_py.Message, payload: tuple[int, bytes]
    ):
        """Publishes the payload to the given address"""
        msg = seanerbus_cpp_py.Message(from_msg.address(), payload[0], payload[1])

        q: asyncio.Queue[seanerbus_cpp_py.ExpectedVoid] = asyncio.Queue()
        self.conn.respond_to(from_msg, msg, lambda conn, res: q.put_nowait(res))

        return VoidHandle(q)
