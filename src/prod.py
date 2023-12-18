# Import necessary libraries
import json
import boto3
from transformers import AutoModel, AutoTokenizer
import torch
import pinecone

# Initialize Pinecone with API key and environment
def initialize_pinecone():
    pinecone.init(api_key='b0', environment='gcp-starter')

# Create a Pinecone index named 'pipeline'
def create_pinecone_index():
    return pinecone.Index('pipeline')

# Download a file from Amazon S3 bucket to a local file path
def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_key, local_file_path)

# Read the content of a file given its file path
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Tokenize a list of sentences using a pre-trained transformer model
def tokenize_sentences(sentences):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    return tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

# Get the mean sentence embedding from the model outputs
def get_sentence_embedding(model_outputs):
    return torch.mean(model_outputs.last_hidden_state, dim=1)

# Upsert a sentence embedding along with metadata to a Pinecone index
def upsert_embedding_to_pinecone(index, embedding, content):
    vector_count = index.describe_index_stats().get('total_vector_count')
    vector_id = str(int(vector_count) + 1)

    index.upsert(
        vectors=[{
            'id': vector_id,
            'values': embedding[0].tolist(),
            'metadata': {'original_text': str(content)}
        }],
        namespace='example-namespace'
    )

# Lambda function handler that processes events triggered by an S3 upload
def handler(event, context):
    # Print the event received (for debugging purposes)
    print(event)

    # Initialize Pinecone
    initialize_pinecone()

    # Create a Pinecone index
    index = create_pinecone_index()

    # Extract S3 bucket and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Set local file path for downloaded file
    local_file_path = '/tmp/' + object_key

    # Download the file from S3 to the local file path
    download_file_from_s3(bucket_name, object_key, local_file_path)

    # Read the content of the file
    content = read_file_content(local_file_path)

    # Prepare a list of sentences for tokenization
    sentences = ["this is a test", content]

    # Tokenize the sentences using a transformer model
    encoded_input = tokenize_sentences(sentences)

    # Load a pre-trained transformer model
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

    # Get model outputs for the tokenized input
    outputs = model(**encoded_input)

    # Get the sentence embedding from the model outputs
    embedding = get_sentence_embedding(outputs)

    # Upsert the sentence embedding and metadata to the Pinecone index
    upsert_embedding_to_pinecone(index, embedding, content)

    # Return a response indicating success
    return {
        'statusCode': 200,
        'body': json.dumps('Here are your encoded inputs! ' + str(encoded_input))
    }
