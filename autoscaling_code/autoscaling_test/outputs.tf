#load-generator-dns
output "load-generator-dns" {
  value = "${aws_instance.load-generator.public_dns}"
}

#web-service-instance-dns that is Application Load Balancer
output "app-load-balancer-dns" {
  value = "${aws_alb.app-load-balancer.dns_name}"
}
