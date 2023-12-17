import pinecone      


pinecone.init( api_key='be7e40', environment='gcp-starter')

index = pinecone.Index('pipeline')

res = index.describe_index_stats()

res.get('total_vector_count')
