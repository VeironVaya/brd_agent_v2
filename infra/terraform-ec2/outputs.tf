output "public_ip" {
  description = "IP publik statis (Elastic IP) instance -- tidak berubah selama instance ini tidak di-terminate."
  value       = aws_eip.app.public_ip
}

output "instance_id" {
  description = "ID instance EC2."
  value       = aws_instance.app.id
}

output "ssh_private_key_path" {
  description = "Path lokal file private key SSH yang di-generate Terraform (0600). Simpan/backup ke tempat aman (password manager, GitHub Actions secret) -- Terraform tidak menyimpannya di tempat lain."
  value       = local_sensitive_file.private_key.filename
}

output "ssh_command" {
  description = "Command untuk SSH manual ke instance."
  value       = "ssh -i ${local_sensitive_file.private_key.filename} ubuntu@${aws_eip.app.public_ip}"
}

output "next_steps" {
  description = "Langkah manual setelah apply."
  value       = <<-EOT
    1. Tunggu ~1-2 menit setelah apply untuk cloud-init (install Docker) selesai.
    2. Cek: ssh -i ${local_sensitive_file.private_key.filename} ubuntu@${aws_eip.app.public_ip} "docker --version && docker compose version"
    3. Simpan isi file ${local_sensitive_file.private_key.filename} sebagai secret
       GitHub Actions (nama: EC2_SSH_PRIVATE_KEY) untuk CI/CD deploy.
    4. Simpan IP publik (${aws_eip.app.public_ip}) sebagai secret GitHub Actions
       (nama: EC2_HOST).
    5. IP ini TETAP selama instance tidak di-terminate (stop/start aman).
  EOT
}
