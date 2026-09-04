data "aws_caller_identity" "current" {}

# User IAM khusus project eksternal "brd-agent-v2". Tidak dipakai untuk
# provisioning infra aurika, dan tidak punya akses ke resource aurika sama
# sekali -- izin dibatasi ke EC2 saja (lihat policy di bawah), di region
# Jakarta (ap-southeast-3), dan tindakan yang mengubah/menghapus instance
# dibatasi hanya pada resource yang bertag Project=brd-agent-v2.
resource "aws_iam_user" "brd_agent_v2" {
  name = "${var.project_name}-ec2-deployer"

  tags = {
    Name = "${var.project_name}-ec2-deployer"
  }
}

# TIDAK membuat access key lewat Terraform -- access key sengaja dibuat
# manual dari AWS Console oleh operator (bukan Kiro/Terraform) supaya
# secret key tidak pernah tersimpan di state file atau riwayat chat.
# Setelah apply, buka: IAM > Users > brd-agent-v2-ec2-deployer >
# Security credentials > Create access key.

resource "aws_iam_policy" "brd_agent_v2_ec2_only" {
  name        = "${var.project_name}-ec2-only-policy"
  description = "Izin terbatas: EC2 saja, region ap-southeast-3 saja, mutasi/hapus hanya pada resource bertag Project=brd-agent-v2."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Baca (read-only) seluruh resource EC2 di region ini -- perlu
        # untuk melihat daftar instance/AMI/security group/dll saat
        # men-deploy lewat console/CLI/Terraform milik project lain.
        # Describe* tidak mendukung resource-level permission di EC2,
        # jadi dibatasi lewat kondisi region saja.
        Sid    = "Ec2ReadOnlyJakarta"
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "ec2:GetConsoleOutput",
          "ec2:GetConsoleScreenshot",
        ]
        Resource = "*"
        Condition = {
          StringEquals = { "aws:RequestedRegion" = var.aws_region }
        }
      },
      {
        # Membuat instance baru DAN resource pendukungnya (security group,
        # key pair, volume, network interface) -- wajib mem-passing tag
        # Project=brd-agent-v2 pada saat pembuatan (RequestTag), sehingga
        # instance/resource yang dibuat otomatis "terkunci" ke tag ini dan
        # bisa dikenali oleh statement mutasi di bawah.
        Sid    = "Ec2CreateWithRequiredTag"
        Effect = "Allow"
        Action = [
          "ec2:RunInstances",
          "ec2:CreateSecurityGroup",
          "ec2:CreateKeyPair",
          # Terraform's aws_key_pair (given a public_key, as opposed to
          # having AWS generate one) calls ImportKeyPair, not
          # CreateKeyPair -- confirmed via a real 403 during apply.
          "ec2:ImportKeyPair",
          "ec2:CreateVolume",
          "ec2:CreateTags",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion"    = var.aws_region
            "aws:RequestTag/Project" = "brd-agent-v2"
          }
        }
      },
      {
        # RunInstances juga menyentuh resource yang SUDAH ada (AMI, subnet
        # default, network interface, DAN security group default VPC yang
        # dipakai instance) -- resource ini tidak perlu/bisa dibatasi tag
        # karena bukan resource yang baru dibuat pada request ini.
        # Dibatasi ke region saja. (security-group ditambahkan setelah
        # 403 nyata saat RunInstances mencoba memakai default security
        # group VPC yang belum bertag Project.)
        Sid    = "Ec2RunInstancesSupportingResources"
        Effect = "Allow"
        Action = [
          "ec2:RunInstances",
        ]
        Resource = [
          "arn:aws:ec2:${var.aws_region}::image/*",
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:subnet/*",
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:network-interface/*",
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:security-group/*",
          # Root/attached EBS volume created as part of the same
          # RunInstances call -- confirmed via a real 403 during apply
          # ("no identity-based policy allows ec2:RunInstances" on
          # resource volume/*). It DOES get the RequestTag/Project tag
          # (via CreateTags propagation from the instance's TagSpecifications),
          # but RunInstances itself still needs an unconditional grant here
          # because the volume doesn't exist yet at authorization time.
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:volume/*",
          # The (pre-existing) key pair referenced by RunInstances also
          # needs its own grant here -- confirmed via a real 403
          # ("no identity-based policy allows ec2:RunInstances" on
          # resource key-pair/*).
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key-pair/*",
        ]
        Condition = {
          StringEquals = { "aws:RequestedRegion" = var.aws_region }
        }
      },
      {
        # CreateSecurityGroup butuh izin pada VPC yang SUDAH ADA (tempat
        # security group itu dibuat), bukan hanya pada security group yang
        # baru dibuat -- VPC ini tidak bisa/tidak perlu dibatasi tag karena
        # bukan resource baru pada request ini. Dibatasi ke region saja.
        # (Ditambahkan setelah 403 nyata: "no identity-based policy allows
        # ec2:CreateSecurityGroup" pada resource vpc/vpc-xxx.)
        Sid    = "Ec2CreateSecurityGroupOnExistingVpc"
        Effect = "Allow"
        Action = [
          "ec2:CreateSecurityGroup",
        ]
        Resource = [
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:vpc/*",
        ]
        Condition = {
          StringEquals = { "aws:RequestedRegion" = var.aws_region }
        }
      },
      {
        # Mutasi/hapus/start/stop HANYA pada instance & resource pendukung
        # yang sudah bertag Project=brd-agent-v2 -- EC2 instance aurika
        # (tag Project=aurika) TIDAK PERNAH bisa disentuh oleh user ini
        # sama sekali, apapun yang terjadi di sisi project lain.
        Sid    = "Ec2ManageOwnTaggedResourcesOnly"
        Effect = "Allow"
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:RebootInstances",
          "ec2:TerminateInstances",
          "ec2:ModifyInstanceAttribute",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:DeleteSecurityGroup",
          "ec2:DeleteKeyPair",
          "ec2:DeleteVolume",
          "ec2:AttachVolume",
          "ec2:DetachVolume",
          "ec2:CreateSnapshot",
          "ec2:DeleteSnapshot",
          "ec2:AssociateAddress",
          "ec2:DisassociateAddress",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion"     = var.aws_region
            "ec2:ResourceTag/Project" = "brd-agent-v2"
          }
        }
      },
      {
        # Elastic IP: allocate/release tidak mendukung ResourceTag condition
        # dengan baik di semua kasus, dibatasi ke region saja -- risiko
        # rendah (hanya menambah/melepas alamat IP, bukan mengontrol
        # instance manapun).
        Sid    = "Ec2ElasticIpJakartaOnly"
        Effect = "Allow"
        Action = [
          "ec2:AllocateAddress",
          "ec2:ReleaseAddress",
        ]
        Resource = "*"
        Condition = {
          StringEquals = { "aws:RequestedRegion" = var.aws_region }
        }
      },
    ]
  })
}

resource "aws_iam_user_policy_attachment" "brd_agent_v2_ec2_only" {
  user       = aws_iam_user.brd_agent_v2.name
  policy_arn = aws_iam_policy.brd_agent_v2_ec2_only.arn
}

# Pastikan user ini TIDAK BISA mengubah policy-nya sendiri atau membuat
# user/role IAM baru -- tanpa ini, user bisa "keluar" dari batasan EC2 di
# atas dengan memberi dirinya izin tambahan sendiri.
resource "aws_iam_user_policy" "brd_agent_v2_deny_iam" {
  name = "${var.project_name}-deny-iam-self-escalation"
  user = aws_iam_user.brd_agent_v2.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "DenyAllIam"
      Effect   = "Deny"
      Action   = "iam:*"
      Resource = "*"
    }]
  })
}
