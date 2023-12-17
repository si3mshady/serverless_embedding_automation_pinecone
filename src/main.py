import json, boto3
from transformers import AutoModel, AutoTokenizer
import torch
import pinecone      

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')



def handler(event, context):
    print(event)
    pinecone.init( api_key='b0', environment='gcp-starter')
    # Get statistics about the index
    index = pinecone.Index('pipeline')
    res = index.describe_index_stats()
    vector_count = res.get('total_vector_count')
    
    s3 = boto3.client('s3')
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    local_file_path = '/tmp/' + object_key


     # Download the object from S3 and save it to /tmp
    s3.download_file(bucket_name, object_key, local_file_path)
    
    # Open the file and add its content to the sentences array
    with open(local_file_path, 'r') as file:
        content = file.read()
        sentences = ["this is a test", content]
    
    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True,  return_tensors="pt")
    outputs = model(**encoded_input)
    # Extract the sentence embedding from the model output
    embedding = torch.mean(outputs.last_hidden_state, dim=1)
    # Insert the embedding into the Pinecone vector store
    
    upsert_response = index.upsert(
    vectors=[
        {
            'id': str(int(vector_count) + 1),
            'values': embedding[0].tolist(),
            'metadata': {'original_text': str(content)}
        }
    ],
    namespace='example-namespace'
        )
   
    # implement
    return {
        'statusCode': 200,
        'body': json.dumps('Here are your encoded inputs!  ' +  str(encoded_input))
    }

