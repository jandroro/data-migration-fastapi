variable "region" {
  type        = string
  description = "The AWS region to deploy resources"
}

variable "project_name" {
  type        = string
  description = "Project name to be used for resource naming"
}

variable "availability_zones" {
  type        = list(string)
  description = "List of availability zones"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR to be assigned to the main VPC"
}

variable "db_port" {
  type        = number
  description = "Database port"
}