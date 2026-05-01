#!/usr/bin/env python3
"""
🚀 API Server - يربط واجهة December بالسرب الحقيقي
"""
import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from swarm import swarm_search

class SwarmAPI(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/search':
            params = parse_qs(parsed.query)
            query = params.get('q', [''])[0]
            
            if not query:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "اكتب موضوعاً للبحث"}).encode())
                return
            
            print(f"🔍 بحث: {query}")
            report = swarm_search(query)
            
            self._set_headers()
            self.wfile.write(json.dumps({"report": report, "query": query}).encode())
        
        elif parsed.path == '/health':
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

if __name__ == "__main__":
    port = 5001
    print(f"🚀 خادم السرب يعمل على http://localhost:{port}")
    print(f"🔍 جرب: http://localhost:{port}/search?q=الذكاء الاصطناعي")
    
    server = HTTPServer(('0.0.0.0', port), SwarmAPI)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 توقف الخادم.")
