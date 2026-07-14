# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from ..client import Connection
from ..msg import ReverseResolveReqV1, ReverseResolveResV1
from ..msg import ResolveResV1, ResolveReqV1
from ..msg import RegisterResolveReqV1, RegisterResolveResV1
from ..msg import UnregisterResolveReqV1, UnregisterResolveResV1
import uuid


async def resolve(name: dict[str, str]) -> list[uuid.UUID]:
    """Use the naming service to translate a Name to an Address"""
    c = await Connection.connect("localhost", 5398)

    msg = ResolveResV1.from_capnp(
        await c.request(uuid.UUID(int=0x10CA105), ResolveReqV1(name).to_capnp())
    )

    return msg.uuids


async def reverse_resolve(addr: uuid.UUID) -> dict[str, str]:
    """Uses the naming service to translate a Address back to a Name"""
    c = await Connection.connect("localhost", 5398)

    msg = ReverseResolveResV1.from_capnp(
        await c.request(uuid.UUID(int=0x10CA105), ReverseResolveReqV1(addr).to_capnp())
    )

    return msg.name


async def register_resolve(name: dict[str, str], addr: uuid.UUID):
    """Registers a name for the given address with the naming service"""

    c = await Connection.connect("localhost", 5398)

    msg = RegisterResolveResV1.from_capnp(
        await c.request(
            uuid.UUID(int=0x10CA105), RegisterResolveReqV1(name, addr).to_capnp()
        )
    )
    return msg


async def unregister_resolve(addr: uuid.UUID):
    """Unregisters an address from the naming service"""

    c = await Connection.connect("localhost", 5398)

    msg = UnregisterResolveResV1.from_capnp(
        await c.request(
            uuid.UUID(int=0x10CA105), UnregisterResolveReqV1(addr).to_capnp()
        )
    )
    return msg
