from http.server import BaseHTTPRequestHandler
import json

meme_upvotes_count = 0

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.end_headers()
        response_data = {'count': meme_upvotes_count}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_POST(self):
        global meme_upvotes_count
        meme_upvotes_count += 1

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.end_headers()
        response_data = {'newCount': meme_upvotes_count}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    # def do_OPTIONS(self):
    #     self.send_response(200)
    #     self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
    #     self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    #     self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    #     self.end_headers()