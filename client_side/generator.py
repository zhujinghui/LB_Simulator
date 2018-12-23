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
               "http://127.0.0.1:5000/",
               "http://127.0.0.1:5001/"
           ] * 1000

    rs = (grequests.head(u) for u in urls)
    print(grequests.map(rs))

    print(time.time() - start_time)
    print("wait 5s")
    time.sleep(5)
