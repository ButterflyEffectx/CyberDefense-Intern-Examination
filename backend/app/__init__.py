import os 
from opensearchpy import OpenSearch, RequestsHttpConnection

def get_client():
    host = os.getenv("OPENSEARCH_HOST", "opensearch")
    port = int(os.getenv("OPENSEARCH_PORT", "9200"))
    use_ssl = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"

    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress = True,
        use_ssl=use_ssl,
        verify_certs = False,
        connection_class=RequestsHttpConnection,
    )
    return client