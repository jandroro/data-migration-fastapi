output "main_vpc_id" {
  value = aws_vpc.main_vpc.id
}

output "subnet_private_ids" {
  value = aws_subnet.private_subnet[*].id
}

output "vpc_security_group_rds_id" {
  value = aws_security_group.rds.id
}