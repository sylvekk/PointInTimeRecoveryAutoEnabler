from os import environ
from moto import mock_dynamodb2
import boto3
import handler
from helpers.db_helper import get_table_point_in_time_recovery_status


@mock_dynamodb2
def test_handler__enables_point_in_time_recovery():
    client = boto3.client('dynamodb', environ['REGION'])
    dynamodb = boto3.resource('dynamodb', environ['REGION'])
    create_table('table_1', dynamodb)
    create_table('table_2', dynamodb)
    create_table('table_3', dynamodb)
    create_table('table_4', dynamodb)

    assert get_table_point_in_time_recovery_status('table_1', client) == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_2', client) == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_3', client) == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_4', client) == 'DISABLED'

    handler.run({'client': client}, {})
    assert get_table_point_in_time_recovery_status('table_1', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_2', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_3', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_4', client) == 'ENABLED'

    disable_point_in_time_recovery('table_2', client)
    disable_point_in_time_recovery('table_4', client)
    assert get_table_point_in_time_recovery_status('table_1', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_2', client) == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_3', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_4', client) == 'DISABLED'

    handler.run({'client': client}, {})
    assert get_table_point_in_time_recovery_status('table_1', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_2', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_3', client) == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_4', client) == 'ENABLED'


def create_table(table_name, dynamodb):
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'codename',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'codename',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return table


def disable_point_in_time_recovery(table_name, client):
    client.update_continuous_backups(
        TableName=table_name,
        PointInTimeRecoverySpecification={
            'PointInTimeRecoveryEnabled': False
        }
    )
