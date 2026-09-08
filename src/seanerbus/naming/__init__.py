# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from ..msg import ErrorResV1, ReverseResolveReqV1, ReverseResolveResV1
from ..msg import ResolveResV1, ResolveReqV1
from ..msg import RegisterResolveReqV1
from ..msg import UnregisterResolveReqV1
from ..msg import msg_capnp
import uuid


async def resolve(conn, name: dict[str, str]) -> list[uuid.UUID]:
    """Use the naming service to translate a Name to an Address"""
    handle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", ResolveReqV1(name).to_capnp()
    )

    msg = ResolveResV1.from_capnp(await handle())

    return msg.uuids


async def reverse_resolve(conn, addr: uuid.UUID) -> dict[str, str]:
    """Uses the naming service to translate a Address back to a Name"""

    handle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", ReverseResolveReqV1(addr).to_capnp()
    )
    msg = ReverseResolveResV1.from_capnp(await handle())

    return msg.name


async def register_resolve(conn, name: dict[str, str], addr: uuid.UUID):
    """Registers a name for the given address with the naming service"""

    handle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105",
        RegisterResolveReqV1(name, addr).to_capnp(),
    )
    msg = ErrorResV1.from_capnp(await handle())

    if msg.error_code != msg_capnp.ErrorCodeV1.ok:
        raise RuntimeError("Failed to register a name resolution: " + msg.what)


async def unregister_resolve(conn, addr: uuid.UUID):
    """Unregisters an address from the naming service"""

    handle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", UnregisterResolveReqV1(addr).to_capnp()
    )
    msg = ErrorResV1.from_capnp(await handle())

    if msg.error_code != msg_capnp.ErrorCodeV1.ok:
        raise RuntimeError("Failed to register a name resolution: " + msg.what)
