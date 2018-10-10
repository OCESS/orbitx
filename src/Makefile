proto:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cs493.proto

.PHONY: clean
clean:
	rm -f *_pb2.py *_pb2_grpc.py
