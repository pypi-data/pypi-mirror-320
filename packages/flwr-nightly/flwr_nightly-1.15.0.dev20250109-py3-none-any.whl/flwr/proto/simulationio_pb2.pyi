"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import flwr.proto.fab_pb2
import flwr.proto.message_pb2
import flwr.proto.run_pb2
import google.protobuf.descriptor
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class PullSimulationInputsRequest(google.protobuf.message.Message):
    """PullSimulationInputs messages"""
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    def __init__(self,
        ) -> None: ...
global___PullSimulationInputsRequest = PullSimulationInputsRequest

class PullSimulationInputsResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    CONTEXT_FIELD_NUMBER: builtins.int
    RUN_FIELD_NUMBER: builtins.int
    FAB_FIELD_NUMBER: builtins.int
    @property
    def context(self) -> flwr.proto.message_pb2.Context: ...
    @property
    def run(self) -> flwr.proto.run_pb2.Run: ...
    @property
    def fab(self) -> flwr.proto.fab_pb2.Fab: ...
    def __init__(self,
        *,
        context: typing.Optional[flwr.proto.message_pb2.Context] = ...,
        run: typing.Optional[flwr.proto.run_pb2.Run] = ...,
        fab: typing.Optional[flwr.proto.fab_pb2.Fab] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["context",b"context","fab",b"fab","run",b"run"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["context",b"context","fab",b"fab","run",b"run"]) -> None: ...
global___PullSimulationInputsResponse = PullSimulationInputsResponse

class PushSimulationOutputsRequest(google.protobuf.message.Message):
    """PushSimulationOutputs messages"""
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    RUN_ID_FIELD_NUMBER: builtins.int
    CONTEXT_FIELD_NUMBER: builtins.int
    run_id: builtins.int
    @property
    def context(self) -> flwr.proto.message_pb2.Context: ...
    def __init__(self,
        *,
        run_id: builtins.int = ...,
        context: typing.Optional[flwr.proto.message_pb2.Context] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["context",b"context"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["context",b"context","run_id",b"run_id"]) -> None: ...
global___PushSimulationOutputsRequest = PushSimulationOutputsRequest

class PushSimulationOutputsResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    def __init__(self,
        ) -> None: ...
global___PushSimulationOutputsResponse = PushSimulationOutputsResponse
