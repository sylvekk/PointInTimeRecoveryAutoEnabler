import logging
from botocore.exceptions import ClientError
import boto3
from os import environ
from helpers.db_helper import get_table_point_in_time_recovery_status

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    if 'client' not in event:
        client = boto3.client('dynamodb', environ['REGION'])
    else:
        client = event['client']
    logger.info('Starting the routine...')
    tables = client.list_tables()
    for table_name in tables['TableNames']:
        maybe_update_continuous_backups(table_name, client)


def maybe_update_continuous_backups(table_name, client):
    logger.info("Checking settings for table  " + table_name)
    try:
        if get_table_point_in_time_recovery_status(table_name, client) != 'ENABLED':
            logger.info("Setting backups for table " + table_name)
            client.update_continuous_backups(
                TableName=table_name,
                PointInTimeRecoverySpecification={
                    'PointInTimeRecoveryEnabled': True
                }
            )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.error(e.response['Error']['Message'])
        else:
            raise


def filter_table_names(table_names):
    filter_expression = 'TableNamePrefix-'
    filtered_names = []
    for table_name in table_names:
        if filter_expression in table_name:
            filtered_names.append(table_name)
    return filtered_names
