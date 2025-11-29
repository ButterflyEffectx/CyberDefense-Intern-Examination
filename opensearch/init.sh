#!/bin/sh
sleep 25

echo "==> Applying index template to OpenSearch"
curl -X PUT "http://opensearch:9200/_index_template/logs_template" -H 'Content-Type: application/json' -d @/init/index_template.json

echo "==> Deleting old ISM policy if exists"
curl -X DELETE "http://opensearch:9200/_plugins/_ism/policies/logs_policy"

echo "==> Applying ILM policy to OpenSearch"
curl -X PUT "http://opensearch:9200/_plugins/_ism/policies/logs_policy" -H 'Content-Type: application/json' -d @/init/ilm_policy.json

echo "==> Initialization completed"