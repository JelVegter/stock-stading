# # S3 buckets
# resource "aws_s3_bucket" "main" {
#   bucket = "${var.project}-s3-eu"
#   acl    = "private"
#   region = "eu-central-1"
# }
data "aws_availability_zones" "available" {}


module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name                 = "${var.project}-vpc-${var.environment}-eu"
  cidr                 = "10.0.0.0/16"
  azs                  = data.aws_availability_zones.available.names
  public_subnets       = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_db_subnet_group" "subnet" {
  name       = "${var.project}-subnet-${var.environment}-eu"
  subnet_ids = module.vpc.public_subnets

}

resource "aws_security_group" "rds" {
  name = "${var.project}-sg-${var.environment}-eu"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

resource "aws_db_parameter_group" "db" {
  name   = "${var.project}-dbpg-${var.environment}-eu"
  family = "postgres14"

  parameter {
    name  = "log_connections"
    value = "1"
  }
}

resource "aws_security_group_rule" "allow_all_outbound" {
  type              = "egress"
  security_group_id = aws_security_group.rds.id

  from_port   = 0
  to_port     = 0
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]
}


resource "aws_db_instance" "stocktrading" {
  identifier             = "${var.project}-db-${var.environment}-eu"
  db_name                = var.db_name
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  engine                 = "postgres"
  engine_version         = "14.3"
  username               = "edu"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.subnet.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.db.name
  publicly_accessible    = true
  skip_final_snapshot    = true
}


# Elastic Container Registry
resource "aws_ecr_repository" "container_registry" {
  name                 = "${var.project}-ecr-${var.environment}-eu"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM role
resource "aws_iam_role" "apprunner_role" {
  name = "apprunner-${var.project}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "build.apprunner.amazonaws.com",
            "tasks.apprunner.amazonaws.com"
          ]
        }
      }
    ]
  })
}

resource "aws_ecr_repository_policy" "apprunner_policy" {
  repository = aws_ecr_repository.container_registry.name
  name = "apprunner-${var.project}-policy"
  role = aws_iam_role.apprunner_role.id

  policy = jsonencode({
    Version = "2008-10-17"
    Statement = [
      {
        Sid       = "AppRunnerAccess"
        Effect    = "Allow"
        Principal = {
          Service = "apprunner.amazonaws.com"
        }
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeImages"
        ]
      }
    ]
  })
}



resource "aws_apprunner_service" "stocktrading" {
  service_name = "apprunner-${var.project}-eu"

  source_configuration {
    image_repository {
      image_configuration {
        port = "8080"
      }

      image_identifier      = aws_ecr_repository.container_registry.repository_url
      image_repository_type = "ECR" 
    }

    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_role.arn
    }
  }
}

output "apprunner_service_stocktrading" {
  value = aws_apprunner_service.stocktrading
}
