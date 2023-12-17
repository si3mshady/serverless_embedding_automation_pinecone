import json
import boto3
from transformers import AutoModel, AutoTokenizer
import torch
import pinecone

def initialize_pinecone():
    pinecone.init(api_key='b0', environment='gcp-starter')

def create_pinecone_index():
    return pinecone.Index('pipeline')

def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_key, local_file_path)

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def tokenize_sentences(sentences):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    return tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

def get_sentence_embedding(model_outputs):
    return torch.mean(model_outputs.last_hidden_state, dim=1)

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

def handler(event, context):
    print(event)
    initialize_pinecone()

    index = create_pinecone_index()

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    local_file_path = '/tmp/' + object_key

    download_file_from_s3(bucket_name, object_key, local_file_path)

    content = read_file_content(local_file_path)
    sentences = ["this is a test", content]

    encoded_input = tokenize_sentences(sentences)

    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    outputs = model(**encoded_input)

    embedding = get_sentence_embedding(outputs)

    upsert_embedding_to_pinecone(index, embedding, content)

    return {
        'statusCode': 200,
        'body': json.dumps('Here are your encoded inputs! ' + str(encoded_input))
    }
