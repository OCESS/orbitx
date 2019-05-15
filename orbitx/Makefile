build:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. orbitx.proto

install:
	pip install -r ../requirements.txt

test:
	python ../test.py

.PHONY: clean
clean:
	rm -f *_pb2.py *_pb2_grpc.py
	rm -rf dist build

.PHONY: format
format:
	python -m autopep8 -j 0 --recursive --in-place .
