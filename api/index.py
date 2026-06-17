"""Vercel Serverless Function for Hotspot API"""
from http.server import BaseHTTPRequestHandler
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "name": "全网热点聚合 API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "/api/hot": "获取所有平台热点",
                "/api/platforms": "获取平台列表"
            }
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        return
