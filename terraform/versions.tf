# versions.tf
# Versions figees : Terraform et le fournisseur AWS.

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Etat local par defaut (suffisant pour un usage personnel / demonstration).
  # Pour un usage en equipe, remplacer par un backend S3 + verrouillage DynamoDB.
  # backend "s3" {
  #   bucket = "cloudapp-terraform-state"
  #   key    = "cloudapp/terraform.tfstate"
  #   region = "eu-west-3"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "cloudapp"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}