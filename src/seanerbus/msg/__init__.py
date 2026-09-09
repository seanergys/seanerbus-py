# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import capnp
import os
from uuid import UUID

from seanerbus_cpp_py import Message


def uuid_to_u64_pair(uuid_str: str) -> tuple[int, int]:
    uuid : UUID= UUID(uuid_str)
    upper = uuid.int >> 64
    lower = uuid.int & (1 << 64) - 1
    return (upper, lower)


msg_capnp = capnp.load(
    os.path.dirname(os.path.abspath(__file__)) + "/schemas/msg.capnp"
)


class TimeValueV1:
    """A time-value pair payload"""

    def __init__(self, time: int, value: float):
        """Creates a TimeValueV1 from a timestamp and value"""
        self.time: int = time
        self.value: float = value

    @staticmethod
    def from_capnp(msg: Message):
        """Takes a message (as returned by Connection.read_msg() and decode it as TimeValueV1 returning it."""
        res = TimeValueV1(0, 0.0)
        if msg.payload_type_as_int() != msg_capnp.MessageTypes.timeValueV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as TimeValueV1 message!"
            )
        with msg_capnp.TimeValueV1.from_bytes(msg.payload()) as tv:
            res.time = tv.time
            res.value = tv.value
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this TimeValueV1 as a Cap'n'Proto Payload"""
        msg = msg_capnp.TimeValueV1.new_message()
        msg.time = self.time
        msg.value = self.value
        return (msg_capnp.MessageTypes.timeValueV1, msg.to_bytes())


class HelloWorldReqV1:
    """A Hello World payload example for req/res (Request half)"""

    def __init__(self, msg: str):
        """Creates a new HelloWorldReqV1 from the given string"""
        self.msg = msg

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a HelloWorldReqV1"""
        res = HelloWorldReqV1("")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.helloWorldReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as HelloWorldReqV1!"
            )

        with msg_capnp.HelloWorldReqV1.from_bytes(msg.payload()) as req:
            res.msg = req.msg
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this HelloWorldReqV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.HelloWorldReqV1.new_message()
        msg.msg = self.msg
        return (msg_capnp.MessageTypes.helloWorldReqV1, msg.to_bytes())


class HelloWorldResV1:
    """A Hello World response payload example that contains a string"""

    def __init__(self, msg: str):
        """Creates a new HelloWorldResV1 from the given string"""
        self.msg = msg

    @staticmethod
    def from_capnp(msg):
        """Decodes the given message (as returned by Connection.read_msg() as a HelloWorldResV1"""
        res = HelloWorldResV1("")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.helloWorldResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as HelloWorldResV1!"
            )

        with msg_capnp.HelloWorldResV1.from_bytes(msg.payload()) as req:
            res.msg = req.msg
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this HelloWorldResV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.HelloWorldResV1.new_message()
        msg.msg = self.msg
        return (msg_capnp.MessageTypes.helloWorldResV1, msg.to_bytes())


class ResolveReqV1:
    """A request for name resolution payload"""

    def __init__(self, kvs: dict[str, str]):
        """Creates a ResolveReqV1 from a name
        :param kvs: The name dict to look up"""
        self.kvs: dict[str, str] = kvs

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a NamingServiceReqV1V1"""
        res = ResolveReqV1({})

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.resolveReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as NamingServiceReqV1!"
            )

        with msg_capnp.ResolveReqV1.from_bytes(msg.payload()) as req:
            for i in req.attributes:
                res.kvs[i.key] = i.value
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this NamingServiceReqV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.ResolveReqV1.new_message()

        list_of_kvs = list(self.kvs.items())

        msg.init("attributes", len(list_of_kvs))

        for num, element in enumerate(list_of_kvs):
            msg.attributes[num].key = element[0]
            msg.attributes[num].value = element[1]
        return (msg_capnp.MessageTypes.resolveReqV1, msg.to_bytes())


class ResolveResV1:
    """A response to a resolve request payload"""

    def __init__(self, uuids: list[str]):
        """Creates a ResolveResV1 from a list of addresses
        :param uuids: The list of addresses to include in the response"""
        self.uuids: list[str] = uuids

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a ResolveResV1"""
        res = ResolveResV1([])

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.resolveResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as ResolveResV1!"
            )

        with msg_capnp.ResolveResV1.from_bytes(msg.payload()) as req:
            for i in req.matchingInterfaces:
                uuid_num = (i.upper << 64) + i.lower
                res.uuids.append(str(UUID(int=uuid_num)))
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this ResolveResV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.ResolveResV1.new_message()

        msg.init("matchingInterfaces", len(self.uuids))

        for num, uuid_in in enumerate(self.uuids):
            (upper, lower) = uuid_to_u64_pair(uuid_in)
            msg.matchingInterfaces[num].upper = upper
            msg.matchingInterfaces[num].lower = lower
        return (msg_capnp.MessageTypes.resolveResV1, msg.to_bytes())


