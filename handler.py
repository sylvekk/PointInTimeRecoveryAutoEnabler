import logging
from botocore.exceptions import ClientError
import boto3
from os import environ

client = boto3.client('dynamodb', environ['REGION'])
dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    logger.info('Starting the routine...')
    tables = client.list_tables()
    for table_name in tables['TableNames']:
        maybe_update_continuous_backups(table_name)


def maybe_update_continuous_backups(table_name):
    logger.info("Checking settings for table  " + table_name)

    table_backup_settings = client.describe_continuous_backups(
        TableName=table_name
    )
    backup_state = table_backup_settings['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
    logger.info("Table's " + table_name + " backup is set to " + backup_state)

    try:
        if backup_state != 'ENABLED':
            logger.info("Enabling backups for table " + table_name)
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
