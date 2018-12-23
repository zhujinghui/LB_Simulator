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
  vpc_id = "vpc-888e83f0"

  #inbound port 80
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
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

resource "aws_instance" "load-generator" {
  ami = "ami-ab3108d1"
  instance_type = "m3.medium"
  availability_zone = "us-east-1c"
  security_groups = ["${aws_security_group.sec-group-lg.name}"]
  monitoring = true
  tags {
    Project = "2.1"
  }
}

resource "aws_instance" "web-service" {
  ami = "ami-e731089d"
  instance_type = "m3.medium"
  availability_zone = "us-east-1c"
  security_groups = ["${aws_security_group.sec-group-lg.name}"]
  monitoring = true
    tags {
    Project = "2.1"
  }
}


#load-generator-dns
output "load-generator-dns" {
  value = "${aws_instance.load-generator.public_dns}"
}

#web-service-instance-dns
output "web-service-dns" {
  value = "${aws_instance.web-service.public_dns}"
}
