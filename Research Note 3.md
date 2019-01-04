# Research Note 3

## 1.simulation results
Take round robin method to simulate multiple servers and record cpu utilization.
With more servers sharing rps, the peak value of cpu utilization decreases, which means when we add more servers in load balancer environment, each server will release some cpu space.  
- Test 1. 1000 rps, 1 server, cpu utilization peak value 93.8%.  
- Test 2. 1000 rps, 2 servers(500 for each server), cpu utilization peak value 86.1%  
- Test 3. 1000 rps, 3 servers(333 for each server), cpu utilization peak value 76.3%    
- Test 4. 1000 rps, 4 servers(250 for each server), cpu utilization peak value 58%  
- Test 5. 1000 rps, 5 servers(200 for each server), cpu utilization peak value 47%  
- Test 6. 1000 rps, 8 servers(125 for each server), cpu utilization peak value 32%  
- Test 7. 1000 rps, 10 servers(100 for each server), cpu utilization peak value 24%  

## 2.cloud platform results

1) Target Tracking Scaling with TargetCPUUtilization = 50%:  
- round 1: 1000 rps, CurrentReplicas = 1  
- roubd 2: 1000 rps, CurrentReplicas = 2,   
- round 3: 1000 rps, CurrentReplicas = 3,   
- round 4: 1000 rps, CurrentReplicas = 4,   
- round 5: 1000 rps, CurrentReplicas = 5,   
- round 6: 1000 rps, CurrentReplicas = 6.  
![img](/Users/zhujinghui/Desktop/Jietu20190104-232306.jpg)


2) Step Scaling Policy:  
Still in process

## 3.structure of paper   
    Introduction  
    Related Work  
    Application Autoscaling   
    Dynamic VM Allocation  
    Evaluation  
    Conclusion  
    Acknowledgement