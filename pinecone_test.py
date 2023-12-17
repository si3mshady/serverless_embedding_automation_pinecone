import pinecone      


pinecone.init( api_key='be794e59-a8e4-4081-a5ce-530689e82e40', environment='gcp-starter')

index = pinecone.Index('pipeline')

res = index.describe_index_stats()

res.get('total_vector_count')