#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import subprocess
import time
import requests
import boto3

print("#-------<Create sec_group instances>-------#")
ec2_clt = boto3.client('ec2', region_name="us-east-1")
ec2_rsc = boto3.resource('ec2', region_name="us-east-1")
response = ec2_clt.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

response = ec2_clt.create_security_group(GroupName='biguosg',
                                     Description='DESCRIPTION',
                                     VpcId=vpc_id)
security_group_id = response['GroupId']
print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

response_e = ec2_clt.authorize_security_group_egress(
    GroupId=security_group_id,
    IpPermissions=[
        {'IpProtocol': '-1',
         'FromPort': 0,
         'ToPort': 65535,
         #'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
         }
    ]
)

response2_in = ec2_clt.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
         },
    ]
)


instance_lg = ec2_rsc.create_instances(
    ImageId='ami-ab3108d1',
    InstanceType='m3.medium',#'m3.medium',
    MaxCount=1,
    MinCount=1,
    Monitoring={
        'Enabled': True
    },
    TagSpecifications=[
        {
            'ResourceType':'instance',
            'Tags': [
                {
                    'Key': 'project',
                    'Value': '2.1'
                },
            ]
        },
    ],
    Placement={
        'AvailabilityZone': 'us-east-1c',
    },
    SecurityGroupIds=[
        security_group_id,
    ],

)

instance_wb = ec2_rsc.create_instances(
    ImageId='ami-e731089d',
    InstanceType='m3.medium',
    MaxCount=1,
    MinCount=1,
    Monitoring={
        'Enabled': True
    },
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'project',
                    'Value': '2.1'
                },
            ]
        },
    ],
    Placement={
        'AvailabilityZone': 'us-east-1c',
    },
    SecurityGroupIds=[
        security_group_id,
    ],

)


instance_lg = instance_lg[0]
instance_wb = instance_wb[0]
instance_lg.wait_until_running()
instance_wb.wait_until_running()

instance_lg.load()
instance_wb.load()

lg_dns = instance_lg.public_dns_name
wb_dns = instance_wb.public_dns_name

print(lg_dns, wb_dns)
# fetch submission passwd and andrewid
with open('.cmucc_passwd') as f:
    r = f.read().strip().split()  # r[0] is submission r[1] is andrewid

print("sleep 10sec")
time.sleep(10)

# todo: authenticate
# Authentication phase
print("#-------<Authenticate my account>-------#")
while True:
    load_gen_auth = 'http://%s/password?passwd=%s&andrewid=%s' % (lg_dns, r[0], r[1])
    print(load_gen_auth)
    try:
        s = requests.session()
        req_auth = s.get(load_gen_auth)
        print(req_auth)
        if str(req_auth).strip() == '<Response [200]>':
            print("Login OK")
            break
        else:
            print("Login fail; sleep 15sec" + str(req_auth).strip())
            time.sleep(15)

    except:
        print("except! 15 sec wait")
        time.sleep(15)
        continue

print(req_auth.text)

    # if str(req_auth).strip() == '<Response [200]>':
    #     print("Login OK")
    #     break
    # else:
    #     print("Login fail"+str(req_auth).strip())
    #     time.sleep(10)

#todo:test
#Submit webservice dns request test
#DNS changed
print("#-------<Submit Web_Service and start test>-------#")
while True:
    try:
        instance_lg.load()
        instance_wb.load()

        lg_dns = instance_lg.public_dns_name
        wb_dns = instance_wb.public_dns_name

        web_test = 'http://%s/test/horizontal?dns=%s'%(lg_dns, wb_dns)
        req_test = requests.get(web_test)
        print("start test: " + web_test)
        print(req_test)
        if str(req_test).strip() == '<Response [200]>':
            print("Login test OK")
            break
        else:
            print("Login test fail; sleep 15sec")
            time.sleep(15)
    except:
        print("test start error, retry; sleep 15sec")
        time.sleep(15)

begin_index = req_test.text.lower().find('log?name=test.')
print("begin index:" + str(begin_index))
test_id = req_test.text[begin_index+14:begin_index+27]
print(test_id)

print("#-------<Monitor the log: goal rps > 60>-------#")
pre_rps = 0
rps = 0
while True:

    while True:
        try:
            instance_lg.load()
            lg_dns = instance_lg.public_dns_name
            print("lg_dns: "+lg_dns )
            print("try to receive test info")
            check_rps = 'http://%s/log?name=test.%s.log' % (lg_dns, test_id)
            req_log = requests.get(check_rps)
            print("test page: " + check_rps)
            print(req_log)
            if str(req_log).strip() == '<Response [200]>':
                print("Login log OK; Let's take a 15 sec rest!😃")
                time.sleep(15)
                break
            else:
                print("Login of fail; sleeep 15sec")
                time.sleep(15)
        except:
            print("retry "+"receiving test info; sleep 15sec")
            time.sleep(15)

    test_rst = req_log.text.strip().split('\n')
    print(test_rst[-1])

    if "[Test End]" in test_rst or rps >= 60:
        print("test finish !!!!!")
        break

    if pre_rps == 0:
        try:
            pre_rps = float(test_rst[-1].split('=')[-1][:-2])
            rps = pre_rps
        except ValueError:
            print("wait the log, sleep 15sec and pass")
            time.sleep(15)
            pass
    else:
        rps = float(test_rst[-1].split('=')[-1][:-2])
        print("rps:" + str(rps) + "; pre_rps:" + str(pre_rps))
        if rps < 60:
            pre_rps = rps
            print("#-------<Create a new instance>-------#")
            new_instance = ec2_rsc.create_instances(
                ImageId='ami-e731089d',
                InstanceType='m3.medium',
                MaxCount=1,
                MinCount=1,
                Monitoring={
                    'Enabled': True
                },
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'project',
                                'Value': '2.1'
                            },
                        ]
                    },
                ],
                Placement={
                    'AvailabilityZone': 'us-east-1c',
                },
                SecurityGroupIds=[
                    security_group_id,
                ],

            )

            instance_lg.load()
            lg_dns = instance_lg.public_dns_name

            new_instance = new_instance[0]
            new_instance.wait_until_running()
            new_instance.load()
            new_wb_dns = new_instance.public_dns_name
            add_instance_url = 'http://%s/test/horizontal/add?dns=%s' % (lg_dns, new_wb_dns)
            print("@ added this dns: "+add_instance_url)
            while True:
                try:
                    #which means it is finished
                    req_log = requests.get(check_rps)
                    test_rst = req_log.text.strip().split('\n')
                    if test_rst[-1].startswith('[Current rps=') == False:
                        break
                    req_add = requests.get(add_instance_url)
                    print("added an instance: " + new_wb_dns)
                    print(req_add)

                    if str(req_add).strip() == '<Response [200]>':
                        print("add instance OK; take a break Orz! 15sec")
                        time.sleep(15)
                        break
                    else:
                        print("add instance fail; sleep 15sec")
                        time.sleep(15)
                except:
                    print("retry " + "added an instance: ;sleep 15sec")
                    time.sleep(15)

print("#-------<Done, and have fun>-------#")
while True:
    a = input("now if your rps>60 please submit your homework in, type ok to continue...")
    if a == "ok":
        break
    else:
        pass


















