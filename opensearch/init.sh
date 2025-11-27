#!/bin/sh
sleep 25

echo "==> Applying index template"
curl -X PUT "http://opensearch:9200/_index_template/logs_template" \
  -H "Content-Type: application/json" \
  --data @/init/index_template.json

echo "==> Applying ILM policy"
curl -X PUT "http://opensearch:9200/_plugins/_ism/policies/logs_policy" \
  -H "Content-Type: application/json" \
  --data @/init/ilm_policy.json

echo "==> OpenSearch init done."
