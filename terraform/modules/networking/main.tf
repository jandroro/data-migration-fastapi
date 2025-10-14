# #####################################
# MAIN VPC
# #####################################

resource "aws_vpc" "main_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    "Name" = "${var.project_name}-vpc"
  }
}

# #####################################
# INTERNET GATEWAY
# #####################################

resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.main_vpc.id

  tags = {
    "Name" = "${var.project_name}-igw"
  }
}

# #####################################
# PUBLIC SUBNETS
# #####################################

resource "aws_subnet" "public_subnet" {
  count             = 1
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone = var.availability_zones[count.index]

  tags = {
    "Name" = "${var.project_name}-public-subnet-${count.index + 1}"
  }
}

# #####################################
# PRIVATE SUBNETS
# #####################################

resource "aws_subnet" "private_subnet" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 2)
  availability_zone = var.availability_zones[count.index]

  tags = {
    "Name" = "${var.project_name}-private-subnet-${count.index + 1}"
  }
}

# #####################################
# ELASTIC IP FOR NAT GATEWAY
# #####################################

resource "aws_eip" "eip_natgw" {
  domain = "vpc"

  tags = {
    "Name" = "${var.project_name}-nat-eip"
  }

  depends_on = [aws_internet_gateway.main_igw]
}

# #####################################
# NAT GATEWAY IN THE PUBLIC SUBNET
# #####################################

resource "aws_nat_gateway" "natgw" {
  allocation_id = aws_eip.eip_natgw.id
  subnet_id     = aws_subnet.public_subnet[0].id

  tags = {
    "Name" = "${var.project_name}-natgw"
  }

  depends_on = [aws_internet_gateway.main_igw]
}

# #####################################
# ROUTE TABLE - PUBLIC SUBNETS
# #####################################

# Route table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }

  tags = {
    "Name" = "${var.project_name}-public-rt"
  }
}

# Subnet association
resource "aws_route_table_association" "public_association" {
  count          = length(aws_subnet.public_subnet)
  subnet_id      = aws_subnet.public_subnet[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

# #####################################
# ROUTE TABLE - PRIVATE SUBNETS
# #####################################

# Route table
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.natgw.id
  }

  tags = {
    "Name" = "${var.project_name}-private-rt"
  }
}

# Subnet association
resource "aws_route_table_association" "private_association" {
  count          = length(aws_subnet.private_subnet)
  subnet_id      = aws_subnet.private_subnet[count.index].id
  route_table_id = aws_route_table.private_rt.id
}

# #####################################
# SECURITY GROUPS
# #####################################

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-sg-"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main_vpc.id

  # Ingress rule - restrict to application security group
  ingress {
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Allow database access from application"
  }

  tags = {
    "Name" : "${var.project_name}-rds-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Application Security Group
resource "aws_security_group" "app" {
  name_prefix = "${var.project_name}-app-sg-"
  description = "Security group for application servers"
  vpc_id      = aws_vpc.main_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-app-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# #####################################
# VPC ENDPOINT
# #####################################

# resource "aws_vpc_endpoint" "apigw_vpc_endpoint" {
#   vpc_id              = aws_vpc.main_vpc.id
#   service_name        = "com.amazonaws.${var.region}.execute-api"
#   vpc_endpoint_type   = "Interface"
#   subnet_ids          = [aws_subnet.private_subnet_01.id]
#   security_group_ids  = [aws_security_group.sg_apigw_vpc_endpoint.id]
#   private_dns_enabled = true

#   tags = {
#     "Name" : "${var.project_name}-vpce-api-gateway"
#   }
# }