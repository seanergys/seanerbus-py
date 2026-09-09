# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from typing import Callable

import capnp
import os
import seanerbus_cpp_py
import asyncio

capnp.remove_import_hook()
msg_capnp = capnp.load(os.path.dirname(os.path.abspath(__file__)) + "/internal.capnp")


def conn_handler(conn: seanerbus_cpp_py.Connection):
    conn.handle()


class MsgHandle:
    """A handle that returns messages from a subscription or exposed req/res service"""

    def __init__(self):
        """Creates a new MsgHandle"""
        self.queue: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg] = asyncio.Queue()

    async def __call__(self) -> seanerbus_cpp_py.Message:
        """Waits for another message.

        :return: The next message"""
        res = await self.queue.get()

        self.queue.task_done()
        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()

    def receiver(
        self,
    ) -> Callable[[seanerbus_cpp_py.Connection, seanerbus_cpp_py.ExpectedMsg], None]:
        return lambda conn, msg: self.queue.put_nowait(msg)


class OneShotMsgHandle:
    """A handle that returns a message when awaited only once"""

    def __init__(self):
        self.shot = False
        self.queue: asyncio.Queue[seanerbus_cpp_py.ExpectedMsg] = asyncio.Queue()

    async def __call__(self) -> seanerbus_cpp_py.Message:
        """Waits for the message.
        Calling this function multiple times is an error!

        :return: A SeanerbUS Message"""
        if self.shot:
            raise RuntimeError("OneShotHandle has already received a message!")
        res = await self.queue.get()
        self.queue.task_done()

        self.shot = True
        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()

    def receiver(
        self,
    ) -> Callable[[seanerbus_cpp_py.Connection, seanerbus_cpp_py.ExpectedMsg], None]:
        return lambda conn, msg: self.queue.put_nowait(msg)


class VoidHandle:
    """A handle for operations that do not return anything on success"""

    def __init__(self):
        self.queue: asyncio.Queue[seanerbus_cpp_py.ExpectedVoid] = asyncio.Queue()

    async def __call__(self) -> None:
        """Waits for the operation that handle represents to finish"""
        res = await self.queue.get()

        self.queue.task_done()
        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()

    def receiver(
        self,
    ) -> Callable[[seanerbus_cpp_py.Connection, seanerbus_cpp_py.ExpectedVoid], None]:
        return lambda conn, msg: self.queue.put_nowait(msg)


class OneShotVoidHandle:
    """A handle which the success of an operation can be queried once"""

    def __init__(self):
        self.queue: asyncio.Queue[seanerbus_cpp_py.ExpectedVoid] = asyncio.Queue()
        self.shot = False

    async def __call__(self) -> None:
        """Waits for the operation to complete"""
        if self.shot:
            raise RuntimeError("OneShotHandle has already received an answer!")
        self.shot = True
        res = await self.queue.get()

        self.queue.task_done()
        if not res.ok():
            raise RuntimeError(res.unwrap_error().what())
        return res.unwrap_ok()

    def receiver(
        self,
    ) -> Callable[[seanerbus_cpp_py.Connection, seanerbus_cpp_py.ExpectedVoid], None]:
        return lambda conn, msg: self.queue.put_nowait(msg)


class Connection:
    """A connection to the dataplane"""

    def __init__(self, pub_sub_endpoint: str, req_res_endpoint: str):
        self.conn: seanerbus_cpp_py.Connection = seanerbus_cpp_py.Connection(
            pub_sub_endpoint, req_res_endpoint
        )
        asyncio.get_event_loop().add_reader(
            self.conn.get_fd(), lambda: conn_handler(self.conn)
        )

    async def subscribe(self, subscribe_to: str):
        """Subscribes to published messages from the address subscribe_to.

        :param subscribe_to: The Address to subscribe to
        :return: a MsgHandle returning subscribed messages when await()ed"""

        handle = MsgHandle()
        self.conn.subscribe(seanerbus_cpp_py.Address(subscribe_to), handle.receiver())

        return handle

    async def register_endpoint(self, register_to: str) -> MsgHandle:
        """Registers a req/res service at register_to.a

        :param register_to: The address to register
        :return: a MsgHandle with which requests can be awaited"""
        handle = MsgHandle()
        self.conn.register_endpoint(
            seanerbus_cpp_py.Address(register_to),
            handle.receiver(),
        )

        return handle

    async def publish(self, addr: str, payload: tuple[int, bytes]):
        """Publishes the payload to the given address

        :param addr: The address to publish to
        :param payload: The payload to publish
        :return: OneShotVoidHandle with which the completion of the publish can be awaited"""
        msg = seanerbus_cpp_py.Message(
            seanerbus_cpp_py.Address(addr), payload[0], payload[1]
        )
        handle = OneShotVoidHandle()
        self.conn.publish(msg, handle.receiver())

        return handle

    async def request(self, addr: str, payload: tuple[int, bytes]):
        """Requests a req/res service

        :param addr: Address of the req/res service to request
        :param payload: payload to send as a request
        :return: OneShotMsgHandle with which the response can be awaited"""
        msg = seanerbus_cpp_py.Message(
            seanerbus_cpp_py.Address(addr), payload[0], payload[1]
        )
        handle = OneShotMsgHandle()

        self.conn.request(msg, handle.receiver())

        return handle

    async def respond_to(
        self, from_msg: seanerbus_cpp_py.Message, payload: tuple[int, bytes]
    ):
        """Responds to an incoming request

        :param from_msg: Message to respond to
        :param payload: Payload to sent as a response
        :return: OneShotVoidHandle with which the sending of the response can be awaited
        """
        handle = OneShotVoidHandle()
        msg = seanerbus_cpp_py.Message(from_msg.address(), payload[0], payload[1])

        self.conn.respond_to(from_msg, msg, handle.receiver())

        return handle
