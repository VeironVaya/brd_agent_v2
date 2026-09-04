data "aws_caller_identity" "current" {}

# Default VPC/subnet -- IAM policy for brd-agent-v2-ec2-deployer only
# grants RunInstances against subnets/network-interfaces in this region
# generically (not tag-scoped), which in practice means the default VPC.
# Provisioning a custom VPC is out of scope (and the IAM policy has no
# vpc:Create* permissions at all).
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Latest Ubuntu 22.04 LTS (amd64) AMI, published by Canonical.
data "aws_ami" "ubuntu_2204" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ---------------------------------------------------------------------------
# SSH key pair -- generated locally by Terraform (tls_private_key), never
# sent anywhere but the local machine running `terraform apply` and AWS
# (which only ever receives the PUBLIC key). The private key is written
# to a local file (0600 perms) and is in .gitignore -- it must be copied
# out and stored somewhere safe (e.g. a password manager or as a GitHub
# Actions secret for CI/CD) after the first apply.
# ---------------------------------------------------------------------------
resource "tls_private_key" "deployer" {
  algorithm = "ED25519"
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-deployer-key"
  public_key = tls_private_key.deployer.public_key_openssh

  tags = {
    Name = "${var.project_name}-deployer-key"
  }
}

resource "local_sensitive_file" "private_key" {
  content         = tls_private_key.deployer.private_key_openssh
  filename        = "${path.module}/${var.project_name}-deployer-key.pem"
  file_permission = "0600"
}

# ---------------------------------------------------------------------------
# Security group -- only 22 (SSH, key-only auth) and 80 (HTTP) are open to
# the internet. Postgres (5432) and the backend API (8000) are NEVER
# exposed here; they're only reachable inside the docker-compose network
# on the instance itself, proxied through nginx on 80.
# ---------------------------------------------------------------------------
resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "brd-agent-v2: SSH (key-only) + HTTP only. No direct DB/API exposure."
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "${var.project_name}-app-sg"
  }
}

resource "aws_security_group_rule" "ssh_in" {
  type              = "ingress"
  security_group_id = aws_security_group.app.id
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.ssh_allowed_cidr]
  description       = "SSH (key-only auth enforced via user_data)"
}

resource "aws_security_group_rule" "http_in" {
  type              = "ingress"
  security_group_id = aws_security_group.app.id
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = [var.http_allowed_cidr]
  description       = "HTTP -- nginx serves frontend + proxies /api and /auth to backend"
}

resource "aws_security_group_rule" "all_out" {
  type              = "egress"
  security_group_id = aws_security_group.app.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow all outbound (docker pull, apt, LiteLLM calls to Gemini/Groq, etc.)"
}

# ---------------------------------------------------------------------------
# EC2 instance
# ---------------------------------------------------------------------------
resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu_2204.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deployer.key_name
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.app.id]

  root_block_device {
    volume_size = var.root_volume_size_gb
    volume_type = "gp3"
    encrypted   = true

    tags = {
      Name = "${var.project_name}-root-volume"
    }
  }

  # Installs Docker + Compose plugin and hardens SSH (key-only, no root
  # password login) on first boot. Idempotent-ish; only runs once per
  # instance (cloud-init behavior), matching how EC2 user_data normally
  # works -- re-provisioning requires replacing the instance.
  user_data = <<-EOT
    #!/bin/bash
    set -euxo pipefail

    # --- Harden SSH: key-only auth, no password/root login ---
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    systemctl reload sshd || systemctl reload ssh || true

    # --- Install Docker Engine + Compose plugin (official repo) ---
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    usermod -aG docker ubuntu

    mkdir -p /opt/brd-agent-v2
    chown ubuntu:ubuntu /opt/brd-agent-v2
  EOT

  tags = {
    Name = "${var.project_name}-app"
  }
}

# ---------------------------------------------------------------------------
# Elastic IP -- static public address that survives instance stop/start
# (does NOT survive instance termination+recreation; re-attach manually
# or via `terraform apply` again if the instance is ever replaced).
# ---------------------------------------------------------------------------
resource "aws_eip" "app" {
  domain   = "vpc"
  instance = aws_instance.app.id

  tags = {
    Name = "${var.project_name}-app-eip"
  }
}
