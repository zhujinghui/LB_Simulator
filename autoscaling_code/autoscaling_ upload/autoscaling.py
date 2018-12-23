#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import requests
from python_terraform import *

print("#-------<Terraform Init Phase Begin🙈 >-------#")
#init phase
os.system('terraform init')

print("#-------<Terraform Plan Phase Begin🙉 >-------#")
#plan phase
os.system('terraform plan')

print("#-------<Terraform Apply Phase Begin🙊 >-------#")
#apply phase
os.system('terraform apply -auto-approve -no-color')


#todo: import python_terraform lib to help interact
tf1 = Terraform()
tf2 = Terraform()


#fetch the output dns
lg_dns = tf1.output('load-generator-dns')
#alb_dns = tf.output('app-load-balancer-dns')
print(lg_dns)

#fetch submission passwd and andrewid
with open('.cmucc_passwd') as f:
    r = f.read().strip().split() #r[0] is submission r[1] is andrewid

print("#-------<Take A Break 10 sec😃 >-------#")
time.sleep(10)


print("#-------<Authenticate My Account😄 >-------#")
#todo: authenticate
#Authentication phase
while True:
    #In case the lg_dns change
    lg_dns = tf1.output('load-generator-dns')

    load_gen_auth = 'http://%s/password?passwd=%s&andrewid=%s' % (lg_dns, r[0], r[1])
    print(load_gen_auth)
    try:
        s = requests.session()
        req_auth = requests.post(load_gen_auth)
        print("Authenticate Result: "+ str(req_auth).strip())

        if str(req_auth).strip() == '<Response [200]>':
            print("Authenticate Succeed😁")
            break
        else:
            print("Authenticate Fail; Sleep 10sec" + str(req_auth).strip())
            time.sleep(10)
    except:
        print("Authenticate Except! Tricky in the test! Wait 10sec")
        time.sleep(10)

print(req_auth.text)


print("#-------<Submit My ALB_DNS and Begin Test😆 >-------#")
#todo: start test
#Submit webservice dns request test
while True:
    try:
        #In case the dns change
        lg_dns = tf1.output('load-generator-dns')
        alb_dns = tf2.output('app-load-balancer-dns')

        asg_test = 'http://%s/autoscaling?dns=%s'%(lg_dns, alb_dns)
        req_test = requests.post(asg_test)
        print("Test URL: " + asg_test)
        print(req_test)
        if str(req_test).strip() == '<Response [200]>':
            print("Test Begin!🤩")
            break
        else:
            print("Test Begin Fail; Sleep 10sec")
            time.sleep(10)
    except:
        print("Test Begin Except; Retry and Sleep 10sec")
        time.sleep(10)

#find test_id
begin_index = req_test.text.lower().find('log?name=test.')
print("begin index:" + str(begin_index))
test_id = req_test.text[begin_index+14:begin_index+27]
print(test_id)


print("#-------<Monitor Log in 48Min🤪 >-------#")
#todo: monitor log
#go to the process page
while True:
    while True:
        try:
            #in case lg_dns change
            lg_dns = tf1.output('load-generator-dns')
            print("Try to receive test page!")
            #The Load Balancer will continue to send traffic to these buggy servers until they are no
            # longer marked as healthy. You need to ensure that most of these requests are not lost by
            # setting up the ELB and/or the Auto Scaling Group to detect and respond to failure. You
            # should also be able to pinpoint exactly when each of your Web Service's instances failed.

            check_log_url = 'http://%s/log?name=test.%s.log' % (lg_dns, test_id)
            req_log = requests.get(check_log_url)
            print("Log Page: "+check_log_url)
            print(req_log)
            if str(req_log).strip() == '<Response [200]>':
                print("Monitor Begin!😎 And take a 10sec break")
                time.sleep(10)
                break
            else:
                print("Monitor Enter Fail; Sleep 10sec")
                time.sleep(10)
        except:
            print("Monitor Except! Retry after 10sec")
            time.sleep(10)

    test_rst = req_log.text.strip().split('\n')
    print(test_rst[-1])

    if "[Test End]" in test_rst:
        print("Test Finish!Go to Check Points and Submit HW😇")
        break
    else:
        print("Test Continue...Be Patient! Sleep 15sec")
        time.sleep(15)


'''
If your RPS is nearly zero (0 <= rps <= 1), please check if there is at least one healthy instance connected to the ELB.
Notice that your solution should be tolerant to instance failures
check your health check configuration, timeouts, etc.
'''

print("#-------<Done, and have fun😺 >-------#")
while True:
    a = input("submit your homework, type 'ok' to continue...")
    if a == "ok":
        break
    else:
        pass

print("#-------<Terraform Destroy By Sequence😺 >-------#")
#detroy phase
# Auto Scaling Group, Load Generator, Load Balancer, Launch Configuration, Security Group
os.system('terraform destroy -force -target aws_autoscaling_group.autoscaling-group')
os.system('terraform destroy -force -target aws_instance.load-generator')
os.system('terraform destroy -force -target aws_alb.app-load-balancer')
os.system('terraform destroy -force -target aws_launch_configuration.launch-conf')
os.system('terraform destroy -force -target aws_security_group.sec-group-lg -target aws_security_group.sec-group-elb-asg')
#comfirm delete all
os.system('terraform destroy -force')

print("#-------<ALL FINISH AND BYE👋 >-------#")











