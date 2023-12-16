#!/bin/bash

# Set variables
local_directory="genai"


# Create the local directory if it does not exist
if [ ! -d "$local_directory" ]; then
  mkdir -p $local_directory
fi

# Create a heredoc to define the Dockerfile content
cat > Dockerfile <<EOF
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements.txt
COPY requirements.txt \${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy all files in ./src
COPY src/* \${LAMBDA_TASK_ROOT}

# Set the CMD to your handler.
CMD [ "main.handler" ]
EOF

# Build the Docker image
docker build -t genfactory . --no-cache


