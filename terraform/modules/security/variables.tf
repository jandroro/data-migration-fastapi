variable "project_name" {
  type        = string
  description = "Project name to be used for resource naming"
}

variable "db_engine" {
  type        = string
  description = "Database engine (postgres, mysql, mariadb)"
}

variable "db_host" {
  type        = string
  description = "Database host address"
}

variable "db_name" {
  type        = string
  description = "Name of the database"
}

variable "db_identifier" {
  type        = string
  description = "Database instance identifier"
}

variable "db_port" {
  type        = number
  description = "Database port"
}

variable "db_username" {
  type        = string
  description = "Master username for the database"
}

variable "db_password" {
  type        = string
  description = "Password for the database"
}