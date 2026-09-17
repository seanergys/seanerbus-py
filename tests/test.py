# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

from seanerbus_cpp_py import Message
import seanerbus_cpp_py
import pytest

from seanerbus.msg import TimeValueV1
from seanerbus.msg import *
from seanerbus.time import Time


def to_from_capnp(tv):
    payload_type, payload = tv.to_capnp()
    msg = Message(
        seanerbus_cpp_py.Entity("15a1a4c6-e83b-4699-bbdb-448b26edf1cc"),
        payload_type,
        payload,
    )
    tv3 = tv.from_capnp(msg)

    assert tv == tv3


def to_from_dict(tv):
    tv2 = tv.from_dict(tv.to_dict())
    assert tv == tv2


def test_timevaluev1():
    tv = TimeValueV1(Time.from_ns(100), 1000)
    assert tv.time.to_ns() == 100
    assert tv.value == 1000

    to_from_dict(tv)
    to_from_capnp(tv)


def test_helloworldreqv1():
    tv = HelloWorldReqV1("Hello World")
    assert tv.msg == "Hello World"

    to_from_dict(tv)
    to_from_capnp(tv)


def test_helloworldresv1():
    tv = HelloWorldResV1("Hello World")
    assert tv.msg == "Hello World"

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ResolveReqV1_empty():
    tv = ResolveReqV1({})
    assert tv.name == {}

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ResolveReqV1():
    tv = ResolveReqV1({"foo": "bar", "bar": "baz"})
    assert tv.name == {"foo": "bar", "bar": "baz"}

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ResolveResV1_error():
    tv = ResolveResV1(["foo"])
    assert tv.entities == ["foo"]

    to_from_dict(tv)
    with pytest.raises(ValueError):
        to_from_capnp(tv)


def test_ResolveResV1_empty():
    tv = ResolveResV1([])
    assert tv.entities == []

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ResolveResV1():
    tv = ResolveResV1(
        ["c0ea7f8d-ba35-4a10-85ba-8d2f45848c93", "3d8a1ee2-9131-40fe-9691-af42d86cd889"]
    )
    assert tv.entities == [
        "c0ea7f8d-ba35-4a10-85ba-8d2f45848c93",
        "3d8a1ee2-9131-40fe-9691-af42d86cd889",
    ]

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ReverseResolveReqV1_error():
    tv = ReverseResolveReqV1("foo")
    assert tv.entity == "foo"

    to_from_dict(tv)
    with pytest.raises(ValueError):
        to_from_capnp(tv)


def test_ReverseResolveReqV1():
    tv = ReverseResolveReqV1("c0ea7f8d-ba35-4a10-85ba-8d2f45848c93")
    assert tv.entity == "c0ea7f8d-ba35-4a10-85ba-8d2f45848c93"

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ReverseResolveResV1_empty():
    tv = ReverseResolveResV1({})
    assert tv.name == {}

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ReverseResolveResV1():
    tv = ReverseResolveResV1({"foo": "bar", "bar": "baz"})
    assert tv.name == {"foo": "bar", "bar": "baz"}

    to_from_dict(tv)
    to_from_capnp(tv)


def test_VectorReqV1():
    tv = VectorReqV1([1, 2, 3, 4])

    assert tv.values == [1, 2, 3, 4]

    to_from_dict(tv)
    to_from_capnp(tv)


def test_VectorResV1():
    tv = VectorResV1([1, 2, 3, 4])

    assert tv.results == [1, 2, 3, 4]

    to_from_dict(tv)
    to_from_capnp(tv)


def test_FluxLifecycleEventV1():
    tv = FluxLifecycleEventV1("foobar")

    assert tv.data == "foobar"

    to_from_dict(tv)
    to_from_capnp(tv)


def test_RegisterResolveReqV1():
    tv = RegisterResolveReqV1({"foo": "bar"}, "c0ea7f8d-ba35-4a10-85ba-8d2f45848c93")

    assert tv.name == {"foo": "bar"}
    assert tv.entity == "c0ea7f8d-ba35-4a10-85ba-8d2f45848c93"

    to_from_dict(tv)
    to_from_capnp(tv)


def test_ErrorResV1():
    tv = ErrorResV1(42, "Not good")

    assert tv.error_code == 42
    assert tv.what == "Not good"

    to_from_dict(tv)
    to_from_capnp(tv)


def test_GetReqV1():
    tv = GetReqV1()

    to_from_dict(tv)
    to_from_capnp(tv)


def test_GetResV1():
    tv = GetResV1(42, Time.from_ns(1234))

    assert tv.value == 42
    assert tv.time.to_ns() == 1234

    to_from_dict(tv)
    to_from_capnp(tv)


def test_SetReqV1():
    tv = SetReqV1(42)

    assert tv.value == 42

    to_from_dict(tv)
    to_from_capnp(tv)


def test_aggregate():
    a = Aggregate(0, 1, 3124, 124, 213, 321)
    assert a.minimum == 0
    assert a.maximum == 1
    assert a.sum == 3124
    assert a.count == 124
    assert a.integral == 213
    assert a.active_time == 321

    a2 = Aggregate.from_capnp(a.to_capnp())

    to_from_dict(a)
    assert a == a2


def test_history_raw():
    h = History.from_raw([1, 2, 3], [4, 5, 6])
    assert h.time_delta == [1, 2, 3]
    assert h.raw == [4, 5, 6]
    assert h.type == "raw"

    to_from_dict(h)
    h2 = History.from_capnp(h.to_capnp())

    assert h == h2


def test_history_aggr():
    aggrs = [
        Aggregate(0, 1, 3124, 124, 213, 321),
        Aggregate(0, 1, 23, 124, 2, 321),
        Aggregate(0, 1, 10000, 124, 2, 32001),
    ]
    h = History.from_aggregate([10, 20, 30], aggrs)

    assert h.time_delta == [10, 20, 30]
    assert h.aggr == aggrs
    assert h.type == "aggregate"

    h2 = History.from_capnp(h.to_capnp())

    to_from_dict(h)
    assert h == h2

    h_res = HistoryResV1(h)

    assert h_res.hist == h

    to_from_capnp(h_res)
    to_from_dict(h_res)


def test_FluxClassifyJobResV1():
    fl = FluxClassifyJobResV1("foo")
    assert fl.result == "foo"
    to_from_capnp(fl)
    to_from_dict(fl)


def test_UserDefinedPayload():
    fl = UserDefinedPayload((1 << 63) + 42, b"foo")
    assert fl.payload_type == (1 << 63) + 42
    assert fl.payload == b"foo"
    to_from_capnp(fl)
