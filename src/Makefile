build:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cs493.proto

install:
	pip install -r ../requirements.txt
	jupyter nbextension enable --py --sys-prefix appmode
	jupyter serverextension enable --py --sys-prefix appmode

.PHONY: clean
clean:
	rm -f *_pb2.py *_pb2_grpc.py

.PHONY: format
format:
	python -m autopep8 -j 0 --recursive --in-place .
