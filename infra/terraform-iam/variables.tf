variable "aws_region" {
  description = "Region AWS -- tetap Jakarta, sama seperti aurika production."
  type        = string
  default     = "ap-southeast-3"
}

variable "aws_profile" {
  description = "Profile AWS CLI lokal (operator) yang dipakai Terraform untuk apply."
  type        = string
  default     = "aurika-prod"
}

variable "project_name" {
  description = "Prefix nama resource IAM untuk project eksternal ini."
  type        = string
  default     = "brd-agent-v2"
}
