# gRPC Gateway Support

This repo generates the openapiv2 python bindings for gRPC Gateway
[gRPC Gateway](https://github.com/grpc-ecosystem/grpc-gateway) protoc annotations.

This package depends on `googleapis-common-protos` to provide `google.api.annotations_pb2` and others
that the generated code will depend on.


## Usage

```shell
pip install grpc-gateway-protoc-openapiv2
```

## Upgrade to new grpc-gateway release

1. Run `./bump_version.sh 2.25.1` (replace 2.25.1 with the corresponding grpc-gateway release)
2. Verify changes and commit
3. Build and distribute


## Building

1. Run `make init`
2. Run `make build` to generate the code from grpc-gateway and build the package
3. Run `pip install dist/grpc-gateway-protoc-openapiv2-2.25.1-py3-none-any.whl` to install in the current Python distribution
