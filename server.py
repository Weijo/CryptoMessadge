import grpc
import logging
from concurrent import futures
from proto import opaque_pb2_grpc
from proto import signalc_pb2_grpc
from Signal.SignalServer import SignalKeyDistribution
from Opaque.OpaqueServer import OpaqueAuthenticationServicer

logger = logging.getLogger(__name__)

OPAQUE_HOST = '0.0.0.0:50051'
SIGNAL_HOST = '0.0.0.0:50052'

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    opaque_pb2_grpc.add_OpaqueAuthenticationServicer_to_server(OpaqueAuthenticationServicer(), server)
    server.add_insecure_port(OPAQUE_HOST)

    signalc_pb2_grpc.add_SignalKeyDistributionServicer_to_server(SignalKeyDistribution(), server)
    server.add_insecure_port(SIGNAL_HOST)
    
    logger.info("Server has started")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(5)
        print("\nExiting...")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serve()
    