class ReverseResolveReqV1:
    """A request payload for a reverse resolve, e.g. address back to name"""

    def __init__(self, addr: str):
        self.addr: str = addr 

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a ReverseResolveRegV1"""
        res = ReverseResolveReqV1("")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.resolveResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as ResolveResV1!"
            )

        with msg_capnp.ReverseResolveReqV1.from_bytes(msg.payload()) as req:
            res.addr = str(UUID(int=(req.address.upper << 64) + req.address.lower))
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this ReverseResolveReqV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.ReverseResolveReqV1.new_message()

        (upper, lower) = uuid_to_u64_pair(self.addr)
        msg.address.upper = upper
        msg.address.lower = lower
        return (msg_capnp.MessageTypes.reverseResolveReqV1, msg.to_bytes())


class ReverseResolveResV1:
    """A reverse resolve response payload for translating addresses back to names"""

    def __init__(self, name: dict[str, str]):
        self.name: dict[str, str] = name

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a NamingServiceReqV1V1"""
        res = ReverseResolveResV1({})

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.reverseResolveResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as NamingServiceReqV1!"
            )

        with msg_capnp.ReverseResolveResV1.from_bytes(msg.payload()) as req:
            for i in req.name:
                res.name[i.key] = i.value
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this NamingServiceReqV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.ReverseResolveResV1.new_message()

        list_of_kvs = list(self.name.items())

        msg.init("name", len(list_of_kvs))

        for num, element in enumerate(list_of_kvs):
            msg.name[num].key = element[0]
            msg.name[num].value = element[1]
        return (msg_capnp.MessageTypes.reverseResolveResV1, msg.to_bytes())


class VectorReqV1:
    """A vector of floats request payload"""

    def __init__(self, values: list[float]):
        """Creates a new VectorReqV1 from the given list of floats"""
        self.values: list[float] = values

    @staticmethod
    def from_capnp(msg):
        """Decodes the given message (as returned by Connection.read_msg()) as a VectorReqV1"""
        req_obj = VectorReqV1([])

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.vectorReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as VectorReqV1!"
            )

        with msg_capnp.VectorReqV1.from_bytes(msg.payload()) as req:
            # Convert Cap’n Proto list -> Python list
            req_obj.values = list(req.values)

        return req_obj

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this VectorReqV1 as a Cap'n Proto payload"""
        msg = msg_capnp.VectorReqV1.new_message()

        # Initialize list with proper size
        values_builder = msg.init("values", len(self.values))

        # Fill list
        for i, v in enumerate(self.values):
            values_builder[i] = v

        return (msg_capnp.MessageTypes.vectorReqV1, msg.to_bytes())


class VectorResV1:
    """A vector of floats response payload"""

    def __init__(self, results: list[float]):
        """Creates a new VectorResV1 from the given list of floats"""
        self.results: list[float] = results

    @staticmethod
    def from_capnp(msg):
        """Decodes the given message (as returned by Connection.read_msg() as a VectorResV1"""
        res = VectorResV1([])

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.vectorResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as VectorResV1!"
            )

        with msg_capnp.VectorResV1.from_bytes(msg.payload()) as req:
            # Convert Cap’n Proto list → Python list
            res.results = list(req.results)

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this VectorResV1 as a Cap'n Proto payload"""
        msg = msg_capnp.VectorResV1.new_message()

        results_builder = msg.init("results", len(self.results))

        # Fill values
        for i, v in enumerate(self.results):
            results_builder[i] = v

        return (msg_capnp.MessageTypes.vectorResV1, msg.to_bytes())


