# #####################################
# TERRAFORM CONFIG
# #####################################

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "The AWS region to deploy resources"
}

variable "aws_profile" {
  type        = string
  default     = "iam_admin-general"
  description = "The AWS CLI profile used to deploy resources"
}

variable "project_name" {
  type        = string
  default     = "data-migration"
  description = "Project name to be used for resource naming"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment (dev, test, prod)"
}

# #####################################
# VPC CONFIG
# #####################################

variable "availability_zones" {
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
  description = "List of availability zones"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR to be assigned to the main VPC"
}

# #####################################
# DATABASE CONFIG
# #####################################

variable "db_engine" {
  type        = string
  default     = "postgres"
  description = "Database engine (postgres, mysql, mariadb)"

  validation {
    condition     = contains(["postgres", "mysql", "mariadb"], var.db_engine)
    error_message = "db_engine must be one of: postgres, mysql, mariadb"
  }
}

variable "db_engine_version" {
  type        = string
  default     = "15"
  description = "Database engine version"
}

variable "db_instance_class" {
  type        = string
  default     = "db.t3.medium"
  description = "RDS instance class"
}

variable "db_allocated_storage" {
  type        = number
  default     = 20
  description = "Allocated storage in GB"
}

variable "db_max_allocated_storage" {
  type        = number
  default     = 100
  description = "Maximum allocated storage in GB for autoscaling"
}

variable "db_name" {
  type        = string
  default     = "myappdb"
  description = "Name of the database to create"
}

variable "db_username" {
  type        = string
  default     = "dbadmin"
  description = "Master username for the database"
}

variable "db_port" {
  type        = number
  default     = 5432
  description = "Database port"
}

variable "db_parameter_group_family" {
  type        = string
  default     = "postgres15"
  description = "Database parameter group family"
}

# #####################################
# DATABASE BACKUP CONFIG
# #####################################

variable "backup_retention_period" {
  type        = number
  default     = 1
  description = "Number of days to retain backups"
}

variable "backup_window" {
  type        = string
  default     = "03:00-04:00"
  description = "Preferred backup window"
}

variable "maintenance_window" {
  type        = string
  default     = "mon:04:00-mon:05:00"
  description = "Preferred maintenance window"
}

variable "log_retention_days" {
  type        = number
  default     = 30
  description = "CloudWatch log retention in days"
}

# #####################################
# MONITORING CONFIG
# #####################################

variable "enabled_cloudwatch_logs_exports" {
  type        = list(string)
  default     = ["postgresql"]
  description = "List of log types to export to CloudWatch"
}

# #####################################
# SECURITY CONFIG
# #####################################

variable "deletion_protection" {
  type        = bool
  default     = false # For production, consider setting this to true
  description = "Enable deletion protection"
}

variable "skip_final_snapshot" {
  type        = bool
  default     = false
  description = "Skip final snapshot on deletion (not recommended for production)"
}

# #####################################
# BASTION CONFIG
# #####################################

variable "bastion_instance_type" {
  type        = string
  default     = "t3.micro"
  description = "Instance type for bastion host"
}

variable "bastion_key_name" {
  type        = string
  default     = null
  description = "SSH key name for bastion host (optional - use SSM Session Manager instead)"
}

variable "enable_ssm_on_bastion" {
  type        = bool
  default     = false # Set to true if you want SSM access
  description = "Enable SSM Session Manager on bastion (requires VPC endpoints or internet access)"
}