#!/bin/bash
echo "🔍 استرجاع قالب من RAG..."
python3 ~/jonjon-lab/rag_to_chat.py "$1"
echo ""
echo "🌐 افتح Open Web UI: http://localhost:3009"
echo "📋 بعد تطوير القالب، انسخه ثم استخدم أمر: save-html"
echo ""
