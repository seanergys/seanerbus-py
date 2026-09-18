# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from ..msg import ErrorResV1, ReverseResolveReqV1, ReverseResolveResV1
from ..msg import ResolveResV1, ResolveReqV1
from ..msg import RegisterResolveReqV1
from ..msg import UnregisterResolveReqV1
from ..msg import msg_capnp
from ..client import OneShotMsgHandle

from ..client import Connection


async def resolve(conn: Connection, name: dict[str, str]) -> dict:
    """Use the naming service to translate a Name to an Entity

    Returns a dictionary with entries 'entities' and 'resolved_terms'.
    The list result['entities'] contains the resolved entities.
    The list result['resolved_terms'] contains the resolved terms of the name look-up wildcards.

    If resolve(conn, {"node" : "4", "cpu" : "*"}) is looked up, then possibly a dict with:

    result = {
        "entities" = [ "e4d6f4e4-0e6b-4572-9586-ad297c01d482", "8ce715f0-069d-42b0-bbe8-6e0d6000a4e2"],
        "resolved_terms" = [{"cpu" : "0"}, {"cpu" : "1"}]
    }"""

    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", ResolveReqV1(name).to_capnp()
    )
    res = await handle()
    msg = ResolveResV1.from_capnp(res)

    return msg.to_dict()


async def reverse_resolve(conn: Connection, entity: str) -> dict[str, str]:
    """Uses the naming service to translate a Entity back to a Name"""

    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105", ReverseResolveReqV1(entity).to_capnp()
    )
    res = await handle()
    msg = ReverseResolveResV1.from_capnp(res)

    return msg.name


async def register_resolve(conn: Connection, name: dict[str, str], entity: str):
    """Registers a name for the given entity with the naming service"""
    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105",
        RegisterResolveReqV1(name, entity).to_capnp(),
    )
    res = await handle()
    msg = ErrorResV1.from_capnp(res)

    if msg.error_code != msg_capnp.ErrorCodeV1.ok:
        raise RuntimeError("Failed to register a name resolution: " + msg.what)


async def unregister_resolve(conn: Connection, entity: str):
    """Unregisters an entity from the naming service"""

    handle: OneShotMsgHandle = await conn.request(
        "00000000-0000-0000-0000-0000010ca105",
        UnregisterResolveReqV1(entity).to_capnp(),
    )
    res = await handle()
    msg = ErrorResV1.from_capnp(res)

    if msg.error_code != msg_capnp.ErrorCodeV1.ok:
        raise RuntimeError("Failed to register a name resolution: " + msg.what)
