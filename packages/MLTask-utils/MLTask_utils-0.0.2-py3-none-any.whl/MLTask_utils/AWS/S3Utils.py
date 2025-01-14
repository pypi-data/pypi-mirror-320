from pprint import pprint
import uuid
import requests
import boto3
import os
import base64
import json

s3 = boto3.client('s3')


def upload_to_s3_and_get_public_url(access_key_id, secret_access_key, bucket_name, filepath):
  # AWS credentials
  file_name_with_extension = os.path.basename(filepath)
  s3 = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
  # # Upload file to S3
  s3.upload_file(filepath, bucket_name, file_name_with_extension)
  s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=file_name_with_extension)
  
  # print(f'{filepath} uploaded to S3 as {file_name_with_extension}')
  # url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': file_name_with_extension}, ExpiresIn=3600)
  return f'https://{bucket_name}.s3.amazonaws.com/{file_name_with_extension}'

def final_user_folder_from_access_level(access_level, userId, userCognitoId):
    final_user_id = userCognitoId
    # user id for public
    if access_level == "public":
        final_user_id = userId
    return final_user_id


def get_s3_link(s3_key, bucket_name=os.environ.get('STORAGE_DTASK_STORAGE_BUCKETNAME')):
    # #region = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
    # s3_link = f"https://s3-{region}.amazonaws.com/{bucket_name}/{s3_key}"
    # return s3_link
    params = {'Bucket': bucket_name, 'Key': s3_key}
    url = s3.generate_presigned_url(
        'get_object', Params=params, ExpiresIn=3600)
    return url


def get_full_s3_key_from_cognito_and_amplify_key(access_level, userId, userCognitoId, s3Key):
    user_folder = final_user_folder_from_access_level(
        access_level, userId, userCognitoId)
    return f"{access_level}/{user_folder}/{s3Key}"


def download_from_s3_from_key(full_s3_key, destination):
    print(f"downloading {full_s3_key} to {destination}")
    if os.path.exists(destination):
        print(f"File already exists at {destination} retuning.....")
        return
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    try:
        print(f"download key = {full_s3_key}")
        s3.download_file(
            os.environ.get('STORAGE_DTASK_STORAGE_BUCKETNAME'), full_s3_key, destination)
        print(f"downloaded file at {destination}")
    except Exception as error:
        print("failed to download file with error:")
        pprint(error)
        raise error


def acl_from_access_level(access_level):
    acl = "private"
    if access_level == "public":
        acl = "public-read"
    return acl


def upload_to_s3_for_user_from_dict(access_level, dict, userId, cognitoId, workspaceId, taskId, filename=f'{str(uuid.uuid4())}.json'):
    """
    Uploads a dictionary as a JSON object to an S3 bucket.

    Returns:
        dict: A dictionary containing the uploaded file information.
            The dictionary has two keys:
            - 'key': The S3 URL of the uploaded file.
            - 'amplifyKey': The Amplify key for the uploaded file.

    Raises:
        Exception: If an error occurs during the S3 upload.

    """

    s3Key = filename
    user_folder = final_user_folder_from_access_level(
        access_level, userId, cognitoId)
    filePath = f"{access_level}/{user_folder}/{workspaceId}/{taskId}/{s3Key}"
    json_string = json.dumps(dict)
    bucket = os.environ.get('STORAGE_DTASK_STORAGE_BUCKETNAME')
    try:
        s3.put_object(
            Bucket=bucket,
            Key=filePath,
            ACL=acl_from_access_level(access_level),
            Body=json_string,
        )

        return {"key": f's3://{bucket}/{filePath}', "amplifyKey": f"{workspaceId}/{taskId}/{s3Key}"}
    except Exception as error:
        print("error = " + str(error))
        raise error
        # return error


def upload_to_s3_for_user_from_link(access_level, link, userId, cognitoId, workspaceId, taskId, extension="wav", filename=None):
    if filename is None:
        filename = str(uuid.uuid4())
    user_folder = final_user_folder_from_access_level(
        access_level, userId, cognitoId)

    response = requests.get(link)
    image_data = response.content
    s3Key = f"{filename}.{extension}"
    # filePath = f"private/{userFolder}/{taskId}/{s3Key}"
    filePath = f"{access_level}/{user_folder}/{workspaceId}/{taskId}/{s3Key}"
    print(acl_from_access_level(access_level))
    try:
        s3.put_object(
            Bucket=os.environ.get('STORAGE_DTASK_STORAGE_BUCKETNAME'),
            Key=filePath,
            ACL=acl_from_access_level(access_level),
            Body=image_data
        )

        return f"{workspaceId}/{taskId}/{s3Key}"
    except Exception as error:
        print("error = " + str(error))
        return error


def upload_to_s3_for_user_from_local_file(access_level, path, userId, cognitoId, workspaceId, taskId, filename=None):
    if not filename:
        filename = str(uuid.uuid4())
    user_folder = final_user_folder_from_access_level(
        access_level, userId, cognitoId)
    try:
        extension = os.path.splitext(path)[1][1:]
        s3_key = f"{filename}.{extension}"
        file_path = f"{access_level}/{user_folder}/{workspaceId}/{taskId}/{s3_key}"

        with open(path, 'rb') as file:
            s3.put_object(
                Bucket=os.environ.get('STORAGE_DTASK_STORAGE_BUCKETNAME'),
                Key=file_path,
                ACL=acl_from_access_level(access_level),
                Body=file
            )

        return f"{workspaceId}/{taskId}/{s3_key}"
    except Exception as error:
        print(f"error = {str(error)}")
        return error


def delete_s3_file(bucket_name, object_key):
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        print("File deleted successfully")
    except Exception as e:
        print(f"Error deleting file: {e}")
        raise e


def convert_url_data_to_file(data_url, file_path):
    # Split the data URL into two parts: the metadata and the data
    metadata, base64_data = data_url.split(",")

    try:
        # Convert the base64-encoded data to bytes
        data = base64.b64decode(base64_data)
        # Write the data to a local file
        with open(file_path, 'wb') as file:
            file.write(data)
        print("The file was saved!")
    except Exception as err:
        print("FAILED TO save!")
        print(err)


def save_url_data_to_temp_file(data_url, extension):
    file_path = f"/tmp/file_{uuid.uuid4()}.{extension}"
    save_url_data_to_file(data_url, file_path)


def save_url_data_to_file(data_url, file_path):
    # Split the data URL into two parts: the metadata and the data
    metadata, base64_data = data_url.split(",")

    try:
        # Convert the base64-encoded data to bytes
        data = base64.b64decode(base64_data)
        # Write the data to a local file
        with open(file_path, 'wb') as file:
            file.write(data)

        print(f"The file was saved here! {file_path}")
        return file_path
    except Exception as err:
        print("FAILED TO save!")
        print(err)
