# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from proto import opaque_pb2 as proto_dot_opaque__pb2


class OpaqueAuthenticationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterUser = channel.unary_unary(
                '/opaque.OpaqueAuthentication/RegisterUser',
                request_serializer=proto_dot_opaque__pb2.RegistrationRequest.SerializeToString,
                response_deserializer=proto_dot_opaque__pb2.RegistrationResponse.FromString,
                )
        self.StoreRecord = channel.unary_unary(
                '/opaque.OpaqueAuthentication/StoreRecord',
                request_serializer=proto_dot_opaque__pb2.FinalizeRequest.SerializeToString,
                response_deserializer=proto_dot_opaque__pb2.FinalizeResponse.FromString,
                )
        self.RequestCredentials = channel.unary_unary(
                '/opaque.OpaqueAuthentication/RequestCredentials',
                request_serializer=proto_dot_opaque__pb2.CredentialRequest.SerializeToString,
                response_deserializer=proto_dot_opaque__pb2.CredentialResponse.FromString,
                )
        self.Authenticate = channel.unary_unary(
                '/opaque.OpaqueAuthentication/Authenticate',
                request_serializer=proto_dot_opaque__pb2.AuthenticationRequest.SerializeToString,
                response_deserializer=proto_dot_opaque__pb2.AuthenticationResponse.FromString,
                )
        self.VerifyToken = channel.unary_unary(
                '/opaque.OpaqueAuthentication/VerifyToken',
                request_serializer=proto_dot_opaque__pb2.VerifyTokenRequest.SerializeToString,
                response_deserializer=proto_dot_opaque__pb2.VerifyTokenResponse.FromString,
                )


class OpaqueAuthenticationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RegisterUser(self, request, context):
        """registration 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StoreRecord(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestCredentials(self, request, context):
        """credential recovery
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Authenticate(self, request, context):
        """Authentication
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VerifyToken(self, request, context):
        """token verification
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OpaqueAuthenticationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterUser,
                    request_deserializer=proto_dot_opaque__pb2.RegistrationRequest.FromString,
                    response_serializer=proto_dot_opaque__pb2.RegistrationResponse.SerializeToString,
            ),
            'StoreRecord': grpc.unary_unary_rpc_method_handler(
                    servicer.StoreRecord,
                    request_deserializer=proto_dot_opaque__pb2.FinalizeRequest.FromString,
                    response_serializer=proto_dot_opaque__pb2.FinalizeResponse.SerializeToString,
            ),
            'RequestCredentials': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestCredentials,
                    request_deserializer=proto_dot_opaque__pb2.CredentialRequest.FromString,
                    response_serializer=proto_dot_opaque__pb2.CredentialResponse.SerializeToString,
            ),
            'Authenticate': grpc.unary_unary_rpc_method_handler(
                    servicer.Authenticate,
                    request_deserializer=proto_dot_opaque__pb2.AuthenticationRequest.FromString,
                    response_serializer=proto_dot_opaque__pb2.AuthenticationResponse.SerializeToString,
            ),
            'VerifyToken': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyToken,
                    request_deserializer=proto_dot_opaque__pb2.VerifyTokenRequest.FromString,
                    response_serializer=proto_dot_opaque__pb2.VerifyTokenResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'opaque.OpaqueAuthentication', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OpaqueAuthentication(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RegisterUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/opaque.OpaqueAuthentication/RegisterUser',
            proto_dot_opaque__pb2.RegistrationRequest.SerializeToString,
            proto_dot_opaque__pb2.RegistrationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StoreRecord(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/opaque.OpaqueAuthentication/StoreRecord',
            proto_dot_opaque__pb2.FinalizeRequest.SerializeToString,
            proto_dot_opaque__pb2.FinalizeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequestCredentials(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/opaque.OpaqueAuthentication/RequestCredentials',
            proto_dot_opaque__pb2.CredentialRequest.SerializeToString,
            proto_dot_opaque__pb2.CredentialResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Authenticate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/opaque.OpaqueAuthentication/Authenticate',
            proto_dot_opaque__pb2.AuthenticationRequest.SerializeToString,
            proto_dot_opaque__pb2.AuthenticationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def VerifyToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/opaque.OpaqueAuthentication/VerifyToken',
            proto_dot_opaque__pb2.VerifyTokenRequest.SerializeToString,
            proto_dot_opaque__pb2.VerifyTokenResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
