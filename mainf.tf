variable "aws_region" {
  type    = string
  default = "us-east-1" # Set your desired AWS region
}

variable "docker_image_tag" {
  type    = string
  default = "dev"
}

variable "ecr_repository_name" {
  type    = string
  default = "genai-automated-deployments"
}

variable "lambda_function_name" {
  type    = string
  default = "genai-pinecone-automation-v2"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "s3_bucket_name" {
  type    = string
  default = "pinecone-genai-bucket"
}

provider "aws" {
  region = var.aws_region
}

data "aws_ecr_repository" "genai-automated-deployments-data" {
  name = var.ecr_repository_name
}

resource "aws_ecr_repository" "genai-automated-deployments" {
  name = var.ecr_repository_name
}

module "ecr_docker_build" {
  source            = "github.com/onnimonni/terraform-ecr-docker-build-module"
  dockerfile_folder = path.module
  docker_image_tag  = var.docker_image_tag
  aws_region        = var.aws_region
  ecr_repository_url = aws_ecr_repository.genai-automated-deployments.repository_url
}

resource "aws_lambda_function" "genai-pinecone-automation-v2" {
  function_name = var.lambda_function_name
  timeout       = 90 # seconds
  image_uri     = "${data.aws_ecr_repository.genai-automated-deployments-data.repository_url}:${var.docker_image_tag}"
  package_type  = "Image"
  role          = aws_iam_role.genai-assume-role-lambda.arn

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}

resource "aws_iam_role" "genai-assume-role-lambda" {
  name = "genai-assume-role-lambda"

  assume_role_policy = jsonencode({
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_s3_bucket_notification" "aws-lambda-trigger" {
  bucket = var.s3_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.genai-pinecone-automation-v2.arn
    events              = ["s3:ObjectCreated:*"]
    # filter_prefix       = "file-prefix"
    filter_suffix       = ".txt"
  }
}

resource "aws_lambda_permission" "invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.genai-pinecone-automation-v2.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.s3_bucket_name}"
}
