variable "aws_region" {
  description = "Region AWS -- Jakarta, harus sama dengan region yang diizinkan di terraform-iam."
  type        = string
  default     = "ap-southeast-3"
}

variable "aws_profile" {
  description = <<-EOT
    Profile AWS CLI lokal yang dipakai Terraform untuk apply -- ini HARUS
    profile milik IAM user "brd-agent-v2-ec2-deployer" (dibuat di
    infra/terraform-iam), BUKAN profile operator (aurika-prod). Setup:
      aws configure --profile brd-agent-v2
    (isi access key/secret key dari IAM user brd-agent-v2-ec2-deployer).
  EOT
  type        = string
  default     = "brd-agent-v2"
}

variable "project_name" {
  description = "Prefix nama resource dan nilai tag Project -- harus sama persis dengan yang diizinkan di policy IAM (brd-agent-v2)."
  type        = string
  default     = "brd-agent-v2"
}

variable "instance_type" {
  description = <<-EOT
    Tipe instance EC2. t3.small (2 vCPU/2GB) -- dipilih untuk menghemat
    biaya. CATATAN: RAM 2GB cukup ketat untuk menjalankan Postgres+pgvector,
    FastAPI, FastEmbed (model embedding di-load ke memory), dan nginx
    bersamaan di satu instance -- jika terlihat sering OOM/swap berat,
    naikkan ke t3.medium (2 vCPU/4GB) dengan `terraform apply` ulang
    setelah mengubah variable ini (instance akan direstart, bukan dibuat
    ulang -- EIP dan data tetap).
  EOT
  type        = string
  default     = "t3.small"
}

variable "root_volume_size_gb" {
  description = "Ukuran EBS root volume (GB). 30GB gp3 -- menampung Docker images, data Postgres, dan corpus referensi RAG."
  type        = number
  default     = 30
}

variable "ssh_allowed_cidr" {
  description = <<-EOT
    CIDR yang diizinkan mengakses port 22 (SSH). Sengaja dibuka ke semua
    IP (0.0.0.0/0) karena deploy dilakukan lewat GitHub Actions
    (GitHub-hosted runner, IP dinamis/tidak statis) -- akses diamankan
    lewat key-only auth (password login dimatikan di user_data), bukan
    lewat pembatasan IP.
  EOT
  type        = string
  default     = "0.0.0.0/0"
}

variable "http_allowed_cidr" {
  description = "CIDR yang diizinkan mengakses port 80 (HTTP) -- dibuka publik karena ini yang diakses end user."
  type        = string
  default     = "0.0.0.0/0"
}
