sudo aws ecr get-login-password --region us-east-1 | \
 docker login --username AWS --password-stdin 335055665325.dkr.ecr.us-east-1.amazonaws.com/genai




 docker login -u AWS -p $(aws ecr get-login-password --region us-east-1)  335055665325.dkr.ecr.us-east-1.amazonaws.com/genai



sudo docker tag si3mshady/llmautomation   335055665325.dkr.ecr.us-east-1.amazonaws.com/genai:1

docker push 335055665325.dkr.ecr.us-east-1.amazonaws.com/genai:1