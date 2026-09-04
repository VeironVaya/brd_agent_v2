data "aws_caller_identity" "current" {}

resource "aws_iam_user" "brd_agent_v2" {
  name = "${var.project_name}-ec2-deployer"

  tags = {
    Name = "${var.project_name}-ec2-deployer"
  }
}

resource "aws_iam_policy" "brd_agent_v2_ec2_only" {
  name        = "${var.project_name}-ec2-only-policy"
  description = "Izin terbatas: EC2 saja, region ap-southeast-3 saja, mutasi/hapus hanya pada resource bertag Project=brd-agent-v2."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
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
        Sid    = "Ec2CreateWithRequiredTag"
        Effect = "Allow"
        Action = [
          "ec2:RunInstances",
          "ec2:CreateSecurityGroup",
          "ec2:CreateKeyPair",
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
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:volume/*",
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key-pair/*",
        ]
        Condition = {
          StringEquals = { "aws:RequestedRegion" = var.aws_region }
        }
      },
      {
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
