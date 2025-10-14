# #####################################
# SECURITY GROUP
# #####################################

resource "aws_security_group" "sg_web_server" {
  name        = "${var.nwt_prefix_name}-web-server-sg"
  description = "Allow Web Server traffic"
  vpc_id      = var.main_vpc_id

  tags = {
    "Name" : "${var.nwt_prefix_name}-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "web_server_allow_tls_ipv4" {
  security_group_id = aws_security_group.sg_web_server.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "web_server_allow_http_ipv4" {
  security_group_id = aws_security_group.sg_web_server.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

resource "aws_vpc_security_group_ingress_rule" "web_server_allow_ssh_ipv4" {
  security_group_id = aws_security_group.sg_web_server.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
}

resource "aws_vpc_security_group_egress_rule" "web_server_allow_all_ipv4" {
  security_group_id = aws_security_group.sg_web_server.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}