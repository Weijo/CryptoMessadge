.EXPORT_ALL_VARIABLES:

LD_LIBRARY_PATH = .

client:
	python3 client.py

server:
	python3 server.py

init:
	python3 -m grpc_tools.protoc -I=. proto/*.proto --python_out=. --grpc_python_out=.