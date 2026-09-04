output "iam_user_name" {
  description = "Nama IAM user untuk project brd-agent-v2."
  value       = aws_iam_user.brd_agent_v2.name
}

output "iam_user_arn" {
  description = "ARN IAM user."
  value       = aws_iam_user.brd_agent_v2.arn
}

output "next_steps" {
  description = "Langkah manual setelah apply."
  value       = <<-EOT
    1. Buka AWS Console > IAM > Users > ${var.project_name}-ec2-deployer
    2. Tab "Security credentials" > "Create access key" > pilih use case
       "Command Line Interface (CLI)" > buat, lalu SIMPAN access key +
       secret key (hanya muncul sekali).
    3. Setup AWS CLI profile lokal untuk project brd-agent-v2, mis.:
       aws configure --profile brd-agent-v2
       (isi access key/secret key dari langkah 2, region ap-southeast-3)
    4. Saat membuat EC2 instance baru untuk project itu (lewat console,
       CLI, atau Terraform-nya sendiri), WAJIB set tag Project=brd-agent-v2
       pada instance & security group -- tanpa tag ini, user tidak akan
       bisa start/stop/terminate/modify resource tersebut (RunInstances
       tetap bisa create, tapi mutasi berikutnya butuh tag yang cocok).
    5. Batasan: user ini HANYA bisa EC2 (+ security group/key pair/volume/
       EIP pendukungnya) di region ap-southeast-3. Tidak ada akses ke S3,
       RDS, IAM, Secrets Manager, VPC creation, atau resource aurika
       manapun (yang bertag Project=aurika).
  EOT
}
