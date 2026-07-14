# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import capnp
import os
import uuid
import random

capnp.remove_import_hook()
msg_capnp = capnp.load(os.path.dirname(os.path.abspath(__file__)) + "/internal.capnp")


def uuid_to_u64_pair(uuid: uuid.UUID) -> tuple[int, int]:
    upper = uuid.int >> 64
    lower = uuid.int & (1 << 64) - 1
    return (upper, lower)


class Connection:
    """A connection to the dataplane"""

    def __init__(self):
        pass

    @staticmethod
    async def connect(host: str, port: int):
        """Connects to the seanerbus at host and port, returns an open connection"""
        conn: Connection = Connection()

        conn.stream: capnp.AsyncIoStream = await capnp.AsyncIoStream.create_connection(
            host=host, port=port
        )
        return conn

    async def subscribe(self, subscribe_to: uuid.UUID):
        """Subscribes to publish messages from the address subscribe_to.
        When messages are published to this address, they will be forwarded to this client and can be read with read_msg()"""
        msg = msg_capnp.Message.new_message()
        (upper, lower) = uuid_to_u64_pair(subscribe_to)
        msg.address.upper = upper
        msg.address.lower = lower
        msg.type = "subscribe"
        msg.payloadType = 0
        msg.payload = b""
        await msg.write_async(self.stream)

    async def register(self, register_to: uuid.UUID):
        """Registers a req/res service at register_to. requests to this address will be then forwarded to this client"""
        msg = msg_capnp.Message.new_message()
        (upper, lower) = uuid_to_u64_pair(register_to)
        msg.address.upper = upper
        msg.address.lower = lower
        msg.type = "register"
        msg.payloadType = 0
        msg.payload = b""
        await msg.write_async(self.stream)

    async def publish(self, addr: uuid.UUID, payload: tuple[int, bytes]):
        """Publishes the payload to the given address"""
        msg = msg_capnp.Message.new_message()
        (upper, lower) = uuid_to_u64_pair(addr)
        msg.address.upper = upper
        msg.address.lower = lower
        msg.type = "publish"
        msg.payloadType = payload[0]
        msg.payload = payload[1]
        await msg.write_async(self.stream)

    async def request(self, addr: uuid.UUID, payload: tuple[int, bytes]):
        """Performs a request to the given address with the given payloadType
        This will block until a response has been received, which will then be returned to the user"""
        msg = msg_capnp.Message.new_message()
        (upper, lower) = uuid_to_u64_pair(addr)
        msg.address.upper = upper
        msg.address.lower = lower
        msg.type = "request"
        msg.payloadType = payload[0]
        msg.payload = payload[1]
        msg.matchingId = random.randint(0, ((1 << 64) - 1))
        await msg.write_async(self.stream)
        message = await msg_capnp.Message.read_async(self.stream)
        return message

    async def respond_to(self, from_msg, payload: tuple[int, bytes]):
        """Responds to the incoming message from_msg with the given payload"""
        msg = msg_capnp.Message.new_message()
        msg.address.upper = from_msg.address.upper
        msg.address.lower = from_msg.address.lower
        msg.type = "response"
        msg.to.upper = getattr(from_msg, "from").upper
        msg.to.lower = getattr(from_msg, "from").lower
        msg.payloadType = payload[0]
        msg.payload = payload[1]
        msg.matchingId = from_msg.matchingId
        await msg.write_async(self.stream)

    async def read_msg(self):
        """Reads a single message from the connection to the SeanerBUS

        This message is either a published message from any of the addresses we have subscribed for or a request from any of the req/res services we have registered with register()"""
        message = await msg_capnp.Message.read_async(self.stream)
        return message
