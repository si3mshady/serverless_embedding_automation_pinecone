provider "aws" {
  region = "us-east-1" # Set your desired AWS region
}

data "aws_ecr_repository" "genai-automated-deployments-data" {
  name = "genai-automated-deployments"
}


# Create ECR repository
resource "aws_ecr_repository" "genai-automated-deployments" {
  name = "genai-automated-deployments"
}

# Build Docker image and push to ECR from folder: ./example-service-directory
module "ecr_docker_build" {
  source = "github.com/onnimonni/terraform-ecr-docker-build-module"

  # Absolute path into the service which needs to be build
  dockerfile_folder = "${path.module}"

  # Tag for the builded Docker image (Defaults to 'latest')
  docker_image_tag = "dev"
  
  # The region which we will log into with aws-cli
  aws_region = "us-east-1"

  # ECR repository where we can push
  ecr_repository_url = "${aws_ecr_repository.genai-automated-deployments.repository_url}"
}

resource "aws_lambda_function" "genai-pinecone-automation-v2" {
  function_name = "genai-pinecone-automation-v2"
  timeout       = 90 # seconds
  image_uri     = "${data.aws_ecr_repository.genai-automated-deployments-data.repository_url}:dev"
  package_type  = "Image"

  role = aws_iam_role.genai-assume-role-lambda.arn

  environment {
    variables = {
      ENVIRONMENT = "dev"
    }
  }
}

resource "aws_iam_role" "genai-assume-role-lambda" {
  name = "genai-assume-role-lambda"

  assume_role_policy = jsonencode({
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}