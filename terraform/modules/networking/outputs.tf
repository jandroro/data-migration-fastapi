output "main_vpc_id" {
  value = aws_vpc.main_vpc.id
}

output "subnet_public_id" {
  value = aws_subnet.public_subnet[0].id
}

output "subnet_private_ids" {
  value = aws_subnet.private_subnet[*].id
}

output "vpc_security_group_rds_id" {
  value = aws_security_group.rds.id
}

output "vpc_security_group_bastion_id" {
  value = aws_security_group.bastion.id
}