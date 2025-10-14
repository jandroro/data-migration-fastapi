variable "project_name" {
  type        = string
  description = "Project name to be used for resource naming"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs for the DB subnet group"
}

variable "db_engine" {
  type        = string
  description = "Database engine (postgres, mysql, mariadb)"
}

variable "db_engine_version" {
  type        = string
  description = "Database engine version"
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage in GB"
}

variable "db_max_allocated_storage" {
  type        = number
  description = "Maximum allocated storage in GB for autoscaling"
}

variable "db_name" {
  type        = string
  description = "Name of the database to create"
}

variable "db_username" {
  type        = string
  description = "Master username for the database"
}

variable "db_password" {
  type        = string
  description = "Password for the database"
}

variable "db_port" {
  type        = number
  description = "Database port"
}

variable "db_parameter_group_family" {
  type        = string
  description = "Database parameter group family"
}

variable "vpc_security_group_rds_id" {
  type        = string
  description = "Security Group ID for the RDS instance"
}

variable "backup_retention_period" {
  type        = number
  description = "Number of days to retain backups"
}

variable "backup_window" {
  type        = string
  description = "Preferred backup window"
}

variable "maintenance_window" {
  type        = string
  description = "Preferred maintenance window"
}

variable "enabled_cloudwatch_logs_exports" {
  type        = list(string)
  description = "List of log types to export to CloudWatch"
}

variable "deletion_protection" {
  type        = bool
  description = "Enable deletion protection"
}

variable "skip_final_snapshot" {
  type        = bool
  description = "Skip final snapshot on deletion (not recommended for production)"
}