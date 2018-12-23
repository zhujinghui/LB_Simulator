#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import boto3
import os
import time

IMAGE_ID = 'ami-cd0f5cb6'
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'project1_test'
SECURITY_GROUP = 'MySecurityGroup'

ec2_client = boto3.client("ec2",
                          region_name="us-east-1")

response = ec2_client.run_instances(
    ImageId=IMAGE_ID,
    InstanceType=INSTANCE_TYPE,
    KeyName=KEY_NAME,
    MaxCount=1,
    MinCount=1,
    SecurityGroups=[
        SECURITY_GROUP,
    ]
)

instance = response.get('Instances')[0]

print("Launched instance with Instance Id: [{}]!".format(instance.get('InstanceId')))
