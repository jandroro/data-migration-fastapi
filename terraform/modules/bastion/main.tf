# #####################################
# EC2 AMI
# #####################################

# Data source for latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# #####################################
# ROLES AND POLICIES
# #####################################

# IAM Role for Bastion (to access Secrets Manager)
resource "aws_iam_role" "bastion" {
  name_prefix = "${var.project_name}-bastion-role-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-bastion-role"
  }
}

# Policy to read Secrets Manager
resource "aws_iam_role_policy" "bastion_secrets" {
  name_prefix = "${var.project_name}-bastion-secrets-"
  role        = aws_iam_role.bastion.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = var.db_credentials_secret_arn
      }
    ]
  })
}

# Conditionally attach SSM policy (only if enabled)
resource "aws_iam_role_policy_attachment" "bastion_ssm" {
  count      = var.enable_ssm_on_bastion ? 1 : 0
  role       = aws_iam_role.bastion.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance Profile
resource "aws_iam_instance_profile" "bastion" {
  name_prefix = "${var.project_name}-bastion-profile-"
  role        = aws_iam_role.bastion.name
}

# #####################################
# BASTION EC2 INSTANCE
# #####################################

resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.bastion_instance_type
  subnet_id                   = var.subnet_public_id
  vpc_security_group_ids      = [var.vpc_security_group_bastion_id]
  iam_instance_profile        = aws_iam_instance_profile.bastion.name
  key_name                    = var.bastion_key_name # Optional: for SSH key access
  associate_public_ip_address = true                 # IMPORTANT: Enable public IP

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    
    # Update system
    dnf update -y
    
    # Install PostgreSQL client (adjust for your DB engine)
    dnf install -y postgresql15
    
    # Install jq for JSON parsing
    dnf install -y jq
    
    # Create helper script to connect to RDS
    cat > /usr/local/bin/connect-to-rds.sh << 'SCRIPT'
    #!/bin/bash
    SECRET_ARN="${var.db_credentials_secret_arn}"
    
    echo "Retrieving database credentials from Secrets Manager..."
    SECRET=$(aws secretsmanager get-secret-value \
      --secret-id "$SECRET_ARN" \
      --query SecretString \
      --output text 2>/dev/null)
    
    if [ $? -ne 0 ]; then
      echo "Error: Unable to retrieve credentials from Secrets Manager"
      echo "Please check IAM permissions"
      exit 1
    fi
    
    DB_HOST=$(echo $SECRET | jq -r '.host')
    DB_PORT=$(echo $SECRET | jq -r '.port')
    DB_NAME=$(echo $SECRET | jq -r '.dbname')
    DB_USER=$(echo $SECRET | jq -r '.username')
    DB_PASS=$(echo $SECRET | jq -r '.password')
    DB_ENGINE=$(echo $SECRET | jq -r '.engine')

    echo "Connecting to $DB_ENGINE database at $DB_HOST:$DB_PORT..."
    
    # Connect based on engine
    if [[ "$DB_ENGINE" == "postgres" ]]; then
        PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
    elif [[ "$DB_ENGINE" == "mysql" ]] || [[ "$DB_ENGINE" == "mariadb" ]]; then
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME"
    else
        echo "Unsupported database engine: $DB_ENGINE"
        exit 1
    fi
    SCRIPT
    
    chmod +x /usr/local/bin/connect-to-rds.sh
    
    # Create README for users
    cat > /home/ec2-user/README.txt << 'README'
    ================================================================================
    Welcome to the RDS Bastion Host!
    ================================================================================
    
    This bastion host provides secure access to your RDS database.
    
    QUICK START:
    ------------
    To connect to the database, run:
        sudo /usr/local/bin/connect-to-rds.sh
    
    MANUAL CONNECTION:
    ------------------
    1. Get database credentials:
        aws secretsmanager get-secret-value \
          --secret-id ${var.db_credentials_secret_arn} \
          --query SecretString --output text | jq .
    
    2. Connect manually:
        # PostgreSQL
        psql -h <HOST> -p <PORT> -U <USER> -d <DBNAME>
        
        # MySQL
        mysql -h <HOST> -P <PORT> -u <USER> -p <DBNAME>
    
    USEFUL COMMANDS:
    ----------------
    - List tables: \dt (PostgreSQL) or SHOW TABLES; (MySQL)
    - Describe table: \d table_name (PostgreSQL) or DESCRIBE table_name; (MySQL)
    - Exit: \q (PostgreSQL) or exit; (MySQL)
    
    DATABASE INFO:
    --------------
    Secret ARN: ${var.db_credentials_secret_arn}
    
    For support, check the project documentation.
    ================================================================================
    README
    
    chown ec2-user:ec2-user /home/ec2-user/README.txt
    
    # Create .bashrc alias for easy connection
    echo "alias db='sudo /usr/local/bin/connect-to-rds.sh'" >> /home/ec2-user/.bashrc
    
    # Log successful setup
    echo "Bastion host setup completed successfully" > /var/log/bastion-setup.log
  EOF
  )

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required" # Enforce IMDSv2
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
  }

  tags = {
    Name = "${var.project_name}-bastion"
  }

  lifecycle {
    ignore_changes = [ami] # Prevent replacement on AMI updates
  }
}