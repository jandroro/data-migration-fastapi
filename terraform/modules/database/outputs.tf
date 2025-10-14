output "db_engine" {
  value = aws_db_instance.main.engine
}

output "db_host" {
  value = aws_db_instance.main.address
}

output "db_name" {
  value = aws_db_instance.main.db_name
}

output "db_identifier" {
  value = aws_db_instance.main.identifier
}

output "db_port" {
  value = aws_db_instance.main.port
}

output "db_username" {
  value = aws_db_instance.main.username
}