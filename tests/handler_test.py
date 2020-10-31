from os import environ
import pytest
from moto.dynamodb2 import mock_dynamodb2, dynamodb_backend2
import boto3
import handler
from helpers.db_helper import get_table_point_in_time_recovery_status
client = boto3.client('dynamodb', environ['REGION'])

@pytest.fixture()
def dynamodb():
    return dynamodb_backend2


@mock_dynamodb2
def test_handler__enables_point_in_time_recovery():
    create_table('table_1')
    create_table('table_2')
    create_table('table_3')
    create_table('table_4')

    assert get_table_point_in_time_recovery_status('table_1') == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_2') == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_3') == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_4') == 'DISABLED'

    handler.run({'client': client}, {})
    assert get_table_point_in_time_recovery_status('table_1') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_2') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_3') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_4') == 'ENABLED'

    disable_point_in_time_recovery('table_2')
    disable_point_in_time_recovery('table_4')
    assert get_table_point_in_time_recovery_status('table_1') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_2') == 'DISABLED'
    assert get_table_point_in_time_recovery_status('table_3') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_4') == 'DISABLED'

    handler.run({}, {})
    assert get_table_point_in_time_recovery_status('table_1') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_2') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_3') == 'ENABLED'
    assert get_table_point_in_time_recovery_status('table_4') == 'ENABLED'


def create_table(table_name):
    table = client.create_table(
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


def disable_point_in_time_recovery(table_name):
    client.update_continuous_backups(
        TableName=table_name,
        PointInTimeRecoverySpecification={
            'PointInTimeRecoveryEnabled': False
        }
    )
