from opensearchpy import OpenSearch
import os

def get_client():
    host = os.getenv("OPENSEARCH_HOST", "opensearch")
    port = int(os.getenv("OPENSEARCH_PORT", "9200"))
    
    client = OpenSearch(
        hosts = [{"host": host, "port": port}],
        http_compress = True,
        use_ssl = False,
        verify_certs = False
    )
    return client