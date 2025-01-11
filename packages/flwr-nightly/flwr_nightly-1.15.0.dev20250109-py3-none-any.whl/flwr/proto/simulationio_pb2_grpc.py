# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from flwr.proto import log_pb2 as flwr_dot_proto_dot_log__pb2
from flwr.proto import run_pb2 as flwr_dot_proto_dot_run__pb2
from flwr.proto import simulationio_pb2 as flwr_dot_proto_dot_simulationio__pb2


class SimulationIoStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PullSimulationInputs = channel.unary_unary(
                '/flwr.proto.SimulationIo/PullSimulationInputs',
                request_serializer=flwr_dot_proto_dot_simulationio__pb2.PullSimulationInputsRequest.SerializeToString,
                response_deserializer=flwr_dot_proto_dot_simulationio__pb2.PullSimulationInputsResponse.FromString,
                )
        self.PushSimulationOutputs = channel.unary_unary(
                '/flwr.proto.SimulationIo/PushSimulationOutputs',
                request_serializer=flwr_dot_proto_dot_simulationio__pb2.PushSimulationOutputsRequest.SerializeToString,
                response_deserializer=flwr_dot_proto_dot_simulationio__pb2.PushSimulationOutputsResponse.FromString,
                )
        self.UpdateRunStatus = channel.unary_unary(
                '/flwr.proto.SimulationIo/UpdateRunStatus',
                request_serializer=flwr_dot_proto_dot_run__pb2.UpdateRunStatusRequest.SerializeToString,
                response_deserializer=flwr_dot_proto_dot_run__pb2.UpdateRunStatusResponse.FromString,
                )
        self.PushLogs = channel.unary_unary(
                '/flwr.proto.SimulationIo/PushLogs',
                request_serializer=flwr_dot_proto_dot_log__pb2.PushLogsRequest.SerializeToString,
                response_deserializer=flwr_dot_proto_dot_log__pb2.PushLogsResponse.FromString,
                )
        self.GetFederationOptions = channel.unary_unary(
                '/flwr.proto.SimulationIo/GetFederationOptions',
                request_serializer=flwr_dot_proto_dot_run__pb2.GetFederationOptionsRequest.SerializeToString,
                response_deserializer=flwr_dot_proto_dot_run__pb2.GetFederationOptionsResponse.FromString,
                )
        self.GetRunStatus = channel.unary_unary(
                '/flwr.proto.SimulationIo/GetRunStatus',
                request_serializer=flwr_dot_proto_dot_run__pb2.GetRunStatusRequest.SerializeToString,
                response_deserializer=flwr_dot_proto_dot_run__pb2.GetRunStatusResponse.FromString,
                )


class SimulationIoServicer(object):
    """Missing associated documentation comment in .proto file."""

    def PullSimulationInputs(self, request, context):
        """Pull Simulation inputs
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PushSimulationOutputs(self, request, context):
        """Push Simulation outputs
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateRunStatus(self, request, context):
        """Update the status of a given run
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PushLogs(self, request, context):
        """Push ServerApp logs
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFederationOptions(self, request, context):
        """Get Federation Options
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetRunStatus(self, request, context):
        """Get Run Status
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SimulationIoServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PullSimulationInputs': grpc.unary_unary_rpc_method_handler(
                    servicer.PullSimulationInputs,
                    request_deserializer=flwr_dot_proto_dot_simulationio__pb2.PullSimulationInputsRequest.FromString,
                    response_serializer=flwr_dot_proto_dot_simulationio__pb2.PullSimulationInputsResponse.SerializeToString,
            ),
            'PushSimulationOutputs': grpc.unary_unary_rpc_method_handler(
                    servicer.PushSimulationOutputs,
                    request_deserializer=flwr_dot_proto_dot_simulationio__pb2.PushSimulationOutputsRequest.FromString,
                    response_serializer=flwr_dot_proto_dot_simulationio__pb2.PushSimulationOutputsResponse.SerializeToString,
            ),
            'UpdateRunStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateRunStatus,
                    request_deserializer=flwr_dot_proto_dot_run__pb2.UpdateRunStatusRequest.FromString,
                    response_serializer=flwr_dot_proto_dot_run__pb2.UpdateRunStatusResponse.SerializeToString,
            ),
            'PushLogs': grpc.unary_unary_rpc_method_handler(
                    servicer.PushLogs,
                    request_deserializer=flwr_dot_proto_dot_log__pb2.PushLogsRequest.FromString,
                    response_serializer=flwr_dot_proto_dot_log__pb2.PushLogsResponse.SerializeToString,
            ),
            'GetFederationOptions': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFederationOptions,
                    request_deserializer=flwr_dot_proto_dot_run__pb2.GetFederationOptionsRequest.FromString,
                    response_serializer=flwr_dot_proto_dot_run__pb2.GetFederationOptionsResponse.SerializeToString,
            ),
            'GetRunStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetRunStatus,
                    request_deserializer=flwr_dot_proto_dot_run__pb2.GetRunStatusRequest.FromString,
                    response_serializer=flwr_dot_proto_dot_run__pb2.GetRunStatusResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'flwr.proto.SimulationIo', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SimulationIo(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def PullSimulationInputs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flwr.proto.SimulationIo/PullSimulationInputs',
            flwr_dot_proto_dot_simulationio__pb2.PullSimulationInputsRequest.SerializeToString,
            flwr_dot_proto_dot_simulationio__pb2.PullSimulationInputsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PushSimulationOutputs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flwr.proto.SimulationIo/PushSimulationOutputs',
            flwr_dot_proto_dot_simulationio__pb2.PushSimulationOutputsRequest.SerializeToString,
            flwr_dot_proto_dot_simulationio__pb2.PushSimulationOutputsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateRunStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flwr.proto.SimulationIo/UpdateRunStatus',
            flwr_dot_proto_dot_run__pb2.UpdateRunStatusRequest.SerializeToString,
            flwr_dot_proto_dot_run__pb2.UpdateRunStatusResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PushLogs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flwr.proto.SimulationIo/PushLogs',
            flwr_dot_proto_dot_log__pb2.PushLogsRequest.SerializeToString,
            flwr_dot_proto_dot_log__pb2.PushLogsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetFederationOptions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flwr.proto.SimulationIo/GetFederationOptions',
            flwr_dot_proto_dot_run__pb2.GetFederationOptionsRequest.SerializeToString,
            flwr_dot_proto_dot_run__pb2.GetFederationOptionsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetRunStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flwr.proto.SimulationIo/GetRunStatus',
            flwr_dot_proto_dot_run__pb2.GetRunStatusRequest.SerializeToString,
            flwr_dot_proto_dot_run__pb2.GetRunStatusResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
