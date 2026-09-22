# network.tf
# Reseau minimal : le VPC par defaut de la region suffit pour une seule instance
# de demonstration (pas de reseau dedie a gerer). Security Group restrictif :
# SSH limite a une IP, HTTP ouvert (Traefik), tout le reste ferme.

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "cloudapp" {
  name        = "cloudapp-${var.environment}"
  description = "CloudApp : SSH restreint + HTTP public (Traefik). Aucun autre port ouvert."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH (administration), depuis une seule IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  ingress {
    description = "HTTP public (Traefik -> frontend + API + Grafana)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Tout le trafic sortant (pull d'images Docker Hub, notifications Resend...)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cloudapp-${var.environment}"
  }
}