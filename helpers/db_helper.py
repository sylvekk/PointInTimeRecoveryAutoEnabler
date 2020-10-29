import logging
import boto3
from os import environ

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_table_backup_state(table_name, client):
    logger.info("Getting table's " + table_name + " backup state ")
    return client.describe_continuous_backups(
        TableName=table_name
    )


def get_table_point_in_time_recovery_status(table_name, client):
    table_backup_settings = get_table_backup_state(table_name, client)
    logger.info("Getting table's " + table_name + " point in time recovery state ")
    return table_backup_settings['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
