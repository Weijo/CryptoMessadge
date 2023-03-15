.EXPORT_ALL_VARIABLES:

LD_LIBRARY_PATH = .
GRPC_TRACE = all

client:
	python3 client.py

server:
	python3 server.py

init:
	python3 -m grpc_tools.protoc -I=. proto/*.proto --python_out=. --grpc_python_out=.	

cert:
	openssl req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 -keyout RootCA.key -out RootCA.pem -subj "/C=US/CN=Example-Root-CA"
	openssl x509 -outform pem -in RootCA.pem -out RootCA.crt
	openssl req -new -nodes -newkey rsa:2048 -keyout localhost.key -out localhost.csr -subj "/C=US/ST=YourState/L=YourCity/O=Example-Certificates/CN=localhost.local"
	openssl x509 -req -sha256 -days 1024 -in localhost.csr -CA RootCA.pem -CAkey RootCA.key -CAcreateserial -extfile domains.ext -out localhost.crt

clear_cert:
	rm -f RootCA.pem RootCA.crt localhost.crt localhost.csr RootCA.key key.pem RootCA.srl certificate.pem

clear_json:
	rm -f *.json

clean: clear_cert clear_json
	