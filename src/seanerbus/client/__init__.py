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
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def __call__(self):
        res = await self.queue.get()

        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()


class Connection:
    """A connection to the dataplane"""

    def __init__(self, pub_sub_endpoint, req_res_endpoint):
        self.conn: seanerbus_cpp_py.Connection = seanerbus_cpp_py.Connection(
            pub_sub_endpoint, req_res_endpoint
        )
        asyncio.get_event_loop().add_reader(
            self.conn.get_fd(), lambda: conn_handler(self.conn)
        )

    async def subscribe(self, subscribe_to: seanerbus_cpp_py.Address):
        """Subscribes to publish messages from the address subscribe_to.
        When messages are published to this address, they will be forwarded to this client and can be read with read_msg()"""
        q = asyncio.Queue()
        if isinstance(subscribe_to, str):
            self.conn.subscribe(
                seanerbus_cpp_py.Address(subscribe_to),
                lambda conn, msg: q.put_nowait(msg),
            )
        else:
            self.conn.subscribe(subscribe_to, lambda conn, msg: q.put_nowait(msg))

        return MsgHandle(q)

    async def register_endpoint(self, register_to):
        """Registers a req/res service at register_to. requests to this address will be then forwarded to this client"""

        q = asyncio.Queue()
        if isinstance(register_to, str):
            self.conn.register_endpoint(
                seanerbus_cpp_py.Address(register_to),
                lambda conn, msg: q.put_nowait(msg),
            )
        else:
            self.conn.register_endpoint(
                register_to, lambda conn, msg: q.put_nowait(msg)
            )

        return MsgHandle(q)

    async def publish(self, addr, payload: tuple[int, bytes]):
        """Publishes the payload to the given address"""
        msg = None
        if isinstance(addr, str):
            msg = seanerbus_cpp_py.Message(
                seanerbus_cpp_py.Address(addr), payload[0], payload[1]
            )
        else:
            msg = seanerbus_cpp_py.Message(addr, payload[0], payload[1])
        q = asyncio.Queue()

        self.conn.publish(msg, lambda conn, res: q.put_nowait(res))

        return MsgHandle(q)

    async def request(self, addr, payload: tuple[int, bytes]):
        """Publishes the payload to the given address"""
        msg = None
        if isinstance(addr, str):
            msg = seanerbus_cpp_py.Message(
                seanerbus_cpp_py.Address(addr), payload[0], payload[1]
            )
        else:
            msg = seanerbus_cpp_py.Message(addr, payload[0], payload[1])
        q = asyncio.Queue()

        self.conn.request(msg, lambda conn, res: q.put_nowait(res))

        return MsgHandle(q)

    async def respond_to(self, from_msg, payload: tuple[int, bytes]):
        """Publishes the payload to the given address"""
        msg = seanerbus_cpp_py.Message(from_msg.address(), payload[0], payload[1])

        q = asyncio.Queue()
        self.conn.respond_to(from_msg, msg, lambda conn, res: q.put_nowait(res))

        return MsgHandle(q)

    async def read_msg(self):
        """Reads a single message from the connection to the SeanerBUS

        This message is either a published message from any of the addresses we have subscribed for or a request from any of the req/res services we have registered with register()"""
        message = await msg_capnp.Message.read_async(self.stream)
        return message
