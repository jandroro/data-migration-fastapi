variable "project_name" {
  type        = string
  description = "Project name to be used for resource naming"
}

variable "db_credentials_secret_arn" {
  type        = string
  description = "ARN of the Secrets Manager secret storing DB credentials"
}

variable "bastion_instance_type" {
  type        = string
  description = "Instance type for bastion host"
}

variable "subnet_public_id" {
  type        = string
  description = "Subnet ID for the public subnet"
}

variable "vpc_security_group_bastion_id" {
  type        = string
  description = "Security Group ID for the bastion host"
}

variable "bastion_key_name" {
  type        = string
  description = "SSH key name for bastion host (optional - use SSM Session Manager instead)"
}

variable "enable_ssm_on_bastion" {
  type        = bool
  description = "Enable SSM Session Manager on bastion (requires VPC endpoints or internet access)"
}