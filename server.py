import grpc
import logging
from concurrent import futures
from proto import opaque_pb2_grpc
from proto import signalc_pb2_grpc
from Signal.SignalServer import SignalKeyDistribution
from Opaque.OpaqueServer import OpaqueAuthenticationServicer
from os.path import exists
from Util.RecordDB import RecordDB

logger = logging.getLogger(__name__)

OPAQUE_HOST = '0.0.0.0:50051'
SIGNAL_HOST = '0.0.0.0:50052'

CERTIFILE_FILE = './localhost.crt'
KEY_FILE = './localhost.key'
DB_FILE = 'server.db'

def serve(secure):
    if secure:
        with open(CERTIFILE_FILE, 'rb') as f:
            server_cert_key_chain = f.read()
        with open(KEY_FILE, 'rb') as f:
            server_private_key = f.read()

        # Create SSL server credentials
        credentials = grpc.ssl_server_credentials(
            [(server_private_key, server_cert_key_chain)],
            root_certificates=None,
            require_client_auth=False,
        )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    recordDB = RecordDB(DB_FILE)

    opaque_pb2_grpc.add_OpaqueAuthenticationServicer_to_server(OpaqueAuthenticationServicer(recordDB), server)
    if secure:
        server.add_secure_port(OPAQUE_HOST, credentials)
    else:
        server.add_insecure_port(OPAQUE_HOST)

    signalc_pb2_grpc.add_SignalKeyDistributionServicer_to_server(SignalKeyDistribution(), server)
    if secure:
        server.add_secure_port(SIGNAL_HOST, credentials)
    else:
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
    if not exists(CERTIFILE_FILE) and not exists(KEY_FILE):
        print("CERTIFICATE FILE MISSING. RUN `make cert`")
        print("Running server without SSL")
        serve(False)
    else:
        serve(True)
    