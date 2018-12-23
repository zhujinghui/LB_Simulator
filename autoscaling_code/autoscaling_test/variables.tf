
variable "aws-region" {
  description = "Servers Region"
  default = "us-east-1c"
}

variable "aws-vpc-id" {
  default = "vpc-888e83f0"
}

variable "aws-ami-load-generator" {
  description = "Do not delete me until the whole task finish"
  default = "ami-ab3108d1"
}

variable "aws-ami-lauch-conf" {
  description = " Launch Configuration for the instances that will become part of the Auto Scaling Group"
  default = "ami-e731089d"
}

variable "aws-instance-type" {
  default = "m3.medium"
}

variable "aws-tag" {
  type = "map"

  default = {
      key = "Project"
      value = "2.1"
      propagate_at_launch = true
    }

}

