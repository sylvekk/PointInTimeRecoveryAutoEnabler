<!--
title: 'Python CRON JOB Lambda for AWS Serverless REST API with DynamoDB'
description: 'This lambda ensures point in time recovery is enabled on all DynamoDB tales'
layout: Doc
framework: v1
platform: AWS
language: Python
authorLink: 'https://github.com/sylvekk'
authorName: 'Sylwester Karwacki'
authorAvatar: 'https://en.gravatar.com/userimage/151138712/3517d1908c28e1b26b2d3cb723921630.jpeg'
-->
## Python CRON JOB Lambda for AWS Serverless REST API

This lambda ensures point in time recovery is enabled on all DynamoDB tales

## Build with Serverless - serverless.yml
#### What is Serverless
[The Serverless is an open-source framework that you can use to build serverless applications on AWS.](https://www.serverless.com/)

#### Setup
If not installed already, install aws cli and serverless

[AWs CLI installation process](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

[SERVERLESS installation process](https://www.serverless.com/framework/docs/getting-started/)

or as a bear minimum run this command to install serverless
```bash
npm install -g serverless
```

Once AWS CLI and SERVERLESS is installed, clone this repo

#### Deployment
This repo does not consider any CI deployment, and only focuses on the standard serverless deploy

Run the standard command to deploy to AWS directly 

```bash
serverless deploy
```

To deploy to specific environment run command below 

```bash
serverless deploy --stage development
```
where 'development' is the environment you want to deploy to



##### What can be customised?

1. The frequency on which the lambda runs is specified in the ```serverless.yml```
Change below code to adjust to your needs:
``` 
functions:
  cron:
    handler: handler.run
    events:
      - schedule: rate(2 hours) #this line specifies the frequency, you can change it to i.e. 1 minute, 2 hours etc
```

2. If you do not want to check all tables you can remove the code that fetches all tables, 
and replace the result with an array of names

``` 
def run(event, context):
    logger.info('Starting the routine...')
    tables = client.list_tables() #remove if you want to specify tables manually
    for table_name in tables['TableNames']: # givethe array of names here
        maybe_update_continuous_backups(table_name)
```

Example
``` 
def run(event, context):
    logger.info('Starting the routine...')
    for table_name in ['TableNames1', 'TableNames2', 'TableNames3']:
        maybe_update_continuous_backups(table_name)
```

You can also filter table names using a function ```filter_table_names```
Example
``` 
def run(event, context):
    logger.info('Starting the routine...')
    tables = client.list_tables()
    for table_name in filter_table_names(tables['TableNames']):
        maybe_update_continuous_backups(table_name)
```
``` 
def filter_table_names(table_names):
    filter_expression = 'TableNamePrefix' #your filter, which can be prefix, sufix, or any part of the Tablename
    for table_name in table_names:
        if filter_expression not in table_name:
            table_names.remove(table_name)
    return table_names
```
