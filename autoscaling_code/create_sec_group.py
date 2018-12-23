#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import boto3

# todo: tag EC2 instances, ELB, ASG

ec2 = boto3.resource('ec2', aws_access_key_id='AWS_ACCESS_KEY_ID',
                     aws_secret_access_key='AWS_SECRET_ACCESS_KEY',
                     region_name='us-east-1')

sec_group = ec2.create_security_group(
    GroupName='LG_sec_group',
    Description='Load Generator sec group',
    VpcId='vpc-888e83f0')
sec_group.authorize_egress(

)
sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=-1,
    ToPort=-1,
    Port=80,
)
print(sec_group.id)
