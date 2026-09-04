terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # State TERPISAH dari infra/terraform (aurika production) secara sengaja
  # -- direktori ini hanya membuat sebuah IAM user + policy terbatas EC2
  # untuk project lain ("brd-agent-v2"), tidak pernah menyentuh VPC/EC2/RDS
  # aurika. Menjaga state terpisah berarti `terraform plan/apply` di sini
  # TIDAK PERNAH bisa merencanakan perubahan pada resource aurika, bahkan
  # secara tidak sengaja.
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project   = "brd-agent-v2"
      ManagedBy = "terraform"
      Purpose   = "iam-boundary-for-external-project"
    }
  }
}
