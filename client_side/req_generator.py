# import requests
#
# r = requests.post("http://bugs.python.org", data={'number': 12524, 'type': 'issue', 'action': 'show'})
# print(r.status_code, r.reason)
# print(r.text[:300] + '...')

import os
import time

start_time = time.time()

while True:
    os.system("ab -t 1 -c 1000 http://load-balancer-1697078231.us-east-1.elb.amazonaws.com/")

