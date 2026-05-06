#!/bin/bash
KNOWLEDGE_ID="22e19db8-d3a-420c-a7a0-356827200564"  # غيرها لمعرفك

for file in /Users/hichem/jonjon-lab/upload/*.html; do
  echo "رفع: $(basename "$file")"
  curl -X POST "http://localhost:3009/api/v1/knowledge/${KNOWLEDGE_ID}/files/upload" \
    -F "file=@$file"
  echo ""
done