class FluxLifecycleEventV1:
    """A payload for publishing Flux lifecycle events"""

    def __init__(self, data: str):
        """Creates a new FluxLifecycleEventV1 from the given list of floats"""
        self.data: str = data

    @staticmethod
    def from_capnp(msg):
        """Decodes the given message (as returned by Connection.read_msg() as a FluxLifecycleEventV1"""
        res = FluxLifecycleEventV1("")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.fluxLifecycleEventV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as FluxLifecycleEventV1!"
            )

        with msg_capnp.FluxLifecycleEventV1.from_bytes(msg.payload()) as req:
            # Convert Cap’n Proto list → Python list
            res.data = list(req.data)

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this FluxLifecycleEventV1 as a Cap'n Proto payload"""
        msg = msg_capnp.FluxLifecycleEventV1.new_message()

        msg.data = self.data

        return (msg_capnp.MessageTypes.fluxLifecycleEventV1, msg.to_bytes())


class RegisterResolveReqV1:
    """A request payload for registering a new name to address mapping"""

    def __init__(self, name: dict[str, str], addr: str):
        self.name: dict[str, str] = name
        self.addr: str = addr

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a ResolveResV1"""
        res = RegisterResolveReqV1({}, "")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.registerResolveReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as ResolveResV1!"
            )

        with msg_capnp.RegisterResolveReqV1.from_bytes(msg.payload()) as req:
            res.addr = str(UUID(int=(req.address.upper << 64) + req.address.lower))
            for i in req.name:
                res.name[i.key] = i.value
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this ResolveResV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.RegisterResolveReqV1.new_message()

        (upper, lower) = uuid_to_u64_pair(self.addr)
        msg.address.upper = upper
        msg.address.lower = lower

        list_of_kvs = list(self.name.items())

        msg.init("name", len(list_of_kvs))

        for num, element in enumerate(list_of_kvs):
            msg.name[num].key = element[0]
            msg.name[num].value = element[1]
        return (msg_capnp.MessageTypes.registerResolveReqV1, msg.to_bytes())


class ErrorResV1:
    """A response payload for signalling errors"""

    def __init__(self, error_code, what):
        """Creates a new ErrorResV1 from the error_code and optionally an error message"""
        self.error_code: int = error_code
        self.what: str = what

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a ErrorResV1"""
        res = ErrorResV1(msg_capnp.ErrorCodeV1.ok, "")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.errorResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as ErrorResV1!"
            )

        with msg_capnp.ErrorResV1.from_bytes(msg.payload()) as req:
            res.error_code = req.errorCode
            res.what = req.what

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this ErrorResV1 as a Cap'n Proto payload"""
        msg = msg_capnp.ErrorResV1.new_message()

        msg.errorCode = self.error_code
        msg.what = self.what

        return (msg_capnp.MessageTypes.errorResV1, msg.to_bytes())


class GetReqV1:
    """A request for requesting singular numeric values"""

    def __init__(self):
        """Creates a new GetReqV1"""

    @staticmethod
    def from_capnp(msg):
        """Decodes the given message (as returned by Connection.read_msg() as a GetReqV1"""
        res = GetReqV1()

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.getReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as GetReqV1!"
            )

        with msg_capnp.GetReqV1.from_bytes(msg.payload()) as _:
            pass

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this GetReqV1 as a Cap'n Proto payload"""
        msg = msg_capnp.GetReqV1.new_message()

        return (msg_capnp.MessageTypes.getReqV1, msg.to_bytes())


class GetResV1:
    """A response to requesting singular numeric values"""

    def __init__(self, value: int):
        self.value: int = value
        """Creates a new GetResV1 from the value that is responded to the get request"""

    @staticmethod
    def from_capnp(msg: Message):
        """Decodes the given message (as returned by Connection.read_msg() as a GetResV1"""
        res = GetResV1(0)

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.getResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as GetResV1!"
            )

        with msg_capnp.GetResV1.from_bytes(msg.payload()) as req:
            res.value = req.value

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this GetResV1 as a Cap'n Proto payload"""
        msg = msg_capnp.GetResV1.new_message()

        msg.value = self.value
        return (msg_capnp.MessageTypes.getResV1, msg.to_bytes())


class SetReqV1:
    """A request for setting a value"""

    def __init__(self, value: int):
        self.value: int = value
        """Creates a new SetReqV1 from the value that is requested to be set"""

    @staticmethod
    def from_capnp(msg):
        """Decodes the given message (as returned by Connection.read_msg() as a SetReqV1"""
        res = SetReqV1(0)

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.setReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as SetReqV1!"
            )

        with msg_capnp.SetReqV1.from_bytes(msg.payload()) as req:
            res.value = req.value

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this SetReqV1 as a Cap'n Proto payload"""
        msg = msg_capnp.SetReqV1.new_message()

        msg.value = self.value
        return (msg_capnp.MessageTypes.setReqV1, msg.to_bytes())


