# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from ..msg import ErrorResV1, ReverseResolveReqV1, ReverseResolveResV1
from ..msg import ResolveResV1, ResolveReqV1
from ..msg import RegisterResolveReqV1
from ..msg import UnregisterResolveReqV1
from ..msg import msg_capnp
from ..client import MsgHandle, OneShotMsgHandle

from ..client import Connection


async def resolve(conn: Connection, name: dict[str, str]) -> list[str]:
    """Use the naming service to translate a Name to an Address"""

    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", ResolveReqV1(name).to_capnp()
    )
    res = await handle()
    msg = ResolveResV1.from_capnp(res)

    return msg.uuids


async def reverse_resolve(conn: Connection, addr: str) -> dict[str, str]:
    """Uses the naming service to translate a Address back to a Name"""

    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", ReverseResolveReqV1(addr).to_capnp()
    )
    res = await handle()
    msg = ReverseResolveResV1.from_capnp(res)

    return msg.name


async def register_resolve(conn: Connection, name: dict[str, str], addr: str):
    """Registers a name for the given address with the naming service"""
    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105",
        RegisterResolveReqV1(name, addr).to_capnp(),
    )
    res = await handle()
    msg = ErrorResV1.from_capnp(res)

    if msg.error_code != msg_capnp.ErrorCodeV1.ok:
        raise RuntimeError("Failed to register a name resolution: " + msg.what)


async def unregister_resolve(conn: Connection, addr: str):
    """Unregisters an address from the naming service"""

    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", UnregisterResolveReqV1(addr).to_capnp()
    )
    res = await handle()
    msg = ErrorResV1.from_capnp(res)

    if msg.error_code != msg_capnp.ErrorCodeV1.ok:
        raise RuntimeError("Failed to register a name resolution: " + msg.what)
