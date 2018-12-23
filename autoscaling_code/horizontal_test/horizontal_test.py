#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import subprocess
import time
import requests

from configparser import ConfigParser

# init phase
os.system('terraform init')

# plan phase
os.system('terraform plan')

# apply phase
os.system('terraform apply -auto-approve -no-color')

# fetch the output dns
cmd_lg_dns = 'terraform output load-generator-dns'
# lg_dns = subprocess.run([cmd_lg_dns], stdout=subprocess.PIPE).stdout.decode('utf-8')
lg_dns = os.popen(cmd_lg_dns).readlines()[0]

cmd_wb_dns = 'terraform output web-service-dns'
# wb_dns = subprocess.run([cmd_wb_dns], stdout=subprocess.PIPE).stdout.decode('utf-8')
wb_dns = os.popen(cmd_wb_dns).readlines()[0]

# fetch submission passwd and andrewid
with open('.cmucc_passwd') as f:
    r = f.read().strip().split()  # r[0] is submission r[1] is andrewid

# sleep 20s so that it can react.
time.sleep(10)

s = requests.Session()
# todo: authenticate
# Authentication phase
while True:
    load_gen_auth = 'http://%s/password?passwd=%s&andrewid=%s' % (lg_dns, r[0], r[1])
    print(load_gen_auth)
    req_auth = s.get(load_gen_auth)
    if str(req_auth).strip() == '<Response [200]>':
        print("Login OK")
        break
    else:
        print("Authentication phase fail; sleep 10sec (T_T)")
        time.sleep(10)

# todo:test
# Submit webservice dns request test

while True:
    hori_test = 'http://%s/test/horizontal?dns=%s' % (lg_dns, wb_dns)
    print(hori_test)
    req_test = requests.get(hori_test)
    if str(req_test).strip() == '<Response [200]>':
        print('start test OK')
        break
    else:
        print("Start test phase fail;wait 10 sec (T-T)")
        time.sleep(10)

begin_index = req_test.text.lower().find('name=test')
test_id = req_test.text[begin_index + 11:begin_index + 24]
print(test_id)

pre_rps = 0
rps = 0
instance_count = 0

while True:
    check_rps = 'http://%s/log?name=test.%s.log' % (lg_dns, test_id)
    print(check_rps)
    req_log = requests.get(check_rps)

    if str(req_log).strip() == '<Response [200]>':
        print("OK you got a new rps (^_^)")
    else:
        print("Maybe you post too fast (T^T)")

    cfg = ConfigParser()
    cfg.read(req_log.content)
    print(cfg.sections())

    if "Minute 30" in cfg.sections() or rps >= 60:
        print("test finish !!!!!")
        break

    if pre_rps == 0:
        pre_rps = float(cfg.sections()[-1].split().split('=')[1])
        rps = pre_rps
    else:
        rps = float(cfg.sections()[-1].split().split('=')[1])
        if rps <= pre_rps and rps < 60:
            os.system('terraform state rm')
            os.system('terraform plan')
            os.system('terraform apply -auto-approve -no-color -target aws_instance.web-service')
            cmd_wb_dns = 'terraform output web-service-dns'
            wb_dns = os.popen(cmd_wb_dns).readlines()[0]
            # subprocess.run([cmd_wb_dns], stdout=subprocess.PIPE).stdout.decode('utf-8')
            add_instance_url = 'http://%s/test/horizontal/add?dns=%s' % (lg_dns, wb_dns)
            requests.get(add_instance_url)

while True:
    a = input("now if your rps>60 please submit your homework in, type ok to continue...")
    if a == "ok":
        break
    else:
        pass
