import boto3
import docker

# Initialize the ECR client
ecr_client = boto3.client('ecr', region_name='your-region')

# Initialize the Docker client
docker_client = docker.from_env()

# Build the Docker image
docker_image, build_logs = docker_client.images.build(path='path-to-dockerfile', tag='your-image-tag')

# Get the ECR authorization token
auth_token = ecr_client.get_authorization_token()
username, password = base64.b64decode(auth_token['authorizationData'][0]['authorizationToken']).decode().split(':')

# Tag the Docker image with the ECR repository URI
ecr_repository_uri = 'your-account-id.dkr.ecr.your-region.amazonaws.com/your-repository'
docker_image.tag(ecr_repository_uri, tag='your-image-tag')

# Push the Docker image to ECR
docker_client.login(username, password, registry=auth_token['authorizationData'][0]['proxyEndpoint'])
docker_client.images.push(ecr_repository_uri, tag='your-image-tag')