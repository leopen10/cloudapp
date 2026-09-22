# instance.tf
# Une instance EC2, une IP fixe (Elastic IP : sans elle, l'adresse change a chaque
# redemarrage — c'etait le cas du deploiement manuel initial, voir README.md du depot),
# et un demarrage entierement automatique (Docker + Swarm + deploiement de la pile).

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "cloudapp" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  key_name               = aws_key_pair.cloudapp.key_name
  vpc_security_group_ids = [aws_security_group.cloudapp.id]

  root_block_device {
    volume_size = var.root_volume_gb
    volume_type = "gp3"
  }

  user_data = templatefile("${path.module}/templates/user_data.sh.tpl", {
    github_repo             = "leopen10/cloudapp"
    docker_username          = var.docker_username
    postgres_password        = var.postgres_password
    jwt_secret_key           = var.jwt_secret_key
    grafana_admin_password   = var.grafana_admin_password
    resend_api_key           = var.resend_api_key
  })

  tags = {
    Name = "cloudapp-${var.environment}"
  }
}

resource "aws_eip" "cloudapp" {
  instance = aws_instance.cloudapp.id
  domain   = "vpc"

  tags = {
    Name = "cloudapp-${var.environment}"
  }
}