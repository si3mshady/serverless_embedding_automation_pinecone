provider "aws" {
  region = "us-east-1" # Set your desired AWS region
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