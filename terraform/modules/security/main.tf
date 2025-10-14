# #####################################
# SECRETS MANAGER
# #####################################

# Secrets Manager Secret
resource "aws_secretsmanager_secret" "db_credentials" {
  name_prefix             = "${var.project_name}-db-credentials-"
  description             = "Database credentials for ${var.project_name}"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-db-credentials"
  }
}

# Store credentials in Secrets Manager
resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username             = var.db_username
    password             = var.db_password
    engine               = var.db_engine
    host                 = var.db_host
    port                 = var.db_port
    dbname               = var.db_name
    dbInstanceIdentifier = var.db_identifier
  })
}