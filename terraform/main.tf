provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  }
}

# Generate random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = true
  # Exclude characters that might cause issues in connection strings
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# VPC and Networking
module "networking" {
  source             = "./modules/networking"
  region             = var.aws_region
  project_name       = var.project_name
  availability_zones = var.availability_zones
  vpc_cidr           = var.vpc_cidr
  db_port            = var.db_port
}

# Database
module "database" {
  source                          = "./modules/database"
  project_name                    = var.project_name
  subnet_ids                      = module.networking.subnet_private_ids
  db_parameter_group_family       = var.db_parameter_group_family
  db_engine                       = var.db_engine
  db_engine_version               = var.db_engine_version
  db_instance_class               = var.db_instance_class
  db_allocated_storage            = var.db_allocated_storage
  db_max_allocated_storage        = var.db_max_allocated_storage
  db_name                         = var.db_name
  db_username                     = var.db_username
  db_password                     = random_password.db_password.result
  db_port                         = var.db_port
  vpc_security_group_rds_id       = module.networking.vpc_security_group_rds_id
  backup_retention_period         = var.backup_retention_period
  backup_window                   = var.backup_window
  maintenance_window              = var.maintenance_window
  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports
  deletion_protection             = var.deletion_protection
  skip_final_snapshot             = var.skip_final_snapshot
  log_retention_days              = var.log_retention_days
}

# Security
module "security" {
  source        = "./modules/security"
  project_name  = var.project_name
  db_engine     = module.database.db_engine
  db_host       = module.database.db_host
  db_name       = module.database.db_name
  db_identifier = module.database.db_identifier
  db_port       = module.database.db_port
  db_username   = module.database.db_username
  db_password   = random_password.db_password.result
}


module "bastion" {
  source                        = "./modules/bastion"
  project_name                  = var.project_name
  db_credentials_secret_arn     = module.security.db_credentials_secret_arn
  bastion_instance_type         = var.bastion_instance_type
  subnet_public_id              = module.networking.subnet_public_id
  vpc_security_group_bastion_id = module.networking.vpc_security_group_bastion_id
  bastion_key_name              = var.bastion_key_name
  enable_ssm_on_bastion         = var.enable_ssm_on_bastion
}
