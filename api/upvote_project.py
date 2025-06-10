from http.server import BaseHTTPRequestHandler
import json
import os
import redis

try:
    r =  redis.from_url(os.environ.get("REDIS_URL","redis://localhost:6379/0"))
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    r = None

class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if r is None:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Redis connection failed'}).encode('utf-8'))
            return
        
        try:
            count_bytes = r.get('project_upvotes')
            project_upvotes_count = int(count_bytes) if count_bytes else 0
        except Exception as e:
            print(f"Error getting project count from Redis: {e}")
            project_upvotes_count = 0
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.end_headers()
        response_data = {'count': project_upvotes_count}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_POST(self):

        if r is None:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Redis connection failed'}).encode('utf-8'))
            return
        
        try:
            project_upvotes_count = r.incr('project_upvotes')
        except Exception as e:
            print(f"Error incrementing project count in Redis: {e}")
            project_upvotes_count = -1

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.end_headers()
        response_data = {'newCount': project_upvotes_count}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()