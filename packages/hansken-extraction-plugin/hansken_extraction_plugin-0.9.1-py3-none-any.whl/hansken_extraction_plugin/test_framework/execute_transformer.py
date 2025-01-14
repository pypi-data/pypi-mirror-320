#!/usr/bin/python3
"""Execute a transformer function of a running extraction plugin."""
import argparse
from typing import Dict, List
import uuid

from hansken.util import Vector

from hansken_extraction_plugin.buildkit.color_log import _log, colored_logging
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcTransformerArgument
from hansken_extraction_plugin.framework.ExtractionPluginService_pb2_grpc import ExtractionPluginServiceStub
from hansken_extraction_plugin.framework.PrimitiveMessages_pb2 import RpcString
from hansken_extraction_plugin.runtime import pack, unpack
from hansken_extraction_plugin.test_framework.validator import DockerTestPluginRunner


def _transform(running_plugin: ExtractionPluginServiceStub, method_name: str, arguments: Dict[str, str]) -> Vector:
    """Connect and execute grpc request to transform function of a running extraction plugin."""
    _log('Executing transformer')
    # TODO HANSKEN-21540: Should be changed to support multiple argument types.
    args = {key: RpcTransformerArgument(string=RpcString(value=value)) for (key, value) in arguments.items()}
    request = pack.transformer_request(method_name=method_name, arguments=args)
    transformer_response = running_plugin.transform(request)
    return unpack.transformer_response(transformer_response)


def _transformer_args(named_arguments: List[str]) -> Dict[str, str]:
    """
    Convert a list of parameter argument pairs to a dictionary of named arguments.

    For example: [a, b, c, '5'] -> {'a': 'b', 'c': '5'}
    """
    if len(named_arguments) < 2:
        raise ValueError('At least one pair of arguments is required.')
    if len(named_arguments) % 2 != 0:
        raise ValueError('Uneven number of arguments, arguments should come in pairs.')

    parameters = named_arguments[0::2]
    arguments = named_arguments[1::2]
    return dict(zip(parameters, arguments))


def main():
    """Execute transformer function of an extraction plugin."""
    with colored_logging('Executor'):
        parser = argparse.ArgumentParser(prog='execute_transformer',
                                         usage='%(prog)s [options]',
                                         description='A script to execute a transformer of a running plugin.')
        parser.add_argument('docker_image', help='Docker image containing the plugin.')
        parser.add_argument('method_name', type=str, help='Method name of the transformer to execute.')
        parser.add_argument('arguments', type=str, nargs='+',
                            help='Pairs of named arguments to provide to the transformer function; e.g. weight 15.')
        parser.add_argument('-t', '--timeout', default=30.0, type=float,
                            help='Time (in seconds) the framework has to wait for the Docker container to be ready.')

        args = parser.parse_args()

        plugin_runner = DockerTestPluginRunner(args.docker_image, args.timeout)
        # Start the plugin as Docker container and invoke a transformer with the provided arguments.
        container = f'executing_transformer_{uuid.uuid4()}'
        with plugin_runner.run_and_connect(container_name=container) as plugin_service_stub:
            result = _transform(plugin_service_stub, args.method_name, _transformer_args(args.arguments))
        print(f'Result of transform function: \n\n{result}')


if __name__ == '__main__':
    main()
