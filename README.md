<!--
title: 'PointInTimeRecoveryAutoEnabler'
description: 'This lambda ensures point in time recovery is enabled on all DynamoDB tales'
layout: Doc
framework: v1
platform: AWS
language: Python
authorLink: 'https://github.com/sylvekk'
authorName: 'Sylwester Karwacki'
authorAvatar: 'https://en.gravatar.com/userimage/151138712/3517d1908c28e1b26b2d3cb723921630.jpeg'
-->
## PointInTimeRecoveryAutoEnabler

##### What is the purpose and why it was developed?
Those who use DynamoDB know how important the ```PointInTimeRecovery``` 
is and how easily it can be turned on or off though the console. The consequences of accidentally turning it off, 
or forgetting to turning it on, may be drastic. 

Moreover, there are some examples where we create the Table programmatically and are unable to set the ```PointInTimeRecovery``` at the same time.
It may be caused by a delay in response from the client, or longer time taken to create the Table. 
Additionally it may simply fail on enabling ```PointInTimeRecovery``` and we may be unaware of it for some time.

This lambda addresses above issues and ensures ```PointInTimeRecovery``` is enabled on all/selected DynamoDB Tables

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
to install testing dependencies run
```
sls plugin install -n serverless-python-requirements
```
``` 
pip3 install -r requirements.txt
 
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

#### Testing
Testing using pytest
install requirements
``` 
pip3 install -r requirements-test.txt

```

Make sure your ```moto``` is at version ```1.3.16``` or higher as otherwise 
```describe_continuous_backups``` will not work within tests.
If you run older version you need to uninstall it and install correct version
``` 
sudo pip3 uninstall moto
```
and then install it with the latest version (1.3.6 a the time of writing)
``` 
git clone git://github.com/spulec/moto.git
cd moto
sudo python setup.py install
```

We are using ```mock_dynamodb2_deprecated``` instead of ```mock_dynamodb2```
 as at the point of writing there is an issue with ```botocore```, and when using ```mock_dynamodb2```
  it creates a real table on AWS
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
    filtered_names = []
    for table_name in table_names:
        if filter_expression in table_name:
            filtered_names.append(table_name)
    return filtered_names
```
