from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json') # Changed to JSON content type
        self.end_headers()
        response_data = {'message': 'Hello world, supreme leader is the man'}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return