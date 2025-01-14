import json
from botocore.config import Config
import boto3


def invoke_sagemaker_endpoint_async(endpoint_name, input_s3_location, region):
    config = Config(
        connect_timeout=180,
        retries={
            'max_attempts': 0,
            'mode': 'standard'
        }
    )
    runtime_sm_client = boto3.client(
        service_name='sagemaker-runtime', region_name=region, config=config)

    print(f'{endpoint_name} {input_s3_location}')
    results = runtime_sm_client.invoke_endpoint_async(
        EndpointName=endpoint_name,
        InputLocation=input_s3_location,
        InvocationTimeoutSeconds=500)

    return results


def invoke_sagemaker_endpoint(endpoint_name, endpoint_input, region):
    content_type = "application/json"
    # Serialize data for endpoint
    data = json.loads(json.dumps(endpoint_input))
    payload = json.dumps(data)

    config = Config(
        connect_timeout=180,
        retries={
            'max_attempts': 0,
            'mode': 'standard'
        }
    )

    runtime_sm_client = boto3.client(
        service_name='sagemaker-runtime', region_name=region, config=config)

    # Endpoint invocation
    response = runtime_sm_client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType=content_type,
        Body=payload)

    results = json.loads(response['Body'].read().decode())
    # results['s3_loc']
    return results
