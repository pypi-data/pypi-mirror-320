# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import server_pb2 as server__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in server_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class GnetcliStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SetupHostParams = channel.unary_unary(
                '/gnetcli.Gnetcli/SetupHostParams',
                request_serializer=server__pb2.HostParams.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.Exec = channel.unary_unary(
                '/gnetcli.Gnetcli/Exec',
                request_serializer=server__pb2.CMD.SerializeToString,
                response_deserializer=server__pb2.CMDResult.FromString,
                _registered_method=True)
        self.ExecChat = channel.stream_stream(
                '/gnetcli.Gnetcli/ExecChat',
                request_serializer=server__pb2.CMD.SerializeToString,
                response_deserializer=server__pb2.CMDResult.FromString,
                _registered_method=True)
        self.AddDevice = channel.unary_unary(
                '/gnetcli.Gnetcli/AddDevice',
                request_serializer=server__pb2.Device.SerializeToString,
                response_deserializer=server__pb2.DeviceResult.FromString,
                _registered_method=True)
        self.ExecNetconf = channel.unary_unary(
                '/gnetcli.Gnetcli/ExecNetconf',
                request_serializer=server__pb2.CMDNetconf.SerializeToString,
                response_deserializer=server__pb2.CMDResult.FromString,
                _registered_method=True)
        self.ExecNetconfChat = channel.stream_stream(
                '/gnetcli.Gnetcli/ExecNetconfChat',
                request_serializer=server__pb2.CMDNetconf.SerializeToString,
                response_deserializer=server__pb2.CMDResult.FromString,
                _registered_method=True)
        self.Download = channel.unary_unary(
                '/gnetcli.Gnetcli/Download',
                request_serializer=server__pb2.FileDownloadRequest.SerializeToString,
                response_deserializer=server__pb2.FilesResult.FromString,
                _registered_method=True)
        self.Upload = channel.unary_unary(
                '/gnetcli.Gnetcli/Upload',
                request_serializer=server__pb2.FileUploadRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)


class GnetcliServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SetupHostParams(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Exec(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecChat(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddDevice(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecNetconf(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecNetconfChat(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Download(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Upload(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GnetcliServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SetupHostParams': grpc.unary_unary_rpc_method_handler(
                    servicer.SetupHostParams,
                    request_deserializer=server__pb2.HostParams.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Exec': grpc.unary_unary_rpc_method_handler(
                    servicer.Exec,
                    request_deserializer=server__pb2.CMD.FromString,
                    response_serializer=server__pb2.CMDResult.SerializeToString,
            ),
            'ExecChat': grpc.stream_stream_rpc_method_handler(
                    servicer.ExecChat,
                    request_deserializer=server__pb2.CMD.FromString,
                    response_serializer=server__pb2.CMDResult.SerializeToString,
            ),
            'AddDevice': grpc.unary_unary_rpc_method_handler(
                    servicer.AddDevice,
                    request_deserializer=server__pb2.Device.FromString,
                    response_serializer=server__pb2.DeviceResult.SerializeToString,
            ),
            'ExecNetconf': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecNetconf,
                    request_deserializer=server__pb2.CMDNetconf.FromString,
                    response_serializer=server__pb2.CMDResult.SerializeToString,
            ),
            'ExecNetconfChat': grpc.stream_stream_rpc_method_handler(
                    servicer.ExecNetconfChat,
                    request_deserializer=server__pb2.CMDNetconf.FromString,
                    response_serializer=server__pb2.CMDResult.SerializeToString,
            ),
            'Download': grpc.unary_unary_rpc_method_handler(
                    servicer.Download,
                    request_deserializer=server__pb2.FileDownloadRequest.FromString,
                    response_serializer=server__pb2.FilesResult.SerializeToString,
            ),
            'Upload': grpc.unary_unary_rpc_method_handler(
                    servicer.Upload,
                    request_deserializer=server__pb2.FileUploadRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'gnetcli.Gnetcli', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('gnetcli.Gnetcli', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Gnetcli(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SetupHostParams(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/gnetcli.Gnetcli/SetupHostParams',
            server__pb2.HostParams.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Exec(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/gnetcli.Gnetcli/Exec',
            server__pb2.CMD.SerializeToString,
            server__pb2.CMDResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ExecChat(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/gnetcli.Gnetcli/ExecChat',
            server__pb2.CMD.SerializeToString,
            server__pb2.CMDResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddDevice(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/gnetcli.Gnetcli/AddDevice',
            server__pb2.Device.SerializeToString,
            server__pb2.DeviceResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ExecNetconf(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/gnetcli.Gnetcli/ExecNetconf',
            server__pb2.CMDNetconf.SerializeToString,
            server__pb2.CMDResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ExecNetconfChat(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/gnetcli.Gnetcli/ExecNetconfChat',
            server__pb2.CMDNetconf.SerializeToString,
            server__pb2.CMDResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Download(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/gnetcli.Gnetcli/Download',
            server__pb2.FileDownloadRequest.SerializeToString,
            server__pb2.FilesResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Upload(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/gnetcli.Gnetcli/Upload',
            server__pb2.FileUploadRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
