"""
Defines a Skyramp client, which can be used to interact with a cluster.
"""

import ctypes
import json
from typing import Optional, Any

from skyramp.utils import _library
from skyramp.test_response2 import ResponseV2
from skyramp.docker_client import _DockerClient
from skyramp.k8s_client import _K8SClient
from skyramp.local_client import _LocalClient

def _client(kubeconfig_path: Optional[str]="",
            kubeconfig_context: Optional[str]="",
            cluster_name: Optional[str]="",
            namespace: Optional[str]="",
            worker_address: Optional[str]="",
            docker_network: Optional[str]="",
            docker_skyramp_port: Optional[int]=None,
            ):
    """
    Create Skyramp Client
    if worker_address is provided, it creates a docker client
    if one of kubeconfig_path, k8s_context, cluster_name, and/or namespace is given,
    it creates a k8s client
    """
    if docker_skyramp_port is not None:
        worker_address = f"localhost:{docker_skyramp_port}"

    if worker_address != "" and (namespace != "" or
             kubeconfig_path != "" or kubeconfig_context != "" or cluster_name != ""):
        raise Exception("Address cannot be used with k8s related parameters")

    if worker_address == "" and namespace == "" and \
            kubeconfig_path  == "" and kubeconfig_context == "" and cluster_name == "":
        return _LocalClient()

    if worker_address != "":
        return _DockerClient(worker_address, network_name=docker_network)

    return _K8SClient(kubeconfig_path, cluster_name, kubeconfig_context, namespace)

@staticmethod
def check_status_code(response: ResponseV2, expected_status: str) -> bool:
    """
    Checks if the response's status code matches the expected status code 
    (with support for wildcards).
    """
    try:
        dic = response.as_response_dict()
        data = json.dumps(dic)  # Convert dictionary to JSON string instead of YAML

        func = _library.checkStatusCodeWrapper
        func.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        func.restype = ctypes.c_char_p
        args = [
            data.encode(),
            expected_status.encode(),
        ]
        result = func(*args)

        if result is None:
            raise Exception('No response from wrapper')

        parsed = json.loads(result.decode('utf-8'))

        if not isinstance(parsed, dict):
            raise Exception('Invalid response format from wrapper')

        if 'error' in parsed:
            raise Exception(parsed['error'])

        if 'result' in parsed:
            return parsed['result']

        raise Exception('Response missing both result and error fields')

    except Exception as err:
        print(f"Error in checkStatusCode: {str(err)}")
        raise  # Re-throw to allow caller to handle errors

@staticmethod
def get_response_value(response: ResponseV2, json_path: str) -> Optional[Any]:
    """
    get value from response body using json_path
    """
    func = _library.getJSONValueWrapper
    func.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
    ]
    func.restype = ctypes.c_char_p
    args = [
        response.response_body.encode(),
        json_path.encode(),
    ]
    result = func(*args)

    if result is None:
        return None

    try:
        # Decode the bytes to string
        json_str = result.decode('utf-8')
        # Parse the JSON string
        parsed = json.loads(json_str)

        # Handle different types
        if isinstance(parsed, dict) and "type" in parsed and "value" in parsed:
            value_type = parsed["type"]
            value = parsed["value"]

            # Return None for complex types (arrays and objects)
            if value_type in ["array", "object" , "[]interface {}"]:
                return None

            ret = value
            # Cast to appropriate Python type
            if value_type == "string":
                ret =  str(value)
            elif value_type == "number":
                ret = float(value) if '.' in str(value) else int(value)
            elif value_type == "boolean":
                ret = bool(value)
            elif value_type == "null":
                ret = None
            return ret
        return parsed
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as exception:
        print(f"Error processing JSONValue: {exception}")
        return None

@staticmethod
def check_schema(response: "ResponseV2", expected_schema: [dict, str]) -> bool:
    """
    Validates the response body against the expected schema.

    :param response: The response object containing the JSON body.
    :param expected_schema: The JSON schema to validate against.
    :return: True if the schema matches, False otherwise.
    """
    func = _library.checkSchemaWrapper
    func.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
    ]
    func.restype = ctypes.c_char_p
    args = [
        response.response_body.encode(),
        expected_schema.encode(),
    ]
    result = func(*args)

    if result is None:
        return False

    try:
        # Decode the bytes to string
        json_str = result.decode('utf-8')
        # Parse the JSON string
        parsed = json.loads(json_str)
        return parsed['result']
    except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
        # return false for other errors
        return False
