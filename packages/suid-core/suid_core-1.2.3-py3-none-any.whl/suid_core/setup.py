#python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. system.proto
from grpc.tools import protoc

def generate_protos():
	protoc.main(
		(
			'',
			'-I.',
			'--python_out=.',
			'--pyi_out=.',
			'--grpc_python_out=.',
			'./system.proto'
		)
	)