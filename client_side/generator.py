import time
import grequests

# while True:
#     r = requests.get("http://127.0.0.1:5000/")
#     print(r.text)
#     time.sleep(1)
#
#     r1 = requests.get("http://127.0.0.1:5001/")
#     print(r1.text)
#     time.sleep(1)

while True:
    start_time = time.time()

    urls = [
            #"load-balancer-1697078231.us-east-1.elb.amazonaws.com",
               "http://3.83.17.78:5000/"
           ] * 5

    rs = (grequests.head(u) for u in urls)
    print(grequests.map(rs))

    print(time.time() - start_time)
    print("wait 2s")
    time.sleep(2)

    # start_time = time.time()
    # urls1 = [
    #            "http://127.0.0.1:5001/"
    #        ] * 500
    #
    # rs = (grequests.head(u) for u in urls1)
    # print(grequests.map(rs))
    #
    # print(time.time() - start_time)
    # print("wait 5s")
    # time.sleep(5)
