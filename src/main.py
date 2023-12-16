import json
from transformers import AutoModel, AutoTokenizer
import torch
import pinecone      


pinecone.init( api_key="0', environment='gcp-starter')

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

index = pinecone.Index('pipeline')

def handler(event, context):
    sentences = ["this is a test"]
    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True,  return_tensors="pt")
    outputs = model(**encoded_input)
    # Extract the sentence embedding from the model output
    embedding = torch.mean(outputs.last_hidden_state, dim=1)
    # Insert the embedding into the Pinecone vector store
    
    upsert_response = index.upsert(
    vectors=[
        {
            'id': 'si3mshady',
            'values': embedding[0].tolist(),
            'metadata': {'original_text': sentences[0]}
        }
    ],
    namespace='example-namespace'
        )
   
    # implement
    return {
        'statusCode': 200,
        'body': json.dumps('Here are your encoded inputs!  ' +  str(encoded_input))
    }


