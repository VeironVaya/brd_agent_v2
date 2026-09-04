terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }

  # State TERPISAH dari infra/terraform-iam dan dari infra aurika -- ini
  # hanya provisioning EC2 instance + Elastic IP + security group untuk
  # project brd-agent-v2, menggunakan kredensial IAM user
  # "brd-agent-v2-ec2-deployer" (bukan operator aurika-prod).
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project   = "brd-agent-v2"
      ManagedBy = "terraform"
    }
  }
}