class UnregisterResolveReqV1:
    """A request payload for unregistering an addr to name mapping"""

    def __init__(self, uuid: str):
        """Creates a new unregister request for the given address"""
        self.uuid: str = uuid

    @staticmethod
    def from_capnp(msg : Message):
        """Decodes the given message (as returned by Connection.read_msg() as a ResolveResV1"""
        res = UnregisterResolveReqV1("")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.unregisterResolveReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as ResolveResV1!"
            )

        with msg_capnp.UnregisterResolveReqV1.from_bytes(msg.payload()) as req:
            res.uuid = (req.address.upper << 64) + req.address.lower
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this ResolveResV1 as a Cap'n'Proto payload, so that it can be used with Connection.subscribe()"""
        msg = msg_capnp.UnregisterResolveReqV1.new_message()

        (upper, lower) = uuid_to_u64_pair(self.uuid)
        msg.address.upper = upper
        msg.address.lower = lower
        return (msg_capnp.MessageTypes.unregisterResolveReqV1, msg.to_bytes())


class HistoryReqV1:
    """A HistoryReqV1 payload for requesting historic time-series data"""

    def __init__(
        self,
        address: str,
        start_time: int,
        end_time: int,
        interval_max: int,
        history_type: str,
    ):
        """Creates a HistoryReqV1

        :param address: Address of the metric to query
        :param start_time: Start of the interval to query
        :param end_time: End of the interval to query
        :interval_max: TODO DOCUMENT (leave as 0 for now)
        :history_type: Type of history, either \"aggregate\" (one Aggregate over the [start, end] or \""""
        self.address: str = address
        self.start_time: int = start_time
        self.end_time: int = end_time
        self.interval_max: int = interval_max
        self.history_type: str = history_type

    @staticmethod
    def from_capnp(msg : Message) -> "HistoryReqV1":
        """Decodes the given message (as returned by Connection.read_msg() as a HistoryReqV1"""
        res = HistoryReqV1("", 0, 0, 0, "")

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.historyReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as UnregisterResolveResV1!"
            )
        with msg_capnp.historyReqV1.from_bytes(msg.payload()) as req:
            res.address = str(UUID((req.address.upper << 64) + req.address.lower))
            res.start_time = req.startTime
            res.end_time = req.endTime
            res.interval_max = req.intervalMax
            res.history_type = req.historyType

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        msg = msg_capnp.HistoryReqV1.new_message()

        (upper, lower) = uuid_to_u64_pair(self.address)
        msg.address.upper = upper
        msg.address.lower = lower
        msg.startTime = self.start_time
        msg.endTime = self.end_time
        msg.intervalMax = self.interval_max
        msg.historyType = self.history_type

        return (msg_capnp.MessageTypes.historyReqV1, msg.to_bytes())


class Aggregate:
    """One Aggregated value from time-series data.

    :param minimum:      Minimum value in the interval given by the Aggregate
    :param maximum:      Maximum value in the interval given by the Aggregate
    :param sum:          Sum of all values in this Aggregate
    :param count:        Number of time-series values in this Aggregate
    :param integral:     Integral of the values in this Aggregate
    :param active_time:  fraction of time this Aggregate was active"""

    def __init__(
        self,
        minimum: float,
        maximum: float,
        sum: float,
        count: int,
        integral: float,
        active_time: int,
    ):
        """Creates a new aggregate"""
        self.minimum: float = minimum
        self.maximum: float = maximum
        self.sum: float = sum
        self.count: int = count
        self.integral: float = integral
        self.active_time: int = active_time

    @staticmethod
    def from_capnp(aggr) -> "Aggregate":
        ret = Aggregate(0, 0, 0, 0, 0, 0)

        ret.minimum = aggr.minimum
        ret.maximum = aggr.maximum
        ret.sum = aggr.sum
        ret.count = aggr.count
        ret.integral = aggr.integral
        ret.active_time = aggr.activeTime

        return ret

    def to_capnp(self):
        ret = msg_capnp.Aggregate.new_message()

        ret.minimum = self.minimum
        ret.maximum = self.maximum
        ret.sum = self.sum
        ret.count = self.count
        ret.integral = self.integral
        ret.active_time = self.active_time

        return ret

    def __str__(self) -> str:
        ret = (
            f"Minimum: {self.minimum}\n"
            + f"Maximum: {self.maximum}\n"
            + f"Sum: {self.sum}\n"
            + f"Count: {self.count}\n"
            + f"Integral: {self.integral}\n"
            + f"Active Time: {self.active_time}\n"
        )
        return ret


