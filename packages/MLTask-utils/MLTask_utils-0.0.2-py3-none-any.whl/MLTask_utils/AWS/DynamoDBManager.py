import os
from botocore.exceptions import ClientError
import boto3
from datetime import datetime
import uuid
from pprint import pprint
from .DynamoDBManagerUtils import deserialize_dynamodb_item


client = boto3.client('dynamodb')
# dynamodb = boto3.resource('dynamodb')
# user_table = dynamodb.Table(os.environ["USER_TABLE_NAME"])
# user_table.get_item
# user_table.put_item
user_table_name = os.environ["USER_TABLE_NAME"]
model_table_name = os.environ["MODEL_TABLE_NAME"]
preset_table_name = os.environ["PRESET_TABLE_NAME"]
task_execution_result_table_name = os.environ["TASK_EXECUTION_RESULT_TABLE_NAME"]
credit_transaction_table_name = os.environ["CREDIT_TRANSACTION_HISTORY_TABLE_NAME"]
# NOTE: Untested code
# def create_task_transaction(userID, task_cost, task_id):
#     client.put_item(TableName=credit_transaction_table_name, Item={
#                     'id': {'S': str(uuid.uuid4())},
#                     'userID': {'S': userID},
#                     'creditAmount': {'N': str(-task_cost)},
#                     'transactionType': {'S': "TASK_EXECUTION"},
#                     'context': {'M': {"taskID": {'S': task_id}}},
#                     'status': {'S': "COMPLETED"},
#                     'createdAt': {'S': datetime.now().isoformat()},
#                     'updatedAt': {'S': datetime.now().isoformat()},
#                     })


def basic_get_item_by_id(item_id, table_name):
    data = client.get_item(
        TableName=table_name,
        Key={"id": {'S': item_id}},
    )
    return deserialize_dynamodb_item(data['Item'])


def get_user_by_ID(user_id):
    return basic_get_item_by_id(user_id, user_table_name)


def get_task_by_ID(task_id):
    return basic_get_item_by_id(task_id, task_execution_result_table_name)


def get_model_by_ID(model_id):
    return basic_get_item_by_id(model_id, model_table_name)


def get_model_input_preset_by_ID(preset_id):
    return basic_get_item_by_id(preset_id, preset_table_name)


def adjust_user_credits(user_id, credit_increment_or_decrement, redeemable_credit_increment_or_decrement):
    client.update_item(
        TableName=user_table_name,
        Key={"id": {'S': user_id}},
        UpdateExpression="ADD #creditsAttr :creditIncrementValue, #redeemableCreditsAttr :redeemableCreditIncrementValue",
        ExpressionAttributeNames={
            "#creditsAttr": "credits",
            "#redeemableCreditsAttr": "redeemableCredits"
        },
        ExpressionAttributeValues={
            ":creditIncrementValue": {"N": str(credit_increment_or_decrement)},
            ":redeemableCreditIncrementValue": {"N": str(redeemable_credit_increment_or_decrement)}
        }
    )


def increment_preset_usage_user_preset_credit_and_create_transaction_for_it(preset_id, preset_version, user_credit_reward, userID, taskID):
    client.transact_write_items(TransactItems=[
        # increment preset usage
        {
            'Update': {
                'TableName': user_table_name,
                'Key': {"id": {"S": preset_id}},
                'UpdateExpression': "ADD #counterAttr :incrementValue",
                'ExpressionAttributeNames': {
                    "#counterAttr": "usage",
                },
                'ExpressionAttributeValues': {
                    ":incrementValue": {"N": "1"},
                },
            }
        },
        # increment user reward
        {
            'Update': {
                'Key': {"id": {"S": userID}},
                'TableName': user_table_name,
                'UpdateExpression': "ADD #counterAttr :incrementValue",
                'ExpressionAttributeNames': {
                    "#counterAttr": "redeemableCredits",
                },
                'ExpressionAttributeValues': {
                    ":incrementValue": {"N": str(user_credit_reward)},
                },
            }
        },
        # Create transaction
        {
            'Put': {
                'TableName': credit_transaction_table_name,
                'Item': {
                    'id': {'S': str(uuid.uuid4())},
                    'userID': {'S': userID},
                    'creditAmount': {'N': str(user_credit_reward)},
                    'transactionType': {'S': "PRESET_USAGE_CREDIT"},
                    'context': {'M': {"taskID": {'S': taskID}, "presetID": {'S': preset_id}, "presetVersion": {'S': preset_version}}},
                    'status': {'S': "COMPLETED"},
                    'createdAt': {'S': datetime.now().isoformat()},
                    'updatedAt': {'S': datetime.now().isoformat()},
                },
            }
        }
    ])
