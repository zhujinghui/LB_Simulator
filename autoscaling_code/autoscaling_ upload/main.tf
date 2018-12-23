
//todo: TAG!! EC2 instances, ELB, ASG

provider "aws" {
  region                  = "us-east-1"
  shared_credentials_file = "~/.aws/credentials"
  #profile                 = "aws_profile"
}

//TODO: NO.1 SETUP SECURITY GROUP
#Create security group for Load Generator
resource "aws_security_group" "sec-group-lg" {
  name = "sec-group-lg"
  description = "security group for Load Generator"
  vpc_id = "${var.aws-vpc-id}"

  #inbound port 80
  ingress {
    from_port = 80
    to_port = 80
    protocol = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #outbound all
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#Create security group for ELB and ASG
resource "aws_security_group" "sec-group-alb-asg" {
  name = "sec-group-alb-asg"
  description = "security group for ELB and ASG"
  vpc_id = "${var.aws-vpc-id}"

  #inbound port 80
  ingress {
    from_port = 80
    to_port = 80
    protocol = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #outbound all
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

//TODO: NO.2 SETUP LOAD GENERATOR in sec_group_ls
resource "aws_instance" "load-generator" {
  ami = "${var.aws-ami-load-generator}"
  instance_type = "${var.aws-instance-type}"
  security_groups = ["${aws_security_group.sec-group-lg.name}"]
  #availability_zone = "${var.aws-region}"
  monitoring = true

  tags {
    Project = "2.1"
  }
}

//TODO: NO.3 SETUP LAUNCH CONFIGURATION in sec_group_elb_asg
resource "aws_launch_configuration" "launch-conf" {
  name = "launch-conf"
  image_id = "${var.aws-ami-lauch-conf}"
  instance_type = "${var.aws-instance-type}"
  security_groups = ["${aws_security_group.sec-group-alb-asg.name}"]
  enable_monitoring = true #Detailed Monitoring: enabled
}




//TODO: NO.4 SETUP APPLICATION LOAD BALANCER
// that redirects HTTP:80 requests from the load balancer to HTTP:80 on the instance. You will have to create a target group.
resource "aws_alb" "app-load-balancer" {
  name = "app-load-balancer"
  security_groups = ["${aws_security_group.sec-group-alb-asg.id}"] #id
  subnets = ["subnet-ac244483","subnet-28ee8b75","subnet-eac0998e"] #same subnet us-east-1

  tags {
    Project = "2.1"
  }
}

//TODO: NO.5 SETUP Target Group for instances using HTTP:80.
//Use / for the Health Check (e.g. heartbeat) path and use HTTP.
resource "aws_alb_target_group" "alb-target-group" {
  name = "alb-target-group"
  vpc_id = "${var.aws-vpc-id}"
  port = 80
  protocol = "HTTP"

  health_check {
    port = 80
    protocol = "HTTP"
    path = "/"
    healthy_threshold = 3 #default 3
    unhealthy_threshold = 3 #default 3
    interval = 30
    timeout = 5
  }

  tags {
    Project = "2.1"
  }
}
#Provides a Load Balancer Listener resource.
resource "aws_alb_listener" "alb-listener" {
  "default_action" {
    target_group_arn = "${aws_alb_target_group.alb-target-group.arn}"
    type = "forward"
  }
  load_balancer_arn = "${aws_alb.app-load-balancer.arn}"
  port = 80
  protocol = "HTTP"

}


//TODO: NO.6 SETUP Auto Scaling Group
resource "aws_autoscaling_group" "autoscaling-group" {
  name = "autoscaling-group"
  launch_configuration = "${aws_launch_configuration.launch-conf.id}" #name or id
  max_size = 6
  min_size = 1
  #desired_capacity = 4 The number of Amazon EC2 instances that should be running in the group.
  availability_zones = ["us-east-1c","us-east-1b","us-east-1a"]
  health_check_grace_period = 120
  health_check_type = "EC2"

  tag {
    key = "Project"
    propagate_at_launch = true
    value = "2.1"
  }
}

//TODO: NO.7 attach autoscaling_group to alb_target_group
resource "aws_autoscaling_attachment" "autoscaling-group-attachment" {
  autoscaling_group_name = "${aws_autoscaling_group.autoscaling-group.id}" #name or id
  alb_target_group_arn = "${aws_alb_target_group.alb-target-group.arn}"
}


//TODO: build up policy
resource "aws_autoscaling_policy" "scale-out-policy" {
  name = "scale-out-policy"
  autoscaling_group_name = "${aws_autoscaling_group.autoscaling-group.id}" #name or id
  adjustment_type = "ChangeInCapacity" #ChangeInCapacity, ExactCapacity, and PercentChangeInCapacity

  #Increase or decrease the current capacity of the group based on a set of scaling adjustments, known as step adjustments, that vary based on the size of the alarm breach.
  policy_type = "StepScaling" #"SimpleScaling" or "StepScaling"
  estimated_instance_warmup = 120 #program should wait at least 100 seconds before it launches another one.

  #according to observation result
  step_adjustment {
    #The number of members by which to scale, when the adjustment bounds are breached. A positive value scales up. A negative value scales down.
    #scaling_adjustment - (Required) The number of members by which to scale, when the adjustment bounds are breached. A positive value scales up. A negative value scales down.
    #The lower bound for the difference between the alarm threshold and the CloudWatch metric.
    #The upper bound for the difference between the alarm threshold and the CloudWatch metric.
    scaling_adjustment = 1
    metric_interval_lower_bound = 0
    metric_interval_upper_bound = 10
  }

  step_adjustment {
    scaling_adjustment = 2
    metric_interval_lower_bound = 10
    metric_interval_upper_bound = 20
  }

    step_adjustment {
    scaling_adjustment = 3
    metric_interval_lower_bound = 20
    metric_interval_upper_bound = 35
  }

  step_adjustment {
    scaling_adjustment = 4
    metric_interval_lower_bound = 35
  }

}

resource "aws_autoscaling_policy" "scale-in-policy" {
  name = "scale-in-policy"
  autoscaling_group_name = "${aws_autoscaling_group.autoscaling-group.id}" #name or id
  adjustment_type = "ChangeInCapacity" #ChangeInCapacity, ExactCapacity, and PercentChangeInCapacity
  policy_type = "StepScaling" #"SimpleScaling" or "StepScaling"
  estimated_instance_warmup = 120 #program should wait at least 100 seconds before it launches another one.

  #according to observation result
  step_adjustment {
    #scaling_adjustment - (Required) The number of members by which to scale, when the adjustment bounds are breached. A positive value scales up. A negative value scales down.
    scaling_adjustment = -1
    metric_interval_lower_bound = -15
    metric_interval_upper_bound = 0
  }

  step_adjustment {
    scaling_adjustment = -2
    metric_interval_lower_bound = -35
    metric_interval_upper_bound = -15
  }

    step_adjustment {
    scaling_adjustment = -3
    metric_interval_upper_bound = -35
  }
}

//todo: CloudWatch Alarms
#Scale out when the group's CPU load exceeds 80% on average over a 5-minute interval.
resource "aws_cloudwatch_metric_alarm" "out-alarm" {
  alarm_name = "out-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = 1
  metric_name = "CPUUtilization"
  namespace = "AWS/EC2"
  period = 120
  threshold = 65
  statistic = "Average"
  insufficient_data_actions = []
  unit = "Percent"

  dimensions {
    AutoScalingGroupName = "${aws_autoscaling_group.autoscaling-group.id}" #name or id
  }
  alarm_description = "Scale_out metric monitors ec2 cpu utilization"
  alarm_actions     = ["${aws_autoscaling_policy.scale-out-policy.arn}"]
}

#Scale in when the group's CPU load is below 20% on average over a 5-minute interval.
resource "aws_cloudwatch_metric_alarm" "in-alarm" {
  alarm_name = "in-alarm"
  comparison_operator = "LessThanThreshold"
  evaluation_periods = 1
  metric_name = "CPUUtilization"
  namespace = "AWS/EC2"
  period = 120
  threshold = 35
  statistic = "Average"
  insufficient_data_actions = []
  unit = "Percent"

  dimensions {
    AutoScalingGroupName = "${aws_autoscaling_group.autoscaling-group.id}" #name or id
  }
  alarm_description = "Scale_in metric monitors ec2 cpu utilization"
  alarm_actions     = ["${aws_autoscaling_policy.scale-in-policy.arn}"]
}