class History:
    """A history of time-series data, containing timestamps and either raw or pre-aggregated values"""

    def __init__(self):
        self.time_delta: list[int]
        self.raw: list[float]
        self.aggr: list[Aggregate]
        self.type: str

    @staticmethod
    def from_capnp(hist) -> "History":

        ret = History()
        which: str = hist.rawOrAgg.which()

        ret.time_delta = []
        for v in hist.timeDelta:
            ret.time_delta.append(v)
        if which == "value":
            ret.raw = []
            ret.type = "raw"
            for v in hist.rawOrAgg.value:
                ret.raw.append(v)
        elif which == "aggregate":
            ret.aggr = []
            ret.type = "aggregate"
            for v in hist.rawOrAgg.aggregate:
                ret.aggr.append(Aggregate.from_capnp(v))

        return ret


class HistoryResV1:
    """A response payload for a request for historic time-series data"""

    def __init__(self):
        self.hist: History

    @staticmethod
    def from_capnp(msg : Message) -> "HistoryResV1":
        ret = HistoryResV1()
        if msg.payload_type_as_int() != msg_capnp.MessageTypes.historyResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as HistoryResV1!"
            )

        with msg_capnp.HistoryResV1.from_bytes(msg.payload()) as res:
            ret.hist = History.from_capnp(res.hist)
        return ret


class FluxClassifyJobReqV1:
    def __init__(self, jobspec):
        """Creates a new FluxClassifyJobReqV1 from the given list of floats"""
        self.jobspec = jobspec

    @staticmethod
    def from_capnp(msg : Message):
        """Decodes the given message (as returned by Connection.read_msg() as a FluxClassifyJobReqV1"""
        res = FluxClassifyJobReqV1(None)

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.fluxClassifyJobReqV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as FluxClassifyJobReqV1!"
            )

        with msg_capnp.FluxClassifyJobReqV1.from_bytes(msg.payload()) as req:
            res.jobspec = req.jobspec

        return req

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this FluxClassifyJobReqV1 as a Cap'n Proto payload"""
        msg = msg_capnp.FluxClassifyJobReqV1.new_message()

        msg.jobspec = self.jobspec

        return (msg_capnp.MessageTypes.fluxClassifyJobReqV1, msg.to_bytes())


class FluxClassifyJobResV1:
    def __init__(self, result):
        """Creates a new FluxClassifyJobResV1 from the given list of floats"""
        self.result = result

    @staticmethod
    def from_capnp(msg : Message):
        """Decodes the given message (as returned by Connection.read_msg() as a FluxClassifyJobResV1"""
        res = FluxClassifyJobResV1(None)

        if msg.payload_type_as_int() != msg_capnp.MessageTypes.fluxClassifyJobResV1:
            raise RuntimeError(
                f"Can not interpret message of type {msg.payload_type_as_int()} as FluxClassifyJobResV1!"
            )

        with msg_capnp.FluxClassifyJobResV1.from_bytes(msg.payload()) as req:
            res.result = req.result

        return res

    def to_capnp(self) -> tuple[int, bytes]:
        """Encodes this FluxClassifyJobResV1 as a Cap'n Proto payload"""
        msg = msg_capnp.FluxClassifyJobResV1.new_message()

        msg.result = self.result

        return (msg_capnp.MessageTypes.fluxClassifyJobResV1, msg.to_bytes())


class UserDefinedPayload:
    def __init__(self, payload_type: int, payload: bytes):
        """Creates a user defined payload from payload_type and payload bytes"""

        if payload_type < 1 << 63:
            raise RuntimeError(
                "Trying to create a user-defined payload with a payload type < 1 << 63"
            )
        self.payload: bytes = payload
        self.payload_type: int = payload_type

    @staticmethod
    def from_capnp(msg : Message):
        res = UserDefinedPayload(msg.payload_type_as_int(), msg.payload())
        return res

    def to_capnp(self) -> tuple[int, bytes]:
        return (self.payload_type, self.payload)
